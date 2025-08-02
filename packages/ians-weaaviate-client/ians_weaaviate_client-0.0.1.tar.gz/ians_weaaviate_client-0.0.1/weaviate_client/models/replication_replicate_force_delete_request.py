from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReplicationReplicateForceDeleteRequest")


@_attrs_define
class ReplicationReplicateForceDeleteRequest:
    """Specifies the parameters available when force deleting replication operations.

    Attributes:
        id (Union[Unset, UUID]): The unique identifier (ID) of the replication operation to be forcefully deleted.
        collection (Union[Unset, str]): The name of the collection to which the shard being replicated belongs.
        shard (Union[Unset, str]): The identifier of the shard involved in the replication operations.
        node (Union[Unset, str]): The name of the target node where the replication operations are registered.
        dry_run (Union[Unset, bool]): If true, the operation will not actually delete anything but will return the
            expected outcome of the deletion. Default: False.
    """

    id: Union[Unset, UUID] = UNSET
    collection: Union[Unset, str] = UNSET
    shard: Union[Unset, str] = UNSET
    node: Union[Unset, str] = UNSET
    dry_run: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: Union[Unset, str] = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        collection = self.collection

        shard = self.shard

        node = self.node

        dry_run = self.dry_run

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if collection is not UNSET:
            field_dict["collection"] = collection
        if shard is not UNSET:
            field_dict["shard"] = shard
        if node is not UNSET:
            field_dict["node"] = node
        if dry_run is not UNSET:
            field_dict["dryRun"] = dry_run

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _id = d.pop("id", UNSET)
        id: Union[Unset, UUID]
        if isinstance(_id, Unset):
            id = UNSET
        else:
            id = UUID(_id)

        collection = d.pop("collection", UNSET)

        shard = d.pop("shard", UNSET)

        node = d.pop("node", UNSET)

        dry_run = d.pop("dryRun", UNSET)

        replication_replicate_force_delete_request = cls(
            id=id,
            collection=collection,
            shard=shard,
            node=node,
            dry_run=dry_run,
        )

        replication_replicate_force_delete_request.additional_properties = d
        return replication_replicate_force_delete_request

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
