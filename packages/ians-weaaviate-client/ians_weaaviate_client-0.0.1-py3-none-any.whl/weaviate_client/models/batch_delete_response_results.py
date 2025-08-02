from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch_delete_response_results_objects_item import BatchDeleteResponseResultsObjectsItem


T = TypeVar("T", bound="BatchDeleteResponseResults")


@_attrs_define
class BatchDeleteResponseResults:
    """
    Attributes:
        matches (Union[Unset, float]): How many objects were matched by the filter.
        limit (Union[Unset, float]): The most amount of objects that can be deleted in a single query, equals
            QUERY_MAXIMUM_RESULTS.
        successful (Union[Unset, float]): How many objects were successfully deleted in this round.
        failed (Union[Unset, float]): How many objects should have been deleted but could not be deleted.
        objects (Union[Unset, list['BatchDeleteResponseResultsObjectsItem']]): With output set to "minimal" only objects
            with error occurred will the be described. Successfully deleted objects would be omitted. Output set to
            "verbose" will list all of the objets with their respective statuses.
    """

    matches: Union[Unset, float] = UNSET
    limit: Union[Unset, float] = UNSET
    successful: Union[Unset, float] = UNSET
    failed: Union[Unset, float] = UNSET
    objects: Union[Unset, list["BatchDeleteResponseResultsObjectsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        matches = self.matches

        limit = self.limit

        successful = self.successful

        failed = self.failed

        objects: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.objects, Unset):
            objects = []
            for objects_item_data in self.objects:
                objects_item = objects_item_data.to_dict()
                objects.append(objects_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if matches is not UNSET:
            field_dict["matches"] = matches
        if limit is not UNSET:
            field_dict["limit"] = limit
        if successful is not UNSET:
            field_dict["successful"] = successful
        if failed is not UNSET:
            field_dict["failed"] = failed
        if objects is not UNSET:
            field_dict["objects"] = objects

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_delete_response_results_objects_item import BatchDeleteResponseResultsObjectsItem

        d = dict(src_dict)
        matches = d.pop("matches", UNSET)

        limit = d.pop("limit", UNSET)

        successful = d.pop("successful", UNSET)

        failed = d.pop("failed", UNSET)

        objects = []
        _objects = d.pop("objects", UNSET)
        for objects_item_data in _objects or []:
            objects_item = BatchDeleteResponseResultsObjectsItem.from_dict(objects_item_data)

            objects.append(objects_item)

        batch_delete_response_results = cls(
            matches=matches,
            limit=limit,
            successful=successful,
            failed=failed,
            objects=objects,
        )

        batch_delete_response_results.additional_properties = d
        return batch_delete_response_results

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
