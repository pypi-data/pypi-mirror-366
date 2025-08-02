from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch_delete_response_match import BatchDeleteResponseMatch
    from ..models.batch_delete_response_results import BatchDeleteResponseResults


T = TypeVar("T", bound="BatchDeleteResponse")


@_attrs_define
class BatchDeleteResponse:
    """Delete Objects response.

    Attributes:
        match (Union[Unset, BatchDeleteResponseMatch]): Outlines how to find the objects to be deleted.
        output (Union[Unset, str]): Controls the verbosity of the output, possible values are: "minimal", "verbose".
            Defaults to "minimal". Default: 'minimal'.
        deletion_time_unix_milli (Union[None, Unset, int]): Timestamp of deletion in milliseconds since epoch UTC.
        dry_run (Union[Unset, bool]): If true, objects will not be deleted yet, but merely listed. Defaults to false.
            Default: False.
        results (Union[Unset, BatchDeleteResponseResults]):
    """

    match: Union[Unset, "BatchDeleteResponseMatch"] = UNSET
    output: Union[Unset, str] = "minimal"
    deletion_time_unix_milli: Union[None, Unset, int] = UNSET
    dry_run: Union[Unset, bool] = False
    results: Union[Unset, "BatchDeleteResponseResults"] = UNSET
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

        results: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.results, Unset):
            results = self.results.to_dict()

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
        if results is not UNSET:
            field_dict["results"] = results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_delete_response_match import BatchDeleteResponseMatch
        from ..models.batch_delete_response_results import BatchDeleteResponseResults

        d = dict(src_dict)
        _match = d.pop("match", UNSET)
        match: Union[Unset, BatchDeleteResponseMatch]
        if isinstance(_match, Unset):
            match = UNSET
        else:
            match = BatchDeleteResponseMatch.from_dict(_match)

        output = d.pop("output", UNSET)

        def _parse_deletion_time_unix_milli(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        deletion_time_unix_milli = _parse_deletion_time_unix_milli(d.pop("deletionTimeUnixMilli", UNSET))

        dry_run = d.pop("dryRun", UNSET)

        _results = d.pop("results", UNSET)
        results: Union[Unset, BatchDeleteResponseResults]
        if isinstance(_results, Unset):
            results = UNSET
        else:
            results = BatchDeleteResponseResults.from_dict(_results)

        batch_delete_response = cls(
            match=match,
            output=output,
            deletion_time_unix_milli=deletion_time_unix_milli,
            dry_run=dry_run,
            results=results,
        )

        batch_delete_response.additional_properties = d
        return batch_delete_response

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
