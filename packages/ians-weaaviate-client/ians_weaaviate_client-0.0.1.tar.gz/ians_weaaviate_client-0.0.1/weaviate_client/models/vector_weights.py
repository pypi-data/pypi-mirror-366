from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VectorWeights")


@_attrs_define
class VectorWeights:
    """Allow custom overrides of vector weights as math expressions. E.g. "pancake": "7" will set the weight for the word
    pancake to 7 in the vectorization, whereas "w * 3" would triple the originally calculated word. This is an open
    object, with OpenAPI Specification 3.0 this will be more detailed. See Weaviate docs for more info. In the future
    this will become a key/value (string/string) object.

    """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        vector_weights = cls()

        vector_weights.additional_properties = d
        return vector_weights

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
