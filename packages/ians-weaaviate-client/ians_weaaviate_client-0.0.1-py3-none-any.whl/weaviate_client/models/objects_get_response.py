from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.additional_properties import AdditionalProperties
    from ..models.deprecation import Deprecation
    from ..models.objects_get_response_result import ObjectsGetResponseResult
    from ..models.property_schema import PropertySchema
    from ..models.vector_weights import VectorWeights
    from ..models.vectors import Vectors


T = TypeVar("T", bound="ObjectsGetResponse")


@_attrs_define
class ObjectsGetResponse:
    """
    Attributes:
        class_ (Union[Unset, str]): Class of the Object, defined in the schema.
        vector_weights (Union[Unset, VectorWeights]): Allow custom overrides of vector weights as math expressions. E.g.
            "pancake": "7" will set the weight for the word pancake to 7 in the vectorization, whereas "w * 3" would triple
            the originally calculated word. This is an open object, with OpenAPI Specification 3.0 this will be more
            detailed. See Weaviate docs for more info. In the future this will become a key/value (string/string) object.
        properties (Union[Unset, PropertySchema]): Names and values of an individual property. A returned response may
            also contain additional metadata, such as from classification or feature projection.
        id (Union[Unset, UUID]): ID of the Object.
        creation_time_unix (Union[Unset, int]): (Response only) Timestamp of creation of this object in milliseconds
            since epoch UTC.
        last_update_time_unix (Union[Unset, int]): (Response only) Timestamp of the last object update in milliseconds
            since epoch UTC.
        vector (Union[Unset, list[float]]): A vector representation of the object in the Contextionary. If provided at
            object creation, this wil take precedence over any vectorizer setting.
        vectors (Union[Unset, Vectors]): A map of named vectors for multi-vector representations.
        tenant (Union[Unset, str]): Name of the Objects tenant.
        additional (Union[Unset, AdditionalProperties]): (Response only) Additional meta information about a single
            object.
        deprecations (Union[Unset, list['Deprecation']]):
        result (Union[Unset, ObjectsGetResponseResult]): Results for this specific Object.
    """

    class_: Union[Unset, str] = UNSET
    vector_weights: Union[Unset, "VectorWeights"] = UNSET
    properties: Union[Unset, "PropertySchema"] = UNSET
    id: Union[Unset, UUID] = UNSET
    creation_time_unix: Union[Unset, int] = UNSET
    last_update_time_unix: Union[Unset, int] = UNSET
    vector: Union[Unset, list[float]] = UNSET
    vectors: Union[Unset, "Vectors"] = UNSET
    tenant: Union[Unset, str] = UNSET
    additional: Union[Unset, "AdditionalProperties"] = UNSET
    deprecations: Union[Unset, list["Deprecation"]] = UNSET
    result: Union[Unset, "ObjectsGetResponseResult"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        class_ = self.class_

        vector_weights: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vector_weights, Unset):
            vector_weights = self.vector_weights.to_dict()

        properties: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        id: Union[Unset, str] = UNSET
        if not isinstance(self.id, Unset):
            id = str(self.id)

        creation_time_unix = self.creation_time_unix

        last_update_time_unix = self.last_update_time_unix

        vector: Union[Unset, list[float]] = UNSET
        if not isinstance(self.vector, Unset):
            vector = self.vector

        vectors: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vectors, Unset):
            vectors = self.vectors.to_dict()

        tenant = self.tenant

        additional: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.additional, Unset):
            additional = self.additional.to_dict()

        deprecations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.deprecations, Unset):
            deprecations = []
            for deprecations_item_data in self.deprecations:
                deprecations_item = deprecations_item_data.to_dict()
                deprecations.append(deprecations_item)

        result: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if class_ is not UNSET:
            field_dict["class"] = class_
        if vector_weights is not UNSET:
            field_dict["vectorWeights"] = vector_weights
        if properties is not UNSET:
            field_dict["properties"] = properties
        if id is not UNSET:
            field_dict["id"] = id
        if creation_time_unix is not UNSET:
            field_dict["creationTimeUnix"] = creation_time_unix
        if last_update_time_unix is not UNSET:
            field_dict["lastUpdateTimeUnix"] = last_update_time_unix
        if vector is not UNSET:
            field_dict["vector"] = vector
        if vectors is not UNSET:
            field_dict["vectors"] = vectors
        if tenant is not UNSET:
            field_dict["tenant"] = tenant
        if additional is not UNSET:
            field_dict["additional"] = additional
        if deprecations is not UNSET:
            field_dict["deprecations"] = deprecations
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.additional_properties import AdditionalProperties
        from ..models.deprecation import Deprecation
        from ..models.objects_get_response_result import ObjectsGetResponseResult
        from ..models.property_schema import PropertySchema
        from ..models.vector_weights import VectorWeights
        from ..models.vectors import Vectors

        d = dict(src_dict)
        class_ = d.pop("class", UNSET)

        _vector_weights = d.pop("vectorWeights", UNSET)
        vector_weights: Union[Unset, VectorWeights]
        if isinstance(_vector_weights, Unset):
            vector_weights = UNSET
        else:
            vector_weights = VectorWeights.from_dict(_vector_weights)

        _properties = d.pop("properties", UNSET)
        properties: Union[Unset, PropertySchema]
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = PropertySchema.from_dict(_properties)

        _id = d.pop("id", UNSET)
        id: Union[Unset, UUID]
        if isinstance(_id, Unset):
            id = UNSET
        else:
            id = UUID(_id)

        creation_time_unix = d.pop("creationTimeUnix", UNSET)

        last_update_time_unix = d.pop("lastUpdateTimeUnix", UNSET)

        vector = cast(list[float], d.pop("vector", UNSET))

        _vectors = d.pop("vectors", UNSET)
        vectors: Union[Unset, Vectors]
        if isinstance(_vectors, Unset):
            vectors = UNSET
        else:
            vectors = Vectors.from_dict(_vectors)

        tenant = d.pop("tenant", UNSET)

        _additional = d.pop("additional", UNSET)
        additional: Union[Unset, AdditionalProperties]
        if isinstance(_additional, Unset):
            additional = UNSET
        else:
            additional = AdditionalProperties.from_dict(_additional)

        deprecations = []
        _deprecations = d.pop("deprecations", UNSET)
        for deprecations_item_data in _deprecations or []:
            deprecations_item = Deprecation.from_dict(deprecations_item_data)

            deprecations.append(deprecations_item)

        _result = d.pop("result", UNSET)
        result: Union[Unset, ObjectsGetResponseResult]
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = ObjectsGetResponseResult.from_dict(_result)

        objects_get_response = cls(
            class_=class_,
            vector_weights=vector_weights,
            properties=properties,
            id=id,
            creation_time_unix=creation_time_unix,
            last_update_time_unix=last_update_time_unix,
            vector=vector,
            vectors=vectors,
            tenant=tenant,
            additional=additional,
            deprecations=deprecations,
            result=result,
        )

        objects_get_response.additional_properties = d
        return objects_get_response

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
