from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.permission_nodes_verbosity import PermissionNodesVerbosity
from ..types import UNSET, Unset

T = TypeVar("T", bound="PermissionNodes")


@_attrs_define
class PermissionNodes:
    """resources applicable for cluster actions

    Attributes:
        verbosity (Union[Unset, PermissionNodesVerbosity]): whether to allow (verbose) returning shards and stats data
            in the response Default: PermissionNodesVerbosity.MINIMAL.
        collection (Union[Unset, str]): string or regex. if a specific collection name, if left empty it will be ALL or
            * Default: '*'.
    """

    verbosity: Union[Unset, PermissionNodesVerbosity] = PermissionNodesVerbosity.MINIMAL
    collection: Union[Unset, str] = "*"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        verbosity: Union[Unset, str] = UNSET
        if not isinstance(self.verbosity, Unset):
            verbosity = self.verbosity.value

        collection = self.collection

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if verbosity is not UNSET:
            field_dict["verbosity"] = verbosity
        if collection is not UNSET:
            field_dict["collection"] = collection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _verbosity = d.pop("verbosity", UNSET)
        verbosity: Union[Unset, PermissionNodesVerbosity]
        if isinstance(_verbosity, Unset):
            verbosity = UNSET
        else:
            verbosity = PermissionNodesVerbosity(_verbosity)

        collection = d.pop("collection", UNSET)

        permission_nodes = cls(
            verbosity=verbosity,
            collection=collection,
        )

        permission_nodes.additional_properties = d
        return permission_nodes

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
