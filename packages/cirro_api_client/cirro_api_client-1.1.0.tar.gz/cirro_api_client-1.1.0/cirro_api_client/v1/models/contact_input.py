from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ContactInput")


@_attrs_define
class ContactInput:
    """
    Attributes:
        title (str):
        description (str):
        name (str):
        phone (str):
        email (str):
    """

    title: str
    description: str
    name: str
    phone: str
    email: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        title = self.title

        description = self.description

        name = self.name

        phone = self.phone

        email = self.email

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "description": description,
                "name": name,
                "phone": phone,
                "email": email,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        title = d.pop("title")

        description = d.pop("description")

        name = d.pop("name")

        phone = d.pop("phone")

        email = d.pop("email")

        contact_input = cls(
            title=title,
            description=description,
            name=name,
            phone=phone,
            email=email,
        )

        contact_input.additional_properties = d
        return contact_input

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
