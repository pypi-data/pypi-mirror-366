from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.replication_shard_replicas import ReplicationShardReplicas


T = TypeVar("T", bound="ReplicationShardingState")


@_attrs_define
class ReplicationShardingState:
    """Details the sharding layout for a specific collection, mapping each shard to its set of replicas across the cluster.

    Attributes:
        collection (Union[Unset, str]): The name of the collection.
        shards (Union[Unset, list['ReplicationShardReplicas']]): An array detailing each shard within the collection and
            the nodes hosting its replicas.
    """

    collection: Union[Unset, str] = UNSET
    shards: Union[Unset, list["ReplicationShardReplicas"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collection = self.collection

        shards: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.shards, Unset):
            shards = []
            for shards_item_data in self.shards:
                shards_item = shards_item_data.to_dict()
                shards.append(shards_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if collection is not UNSET:
            field_dict["collection"] = collection
        if shards is not UNSET:
            field_dict["shards"] = shards

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.replication_shard_replicas import ReplicationShardReplicas

        d = dict(src_dict)
        collection = d.pop("collection", UNSET)

        shards = []
        _shards = d.pop("shards", UNSET)
        for shards_item_data in _shards or []:
            shards_item = ReplicationShardReplicas.from_dict(shards_item_data)

            shards.append(shards_item)

        replication_sharding_state = cls(
            collection=collection,
            shards=shards,
        )

        replication_sharding_state.additional_properties = d
        return replication_sharding_state

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
