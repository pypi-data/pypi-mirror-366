from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReplicationReplicateForceDeleteResponse")


@_attrs_define
class ReplicationReplicateForceDeleteResponse:
    """Provides the UUIDs that were successfully force deleted as part of the replication operation. If dryRun is true,
    this will return the expected outcome without actually deleting anything.

        Attributes:
            deleted (Union[Unset, list[UUID]]): The unique identifiers (IDs) of the replication operations that were
                forcefully deleted.
            dry_run (Union[Unset, bool]): Indicates whether the operation was a dry run (true) or an actual deletion
                (false).
    """

    deleted: Union[Unset, list[UUID]] = UNSET
    dry_run: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        deleted: Union[Unset, list[str]] = UNSET
        if not isinstance(self.deleted, Unset):
            deleted = []
            for deleted_item_data in self.deleted:
                deleted_item = str(deleted_item_data)
                deleted.append(deleted_item)

        dry_run = self.dry_run

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if dry_run is not UNSET:
            field_dict["dryRun"] = dry_run

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        deleted = []
        _deleted = d.pop("deleted", UNSET)
        for deleted_item_data in _deleted or []:
            deleted_item = UUID(deleted_item_data)

            deleted.append(deleted_item)

        dry_run = d.pop("dryRun", UNSET)

        replication_replicate_force_delete_response = cls(
            deleted=deleted,
            dry_run=dry_run,
        )

        replication_replicate_force_delete_response.additional_properties = d
        return replication_replicate_force_delete_response

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
