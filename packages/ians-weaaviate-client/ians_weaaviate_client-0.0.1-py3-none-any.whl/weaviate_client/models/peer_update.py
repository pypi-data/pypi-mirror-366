from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PeerUpdate")


@_attrs_define
class PeerUpdate:
    """A single peer in the network.

    Attributes:
        id (Union[Unset, UUID]): The session ID of the peer.
        name (Union[Unset, str]): Human readable name.
        uri (Union[Unset, str]): The location where the peer is exposed to the internet.
        schema_hash (Union[Unset, str]): The latest known hash of the peer's schema.
    """

    id: Union[Unset, UUID] = UNSET
    name: Union[Unset, str] = UNSET
    uri: Union[Unset, str] = UNSET
    schema_hash: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: Union[Unset, str] = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        name = self.name

        uri = self.uri

        schema_hash = self.schema_hash

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if uri is not UNSET:
            field_dict["uri"] = uri
        if schema_hash is not UNSET:
            field_dict["schemaHash"] = schema_hash

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

        name = d.pop("name", UNSET)

        uri = d.pop("uri", UNSET)

        schema_hash = d.pop("schemaHash", UNSET)

        peer_update = cls(
            id=id,
            name=name,
            uri=uri,
            schema_hash=schema_hash,
        )

        peer_update.additional_properties = d
        return peer_update

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
