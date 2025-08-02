from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.replication_replicate_details_replica_response_type import ReplicationReplicateDetailsReplicaResponseType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.replication_replicate_details_replica_status import ReplicationReplicateDetailsReplicaStatus


T = TypeVar("T", bound="ReplicationReplicateDetailsReplicaResponse")


@_attrs_define
class ReplicationReplicateDetailsReplicaResponse:
    """Provides a comprehensive overview of a specific replication operation, detailing its unique ID, the involved
    collection, shard, source and target nodes, transfer type, current status, and optionally, its status history.

        Attributes:
            id (UUID): The unique identifier (ID) of this specific replication operation.
            shard (str): The name of the shard involved in this replication operation.
            collection (str): The name of the collection to which the shard being replicated belongs.
            source_node (str): The identifier of the node from which the replica is being moved or copied (the source node).
            target_node (str): The identifier of the node to which the replica is being moved or copied (the target node).
            type_ (ReplicationReplicateDetailsReplicaResponseType): Indicates whether the operation is a 'COPY' (source
                replica remains) or a 'MOVE' (source replica is removed after successful transfer).
            status (ReplicationReplicateDetailsReplicaStatus): Represents the current or historical status of a shard
                replica involved in a replication operation, including its operational state and any associated errors.
            uncancelable (Union[Unset, bool]): Whether the replica operation is uncancelable.
            scheduled_for_cancel (Union[Unset, bool]): Whether the replica operation is scheduled for cancellation.
            scheduled_for_delete (Union[Unset, bool]): Whether the replica operation is scheduled for deletion.
            status_history (Union[Unset, list['ReplicationReplicateDetailsReplicaStatus']]): An array detailing the
                historical sequence of statuses the replication operation has transitioned through, if requested and available.
            when_started_unix_ms (Union[Unset, int]): The UNIX timestamp in ms when the replication operation was initiated.
                This is an approximate time and so should not be used for precise timing.
    """

    id: UUID
    shard: str
    collection: str
    source_node: str
    target_node: str
    type_: ReplicationReplicateDetailsReplicaResponseType
    status: "ReplicationReplicateDetailsReplicaStatus"
    uncancelable: Union[Unset, bool] = UNSET
    scheduled_for_cancel: Union[Unset, bool] = UNSET
    scheduled_for_delete: Union[Unset, bool] = UNSET
    status_history: Union[Unset, list["ReplicationReplicateDetailsReplicaStatus"]] = UNSET
    when_started_unix_ms: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        shard = self.shard

        collection = self.collection

        source_node = self.source_node

        target_node = self.target_node

        type_ = self.type_.value

        status = self.status.to_dict()

        uncancelable = self.uncancelable

        scheduled_for_cancel = self.scheduled_for_cancel

        scheduled_for_delete = self.scheduled_for_delete

        status_history: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.status_history, Unset):
            status_history = []
            for status_history_item_data in self.status_history:
                status_history_item = status_history_item_data.to_dict()
                status_history.append(status_history_item)

        when_started_unix_ms = self.when_started_unix_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "shard": shard,
                "collection": collection,
                "sourceNode": source_node,
                "targetNode": target_node,
                "type": type_,
                "status": status,
            }
        )
        if uncancelable is not UNSET:
            field_dict["uncancelable"] = uncancelable
        if scheduled_for_cancel is not UNSET:
            field_dict["scheduledForCancel"] = scheduled_for_cancel
        if scheduled_for_delete is not UNSET:
            field_dict["scheduledForDelete"] = scheduled_for_delete
        if status_history is not UNSET:
            field_dict["statusHistory"] = status_history
        if when_started_unix_ms is not UNSET:
            field_dict["whenStartedUnixMs"] = when_started_unix_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.replication_replicate_details_replica_status import ReplicationReplicateDetailsReplicaStatus

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        shard = d.pop("shard")

        collection = d.pop("collection")

        source_node = d.pop("sourceNode")

        target_node = d.pop("targetNode")

        type_ = ReplicationReplicateDetailsReplicaResponseType(d.pop("type"))

        status = ReplicationReplicateDetailsReplicaStatus.from_dict(d.pop("status"))

        uncancelable = d.pop("uncancelable", UNSET)

        scheduled_for_cancel = d.pop("scheduledForCancel", UNSET)

        scheduled_for_delete = d.pop("scheduledForDelete", UNSET)

        status_history = []
        _status_history = d.pop("statusHistory", UNSET)
        for status_history_item_data in _status_history or []:
            status_history_item = ReplicationReplicateDetailsReplicaStatus.from_dict(status_history_item_data)

            status_history.append(status_history_item)

        when_started_unix_ms = d.pop("whenStartedUnixMs", UNSET)

        replication_replicate_details_replica_response = cls(
            id=id,
            shard=shard,
            collection=collection,
            source_node=source_node,
            target_node=target_node,
            type_=type_,
            status=status,
            uncancelable=uncancelable,
            scheduled_for_cancel=scheduled_for_cancel,
            scheduled_for_delete=scheduled_for_delete,
            status_history=status_history,
            when_started_unix_ms=when_started_unix_ms,
        )

        replication_replicate_details_replica_response.additional_properties = d
        return replication_replicate_details_replica_response

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
