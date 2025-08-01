from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.governance_file_type import GovernanceFileType

T = TypeVar("T", bound="GovernanceFileInput")


@_attrs_define
class GovernanceFileInput:
    """
    Attributes:
        name (str):
        description (str):
        src (str):
        type (GovernanceFileType): The options for supplementals for governance requirements
    """

    name: str
    description: str
    src: str
    type: GovernanceFileType
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        description = self.description

        src = self.src

        type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "src": src,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        src = d.pop("src")

        type = GovernanceFileType(d.pop("type"))

        governance_file_input = cls(
            name=name,
            description=description,
            src=src,
            type=type,
        )

        governance_file_input.additional_properties = d
        return governance_file_input

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
