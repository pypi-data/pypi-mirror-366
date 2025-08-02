from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="C11YVectorBasedQuestionItemClassPropsItem")


@_attrs_define
class C11YVectorBasedQuestionItemClassPropsItem:
    """
    Attributes:
        props_vectors (Union[Unset, list[float]]):
        value (Union[Unset, str]): String with valuename.
    """

    props_vectors: Union[Unset, list[float]] = UNSET
    value: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        props_vectors: Union[Unset, list[float]] = UNSET
        if not isinstance(self.props_vectors, Unset):
            props_vectors = self.props_vectors

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if props_vectors is not UNSET:
            field_dict["propsVectors"] = props_vectors
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        props_vectors = cast(list[float], d.pop("propsVectors", UNSET))

        value = d.pop("value", UNSET)

        c11y_vector_based_question_item_class_props_item = cls(
            props_vectors=props_vectors,
            value=value,
        )

        c11y_vector_based_question_item_class_props_item.additional_properties = d
        return c11y_vector_based_question_item_class_props_item

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
