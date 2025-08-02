from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReplicationReplicateDetailsReplicaStatusError")


@_attrs_define
class ReplicationReplicateDetailsReplicaStatusError:
    """Represents an error encountered during a replication operation, including its timestamp and a human-readable
    message.

        Attributes:
            when_errored_unix_ms (Union[Unset, int]): The unix timestamp in ms when the error occurred. This is an
                approximate time and so should not be used for precise timing.
            message (Union[Unset, str]): A human-readable message describing the error.
    """

    when_errored_unix_ms: Union[Unset, int] = UNSET
    message: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        when_errored_unix_ms = self.when_errored_unix_ms

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if when_errored_unix_ms is not UNSET:
            field_dict["whenErroredUnixMs"] = when_errored_unix_ms
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        when_errored_unix_ms = d.pop("whenErroredUnixMs", UNSET)

        message = d.pop("message", UNSET)

        replication_replicate_details_replica_status_error = cls(
            when_errored_unix_ms=when_errored_unix_ms,
            message=message,
        )

        replication_replicate_details_replica_status_error.additional_properties = d
        return replication_replicate_details_replica_status_error

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
