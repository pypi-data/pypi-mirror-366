from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.c11y_vector_based_question_item_class_props_item import C11YVectorBasedQuestionItemClassPropsItem


T = TypeVar("T", bound="C11YVectorBasedQuestionItem")


@_attrs_define
class C11YVectorBasedQuestionItem:
    """
    Attributes:
        class_vectors (Union[Unset, list[float]]): Vectorized classname.
        class_props (Union[Unset, list['C11YVectorBasedQuestionItemClassPropsItem']]): Vectorized properties.
    """

    class_vectors: Union[Unset, list[float]] = UNSET
    class_props: Union[Unset, list["C11YVectorBasedQuestionItemClassPropsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        class_vectors: Union[Unset, list[float]] = UNSET
        if not isinstance(self.class_vectors, Unset):
            class_vectors = self.class_vectors

        class_props: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.class_props, Unset):
            class_props = []
            for class_props_item_data in self.class_props:
                class_props_item = class_props_item_data.to_dict()
                class_props.append(class_props_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if class_vectors is not UNSET:
            field_dict["classVectors"] = class_vectors
        if class_props is not UNSET:
            field_dict["classProps"] = class_props

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.c11y_vector_based_question_item_class_props_item import C11YVectorBasedQuestionItemClassPropsItem

        d = dict(src_dict)
        class_vectors = cast(list[float], d.pop("classVectors", UNSET))

        class_props = []
        _class_props = d.pop("classProps", UNSET)
        for class_props_item_data in _class_props or []:
            class_props_item = C11YVectorBasedQuestionItemClassPropsItem.from_dict(class_props_item_data)

            class_props.append(class_props_item)

        c11y_vector_based_question_item = cls(
            class_vectors=class_vectors,
            class_props=class_props,
        )

        c11y_vector_based_question_item.additional_properties = d
        return c11y_vector_based_question_item

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
