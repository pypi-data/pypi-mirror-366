from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.replication_config_deletion_strategy import ReplicationConfigDeletionStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReplicationConfig")


@_attrs_define
class ReplicationConfig:
    """Configure how replication is executed in a cluster

    Attributes:
        factor (Union[Unset, int]): Number of times a class is replicated (default: 1).
        async_enabled (Union[Unset, bool]): Enable asynchronous replication (default: false).
        deletion_strategy (Union[Unset, ReplicationConfigDeletionStrategy]): Conflict resolution strategy for deleted
            objects.
    """

    factor: Union[Unset, int] = UNSET
    async_enabled: Union[Unset, bool] = UNSET
    deletion_strategy: Union[Unset, ReplicationConfigDeletionStrategy] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        factor = self.factor

        async_enabled = self.async_enabled

        deletion_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.deletion_strategy, Unset):
            deletion_strategy = self.deletion_strategy.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if factor is not UNSET:
            field_dict["factor"] = factor
        if async_enabled is not UNSET:
            field_dict["asyncEnabled"] = async_enabled
        if deletion_strategy is not UNSET:
            field_dict["deletionStrategy"] = deletion_strategy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        factor = d.pop("factor", UNSET)

        async_enabled = d.pop("asyncEnabled", UNSET)

        _deletion_strategy = d.pop("deletionStrategy", UNSET)
        deletion_strategy: Union[Unset, ReplicationConfigDeletionStrategy]
        if isinstance(_deletion_strategy, Unset):
            deletion_strategy = UNSET
        else:
            deletion_strategy = ReplicationConfigDeletionStrategy(_deletion_strategy)

        replication_config = cls(
            factor=factor,
            async_enabled=async_enabled,
            deletion_strategy=deletion_strategy,
        )

        replication_config.additional_properties = d
        return replication_config

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
