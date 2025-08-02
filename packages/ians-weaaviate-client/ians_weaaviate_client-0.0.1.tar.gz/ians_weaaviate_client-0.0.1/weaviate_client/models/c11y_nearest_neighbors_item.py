from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="C11YNearestNeighborsItem")


@_attrs_define
class C11YNearestNeighborsItem:
    """
    Attributes:
        word (Union[Unset, str]):
        distance (Union[Unset, float]):
    """

    word: Union[Unset, str] = UNSET
    distance: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        word = self.word

        distance = self.distance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if word is not UNSET:
            field_dict["word"] = word
        if distance is not UNSET:
            field_dict["distance"] = distance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        word = d.pop("word", UNSET)

        distance = d.pop("distance", UNSET)

        c11y_nearest_neighbors_item = cls(
            word=word,
            distance=distance,
        )

        c11y_nearest_neighbors_item.additional_properties = d
        return c11y_nearest_neighbors_item

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
