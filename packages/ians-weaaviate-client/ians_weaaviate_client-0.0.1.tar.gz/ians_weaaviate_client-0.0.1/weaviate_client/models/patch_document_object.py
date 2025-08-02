from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.patch_document_object_op import PatchDocumentObjectOp
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.object_ import Object
    from ..models.patch_document_object_value import PatchDocumentObjectValue


T = TypeVar("T", bound="PatchDocumentObject")


@_attrs_define
class PatchDocumentObject:
    """Either a JSONPatch document as defined by RFC 6902 (from, op, path, value), or a merge document (RFC 7396).

    Attributes:
        op (PatchDocumentObjectOp): The operation to be performed.
        path (str): A JSON-Pointer.
        from_ (Union[Unset, str]): A string containing a JSON Pointer value.
        value (Union[Unset, PatchDocumentObjectValue]): The value to be used within the operations.
        merge (Union[Unset, Object]):
    """

    op: PatchDocumentObjectOp
    path: str
    from_: Union[Unset, str] = UNSET
    value: Union[Unset, "PatchDocumentObjectValue"] = UNSET
    merge: Union[Unset, "Object"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        op = self.op.value

        path = self.path

        from_ = self.from_

        value: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.value, Unset):
            value = self.value.to_dict()

        merge: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.merge, Unset):
            merge = self.merge.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "op": op,
                "path": path,
            }
        )
        if from_ is not UNSET:
            field_dict["from"] = from_
        if value is not UNSET:
            field_dict["value"] = value
        if merge is not UNSET:
            field_dict["merge"] = merge

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.object_ import Object
        from ..models.patch_document_object_value import PatchDocumentObjectValue

        d = dict(src_dict)
        op = PatchDocumentObjectOp(d.pop("op"))

        path = d.pop("path")

        from_ = d.pop("from", UNSET)

        _value = d.pop("value", UNSET)
        value: Union[Unset, PatchDocumentObjectValue]
        if isinstance(_value, Unset):
            value = UNSET
        else:
            value = PatchDocumentObjectValue.from_dict(_value)

        _merge = d.pop("merge", UNSET)
        merge: Union[Unset, Object]
        if isinstance(_merge, Unset):
            merge = UNSET
        else:
            merge = Object.from_dict(_merge)

        patch_document_object = cls(
            op=op,
            path=path,
            from_=from_,
            value=value,
            merge=merge,
        )

        patch_document_object.additional_properties = d
        return patch_document_object

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
