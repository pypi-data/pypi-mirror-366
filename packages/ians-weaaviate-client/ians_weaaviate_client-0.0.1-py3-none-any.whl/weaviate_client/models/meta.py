from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.meta_modules import MetaModules


T = TypeVar("T", bound="Meta")


@_attrs_define
class Meta:
    """Contains meta information of the current Weaviate instance.

    Attributes:
        hostname (Union[Unset, str]): The url of the host.
        version (Union[Unset, str]): The Weaviate server version.
        modules (Union[Unset, MetaModules]): Module-specific meta information.
        grpc_max_message_size (Union[Unset, int]): Max message size for GRPC connection in bytes.
    """

    hostname: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    modules: Union[Unset, "MetaModules"] = UNSET
    grpc_max_message_size: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hostname = self.hostname

        version = self.version

        modules: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.modules, Unset):
            modules = self.modules.to_dict()

        grpc_max_message_size = self.grpc_max_message_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if version is not UNSET:
            field_dict["version"] = version
        if modules is not UNSET:
            field_dict["modules"] = modules
        if grpc_max_message_size is not UNSET:
            field_dict["grpcMaxMessageSize"] = grpc_max_message_size

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.meta_modules import MetaModules

        d = dict(src_dict)
        hostname = d.pop("hostname", UNSET)

        version = d.pop("version", UNSET)

        _modules = d.pop("modules", UNSET)
        modules: Union[Unset, MetaModules]
        if isinstance(_modules, Unset):
            modules = UNSET
        else:
            modules = MetaModules.from_dict(_modules)

        grpc_max_message_size = d.pop("grpcMaxMessageSize", UNSET)

        meta = cls(
            hostname=hostname,
            version=version,
            modules=modules,
            grpc_max_message_size=grpc_max_message_size,
        )

        meta.additional_properties = d
        return meta

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
