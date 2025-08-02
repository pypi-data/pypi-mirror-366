import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Deprecation")


@_attrs_define
class Deprecation:
    """
    Attributes:
        id (Union[Unset, str]): The id that uniquely identifies this particular deprecations (mostly used internally)
        status (Union[Unset, str]): Whether the problematic API functionality is deprecated (planned to be removed) or
            already removed
        api_type (Union[Unset, str]): Describes which API is effected, usually one of: REST, GraphQL
        msg (Union[Unset, str]): What this deprecation is about
        mitigation (Union[Unset, str]): User-required object to not be affected by the (planned) removal
        since_version (Union[Unset, str]): The deprecation was introduced in this version
        planned_removal_version (Union[Unset, str]): A best-effort guess of which upcoming version will remove the
            feature entirely
        removed_in (Union[None, Unset, str]): If the feature has already been removed, it was removed in this version
        removed_time (Union[None, Unset, datetime.datetime]): If the feature has already been removed, it was removed at
            this timestamp
        since_time (Union[Unset, datetime.datetime]): The deprecation was introduced in this version
        locations (Union[Unset, list[str]]): The locations within the specified API affected by this deprecation
    """

    id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    api_type: Union[Unset, str] = UNSET
    msg: Union[Unset, str] = UNSET
    mitigation: Union[Unset, str] = UNSET
    since_version: Union[Unset, str] = UNSET
    planned_removal_version: Union[Unset, str] = UNSET
    removed_in: Union[None, Unset, str] = UNSET
    removed_time: Union[None, Unset, datetime.datetime] = UNSET
    since_time: Union[Unset, datetime.datetime] = UNSET
    locations: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status

        api_type = self.api_type

        msg = self.msg

        mitigation = self.mitigation

        since_version = self.since_version

        planned_removal_version = self.planned_removal_version

        removed_in: Union[None, Unset, str]
        if isinstance(self.removed_in, Unset):
            removed_in = UNSET
        else:
            removed_in = self.removed_in

        removed_time: Union[None, Unset, str]
        if isinstance(self.removed_time, Unset):
            removed_time = UNSET
        elif isinstance(self.removed_time, datetime.datetime):
            removed_time = self.removed_time.isoformat()
        else:
            removed_time = self.removed_time

        since_time: Union[Unset, str] = UNSET
        if not isinstance(self.since_time, Unset):
            since_time = self.since_time.isoformat()

        locations: Union[Unset, list[str]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = self.locations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if status is not UNSET:
            field_dict["status"] = status
        if api_type is not UNSET:
            field_dict["apiType"] = api_type
        if msg is not UNSET:
            field_dict["msg"] = msg
        if mitigation is not UNSET:
            field_dict["mitigation"] = mitigation
        if since_version is not UNSET:
            field_dict["sinceVersion"] = since_version
        if planned_removal_version is not UNSET:
            field_dict["plannedRemovalVersion"] = planned_removal_version
        if removed_in is not UNSET:
            field_dict["removedIn"] = removed_in
        if removed_time is not UNSET:
            field_dict["removedTime"] = removed_time
        if since_time is not UNSET:
            field_dict["sinceTime"] = since_time
        if locations is not UNSET:
            field_dict["locations"] = locations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        status = d.pop("status", UNSET)

        api_type = d.pop("apiType", UNSET)

        msg = d.pop("msg", UNSET)

        mitigation = d.pop("mitigation", UNSET)

        since_version = d.pop("sinceVersion", UNSET)

        planned_removal_version = d.pop("plannedRemovalVersion", UNSET)

        def _parse_removed_in(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        removed_in = _parse_removed_in(d.pop("removedIn", UNSET))

        def _parse_removed_time(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                removed_time_type_0 = isoparse(data)

                return removed_time_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        removed_time = _parse_removed_time(d.pop("removedTime", UNSET))

        _since_time = d.pop("sinceTime", UNSET)
        since_time: Union[Unset, datetime.datetime]
        if isinstance(_since_time, Unset):
            since_time = UNSET
        else:
            since_time = isoparse(_since_time)

        locations = cast(list[str], d.pop("locations", UNSET))

        deprecation = cls(
            id=id,
            status=status,
            api_type=api_type,
            msg=msg,
            mitigation=mitigation,
            since_version=since_version,
            planned_removal_version=planned_removal_version,
            removed_in=removed_in,
            removed_time=removed_time,
            since_time=since_time,
            locations=locations,
        )

        deprecation.additional_properties = d
        return deprecation

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
