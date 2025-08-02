from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.tenant_activity_status import TenantActivityStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="Tenant")


@_attrs_define
class Tenant:
    """attributes representing a single tenant within weaviate

    Attributes:
        name (Union[Unset, str]): The name of the tenant (required).
        activity_status (Union[Unset, TenantActivityStatus]): activity status of the tenant's shard. Optional for
            creating tenant (implicit `ACTIVE`) and required for updating tenant. For creation, allowed values are `ACTIVE`
            - tenant is fully active and `INACTIVE` - tenant is inactive; no actions can be performed on tenant, tenant's
            files are stored locally. For updating, `ACTIVE`, `INACTIVE` and also `OFFLOADED` - as INACTIVE, but files are
            stored on cloud storage. The following values are read-only and are set by the server for internal use:
            `OFFLOADING` - tenant is transitioning from ACTIVE/INACTIVE to OFFLOADED, `ONLOADING` - tenant is transitioning
            from OFFLOADED to ACTIVE/INACTIVE. We still accept deprecated names `HOT` (now `ACTIVE`), `COLD` (now
            `INACTIVE`), `FROZEN` (now `OFFLOADED`), `FREEZING` (now `OFFLOADING`), `UNFREEZING` (now `ONLOADING`).
    """

    name: Union[Unset, str] = UNSET
    activity_status: Union[Unset, TenantActivityStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        activity_status: Union[Unset, str] = UNSET
        if not isinstance(self.activity_status, Unset):
            activity_status = self.activity_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if activity_status is not UNSET:
            field_dict["activityStatus"] = activity_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _activity_status = d.pop("activityStatus", UNSET)
        activity_status: Union[Unset, TenantActivityStatus]
        if isinstance(_activity_status, Unset):
            activity_status = UNSET
        else:
            activity_status = TenantActivityStatus(_activity_status)

        tenant = cls(
            name=name,
            activity_status=activity_status,
        )

        tenant.additional_properties = d
        return tenant

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
