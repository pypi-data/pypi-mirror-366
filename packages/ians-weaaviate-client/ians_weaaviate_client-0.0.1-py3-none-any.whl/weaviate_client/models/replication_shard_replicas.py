from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReplicationShardReplicas")


@_attrs_define
class ReplicationShardReplicas:
    """Represents a shard and lists the nodes that currently host its replicas.

    Attributes:
        shard (Union[Unset, str]):
        replicas (Union[Unset, list[str]]):
    """

    shard: Union[Unset, str] = UNSET
    replicas: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        shard = self.shard

        replicas: Union[Unset, list[str]] = UNSET
        if not isinstance(self.replicas, Unset):
            replicas = self.replicas

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if shard is not UNSET:
            field_dict["shard"] = shard
        if replicas is not UNSET:
            field_dict["replicas"] = replicas

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        shard = d.pop("shard", UNSET)

        replicas = cast(list[str], d.pop("replicas", UNSET))

        replication_shard_replicas = cls(
            shard=shard,
            replicas=replicas,
        )

        replication_shard_replicas.additional_properties = d
        return replication_shard_replicas

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
