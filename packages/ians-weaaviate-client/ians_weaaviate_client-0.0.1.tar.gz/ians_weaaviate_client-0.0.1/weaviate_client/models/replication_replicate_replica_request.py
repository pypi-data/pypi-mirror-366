from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.replication_replicate_replica_request_type import ReplicationReplicateReplicaRequestType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReplicationReplicateReplicaRequest")


@_attrs_define
class ReplicationReplicateReplicaRequest:
    """Specifies the parameters required to initiate a shard replica movement operation between two nodes for a given
    collection and shard. This request defines the source and target node, the collection and type of transfer.

        Attributes:
            source_node (str): The name of the Weaviate node currently hosting the shard replica that needs to be moved or
                copied.
            target_node (str): The name of the Weaviate node where the new shard replica will be created as part of the
                movement or copy operation.
            collection (str): The name of the collection to which the target shard belongs.
            shard (str): The name of the shard whose replica is to be moved or copied.
            type_ (Union[Unset, ReplicationReplicateReplicaRequestType]): Specifies the type of replication operation to
                perform. 'COPY' creates a new replica on the target node while keeping the source replica. 'MOVE' creates a new
                replica on the target node and then removes the source replica upon successful completion. Defaults to 'COPY' if
                omitted. Default: ReplicationReplicateReplicaRequestType.COPY.
    """

    source_node: str
    target_node: str
    collection: str
    shard: str
    type_: Union[Unset, ReplicationReplicateReplicaRequestType] = ReplicationReplicateReplicaRequestType.COPY
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_node = self.source_node

        target_node = self.target_node

        collection = self.collection

        shard = self.shard

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sourceNode": source_node,
                "targetNode": target_node,
                "collection": collection,
                "shard": shard,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_node = d.pop("sourceNode")

        target_node = d.pop("targetNode")

        collection = d.pop("collection")

        shard = d.pop("shard")

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, ReplicationReplicateReplicaRequestType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = ReplicationReplicateReplicaRequestType(_type_)

        replication_replicate_replica_request = cls(
            source_node=source_node,
            target_node=target_node,
            collection=collection,
            shard=shard,
            type_=type_,
        )

        replication_replicate_replica_request.additional_properties = d
        return replication_replicate_replica_request

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
