from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.backup_config import BackupConfig


T = TypeVar("T", bound="BackupCreateRequest")


@_attrs_define
class BackupCreateRequest:
    """Request body for creating a backup of a set of classes

    Attributes:
        id (Union[Unset, str]): The ID of the backup (required). Must be URL-safe and work as a filesystem path, only
            lowercase, numbers, underscore, minus characters allowed.
        config (Union[Unset, BackupConfig]): Backup custom configuration
        include (Union[Unset, list[str]]): List of collections to include in the backup creation process. If not set,
            all collections are included. Cannot be used together with `exclude`.
        exclude (Union[Unset, list[str]]): List of collections to exclude from the backup creation process. If not set,
            all collections are included. Cannot be used together with `include`.
    """

    id: Union[Unset, str] = UNSET
    config: Union[Unset, "BackupConfig"] = UNSET
    include: Union[Unset, list[str]] = UNSET
    exclude: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        include: Union[Unset, list[str]] = UNSET
        if not isinstance(self.include, Unset):
            include = self.include

        exclude: Union[Unset, list[str]] = UNSET
        if not isinstance(self.exclude, Unset):
            exclude = self.exclude

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if config is not UNSET:
            field_dict["config"] = config
        if include is not UNSET:
            field_dict["include"] = include
        if exclude is not UNSET:
            field_dict["exclude"] = exclude

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.backup_config import BackupConfig

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, BackupConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = BackupConfig.from_dict(_config)

        include = cast(list[str], d.pop("include", UNSET))

        exclude = cast(list[str], d.pop("exclude", UNSET))

        backup_create_request = cls(
            id=id,
            config=config,
            include=include,
            exclude=exclude,
        )

        backup_create_request.additional_properties = d
        return backup_create_request

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
