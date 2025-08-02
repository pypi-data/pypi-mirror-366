from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.async_replication_status import AsyncReplicationStatus
    from ..models.node_shard_status_compressed import NodeShardStatusCompressed
    from ..models.node_shard_status_vector_indexing_status import NodeShardStatusVectorIndexingStatus


T = TypeVar("T", bound="NodeShardStatus")


@_attrs_define
class NodeShardStatus:
    """The definition of a node shard status response body

    Attributes:
        name (Union[Unset, str]): The name of the shard.
        class_ (Union[Unset, str]): The name of shard's class.
        object_count (Union[Unset, float]): The number of objects in shard.
        vector_indexing_status (Union[Unset, NodeShardStatusVectorIndexingStatus]): The status of the vector indexing
            process.
        compressed (Union[Unset, NodeShardStatusCompressed]): The status of vector compression/quantization.
        vector_queue_length (Union[Unset, float]): The length of the vector indexing queue.
        loaded (Union[Unset, bool]): The load status of the shard.
        async_replication_status (Union[Unset, list['AsyncReplicationStatus']]): The status of the async replication.
    """

    name: Union[Unset, str] = UNSET
    class_: Union[Unset, str] = UNSET
    object_count: Union[Unset, float] = UNSET
    vector_indexing_status: Union[Unset, "NodeShardStatusVectorIndexingStatus"] = UNSET
    compressed: Union[Unset, "NodeShardStatusCompressed"] = UNSET
    vector_queue_length: Union[Unset, float] = UNSET
    loaded: Union[Unset, bool] = UNSET
    async_replication_status: Union[Unset, list["AsyncReplicationStatus"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        class_ = self.class_

        object_count = self.object_count

        vector_indexing_status: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vector_indexing_status, Unset):
            vector_indexing_status = self.vector_indexing_status.to_dict()

        compressed: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.compressed, Unset):
            compressed = self.compressed.to_dict()

        vector_queue_length = self.vector_queue_length

        loaded = self.loaded

        async_replication_status: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.async_replication_status, Unset):
            async_replication_status = []
            for async_replication_status_item_data in self.async_replication_status:
                async_replication_status_item = async_replication_status_item_data.to_dict()
                async_replication_status.append(async_replication_status_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if class_ is not UNSET:
            field_dict["class"] = class_
        if object_count is not UNSET:
            field_dict["objectCount"] = object_count
        if vector_indexing_status is not UNSET:
            field_dict["vectorIndexingStatus"] = vector_indexing_status
        if compressed is not UNSET:
            field_dict["compressed"] = compressed
        if vector_queue_length is not UNSET:
            field_dict["vectorQueueLength"] = vector_queue_length
        if loaded is not UNSET:
            field_dict["loaded"] = loaded
        if async_replication_status is not UNSET:
            field_dict["asyncReplicationStatus"] = async_replication_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.async_replication_status import AsyncReplicationStatus
        from ..models.node_shard_status_compressed import NodeShardStatusCompressed
        from ..models.node_shard_status_vector_indexing_status import NodeShardStatusVectorIndexingStatus

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        class_ = d.pop("class", UNSET)

        object_count = d.pop("objectCount", UNSET)

        _vector_indexing_status = d.pop("vectorIndexingStatus", UNSET)
        vector_indexing_status: Union[Unset, NodeShardStatusVectorIndexingStatus]
        if isinstance(_vector_indexing_status, Unset):
            vector_indexing_status = UNSET
        else:
            vector_indexing_status = NodeShardStatusVectorIndexingStatus.from_dict(_vector_indexing_status)

        _compressed = d.pop("compressed", UNSET)
        compressed: Union[Unset, NodeShardStatusCompressed]
        if isinstance(_compressed, Unset):
            compressed = UNSET
        else:
            compressed = NodeShardStatusCompressed.from_dict(_compressed)

        vector_queue_length = d.pop("vectorQueueLength", UNSET)

        loaded = d.pop("loaded", UNSET)

        async_replication_status = []
        _async_replication_status = d.pop("asyncReplicationStatus", UNSET)
        for async_replication_status_item_data in _async_replication_status or []:
            async_replication_status_item = AsyncReplicationStatus.from_dict(async_replication_status_item_data)

            async_replication_status.append(async_replication_status_item)

        node_shard_status = cls(
            name=name,
            class_=class_,
            object_count=object_count,
            vector_indexing_status=vector_indexing_status,
            compressed=compressed,
            vector_queue_length=vector_queue_length,
            loaded=loaded,
            async_replication_status=async_replication_status,
        )

        node_shard_status.additional_properties = d
        return node_shard_status

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
