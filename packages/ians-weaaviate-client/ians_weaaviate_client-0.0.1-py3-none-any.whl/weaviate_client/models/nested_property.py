from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.nested_property_tokenization import NestedPropertyTokenization
from ..types import UNSET, Unset

T = TypeVar("T", bound="NestedProperty")


@_attrs_define
class NestedProperty:
    """
    Attributes:
        data_type (Union[Unset, list[str]]):
        description (Union[Unset, str]):
        name (Union[Unset, str]):
        index_filterable (Union[None, Unset, bool]):
        index_searchable (Union[None, Unset, bool]):
        index_range_filters (Union[None, Unset, bool]):
        tokenization (Union[Unset, NestedPropertyTokenization]):
        nested_properties (Union[Unset, list['NestedProperty']]): The properties of the nested object(s). Applies to
            object and object[] data types.
    """

    data_type: Union[Unset, list[str]] = UNSET
    description: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    index_filterable: Union[None, Unset, bool] = UNSET
    index_searchable: Union[None, Unset, bool] = UNSET
    index_range_filters: Union[None, Unset, bool] = UNSET
    tokenization: Union[Unset, NestedPropertyTokenization] = UNSET
    nested_properties: Union[Unset, list["NestedProperty"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_type: Union[Unset, list[str]] = UNSET
        if not isinstance(self.data_type, Unset):
            data_type = self.data_type

        description = self.description

        name = self.name

        index_filterable: Union[None, Unset, bool]
        if isinstance(self.index_filterable, Unset):
            index_filterable = UNSET
        else:
            index_filterable = self.index_filterable

        index_searchable: Union[None, Unset, bool]
        if isinstance(self.index_searchable, Unset):
            index_searchable = UNSET
        else:
            index_searchable = self.index_searchable

        index_range_filters: Union[None, Unset, bool]
        if isinstance(self.index_range_filters, Unset):
            index_range_filters = UNSET
        else:
            index_range_filters = self.index_range_filters

        tokenization: Union[Unset, str] = UNSET
        if not isinstance(self.tokenization, Unset):
            tokenization = self.tokenization.value

        nested_properties: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nested_properties, Unset):
            nested_properties = []
            for nested_properties_item_data in self.nested_properties:
                nested_properties_item = nested_properties_item_data.to_dict()
                nested_properties.append(nested_properties_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data_type is not UNSET:
            field_dict["dataType"] = data_type
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name
        if index_filterable is not UNSET:
            field_dict["indexFilterable"] = index_filterable
        if index_searchable is not UNSET:
            field_dict["indexSearchable"] = index_searchable
        if index_range_filters is not UNSET:
            field_dict["indexRangeFilters"] = index_range_filters
        if tokenization is not UNSET:
            field_dict["tokenization"] = tokenization
        if nested_properties is not UNSET:
            field_dict["nestedProperties"] = nested_properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data_type = cast(list[str], d.pop("dataType", UNSET))

        description = d.pop("description", UNSET)

        name = d.pop("name", UNSET)

        def _parse_index_filterable(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        index_filterable = _parse_index_filterable(d.pop("indexFilterable", UNSET))

        def _parse_index_searchable(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        index_searchable = _parse_index_searchable(d.pop("indexSearchable", UNSET))

        def _parse_index_range_filters(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        index_range_filters = _parse_index_range_filters(d.pop("indexRangeFilters", UNSET))

        _tokenization = d.pop("tokenization", UNSET)
        tokenization: Union[Unset, NestedPropertyTokenization]
        if isinstance(_tokenization, Unset):
            tokenization = UNSET
        else:
            tokenization = NestedPropertyTokenization(_tokenization)

        nested_properties = []
        _nested_properties = d.pop("nestedProperties", UNSET)
        for nested_properties_item_data in _nested_properties or []:
            nested_properties_item = NestedProperty.from_dict(nested_properties_item_data)

            nested_properties.append(nested_properties_item)

        nested_property = cls(
            data_type=data_type,
            description=description,
            name=name,
            index_filterable=index_filterable,
            index_searchable=index_searchable,
            index_range_filters=index_range_filters,
            tokenization=tokenization,
            nested_properties=nested_properties,
        )

        nested_property.additional_properties = d
        return nested_property

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
