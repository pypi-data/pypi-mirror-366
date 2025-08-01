import datetime
from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="GovernanceContact")


@_attrs_define
class GovernanceContact:
    """
    Attributes:
        id (str):
        title (str):
        description (str):
        name (str):
        phone (str):
        email (str):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    title: str
    description: str
    name: str
    phone: str
    email: str
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        title = self.title

        description = self.description

        name = self.name

        phone = self.phone

        email = self.email

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "description": description,
                "name": name,
                "phone": phone,
                "email": email,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        title = d.pop("title")

        description = d.pop("description")

        name = d.pop("name")

        phone = d.pop("phone")

        email = d.pop("email")

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        governance_contact = cls(
            id=id,
            title=title,
            description=description,
            name=name,
            phone=phone,
            email=email,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
        )

        governance_contact.additional_properties = d
        return governance_contact

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
