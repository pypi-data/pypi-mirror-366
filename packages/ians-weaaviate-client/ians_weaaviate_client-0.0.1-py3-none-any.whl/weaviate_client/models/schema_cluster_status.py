from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SchemaClusterStatus")


@_attrs_define
class SchemaClusterStatus:
    """Indicates the health of the schema in a cluster.

    Attributes:
        healthy (Union[Unset, bool]): True if the cluster is in sync, false if there is an issue (see error).
        error (Union[Unset, str]): Contains the sync check error if one occurred
        hostname (Union[Unset, str]): Hostname of the coordinating node, i.e. the one that received the cluster. This
            can be useful information if the error message contains phrases such as 'other nodes agree, but local does not',
            etc.
        node_count (Union[Unset, float]): Number of nodes that participated in the sync check
        ignore_schema_sync (Union[Unset, bool]): The cluster check at startup can be ignored (to recover from an out-of-
            sync situation).
    """

    healthy: Union[Unset, bool] = UNSET
    error: Union[Unset, str] = UNSET
    hostname: Union[Unset, str] = UNSET
    node_count: Union[Unset, float] = UNSET
    ignore_schema_sync: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        healthy = self.healthy

        error = self.error

        hostname = self.hostname

        node_count = self.node_count

        ignore_schema_sync = self.ignore_schema_sync

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if healthy is not UNSET:
            field_dict["healthy"] = healthy
        if error is not UNSET:
            field_dict["error"] = error
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if node_count is not UNSET:
            field_dict["nodeCount"] = node_count
        if ignore_schema_sync is not UNSET:
            field_dict["ignoreSchemaSync"] = ignore_schema_sync

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        healthy = d.pop("healthy", UNSET)

        error = d.pop("error", UNSET)

        hostname = d.pop("hostname", UNSET)

        node_count = d.pop("nodeCount", UNSET)

        ignore_schema_sync = d.pop("ignoreSchemaSync", UNSET)

        schema_cluster_status = cls(
            healthy=healthy,
            error=error,
            hostname=hostname,
            node_count=node_count,
            ignore_schema_sync=ignore_schema_sync,
        )

        schema_cluster_status.additional_properties = d
        return schema_cluster_status

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
