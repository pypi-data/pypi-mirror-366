import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.discussion_type import DiscussionType

if TYPE_CHECKING:
    from ..models.entity import Entity


T = TypeVar("T", bound="Discussion")


@_attrs_define
class Discussion:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        entity (Entity):
        type (DiscussionType):
        project_id (str):
        created_by (str):
        last_message_time (datetime.datetime):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    name: str
    description: str
    entity: "Entity"
    type: DiscussionType
    project_id: str
    created_by: str
    last_message_time: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        entity = self.entity.to_dict()

        type = self.type.value

        project_id = self.project_id

        created_by = self.created_by

        last_message_time = self.last_message_time.isoformat()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "entity": entity,
                "type": type,
                "projectId": project_id,
                "createdBy": created_by,
                "lastMessageTime": last_message_time,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.entity import Entity

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        entity = Entity.from_dict(d.pop("entity"))

        type = DiscussionType(d.pop("type"))

        project_id = d.pop("projectId")

        created_by = d.pop("createdBy")

        last_message_time = isoparse(d.pop("lastMessageTime"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        discussion = cls(
            id=id,
            name=name,
            description=description,
            entity=entity,
            type=type,
            project_id=project_id,
            created_by=created_by,
            last_message_time=last_message_time,
            created_at=created_at,
            updated_at=updated_at,
        )

        discussion.additional_properties = d
        return discussion

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
