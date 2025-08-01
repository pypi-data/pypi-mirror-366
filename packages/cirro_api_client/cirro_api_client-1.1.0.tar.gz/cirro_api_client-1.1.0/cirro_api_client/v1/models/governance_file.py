from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.governance_file_type import GovernanceFileType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GovernanceFile")


@_attrs_define
class GovernanceFile:
    """
    Attributes:
        name (Union[Unset, str]): The title of the resource visible to users
        description (Union[Unset, str]): A description of the resource visible to users
        src (Union[Unset, str]): The file name without path or the full link path
        type (Union[Unset, GovernanceFileType]): The options for supplementals for governance requirements
    """

    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    src: Union[Unset, str] = UNSET
    type: Union[Unset, GovernanceFileType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        description = self.description

        src = self.src

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if src is not UNSET:
            field_dict["src"] = src
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        src = d.pop("src", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, GovernanceFileType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = GovernanceFileType(_type)

        governance_file = cls(
            name=name,
            description=description,
            src=src,
            type=type,
        )

        governance_file.additional_properties = d
        return governance_file

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
