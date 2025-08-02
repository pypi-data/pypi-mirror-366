from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch_delete_match import BatchDeleteMatch


T = TypeVar("T", bound="BatchDelete")


@_attrs_define
class BatchDelete:
    """
    Attributes:
        match (Union[Unset, BatchDeleteMatch]): Outlines how to find the objects to be deleted.
        output (Union[Unset, str]): Controls the verbosity of the output, possible values are: "minimal", "verbose".
            Defaults to "minimal". Default: 'minimal'.
        deletion_time_unix_milli (Union[None, Unset, int]): Timestamp of deletion in milliseconds since epoch UTC.
        dry_run (Union[Unset, bool]): If true, the call will show which objects would be matched using the specified
            filter without deleting any objects. <br/><br/>Depending on the configured verbosity, you will either receive a
            count of affected objects, or a list of IDs. Default: False.
    """

    match: Union[Unset, "BatchDeleteMatch"] = UNSET
    output: Union[Unset, str] = "minimal"
    deletion_time_unix_milli: Union[None, Unset, int] = UNSET
    dry_run: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        match: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.match, Unset):
            match = self.match.to_dict()

        output = self.output

        deletion_time_unix_milli: Union[None, Unset, int]
        if isinstance(self.deletion_time_unix_milli, Unset):
            deletion_time_unix_milli = UNSET
        else:
            deletion_time_unix_milli = self.deletion_time_unix_milli

        dry_run = self.dry_run

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if match is not UNSET:
            field_dict["match"] = match
        if output is not UNSET:
            field_dict["output"] = output
        if deletion_time_unix_milli is not UNSET:
            field_dict["deletionTimeUnixMilli"] = deletion_time_unix_milli
        if dry_run is not UNSET:
            field_dict["dryRun"] = dry_run

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_delete_match import BatchDeleteMatch

        d = dict(src_dict)
        _match = d.pop("match", UNSET)
        match: Union[Unset, BatchDeleteMatch]
        if isinstance(_match, Unset):
            match = UNSET
        else:
            match = BatchDeleteMatch.from_dict(_match)

        output = d.pop("output", UNSET)

        def _parse_deletion_time_unix_milli(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        deletion_time_unix_milli = _parse_deletion_time_unix_milli(d.pop("deletionTimeUnixMilli", UNSET))

        dry_run = d.pop("dryRun", UNSET)

        batch_delete = cls(
            match=match,
            output=output,
            deletion_time_unix_milli=deletion_time_unix_milli,
            dry_run=dry_run,
        )

        batch_delete.additional_properties = d
        return batch_delete

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
