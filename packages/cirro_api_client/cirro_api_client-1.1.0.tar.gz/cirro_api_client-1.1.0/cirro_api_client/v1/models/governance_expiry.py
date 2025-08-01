import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.governance_expiry_type import GovernanceExpiryType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GovernanceExpiry")


@_attrs_define
class GovernanceExpiry:
    """
    Attributes:
        type (Union[Unset, GovernanceExpiryType]): The expiry conditions that can be applied to governance requirements.
        days (Union[None, Unset, int]): The number of days for a relative expiration
        date (Union[None, Unset, datetime.datetime]): The date for an absolute expiration
    """

    type: Union[Unset, GovernanceExpiryType] = UNSET
    days: Union[None, Unset, int] = UNSET
    date: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        days: Union[None, Unset, int]
        if isinstance(self.days, Unset):
            days = UNSET
        else:
            days = self.days

        date: Union[None, Unset, str]
        if isinstance(self.date, Unset):
            date = UNSET
        elif isinstance(self.date, datetime.datetime):
            date = self.date.isoformat()
        else:
            date = self.date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type is not UNSET:
            field_dict["type"] = type
        if days is not UNSET:
            field_dict["days"] = days
        if date is not UNSET:
            field_dict["date"] = date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _type = d.pop("type", UNSET)
        type: Union[Unset, GovernanceExpiryType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = GovernanceExpiryType(_type)

        def _parse_days(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        days = _parse_days(d.pop("days", UNSET))

        def _parse_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                date_type_0 = isoparse(data)

                return date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        date = _parse_date(d.pop("date", UNSET))

        governance_expiry = cls(
            type=type,
            days=days,
            date=date,
        )

        governance_expiry.additional_properties = d
        return governance_expiry

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
