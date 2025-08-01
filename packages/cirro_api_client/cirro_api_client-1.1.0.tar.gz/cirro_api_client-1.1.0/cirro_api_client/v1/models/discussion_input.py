from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.discussion_type import DiscussionType

if TYPE_CHECKING:
    from ..models.entity import Entity


T = TypeVar("T", bound="DiscussionInput")


@_attrs_define
class DiscussionInput:
    """
    Attributes:
        name (str):
        description (str):
        entity (Entity):
        type (DiscussionType):
        project_id (str):
    """

    name: str
    description: str
    entity: "Entity"
    type: DiscussionType
    project_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        description = self.description

        entity = self.entity.to_dict()

        type = self.type.value

        project_id = self.project_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "entity": entity,
                "type": type,
                "projectId": project_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.entity import Entity

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        entity = Entity.from_dict(d.pop("entity"))

        type = DiscussionType(d.pop("type"))

        project_id = d.pop("projectId")

        discussion_input = cls(
            name=name,
            description=description,
            entity=entity,
            type=type,
            project_id=project_id,
        )

        discussion_input.additional_properties = d
        return discussion_input

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
