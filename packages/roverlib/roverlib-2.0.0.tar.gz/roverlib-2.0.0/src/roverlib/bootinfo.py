from enum import Enum
from typing import Optional, Union, Any, List, TypeVar, Type, Callable, cast

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except Exception:
            pass
    assert False


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class TypeEnum(Enum):
    """The type of this configuration option"""

    NUMBER = "number"
    STRING = "string"


class Configuration:
    name: Optional[str]
    """Unique name of this configuration option"""

    tunable: Optional[bool]
    """Whether or not this value can be tuned (ota)"""

    type: Optional[TypeEnum]
    """The type of this configuration option"""

    value: Optional[Union[float, str]]
    """The value of this configuration option, which can be a string or float"""

    def __init__(self, name: Optional[str], tunable: Optional[bool], type: Optional[TypeEnum], value: Optional[Union[float, str]]) -> None:
        self.name = name
        self.tunable = tunable
        self.type = type
        self.value = value

    @staticmethod
    def from_dict(obj: Any) -> 'Configuration':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        tunable = from_union([from_bool, from_none], obj.get("tunable"))
        type = from_union([TypeEnum, from_none], obj.get("type"))
        value = from_union([from_float, from_str, from_none], obj.get("value"))
        return Configuration(name, tunable, type, value)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.tunable is not None:
            result["tunable"] = from_union([from_bool, from_none], self.tunable)
        if self.type is not None:
            result["type"] = from_union([lambda x: to_enum(TypeEnum, x), from_none], self.type)
        if self.value is not None:
            result["value"] = from_union([to_float, from_str, from_none], self.value)
        return result


class Stream:
    address: Optional[str]
    """The (zmq) socket address that input can be read on"""

    name: Optional[str]
    """The name of the stream as outputted by the dependency service"""

    def __init__(self, address: Optional[str], name: Optional[str]) -> None:
        self.address = address
        self.name = name

    @staticmethod
    def from_dict(obj: Any) -> 'Stream':
        assert isinstance(obj, dict)
        address = from_union([from_str, from_none], obj.get("address"))
        name = from_union([from_str, from_none], obj.get("name"))
        return Stream(address, name)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.address is not None:
            result["address"] = from_union([from_str, from_none], self.address)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        return result


class Input:
    service: Optional[str]
    """The name of the service for this dependency"""

    streams: Optional[List[Stream]]

    def __init__(self, service: Optional[str], streams: Optional[List[Stream]]) -> None:
        self.service = service
        self.streams = streams

    @staticmethod
    def from_dict(obj: Any) -> 'Input':
        assert isinstance(obj, dict)
        service = from_union([from_str, from_none], obj.get("service"))
        streams = from_union([lambda x: from_list(Stream.from_dict, x), from_none], obj.get("streams"))
        return Input(service, streams)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.service is not None:
            result["service"] = from_union([from_str, from_none], self.service)
        if self.streams is not None:
            result["streams"] = from_union([lambda x: from_list(lambda x: to_class(Stream, x), x), from_none], self.streams)
        return result


class Output:
    address: Optional[str]
    """The (zmq) socket address that output can be written to"""

    name: Optional[str]
    """Name of the output published by this service"""

    def __init__(self, address: Optional[str], name: Optional[str]) -> None:
        self.address = address
        self.name = name

    @staticmethod
    def from_dict(obj: Any) -> 'Output':
        assert isinstance(obj, dict)
        address = from_union([from_str, from_none], obj.get("address"))
        name = from_union([from_str, from_none], obj.get("name"))
        return Output(address, name)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.address is not None:
            result["address"] = from_union([from_str, from_none], self.address)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        return result


class Tuning:
    address: Optional[str]
    """(If enabled) the (zmq) socket address that tuning data can be read from"""

    enabled: Optional[bool]
    """Whether or not live (ota) tuning is enabled"""

    def __init__(self, address: Optional[str], enabled: Optional[bool]) -> None:
        self.address = address
        self.enabled = enabled

    @staticmethod
    def from_dict(obj: Any) -> 'Tuning':
        assert isinstance(obj, dict)
        address = from_union([from_str, from_none], obj.get("address"))
        enabled = from_union([from_bool, from_none], obj.get("enabled"))
        return Tuning(address, enabled)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.address is not None:
            result["address"] = from_union([from_str, from_none], self.address)
        if self.enabled is not None:
            result["enabled"] = from_union([from_bool, from_none], self.enabled)
        return result


class Service:
    """The object that injected into a rover process by roverd and then parsed by roverlib to be
    made available for the user process
    """
    configuration: List[Configuration]
    inputs: List[Input]
    """The resolved input dependencies"""

    name: Optional[str]
    """The name of the service (only lowercase letters and hyphens)"""

    outputs: List[Output]
    tuning: Tuning
    version: Optional[str]
    """The specific version of the service"""

    service: Any

    def __init__(self, configuration: List[Configuration], inputs: List[Input], name: Optional[str], outputs: List[Output], tuning: Tuning, version: Optional[str], service: Any) -> None:
        self.configuration = configuration
        self.inputs = inputs
        self.name = name
        self.outputs = outputs
        self.tuning = tuning
        self.version = version
        self.service = service

    @staticmethod
    def from_dict(obj: Any) -> 'Service':
        assert isinstance(obj, dict)
        configuration = from_list(Configuration.from_dict, obj.get("configuration"))
        inputs = from_list(Input.from_dict, obj.get("inputs"))
        name = from_union([from_str, from_none], obj.get("name"))
        outputs = from_list(Output.from_dict, obj.get("outputs"))
        tuning = Tuning.from_dict(obj.get("tuning"))
        version = from_union([from_str, from_none], obj.get("version"))
        service = obj.get("service")
        return Service(configuration, inputs, name, outputs, tuning, version, service)

    def to_dict(self) -> dict:
        result: dict = {}
        result["configuration"] = from_list(lambda x: to_class(Configuration, x), self.configuration)
        result["inputs"] = from_list(lambda x: to_class(Input, x), self.inputs)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        result["outputs"] = from_list(lambda x: to_class(Output, x), self.outputs)
        result["tuning"] = to_class(Tuning, self.tuning)
        if self.version is not None:
            result["version"] = from_union([from_str, from_none], self.version)
        result["service"] = self.service
        return result

def service_from_dict(s: Any) -> Service:
    return Service.from_dict(s)


def service_to_dict(x: Service) -> Any:
    return to_class(Service, x)
