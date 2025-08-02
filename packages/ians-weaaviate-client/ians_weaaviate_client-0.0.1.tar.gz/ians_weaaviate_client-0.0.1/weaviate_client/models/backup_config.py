from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.backup_config_compression_level import BackupConfigCompressionLevel
from ..types import UNSET, Unset

T = TypeVar("T", bound="BackupConfig")


@_attrs_define
class BackupConfig:
    """Backup custom configuration

    Attributes:
        endpoint (Union[Unset, str]): name of the endpoint, e.g. s3.amazonaws.com
        bucket (Union[Unset, str]): Name of the bucket, container, volume, etc
        path (Union[Unset, str]): Path or key within the bucket
        cpu_percentage (Union[Unset, int]): Desired CPU core utilization ranging from 1%-80%
        chunk_size (Union[Unset, int]): Aimed chunk size, with a minimum of 2MB, default of 128MB, and a maximum of
            512MB. The actual chunk size may vary.
        compression_level (Union[Unset, BackupConfigCompressionLevel]): compression level used by compression algorithm
            Default: BackupConfigCompressionLevel.DEFAULTCOMPRESSION.
    """

    endpoint: Union[Unset, str] = UNSET
    bucket: Union[Unset, str] = UNSET
    path: Union[Unset, str] = UNSET
    cpu_percentage: Union[Unset, int] = UNSET
    chunk_size: Union[Unset, int] = UNSET
    compression_level: Union[Unset, BackupConfigCompressionLevel] = BackupConfigCompressionLevel.DEFAULTCOMPRESSION
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        endpoint = self.endpoint

        bucket = self.bucket

        path = self.path

        cpu_percentage = self.cpu_percentage

        chunk_size = self.chunk_size

        compression_level: Union[Unset, str] = UNSET
        if not isinstance(self.compression_level, Unset):
            compression_level = self.compression_level.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if endpoint is not UNSET:
            field_dict["Endpoint"] = endpoint
        if bucket is not UNSET:
            field_dict["Bucket"] = bucket
        if path is not UNSET:
            field_dict["Path"] = path
        if cpu_percentage is not UNSET:
            field_dict["CPUPercentage"] = cpu_percentage
        if chunk_size is not UNSET:
            field_dict["ChunkSize"] = chunk_size
        if compression_level is not UNSET:
            field_dict["CompressionLevel"] = compression_level

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        endpoint = d.pop("Endpoint", UNSET)

        bucket = d.pop("Bucket", UNSET)

        path = d.pop("Path", UNSET)

        cpu_percentage = d.pop("CPUPercentage", UNSET)

        chunk_size = d.pop("ChunkSize", UNSET)

        _compression_level = d.pop("CompressionLevel", UNSET)
        compression_level: Union[Unset, BackupConfigCompressionLevel]
        if isinstance(_compression_level, Unset):
            compression_level = UNSET
        else:
            compression_level = BackupConfigCompressionLevel(_compression_level)

        backup_config = cls(
            endpoint=endpoint,
            bucket=bucket,
            path=path,
            cpu_percentage=cpu_percentage,
            chunk_size=chunk_size,
            compression_level=compression_level,
        )

        backup_config.additional_properties = d
        return backup_config

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
