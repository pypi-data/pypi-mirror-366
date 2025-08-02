from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.class_ import Class


T = TypeVar("T", bound="Schema")


@_attrs_define
class Schema:
    """Definitions of semantic schemas (also see: https://github.com/weaviate/weaviate-semantic-schemas).

    Attributes:
        classes (Union[Unset, list['Class']]): Semantic classes that are available.
        maintainer (Union[Unset, str]): Email of the maintainer.
        name (Union[Unset, str]): Name of the schema.
    """

    classes: Union[Unset, list["Class"]] = UNSET
    maintainer: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        classes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.classes, Unset):
            classes = []
            for classes_item_data in self.classes:
                classes_item = classes_item_data.to_dict()
                classes.append(classes_item)

        maintainer = self.maintainer

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if classes is not UNSET:
            field_dict["classes"] = classes
        if maintainer is not UNSET:
            field_dict["maintainer"] = maintainer
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.class_ import Class

        d = dict(src_dict)
        classes = []
        _classes = d.pop("classes", UNSET)
        for classes_item_data in _classes or []:
            classes_item = Class.from_dict(classes_item_data)

            classes.append(classes_item)

        maintainer = d.pop("maintainer", UNSET)

        name = d.pop("name", UNSET)

        schema = cls(
            classes=classes,
            maintainer=maintainer,
            name=name,
        )

        schema.additional_properties = d
        return schema

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
