from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.backup_restore_request_node_mapping import BackupRestoreRequestNodeMapping
    from ..models.restore_config import RestoreConfig


T = TypeVar("T", bound="BackupRestoreRequest")


@_attrs_define
class BackupRestoreRequest:
    """Request body for restoring a backup for a set of classes

    Attributes:
        config (Union[Unset, RestoreConfig]): Backup custom configuration
        include (Union[Unset, list[str]]): List of classes to include in the backup restoration process
        exclude (Union[Unset, list[str]]): List of classes to exclude from the backup restoration process
        node_mapping (Union[Unset, BackupRestoreRequestNodeMapping]): Allows overriding the node names stored in the
            backup with different ones. Useful when restoring backups to a different environment.
    """

    config: Union[Unset, "RestoreConfig"] = UNSET
    include: Union[Unset, list[str]] = UNSET
    exclude: Union[Unset, list[str]] = UNSET
    node_mapping: Union[Unset, "BackupRestoreRequestNodeMapping"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        include: Union[Unset, list[str]] = UNSET
        if not isinstance(self.include, Unset):
            include = self.include

        exclude: Union[Unset, list[str]] = UNSET
        if not isinstance(self.exclude, Unset):
            exclude = self.exclude

        node_mapping: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.node_mapping, Unset):
            node_mapping = self.node_mapping.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config is not UNSET:
            field_dict["config"] = config
        if include is not UNSET:
            field_dict["include"] = include
        if exclude is not UNSET:
            field_dict["exclude"] = exclude
        if node_mapping is not UNSET:
            field_dict["node_mapping"] = node_mapping

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.backup_restore_request_node_mapping import BackupRestoreRequestNodeMapping
        from ..models.restore_config import RestoreConfig

        d = dict(src_dict)
        _config = d.pop("config", UNSET)
        config: Union[Unset, RestoreConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = RestoreConfig.from_dict(_config)

        include = cast(list[str], d.pop("include", UNSET))

        exclude = cast(list[str], d.pop("exclude", UNSET))

        _node_mapping = d.pop("node_mapping", UNSET)
        node_mapping: Union[Unset, BackupRestoreRequestNodeMapping]
        if isinstance(_node_mapping, Unset):
            node_mapping = UNSET
        else:
            node_mapping = BackupRestoreRequestNodeMapping.from_dict(_node_mapping)

        backup_restore_request = cls(
            config=config,
            include=include,
            exclude=exclude,
            node_mapping=node_mapping,
        )

        backup_restore_request.additional_properties = d
        return backup_restore_request

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
