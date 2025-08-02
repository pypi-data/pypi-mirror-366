"""PTAG ~ 'Pydantic Type Adapter GRPC'"""

import inspect
import types
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Dict, get_type_hints, Tuple, TypeVar, List

from grpc import ServicerContext, StatusCode, insecure_channel
from loguru import logger
from pydantic import TypeAdapter

from .PTAG_pb2 import PTAGResponse, PTAGRequest
from .PTAG_pb2_grpc import PTAGServiceServicer, add_PTAGServiceServicer_to_server, PTAGServiceStub
from google.protobuf.message import Message


T = TypeVar("T")
REQUEST_ID = "request_id"
REQUEST_ID_DEFAULT = "SYSTEM_LOG"
ArgName = str
ArgDefault = any
ArgMetadata = Tuple[ArgName, type, ArgDefault]
ArgsMetadata = List[ArgMetadata]
empty = inspect.Parameter.empty


@contextmanager
def contextualize(context: ServicerContext):
    metadata = dict(context.invocation_metadata())
    request_id = metadata.get(REQUEST_ID, REQUEST_ID_DEFAULT)
    with logger.contextualize(request_id=request_id):
        yield


@dataclass
class MethodMetadata:
    name: str
    method: Callable
    args_metadata: ArgsMetadata
    args_adapter: TypeAdapter
    result_adapter: TypeAdapter


# kwargs -> tuple


def _parse_param(param) -> ArgMetadata | None:
    name = param.name
    if name == "self":
        return
    param_type = param.annotation
    if param_type == empty:
        raise ValueError(f"Not found type for parameter `{name}`")
    # todo validate param_type: allow only builtins and pydantic
    default = param.default
    if default != empty and not isinstance(default, param_type):
        raise ValueError(f"For argument `{name}` type {param_type} is not aligned with default value: {default}")
    return (name, param_type, default)


def _parse_args(method: Callable) -> ArgsMetadata:
    signature = inspect.signature(method)
    parameters = signature.parameters.values()
    res_0 = [_parse_param(param) for param in parameters]
    res = [am for am in res_0 if am]
    return res


def _bind_arg(arg_metadata: ArgMetadata, kwargs: dict):
    name, arg_type, default = arg_metadata
    if name in kwargs:
        arg_val = kwargs[name]
        if not isinstance(arg_val, arg_type):
            raise ValueError(f"Argument `{name}`: expected type `{arg_type}`, found: {type(arg_val)}")
    elif default is not empty:
        arg_val = default
    else:
        raise ValueError(f"Argument `{name}`: not found")
    return arg_val


def _bind_args(args_metadata: ArgsMetadata, kwargs: dict) -> tuple:
    excess_args = set(kwargs) - set(am[0] for am in args_metadata)
    if excess_args:
        raise ValueError(f"Unexpected excess arguments passed: {excess_args}")
    args = tuple(_bind_arg(am, kwargs) for am in args_metadata)
    return args


def prettify_args_metatadata(args_metadata: ArgsMetadata):
    return ", ".join(f"{an}:{at}" if ad is empty else f"{an}:{at}={ad}" for an, at, ad in args_metadata)


def filter_request_id(args_metadata: ArgsMetadata) -> ArgsMetadata:
    if not args_metadata:
        return args_metadata
    am_last = args_metadata[-1]
    if am_last == REQUEST_ID:
        # todo check default arg
        args_metadata.pop()
        return args_metadata
    for am in args_metadata[:-1]:
        if am[0] == REQUEST_ID:
            am_pretty = prettify_args_metatadata(args_metadata)
            raise ValueError(f"Bad signature [{am_pretty}]: unexpected request_id on non-last position")
    return args_metadata


def _analyze_method(method: Callable) -> dict | None:
    """
    Analyze a method's type hints and return Pydantic adapters for the argument and return value.
    """
    method_name = method.__name__
    if method_name.startswith("_"):
        return

    type_hints = get_type_hints(method)
    args_metadata = _parse_args(method)
    args_metadata = filter_request_id(args_metadata)
    args_type = Tuple[*(am[1] for am in args_metadata)]
    result_type = type_hints.get("return")
    if not result_type:
        raise ValueError(f"return type annotation for method `{method_name}` should present but not found!")
    args_adapter = TypeAdapter(args_type)
    result_adapter = TypeAdapter(result_type)
    method_metadata = MethodMetadata(
        method=method,
        name=method_name,
        args_metadata=args_metadata,
        args_adapter=args_adapter,
        result_adapter=result_adapter,
    )
    return method_metadata


def _analyze_obj_methods(obj) -> Dict[str, MethodMetadata]:
    methods = {}
    for name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
        # also can see only on method from the base interface class
        method_metadata = _analyze_method(method)
        if method_metadata:
            methods[name] = method_metadata
    return methods


def _analyze_interface_methods(interface) -> Dict[str, MethodMetadata]:
    methods = {}
    for name, method in inspect.getmembers(interface, predicate=inspect.isfunction):
        method_metadata = _analyze_method(method)
        if method_metadata is None:
            raise ValueError(f"Failed to parse interface method: {method.__name__}")
        methods[name] = method_metadata
    return methods


class WrappedPTAGService(PTAGServiceServicer):
    def __init__(self, service_object):
        self.methods = _analyze_obj_methods(service_object)

    def Invoke(self, request: Message, context: ServicerContext):
        method_name = request.FunctionName
        method_metadata = self.methods.get(method_name)

        if method_metadata is None:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(f"Method {method_name} not found")
            return PTAGResponse()

        method = method_metadata.method
        args_adapter = method_metadata.args_adapter
        result_adapter = method_metadata.result_adapter

        # [args_bytes] -(args_adapter.validate)-> [args] -(method)-> [result] -(result_adapter.dump)-> [result_bytes]
        try:
            input_obj = args_adapter.validate_json(request.Payload)
            with contextualize(context):
                output_obj = method(*input_obj)
            payload = result_adapter.dump_json(output_obj)
            return PTAGResponse(FunctionName=method_name, Payload=payload)
        except Exception as e:
            logger.exception(f"Failed to process request: {e}")
            context.set_code(StatusCode.INTERNAL)
            context.set_details(str(e))
            return PTAGResponse()


def make_proxy(grpc_stub, method_metadata: MethodMetadata):
    mm = method_metadata

    # only **kwargs supported
    # [args] -(args_adapter.dump)-> [args_bytes] -(send)-> [result_bytes] -(return_adapter.validate)-> [result]
    def proxy(self, *args, **kwargs):
        if args:
            raise ValueError(f"Method `{mm.name}`: only kwargs supported, but args found: `{args}`")
        request_id = kwargs.pop(REQUEST_ID, None)
        metadata = [(REQUEST_ID, request_id)] if request_id else []

        args = _bind_args(mm.args_metadata, kwargs)
        args_bytes = mm.args_adapter.dump_json(args)
        request = PTAGRequest(FunctionName=mm.name, Payload=args_bytes)
        response = grpc_stub.Invoke(request, metadata=metadata)
        result_bytes = response.Payload
        result = mm.result_adapter.validate_json(result_bytes)
        return result

    return proxy


class ClientProxy:
    def __init__(self, service_interface, grpc_stub):
        methods = _analyze_interface_methods(service_interface)

        for mm in methods.values():
            proxy = make_proxy(grpc_stub, mm)
            bound_method = types.MethodType(proxy, self)
            setattr(self, mm.name, bound_method)


def ptag_attach(server, service_object):
    """
    Attach a service object implementing the interface to a gRPC server.
    """
    service = WrappedPTAGService(service_object)
    add_PTAGServiceServicer_to_server(service, server)


def ptag_client(service_interface: T, address: str) -> T:
    """
    Create a dynamic client for the given interface at the provided gRPC address.
    """
    # todo fix: use AbstractClient here?
    channel = insecure_channel(address)
    stub = PTAGServiceStub(channel)
    return ClientProxy(service_interface, stub)
