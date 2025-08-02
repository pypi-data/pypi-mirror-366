from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.replication_sharding_state import ReplicationShardingState


T = TypeVar("T", bound="ReplicationShardingStateResponse")


@_attrs_define
class ReplicationShardingStateResponse:
    """Provides the detailed sharding state for one or more collections, including the distribution of shards and their
    replicas across the cluster nodes.

        Attributes:
            sharding_state (Union[Unset, ReplicationShardingState]): Details the sharding layout for a specific collection,
                mapping each shard to its set of replicas across the cluster.
    """

    sharding_state: Union[Unset, "ReplicationShardingState"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sharding_state: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sharding_state, Unset):
            sharding_state = self.sharding_state.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sharding_state is not UNSET:
            field_dict["shardingState"] = sharding_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.replication_sharding_state import ReplicationShardingState

        d = dict(src_dict)
        _sharding_state = d.pop("shardingState", UNSET)
        sharding_state: Union[Unset, ReplicationShardingState]
        if isinstance(_sharding_state, Unset):
            sharding_state = UNSET
        else:
            sharding_state = ReplicationShardingState.from_dict(_sharding_state)

        replication_sharding_state_response = cls(
            sharding_state=sharding_state,
        )

        replication_sharding_state_response.additional_properties = d
        return replication_sharding_state_response

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
