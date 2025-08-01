from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.governance_access_type import GovernanceAccessType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GovernanceFileAccessRequest")


@_attrs_define
class GovernanceFileAccessRequest:
    """
    Attributes:
        access_type (GovernanceAccessType):
        fulfillment_id (Union[None, Unset, str]):
        project_id (Union[None, Unset, str]):
        token_lifetime_hours (Union[None, Unset, int]):
    """

    access_type: GovernanceAccessType
    fulfillment_id: Union[None, Unset, str] = UNSET
    project_id: Union[None, Unset, str] = UNSET
    token_lifetime_hours: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        access_type = self.access_type.value

        fulfillment_id: Union[None, Unset, str]
        if isinstance(self.fulfillment_id, Unset):
            fulfillment_id = UNSET
        else:
            fulfillment_id = self.fulfillment_id

        project_id: Union[None, Unset, str]
        if isinstance(self.project_id, Unset):
            project_id = UNSET
        else:
            project_id = self.project_id

        token_lifetime_hours: Union[None, Unset, int]
        if isinstance(self.token_lifetime_hours, Unset):
            token_lifetime_hours = UNSET
        else:
            token_lifetime_hours = self.token_lifetime_hours

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accessType": access_type,
            }
        )
        if fulfillment_id is not UNSET:
            field_dict["fulfillmentId"] = fulfillment_id
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if token_lifetime_hours is not UNSET:
            field_dict["tokenLifetimeHours"] = token_lifetime_hours

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        access_type = GovernanceAccessType(d.pop("accessType"))

        def _parse_fulfillment_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        fulfillment_id = _parse_fulfillment_id(d.pop("fulfillmentId", UNSET))

        def _parse_project_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        project_id = _parse_project_id(d.pop("projectId", UNSET))

        def _parse_token_lifetime_hours(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        token_lifetime_hours = _parse_token_lifetime_hours(d.pop("tokenLifetimeHours", UNSET))

        governance_file_access_request = cls(
            access_type=access_type,
            fulfillment_id=fulfillment_id,
            project_id=project_id,
            token_lifetime_hours=token_lifetime_hours,
        )

        governance_file_access_request.additional_properties = d
        return governance_file_access_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
