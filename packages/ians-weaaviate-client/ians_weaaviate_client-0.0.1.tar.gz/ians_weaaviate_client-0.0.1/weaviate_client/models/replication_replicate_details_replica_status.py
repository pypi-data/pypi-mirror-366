from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.replication_replicate_details_replica_status_state import ReplicationReplicateDetailsReplicaStatusState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.replication_replicate_details_replica_status_error import (
        ReplicationReplicateDetailsReplicaStatusError,
    )


T = TypeVar("T", bound="ReplicationReplicateDetailsReplicaStatus")


@_attrs_define
class ReplicationReplicateDetailsReplicaStatus:
    """Represents the current or historical status of a shard replica involved in a replication operation, including its
    operational state and any associated errors.

        Attributes:
            state (Union[Unset, ReplicationReplicateDetailsReplicaStatusState]): The current operational state of the
                replica during the replication process.
            when_started_unix_ms (Union[Unset, int]): The UNIX timestamp in ms when this state was first entered. This is an
                approximate time and so should not be used for precise timing.
            errors (Union[Unset, list['ReplicationReplicateDetailsReplicaStatusError']]): A list of error messages
                encountered by this replica during the replication operation, if any.
    """

    state: Union[Unset, ReplicationReplicateDetailsReplicaStatusState] = UNSET
    when_started_unix_ms: Union[Unset, int] = UNSET
    errors: Union[Unset, list["ReplicationReplicateDetailsReplicaStatusError"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        when_started_unix_ms = self.when_started_unix_ms

        errors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = []
            for errors_item_data in self.errors:
                errors_item = errors_item_data.to_dict()
                errors.append(errors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if state is not UNSET:
            field_dict["state"] = state
        if when_started_unix_ms is not UNSET:
            field_dict["whenStartedUnixMs"] = when_started_unix_ms
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.replication_replicate_details_replica_status_error import (
            ReplicationReplicateDetailsReplicaStatusError,
        )

        d = dict(src_dict)
        _state = d.pop("state", UNSET)
        state: Union[Unset, ReplicationReplicateDetailsReplicaStatusState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = ReplicationReplicateDetailsReplicaStatusState(_state)

        when_started_unix_ms = d.pop("whenStartedUnixMs", UNSET)

        errors = []
        _errors = d.pop("errors", UNSET)
        for errors_item_data in _errors or []:
            errors_item = ReplicationReplicateDetailsReplicaStatusError.from_dict(errors_item_data)

            errors.append(errors_item)

        replication_replicate_details_replica_status = cls(
            state=state,
            when_started_unix_ms=when_started_unix_ms,
            errors=errors,
        )

        replication_replicate_details_replica_status.additional_properties = d
        return replication_replicate_details_replica_status

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
