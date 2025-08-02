from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.property_tokenization import PropertyTokenization
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.nested_property import NestedProperty
    from ..models.property_module_config import PropertyModuleConfig


T = TypeVar("T", bound="Property")


@_attrs_define
class Property:
    """
    Attributes:
        data_type (Union[Unset, list[str]]): Data type of the property (required). If it starts with a capital (for
            example Person), may be a reference to another type.
        description (Union[Unset, str]): Description of the property.
        module_config (Union[Unset, PropertyModuleConfig]): Configuration specific to modules this Weaviate instance has
            installed
        name (Union[Unset, str]): The name of the property (required). Multiple words should be concatenated in
            camelCase, e.g. `nameOfAuthor`.
        index_inverted (Union[None, Unset, bool]): (Deprecated). Whether to include this property in the inverted index.
            If `false`, this property cannot be used in `where` filters, `bm25` or `hybrid` search. <br/><br/>Unrelated to
            vectorization behavior (deprecated as of v1.19; use indexFilterable or/and indexSearchable instead)
        index_filterable (Union[None, Unset, bool]): Whether to include this property in the filterable, Roaring Bitmap
            index. If `false`, this property cannot be used in `where` filters. <br/><br/>Note: Unrelated to vectorization
            behavior.
        index_searchable (Union[None, Unset, bool]): Optional. Should this property be indexed in the inverted index.
            Defaults to true. Applicable only to properties of data type text and text[]. If you choose false, you will not
            be able to use this property in bm25 or hybrid search. This property has no affect on vectorization decisions
            done by modules
        index_range_filters (Union[None, Unset, bool]): Whether to include this property in the filterable, range-based
            Roaring Bitmap index. Provides better performance for range queries compared to filterable index in large
            datasets. Applicable only to properties of data type int, number, date.
        tokenization (Union[Unset, PropertyTokenization]): Determines tokenization of the property as separate words or
            whole field. Optional. Applies to text and text[] data types. Allowed values are `word` (default; splits on any
            non-alphanumerical, lowercases), `lowercase` (splits on white spaces, lowercases), `whitespace` (splits on white
            spaces), `field` (trims). Not supported for remaining data types
        nested_properties (Union[Unset, list['NestedProperty']]): The properties of the nested object(s). Applies to
            object and object[] data types.
    """

    data_type: Union[Unset, list[str]] = UNSET
    description: Union[Unset, str] = UNSET
    module_config: Union[Unset, "PropertyModuleConfig"] = UNSET
    name: Union[Unset, str] = UNSET
    index_inverted: Union[None, Unset, bool] = UNSET
    index_filterable: Union[None, Unset, bool] = UNSET
    index_searchable: Union[None, Unset, bool] = UNSET
    index_range_filters: Union[None, Unset, bool] = UNSET
    tokenization: Union[Unset, PropertyTokenization] = UNSET
    nested_properties: Union[Unset, list["NestedProperty"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_type: Union[Unset, list[str]] = UNSET
        if not isinstance(self.data_type, Unset):
            data_type = self.data_type

        description = self.description

        module_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.module_config, Unset):
            module_config = self.module_config.to_dict()

        name = self.name

        index_inverted: Union[None, Unset, bool]
        if isinstance(self.index_inverted, Unset):
            index_inverted = UNSET
        else:
            index_inverted = self.index_inverted

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
        if module_config is not UNSET:
            field_dict["moduleConfig"] = module_config
        if name is not UNSET:
            field_dict["name"] = name
        if index_inverted is not UNSET:
            field_dict["indexInverted"] = index_inverted
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
        from ..models.nested_property import NestedProperty
        from ..models.property_module_config import PropertyModuleConfig

        d = dict(src_dict)
        data_type = cast(list[str], d.pop("dataType", UNSET))

        description = d.pop("description", UNSET)

        _module_config = d.pop("moduleConfig", UNSET)
        module_config: Union[Unset, PropertyModuleConfig]
        if isinstance(_module_config, Unset):
            module_config = UNSET
        else:
            module_config = PropertyModuleConfig.from_dict(_module_config)

        name = d.pop("name", UNSET)

        def _parse_index_inverted(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        index_inverted = _parse_index_inverted(d.pop("indexInverted", UNSET))

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
        tokenization: Union[Unset, PropertyTokenization]
        if isinstance(_tokenization, Unset):
            tokenization = UNSET
        else:
            tokenization = PropertyTokenization(_tokenization)

        nested_properties = []
        _nested_properties = d.pop("nestedProperties", UNSET)
        for nested_properties_item_data in _nested_properties or []:
            nested_properties_item = NestedProperty.from_dict(nested_properties_item_data)

            nested_properties.append(nested_properties_item)

        property_ = cls(
            data_type=data_type,
            description=description,
            module_config=module_config,
            name=name,
            index_inverted=index_inverted,
            index_filterable=index_filterable,
            index_searchable=index_searchable,
            index_range_filters=index_range_filters,
            tokenization=tokenization,
            nested_properties=nested_properties,
        )

        property_.additional_properties = d
        return property_

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
