from typing_extensions import NotRequired, TypedDict


class TouchPoint(TypedDict):
    x: int
    y: int
    radiusX: NotRequired[float]
    radiusY: NotRequired[float]
    rotationAngle: NotRequired[float]
    force: NotRequired[float]
    tangentialPressure: NotRequired[float]
    tiltX: NotRequired[float]
    tiltY: NotRequired[float]
    twist: NotRequired[int]
    id: NotRequired[int]


class DragDataItem(TypedDict):
    mimeType: str
    data: str
    title: NotRequired[str]
    baseURL: NotRequired[str]


class DragData(TypedDict):
    items: list[DragDataItem]
    files: NotRequired[list[str]]
    dragOperationMask: int
