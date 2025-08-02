from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReplicationDeleteReplicaRequest")


@_attrs_define
class ReplicationDeleteReplicaRequest:
    """Specifies the parameters required to permanently delete a specific shard replica from a particular node. This action
    will remove the replica's data from the node.

        Attributes:
            node (str): The name of the Weaviate node from which the shard replica will be deleted.
            collection (str): The name of the collection to which the shard replica belongs.
            shard (str): The ID of the shard whose replica is to be deleted.
    """

    node: str
    collection: str
    shard: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node = self.node

        collection = self.collection

        shard = self.shard

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node": node,
                "collection": collection,
                "shard": shard,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        node = d.pop("node")

        collection = d.pop("collection")

        shard = d.pop("shard")

        replication_delete_replica_request = cls(
            node=node,
            collection=collection,
            shard=shard,
        )

        replication_delete_replica_request.additional_properties = d
        return replication_delete_replica_request

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
