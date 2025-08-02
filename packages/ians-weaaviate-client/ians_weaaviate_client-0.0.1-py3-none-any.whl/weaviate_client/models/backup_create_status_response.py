from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.backup_create_status_response_status import BackupCreateStatusResponseStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="BackupCreateStatusResponse")


@_attrs_define
class BackupCreateStatusResponse:
    """The definition of a backup create metadata

    Attributes:
        id (Union[Unset, str]): The ID of the backup. Must be URL-safe and work as a filesystem path, only lowercase,
            numbers, underscore, minus characters allowed.
        backend (Union[Unset, str]): Backup backend name e.g. filesystem, gcs, s3.
        path (Union[Unset, str]): destination path of backup files proper to selected backend
        error (Union[Unset, str]): error message if creation failed
        status (Union[Unset, BackupCreateStatusResponseStatus]): phase of backup creation process Default:
            BackupCreateStatusResponseStatus.STARTED.
    """

    id: Union[Unset, str] = UNSET
    backend: Union[Unset, str] = UNSET
    path: Union[Unset, str] = UNSET
    error: Union[Unset, str] = UNSET
    status: Union[Unset, BackupCreateStatusResponseStatus] = BackupCreateStatusResponseStatus.STARTED
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        backend = self.backend

        path = self.path

        error = self.error

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if backend is not UNSET:
            field_dict["backend"] = backend
        if path is not UNSET:
            field_dict["path"] = path
        if error is not UNSET:
            field_dict["error"] = error
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        backend = d.pop("backend", UNSET)

        path = d.pop("path", UNSET)

        error = d.pop("error", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, BackupCreateStatusResponseStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = BackupCreateStatusResponseStatus(_status)

        backup_create_status_response = cls(
            id=id,
            backend=backend,
            path=path,
            error=error,
            status=status,
        )

        backup_create_status_response.additional_properties = d
        return backup_create_status_response

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
