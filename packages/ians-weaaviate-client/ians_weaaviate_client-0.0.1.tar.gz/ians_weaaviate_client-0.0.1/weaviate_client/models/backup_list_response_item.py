from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.backup_list_response_item_status import BackupListResponseItemStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="BackupListResponseItem")


@_attrs_define
class BackupListResponseItem:
    """
    Attributes:
        id (Union[Unset, str]): The ID of the backup. Must be URL-safe and work as a filesystem path, only lowercase,
            numbers, underscore, minus characters allowed.
        path (Union[Unset, str]): destination path of backup files proper to selected backend
        classes (Union[Unset, list[str]]): The list of classes for which the existed backup process
        status (Union[Unset, BackupListResponseItemStatus]): status of backup process
    """

    id: Union[Unset, str] = UNSET
    path: Union[Unset, str] = UNSET
    classes: Union[Unset, list[str]] = UNSET
    status: Union[Unset, BackupListResponseItemStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        path = self.path

        classes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.classes, Unset):
            classes = self.classes

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if path is not UNSET:
            field_dict["path"] = path
        if classes is not UNSET:
            field_dict["classes"] = classes
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        path = d.pop("path", UNSET)

        classes = cast(list[str], d.pop("classes", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, BackupListResponseItemStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = BackupListResponseItemStatus(_status)

        backup_list_response_item = cls(
            id=id,
            path=path,
            classes=classes,
            status=status,
        )

        backup_list_response_item.additional_properties = d
        return backup_list_response_item

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
