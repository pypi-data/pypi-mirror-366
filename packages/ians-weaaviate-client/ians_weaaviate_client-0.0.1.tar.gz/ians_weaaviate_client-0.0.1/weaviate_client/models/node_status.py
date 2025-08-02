from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.node_status_status import NodeStatusStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch_stats import BatchStats
    from ..models.node_shard_status import NodeShardStatus
    from ..models.node_stats import NodeStats


T = TypeVar("T", bound="NodeStatus")


@_attrs_define
class NodeStatus:
    """The definition of a backup node status response body

    Attributes:
        name (Union[Unset, str]): The name of the node.
        status (Union[Unset, NodeStatusStatus]): Node's status. Default: NodeStatusStatus.HEALTHY.
        version (Union[Unset, str]): The version of Weaviate.
        git_hash (Union[Unset, str]): The gitHash of Weaviate.
        stats (Union[Unset, NodeStats]): The summary of Weaviate's statistics.
        batch_stats (Union[Unset, BatchStats]): The summary of a nodes batch queue congestion status.
        shards (Union[Unset, list['NodeShardStatus']]): The list of the shards with it's statistics.
    """

    name: Union[Unset, str] = UNSET
    status: Union[Unset, NodeStatusStatus] = NodeStatusStatus.HEALTHY
    version: Union[Unset, str] = UNSET
    git_hash: Union[Unset, str] = UNSET
    stats: Union[Unset, "NodeStats"] = UNSET
    batch_stats: Union[Unset, "BatchStats"] = UNSET
    shards: Union[Unset, list["NodeShardStatus"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        version = self.version

        git_hash = self.git_hash

        stats: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats.to_dict()

        batch_stats: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.batch_stats, Unset):
            batch_stats = self.batch_stats.to_dict()

        shards: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.shards, Unset):
            shards = []
            for shards_item_data in self.shards:
                shards_item = shards_item_data.to_dict()
                shards.append(shards_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if version is not UNSET:
            field_dict["version"] = version
        if git_hash is not UNSET:
            field_dict["gitHash"] = git_hash
        if stats is not UNSET:
            field_dict["stats"] = stats
        if batch_stats is not UNSET:
            field_dict["batchStats"] = batch_stats
        if shards is not UNSET:
            field_dict["shards"] = shards

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_stats import BatchStats
        from ..models.node_shard_status import NodeShardStatus
        from ..models.node_stats import NodeStats

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, NodeStatusStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = NodeStatusStatus(_status)

        version = d.pop("version", UNSET)

        git_hash = d.pop("gitHash", UNSET)

        _stats = d.pop("stats", UNSET)
        stats: Union[Unset, NodeStats]
        if isinstance(_stats, Unset):
            stats = UNSET
        else:
            stats = NodeStats.from_dict(_stats)

        _batch_stats = d.pop("batchStats", UNSET)
        batch_stats: Union[Unset, BatchStats]
        if isinstance(_batch_stats, Unset):
            batch_stats = UNSET
        else:
            batch_stats = BatchStats.from_dict(_batch_stats)

        shards = []
        _shards = d.pop("shards", UNSET)
        for shards_item_data in _shards or []:
            shards_item = NodeShardStatus.from_dict(shards_item_data)

            shards.append(shards_item)

        node_status = cls(
            name=name,
            status=status,
            version=version,
            git_hash=git_hash,
            stats=stats,
            batch_stats=batch_stats,
            shards=shards,
        )

        node_status.additional_properties = d
        return node_status

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
