from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MultiTenancyConfig")


@_attrs_define
class MultiTenancyConfig:
    """Configuration related to multi-tenancy within a class

    Attributes:
        enabled (Union[Unset, bool]): Whether or not multi-tenancy is enabled for this class (default: false).
        auto_tenant_creation (Union[Unset, bool]): Nonexistent tenants should (not) be created implicitly (default:
            false).
        auto_tenant_activation (Union[Unset, bool]): Existing tenants should (not) be turned HOT implicitly when they
            are accessed and in another activity status (default: false).
    """

    enabled: Union[Unset, bool] = UNSET
    auto_tenant_creation: Union[Unset, bool] = UNSET
    auto_tenant_activation: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        auto_tenant_creation = self.auto_tenant_creation

        auto_tenant_activation = self.auto_tenant_activation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if auto_tenant_creation is not UNSET:
            field_dict["autoTenantCreation"] = auto_tenant_creation
        if auto_tenant_activation is not UNSET:
            field_dict["autoTenantActivation"] = auto_tenant_activation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        auto_tenant_creation = d.pop("autoTenantCreation", UNSET)

        auto_tenant_activation = d.pop("autoTenantActivation", UNSET)

        multi_tenancy_config = cls(
            enabled=enabled,
            auto_tenant_creation=auto_tenant_creation,
            auto_tenant_activation=auto_tenant_activation,
        )

        multi_tenancy_config.additional_properties = d
        return multi_tenancy_config

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
