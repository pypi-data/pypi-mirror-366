from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.batch_objects_create_body_fields_item import BatchObjectsCreateBodyFieldsItem
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.object_ import Object


T = TypeVar("T", bound="BatchObjectsCreateBody")


@_attrs_define
class BatchObjectsCreateBody:
    """
    Attributes:
        fields (Union[Unset, list[BatchObjectsCreateBodyFieldsItem]]): Define which fields need to be returned. Default
            value is ALL
        objects (Union[Unset, list['Object']]):
    """

    fields: Union[Unset, list[BatchObjectsCreateBodyFieldsItem]] = UNSET
    objects: Union[Unset, list["Object"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fields: Union[Unset, list[str]] = UNSET
        if not isinstance(self.fields, Unset):
            fields = []
            for fields_item_data in self.fields:
                fields_item = fields_item_data.value
                fields.append(fields_item)

        objects: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.objects, Unset):
            objects = []
            for objects_item_data in self.objects:
                objects_item = objects_item_data.to_dict()
                objects.append(objects_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fields is not UNSET:
            field_dict["fields"] = fields
        if objects is not UNSET:
            field_dict["objects"] = objects

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.object_ import Object

        d = dict(src_dict)
        fields = []
        _fields = d.pop("fields", UNSET)
        for fields_item_data in _fields or []:
            fields_item = BatchObjectsCreateBodyFieldsItem(fields_item_data)

            fields.append(fields_item)

        objects = []
        _objects = d.pop("objects", UNSET)
        for objects_item_data in _objects or []:
            objects_item = Object.from_dict(objects_item_data)

            objects.append(objects_item)

        batch_objects_create_body = cls(
            fields=fields,
            objects=objects,
        )

        batch_objects_create_body.additional_properties = d
        return batch_objects_create_body

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
