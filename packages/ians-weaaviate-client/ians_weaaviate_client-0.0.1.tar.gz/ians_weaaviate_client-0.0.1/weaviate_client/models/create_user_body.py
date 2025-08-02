import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateUserBody")


@_attrs_define
class CreateUserBody:
    """
    Attributes:
        import_ (Union[Unset, bool]): EXPERIMENTAL, DONT USE. THIS WILL BE REMOVED AGAIN. - import api key from static
            user Default: False.
        create_time (Union[Unset, datetime.datetime]): EXPERIMENTAL, DONT USE. THIS WILL BE REMOVED AGAIN. - set the
            given time as creation time
    """

    import_: Union[Unset, bool] = False
    create_time: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        import_ = self.import_

        create_time: Union[Unset, str] = UNSET
        if not isinstance(self.create_time, Unset):
            create_time = self.create_time.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if import_ is not UNSET:
            field_dict["import"] = import_
        if create_time is not UNSET:
            field_dict["createTime"] = create_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        import_ = d.pop("import", UNSET)

        _create_time = d.pop("createTime", UNSET)
        create_time: Union[Unset, datetime.datetime]
        if isinstance(_create_time, Unset):
            create_time = UNSET
        else:
            create_time = isoparse(_create_time)

        create_user_body = cls(
            import_=import_,
            create_time=create_time,
        )

        create_user_body.additional_properties = d
        return create_user_body

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
