from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.restore_config_roles_options import RestoreConfigRolesOptions
from ..models.restore_config_users_options import RestoreConfigUsersOptions
from ..types import UNSET, Unset

T = TypeVar("T", bound="RestoreConfig")


@_attrs_define
class RestoreConfig:
    """Backup custom configuration

    Attributes:
        endpoint (Union[Unset, str]): name of the endpoint, e.g. s3.amazonaws.com
        bucket (Union[Unset, str]): Name of the bucket, container, volume, etc
        path (Union[Unset, str]): Path within the bucket
        cpu_percentage (Union[Unset, int]): Desired CPU core utilization ranging from 1%-80%
        roles_options (Union[Unset, RestoreConfigRolesOptions]): How roles should be restored Default:
            RestoreConfigRolesOptions.NORESTORE.
        users_options (Union[Unset, RestoreConfigUsersOptions]): How users should be restored Default:
            RestoreConfigUsersOptions.NORESTORE.
    """

    endpoint: Union[Unset, str] = UNSET
    bucket: Union[Unset, str] = UNSET
    path: Union[Unset, str] = UNSET
    cpu_percentage: Union[Unset, int] = UNSET
    roles_options: Union[Unset, RestoreConfigRolesOptions] = RestoreConfigRolesOptions.NORESTORE
    users_options: Union[Unset, RestoreConfigUsersOptions] = RestoreConfigUsersOptions.NORESTORE
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        endpoint = self.endpoint

        bucket = self.bucket

        path = self.path

        cpu_percentage = self.cpu_percentage

        roles_options: Union[Unset, str] = UNSET
        if not isinstance(self.roles_options, Unset):
            roles_options = self.roles_options.value

        users_options: Union[Unset, str] = UNSET
        if not isinstance(self.users_options, Unset):
            users_options = self.users_options.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if endpoint is not UNSET:
            field_dict["Endpoint"] = endpoint
        if bucket is not UNSET:
            field_dict["Bucket"] = bucket
        if path is not UNSET:
            field_dict["Path"] = path
        if cpu_percentage is not UNSET:
            field_dict["CPUPercentage"] = cpu_percentage
        if roles_options is not UNSET:
            field_dict["rolesOptions"] = roles_options
        if users_options is not UNSET:
            field_dict["usersOptions"] = users_options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        endpoint = d.pop("Endpoint", UNSET)

        bucket = d.pop("Bucket", UNSET)

        path = d.pop("Path", UNSET)

        cpu_percentage = d.pop("CPUPercentage", UNSET)

        _roles_options = d.pop("rolesOptions", UNSET)
        roles_options: Union[Unset, RestoreConfigRolesOptions]
        if isinstance(_roles_options, Unset):
            roles_options = UNSET
        else:
            roles_options = RestoreConfigRolesOptions(_roles_options)

        _users_options = d.pop("usersOptions", UNSET)
        users_options: Union[Unset, RestoreConfigUsersOptions]
        if isinstance(_users_options, Unset):
            users_options = UNSET
        else:
            users_options = RestoreConfigUsersOptions(_users_options)

        restore_config = cls(
            endpoint=endpoint,
            bucket=bucket,
            path=path,
            cpu_percentage=cpu_percentage,
            roles_options=roles_options,
            users_options=users_options,
        )

        restore_config.additional_properties = d
        return restore_config

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
