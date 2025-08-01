from typing import ClassVar, overload

class Config:
    configVersion: str | None
    model: Model
    @overload
    def __init__(self) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: depthai.nn_archive.v1.Config) -> None

        2. __init__(self: depthai.nn_archive.v1.Config, configVersion: str, model: depthai.nn_archive.v1.Model) -> None
        """
    @overload
    def __init__(self, configVersion: str, model: Model) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: depthai.nn_archive.v1.Config) -> None

        2. __init__(self: depthai.nn_archive.v1.Config, configVersion: str, model: depthai.nn_archive.v1.Model) -> None
        """

class DataType:
    __members__: ClassVar[dict] = ...  # read-only
    BOOLEAN: ClassVar[DataType] = ...
    FLOAT16: ClassVar[DataType] = ...
    FLOAT32: ClassVar[DataType] = ...
    FLOAT64: ClassVar[DataType] = ...
    INT16: ClassVar[DataType] = ...
    INT32: ClassVar[DataType] = ...
    INT4: ClassVar[DataType] = ...
    INT64: ClassVar[DataType] = ...
    INT8: ClassVar[DataType] = ...
    STRING: ClassVar[DataType] = ...
    UINT16: ClassVar[DataType] = ...
    UINT32: ClassVar[DataType] = ...
    UINT4: ClassVar[DataType] = ...
    UINT64: ClassVar[DataType] = ...
    UINT8: ClassVar[DataType] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: depthai.nn_archive.v1.DataType, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: depthai.nn_archive.v1.DataType) -> int"""
    def __int__(self) -> int:
        """__int__(self: depthai.nn_archive.v1.DataType) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class Head:
    metadata: Metadata
    name: str | None
    outputs: list[str] | None
    parser: str
    def __init__(self) -> None:
        """__init__(self: depthai.nn_archive.v1.Head) -> None"""

class Input:
    dtype: DataType
    inputType: InputType
    layout: str | None
    name: str
    preprocessing: PreprocessingBlock
    shape: list[int]
    def __init__(self) -> None:
        """__init__(self: depthai.nn_archive.v1.Input) -> None"""

class InputType:
    __members__: ClassVar[dict] = ...  # read-only
    IMAGE: ClassVar[InputType] = ...
    RAW: ClassVar[InputType] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: depthai.nn_archive.v1.InputType, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: depthai.nn_archive.v1.InputType) -> int"""
    def __int__(self) -> int:
        """__int__(self: depthai.nn_archive.v1.InputType) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class Metadata:
    anchors: list[list[list[float]]] | None
    anglesOutputs: list[str] | None
    boxesOutputs: str | None
    classes: list[str] | None
    confThreshold: float | None
    extraParams: json
    iouThreshold: float | None
    isSoftmax: bool | None
    keypointsOutputs: list[str] | None
    maskOutputs: list[str] | None
    maxDet: int | None
    nClasses: int | None
    nKeypoints: int | None
    nPrototypes: int | None
    postprocessorPath: str | None
    protosOutputs: str | None
    scoresOutputs: str | None
    subtype: str | None
    yoloOutputs: list[str] | None
    def __init__(self) -> None:
        """__init__(self: depthai.nn_archive.v1.Metadata) -> None"""

class MetadataClass:
    name: str
    path: str
    precision: DataType | None
    def __init__(self) -> None:
        """__init__(self: depthai.nn_archive.v1.MetadataClass) -> None"""

class Model:
    heads: list[Head] | None
    inputs: list[Input]
    metadata: MetadataClass
    outputs: list[Output]
    def __init__(self) -> None:
        """__init__(self: depthai.nn_archive.v1.Model) -> None"""

class Output:
    dtype: DataType
    layout: str | None
    name: str
    shape: list[int] | None
    def __init__(self) -> None:
        """__init__(self: depthai.nn_archive.v1.Output) -> None"""

class PreprocessingBlock:
    daiType: str | None
    interleavedToPlanar: bool | None
    mean: list[float] | None
    reverseChannels: bool | None
    scale: list[float] | None
    def __init__(self) -> None:
        """__init__(self: depthai.nn_archive.v1.PreprocessingBlock) -> None"""
