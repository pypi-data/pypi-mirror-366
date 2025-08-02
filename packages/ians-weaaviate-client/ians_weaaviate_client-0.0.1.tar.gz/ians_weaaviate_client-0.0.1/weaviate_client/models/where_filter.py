from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.where_filter_operator import WhereFilterOperator
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.where_filter_geo_range import WhereFilterGeoRange


T = TypeVar("T", bound="WhereFilter")


@_attrs_define
class WhereFilter:
    """Filter search results using a where filter

    Attributes:
        operands (Union[Unset, list['WhereFilter']]): combine multiple where filters, requires 'And' or 'Or' operator
        operator (Union[Unset, WhereFilterOperator]): operator to use Example: GreaterThanEqual.
        path (Union[Unset, list[str]]): path to the property currently being filtered Example: ['inCity', 'City',
            'name'].
        value_int (Union[None, Unset, int]): value as integer Example: 2000.
        value_number (Union[None, Unset, float]): value as number/float Example: 3.14.
        value_boolean (Union[None, Unset, bool]): value as boolean
        value_string (Union[None, Unset, str]): value as text (deprecated as of v1.19; alias for valueText) Example: my
            search term.
        value_text (Union[None, Unset, str]): value as text Example: my search term.
        value_date (Union[None, Unset, str]): value as date (as string) Example: TODO.
        value_int_array (Union[None, Unset, list[int]]): value as integer Example: [100, 200].
        value_number_array (Union[None, Unset, list[float]]): value as number/float Example: [3.14].
        value_boolean_array (Union[None, Unset, list[bool]]): value as boolean Example: [True, False].
        value_string_array (Union[None, Unset, list[str]]): value as text (deprecated as of v1.19; alias for valueText)
            Example: ['my search term'].
        value_text_array (Union[None, Unset, list[str]]): value as text Example: ['my search term'].
        value_date_array (Union[None, Unset, list[str]]): value as date (as string) Example: TODO.
        value_geo_range (Union[Unset, WhereFilterGeoRange]): filter within a distance of a georange
    """

    operands: Union[Unset, list["WhereFilter"]] = UNSET
    operator: Union[Unset, WhereFilterOperator] = UNSET
    path: Union[Unset, list[str]] = UNSET
    value_int: Union[None, Unset, int] = UNSET
    value_number: Union[None, Unset, float] = UNSET
    value_boolean: Union[None, Unset, bool] = UNSET
    value_string: Union[None, Unset, str] = UNSET
    value_text: Union[None, Unset, str] = UNSET
    value_date: Union[None, Unset, str] = UNSET
    value_int_array: Union[None, Unset, list[int]] = UNSET
    value_number_array: Union[None, Unset, list[float]] = UNSET
    value_boolean_array: Union[None, Unset, list[bool]] = UNSET
    value_string_array: Union[None, Unset, list[str]] = UNSET
    value_text_array: Union[None, Unset, list[str]] = UNSET
    value_date_array: Union[None, Unset, list[str]] = UNSET
    value_geo_range: Union[Unset, "WhereFilterGeoRange"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        operands: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.operands, Unset):
            operands = []
            for operands_item_data in self.operands:
                operands_item = operands_item_data.to_dict()
                operands.append(operands_item)

        operator: Union[Unset, str] = UNSET
        if not isinstance(self.operator, Unset):
            operator = self.operator.value

        path: Union[Unset, list[str]] = UNSET
        if not isinstance(self.path, Unset):
            path = self.path

        value_int: Union[None, Unset, int]
        if isinstance(self.value_int, Unset):
            value_int = UNSET
        else:
            value_int = self.value_int

        value_number: Union[None, Unset, float]
        if isinstance(self.value_number, Unset):
            value_number = UNSET
        else:
            value_number = self.value_number

        value_boolean: Union[None, Unset, bool]
        if isinstance(self.value_boolean, Unset):
            value_boolean = UNSET
        else:
            value_boolean = self.value_boolean

        value_string: Union[None, Unset, str]
        if isinstance(self.value_string, Unset):
            value_string = UNSET
        else:
            value_string = self.value_string

        value_text: Union[None, Unset, str]
        if isinstance(self.value_text, Unset):
            value_text = UNSET
        else:
            value_text = self.value_text

        value_date: Union[None, Unset, str]
        if isinstance(self.value_date, Unset):
            value_date = UNSET
        else:
            value_date = self.value_date

        value_int_array: Union[None, Unset, list[int]]
        if isinstance(self.value_int_array, Unset):
            value_int_array = UNSET
        elif isinstance(self.value_int_array, list):
            value_int_array = self.value_int_array

        else:
            value_int_array = self.value_int_array

        value_number_array: Union[None, Unset, list[float]]
        if isinstance(self.value_number_array, Unset):
            value_number_array = UNSET
        elif isinstance(self.value_number_array, list):
            value_number_array = self.value_number_array

        else:
            value_number_array = self.value_number_array

        value_boolean_array: Union[None, Unset, list[bool]]
        if isinstance(self.value_boolean_array, Unset):
            value_boolean_array = UNSET
        elif isinstance(self.value_boolean_array, list):
            value_boolean_array = self.value_boolean_array

        else:
            value_boolean_array = self.value_boolean_array

        value_string_array: Union[None, Unset, list[str]]
        if isinstance(self.value_string_array, Unset):
            value_string_array = UNSET
        elif isinstance(self.value_string_array, list):
            value_string_array = self.value_string_array

        else:
            value_string_array = self.value_string_array

        value_text_array: Union[None, Unset, list[str]]
        if isinstance(self.value_text_array, Unset):
            value_text_array = UNSET
        elif isinstance(self.value_text_array, list):
            value_text_array = self.value_text_array

        else:
            value_text_array = self.value_text_array

        value_date_array: Union[None, Unset, list[str]]
        if isinstance(self.value_date_array, Unset):
            value_date_array = UNSET
        elif isinstance(self.value_date_array, list):
            value_date_array = self.value_date_array

        else:
            value_date_array = self.value_date_array

        value_geo_range: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.value_geo_range, Unset):
            value_geo_range = self.value_geo_range.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if operands is not UNSET:
            field_dict["operands"] = operands
        if operator is not UNSET:
            field_dict["operator"] = operator
        if path is not UNSET:
            field_dict["path"] = path
        if value_int is not UNSET:
            field_dict["valueInt"] = value_int
        if value_number is not UNSET:
            field_dict["valueNumber"] = value_number
        if value_boolean is not UNSET:
            field_dict["valueBoolean"] = value_boolean
        if value_string is not UNSET:
            field_dict["valueString"] = value_string
        if value_text is not UNSET:
            field_dict["valueText"] = value_text
        if value_date is not UNSET:
            field_dict["valueDate"] = value_date
        if value_int_array is not UNSET:
            field_dict["valueIntArray"] = value_int_array
        if value_number_array is not UNSET:
            field_dict["valueNumberArray"] = value_number_array
        if value_boolean_array is not UNSET:
            field_dict["valueBooleanArray"] = value_boolean_array
        if value_string_array is not UNSET:
            field_dict["valueStringArray"] = value_string_array
        if value_text_array is not UNSET:
            field_dict["valueTextArray"] = value_text_array
        if value_date_array is not UNSET:
            field_dict["valueDateArray"] = value_date_array
        if value_geo_range is not UNSET:
            field_dict["valueGeoRange"] = value_geo_range

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.where_filter_geo_range import WhereFilterGeoRange

        d = dict(src_dict)
        operands = []
        _operands = d.pop("operands", UNSET)
        for operands_item_data in _operands or []:
            operands_item = WhereFilter.from_dict(operands_item_data)

            operands.append(operands_item)

        _operator = d.pop("operator", UNSET)
        operator: Union[Unset, WhereFilterOperator]
        if isinstance(_operator, Unset):
            operator = UNSET
        else:
            operator = WhereFilterOperator(_operator)

        path = cast(list[str], d.pop("path", UNSET))

        def _parse_value_int(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        value_int = _parse_value_int(d.pop("valueInt", UNSET))

        def _parse_value_number(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        value_number = _parse_value_number(d.pop("valueNumber", UNSET))

        def _parse_value_boolean(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        value_boolean = _parse_value_boolean(d.pop("valueBoolean", UNSET))

        def _parse_value_string(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        value_string = _parse_value_string(d.pop("valueString", UNSET))

        def _parse_value_text(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        value_text = _parse_value_text(d.pop("valueText", UNSET))

        def _parse_value_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        value_date = _parse_value_date(d.pop("valueDate", UNSET))

        def _parse_value_int_array(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_int_array_type_0 = cast(list[int], data)

                return value_int_array_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        value_int_array = _parse_value_int_array(d.pop("valueIntArray", UNSET))

        def _parse_value_number_array(data: object) -> Union[None, Unset, list[float]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_number_array_type_0 = cast(list[float], data)

                return value_number_array_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[float]], data)

        value_number_array = _parse_value_number_array(d.pop("valueNumberArray", UNSET))

        def _parse_value_boolean_array(data: object) -> Union[None, Unset, list[bool]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_boolean_array_type_0 = cast(list[bool], data)

                return value_boolean_array_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[bool]], data)

        value_boolean_array = _parse_value_boolean_array(d.pop("valueBooleanArray", UNSET))

        def _parse_value_string_array(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_string_array_type_0 = cast(list[str], data)

                return value_string_array_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        value_string_array = _parse_value_string_array(d.pop("valueStringArray", UNSET))

        def _parse_value_text_array(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_text_array_type_0 = cast(list[str], data)

                return value_text_array_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        value_text_array = _parse_value_text_array(d.pop("valueTextArray", UNSET))

        def _parse_value_date_array(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_date_array_type_0 = cast(list[str], data)

                return value_date_array_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        value_date_array = _parse_value_date_array(d.pop("valueDateArray", UNSET))

        _value_geo_range = d.pop("valueGeoRange", UNSET)
        value_geo_range: Union[Unset, WhereFilterGeoRange]
        if isinstance(_value_geo_range, Unset):
            value_geo_range = UNSET
        else:
            value_geo_range = WhereFilterGeoRange.from_dict(_value_geo_range)

        where_filter = cls(
            operands=operands,
            operator=operator,
            path=path,
            value_int=value_int,
            value_number=value_number,
            value_boolean=value_boolean,
            value_string=value_string,
            value_text=value_text,
            value_date=value_date,
            value_int_array=value_int_array,
            value_number_array=value_number_array,
            value_boolean_array=value_boolean_array,
            value_string_array=value_string_array,
            value_text_array=value_text_array,
            value_date_array=value_date_array,
            value_geo_range=value_geo_range,
        )

        where_filter.additional_properties = d
        return where_filter

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
