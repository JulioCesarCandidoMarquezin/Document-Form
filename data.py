from flet import TextField, Checkbox
from typing import List, Tuple, Dict, Union, Sequence, Any, Type


class PDFLineText:
    def __init__(self, index: int, words: List[Tuple[float, float, float, float, str]] | None):
        if words is None:
            words = []

        self.index: int = index
        self.words: List[Tuple[float, float, float, float, str]] = words
        self.x1: float = min([word[0] for word in words])
        self.y1: float = min([word[1] for word in words])
        self.x2: float = max([word[2] for word in words])
        self.y2: float = max([word[3] for word in words])
        self.text: str = ''.join([word[4] for word in words])
        self.font_size: float = self.y2 - self.y1


class FieldData:
    def __init__(
            self,
            component_type: Union[Type[TextField], Type[Checkbox]],
            page_number: int,
            bbox: Sequence[float],
            value: Any,
            args: Dict[str, Any]
    ):
        self.component_type: Any = component_type
        self.page_number: int = page_number
        self.bbox: Sequence[float] = bbox
        self.value: Any = value
        self.args: Dict[str, Any] = args


class FieldsData:
    def __init__(
            self,
            components_type: List[Union[Union[Type[TextField], Type[Checkbox]]]] | None = None,
            pages_number: List[int] | None = None,
            bboxes: List[Sequence[float]] | None = None,
            values: List[Any] | None = None,
            args: List[Dict[str, Any]] | None = None

    ):
        if components_type is None:
            components_type = []

        if pages_number is None:
            pages_number = []

        if bboxes is None:
            bboxes = []

        if values is None:
            values = []

        if args is None:
            args = []

        self.index = -1
        self.components_data = [
            FieldData(component_type, page_number, bbox, value, args)
            for component_type, page_number, bbox, value, args in
            zip(components_type, pages_number, bboxes, values, args)
        ]

    def add(
            self,
            component_type: Union[Type[TextField], Type[Checkbox]],
            page_number: int,
            bbox: Sequence[float],
            value: Any,
            args: Dict[str, Any],
    ) -> None:
        self.components_data.append(FieldData(component_type, page_number, bbox, value, args))

    def remove(self, index: int = -1) -> FieldData | None:
        try:
            return self.components_data.pop(index)
        except IndexError:
            return None

    def preview(self) -> FieldData | None:
        try:
            self.index -= 1
            return self.components_data[self.index]
        except IndexError:
            return None

    def next(self) -> FieldData | None:
        try:
            self.index += 1
            return self.components_data[self.index]
        except IndexError:
            return None
