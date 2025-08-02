from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.classification_status import ClassificationStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.classification_filters import ClassificationFilters
    from ..models.classification_meta import ClassificationMeta
    from ..models.classification_settings import ClassificationSettings


T = TypeVar("T", bound="Classification")


@_attrs_define
class Classification:
    """Manage classifications, trigger them and view status of past classifications.

    Attributes:
        id (Union[Unset, UUID]): ID to uniquely identify this classification run Example:
            ee722219-b8ec-4db1-8f8d-5150bb1a9e0c.
        class_ (Union[Unset, str]): class (name) which is used in this classification Example: City.
        classify_properties (Union[Unset, list[str]]): which ref-property to set as part of the classification Example:
            ['inCountry'].
        based_on_properties (Union[Unset, list[str]]): base the text-based classification on these fields (of type text)
            Example: ['description'].
        status (Union[Unset, ClassificationStatus]): status of this classification Example: running.
        meta (Union[Unset, ClassificationMeta]): Additional information to a specific classification
        type_ (Union[Unset, str]): which algorithm to use for classifications
        settings (Union[Unset, ClassificationSettings]): classification-type specific settings
        error (Union[Unset, str]): error message if status == failed Default: ''. Example: classify xzy: something went
            wrong.
        filters (Union[Unset, ClassificationFilters]):
    """

    id: Union[Unset, UUID] = UNSET
    class_: Union[Unset, str] = UNSET
    classify_properties: Union[Unset, list[str]] = UNSET
    based_on_properties: Union[Unset, list[str]] = UNSET
    status: Union[Unset, ClassificationStatus] = UNSET
    meta: Union[Unset, "ClassificationMeta"] = UNSET
    type_: Union[Unset, str] = UNSET
    settings: Union[Unset, "ClassificationSettings"] = UNSET
    error: Union[Unset, str] = ""
    filters: Union[Unset, "ClassificationFilters"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: Union[Unset, str] = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        class_ = self.class_

        classify_properties: Union[Unset, list[str]] = UNSET
        if not isinstance(self.classify_properties, Unset):
            classify_properties = self.classify_properties

        based_on_properties: Union[Unset, list[str]] = UNSET
        if not isinstance(self.based_on_properties, Unset):
            based_on_properties = self.based_on_properties

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        meta: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        type_ = self.type_

        settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        error = self.error

        filters: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if class_ is not UNSET:
            field_dict["class"] = class_
        if classify_properties is not UNSET:
            field_dict["classifyProperties"] = classify_properties
        if based_on_properties is not UNSET:
            field_dict["basedOnProperties"] = based_on_properties
        if status is not UNSET:
            field_dict["status"] = status
        if meta is not UNSET:
            field_dict["meta"] = meta
        if type_ is not UNSET:
            field_dict["type"] = type_
        if settings is not UNSET:
            field_dict["settings"] = settings
        if error is not UNSET:
            field_dict["error"] = error
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.classification_filters import ClassificationFilters
        from ..models.classification_meta import ClassificationMeta
        from ..models.classification_settings import ClassificationSettings

        d = dict(src_dict)
        _id = d.pop("id", UNSET)
        id: Union[Unset, UUID]
        if isinstance(_id, Unset):
            id = UNSET
        else:
            id = UUID(_id)

        class_ = d.pop("class", UNSET)

        classify_properties = cast(list[str], d.pop("classifyProperties", UNSET))

        based_on_properties = cast(list[str], d.pop("basedOnProperties", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, ClassificationStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ClassificationStatus(_status)

        _meta = d.pop("meta", UNSET)
        meta: Union[Unset, ClassificationMeta]
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = ClassificationMeta.from_dict(_meta)

        type_ = d.pop("type", UNSET)

        _settings = d.pop("settings", UNSET)
        settings: Union[Unset, ClassificationSettings]
        if isinstance(_settings, Unset):
            settings = UNSET
        else:
            settings = ClassificationSettings.from_dict(_settings)

        error = d.pop("error", UNSET)

        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, ClassificationFilters]
        if isinstance(_filters, Unset):
            filters = UNSET
        else:
            filters = ClassificationFilters.from_dict(_filters)

        classification = cls(
            id=id,
            class_=class_,
            classify_properties=classify_properties,
            based_on_properties=based_on_properties,
            status=status,
            meta=meta,
            type_=type_,
            settings=settings,
            error=error,
            filters=filters,
        )

        classification.additional_properties = d
        return classification

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
