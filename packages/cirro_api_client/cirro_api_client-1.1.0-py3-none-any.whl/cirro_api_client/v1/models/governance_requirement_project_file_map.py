from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.governance_file import GovernanceFile


T = TypeVar("T", bound="GovernanceRequirementProjectFileMap")


@_attrs_define
class GovernanceRequirementProjectFileMap:
    """Files supplied by each project when authorship is project"""

    additional_properties: Dict[str, "GovernanceFile"] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.governance_file import GovernanceFile

        d = src_dict.copy()
        governance_requirement_project_file_map = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = GovernanceFile.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        governance_requirement_project_file_map.additional_properties = additional_properties
        return governance_requirement_project_file_map

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
