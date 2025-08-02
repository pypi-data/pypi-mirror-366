from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.vector_config_vector_index_config import VectorConfigVectorIndexConfig
    from ..models.vector_config_vectorizer import VectorConfigVectorizer


T = TypeVar("T", bound="VectorConfig")


@_attrs_define
class VectorConfig:
    """
    Attributes:
        vectorizer (Union[Unset, VectorConfigVectorizer]): Configuration of a specific vectorizer used by this vector
        vector_index_type (Union[Unset, str]): Name of the vector index to use, eg. (HNSW)
        vector_index_config (Union[Unset, VectorConfigVectorIndexConfig]): Vector-index config, that is specific to the
            type of index selected in vectorIndexType
    """

    vectorizer: Union[Unset, "VectorConfigVectorizer"] = UNSET
    vector_index_type: Union[Unset, str] = UNSET
    vector_index_config: Union[Unset, "VectorConfigVectorIndexConfig"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vectorizer: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vectorizer, Unset):
            vectorizer = self.vectorizer.to_dict()

        vector_index_type = self.vector_index_type

        vector_index_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vector_index_config, Unset):
            vector_index_config = self.vector_index_config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if vectorizer is not UNSET:
            field_dict["vectorizer"] = vectorizer
        if vector_index_type is not UNSET:
            field_dict["vectorIndexType"] = vector_index_type
        if vector_index_config is not UNSET:
            field_dict["vectorIndexConfig"] = vector_index_config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vector_config_vector_index_config import VectorConfigVectorIndexConfig
        from ..models.vector_config_vectorizer import VectorConfigVectorizer

        d = dict(src_dict)
        _vectorizer = d.pop("vectorizer", UNSET)
        vectorizer: Union[Unset, VectorConfigVectorizer]
        if isinstance(_vectorizer, Unset):
            vectorizer = UNSET
        else:
            vectorizer = VectorConfigVectorizer.from_dict(_vectorizer)

        vector_index_type = d.pop("vectorIndexType", UNSET)

        _vector_index_config = d.pop("vectorIndexConfig", UNSET)
        vector_index_config: Union[Unset, VectorConfigVectorIndexConfig]
        if isinstance(_vector_index_config, Unset):
            vector_index_config = UNSET
        else:
            vector_index_config = VectorConfigVectorIndexConfig.from_dict(_vector_index_config)

        vector_config = cls(
            vectorizer=vectorizer,
            vector_index_type=vector_index_type,
            vector_index_config=vector_index_config,
        )

        vector_config.additional_properties = d
        return vector_config

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
