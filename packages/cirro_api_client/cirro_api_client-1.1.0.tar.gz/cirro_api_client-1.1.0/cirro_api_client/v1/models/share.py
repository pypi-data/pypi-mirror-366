import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.share_type import ShareType

if TYPE_CHECKING:
    from ..models.dataset_condition import DatasetCondition


T = TypeVar("T", bound="Share")


@_attrs_define
class Share:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        originating_project_id (str): The ID of the project that owns the share
        share_type (ShareType):
        conditions (List['DatasetCondition']):
        classification_ids (List[str]):
        keywords (List[str]):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    name: str
    description: str
    originating_project_id: str
    share_type: ShareType
    conditions: List["DatasetCondition"]
    classification_ids: List[str]
    keywords: List[str]
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        originating_project_id = self.originating_project_id

        share_type = self.share_type.value

        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        classification_ids = self.classification_ids

        keywords = self.keywords

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "originatingProjectId": originating_project_id,
                "shareType": share_type,
                "conditions": conditions,
                "classificationIds": classification_ids,
                "keywords": keywords,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.dataset_condition import DatasetCondition

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        originating_project_id = d.pop("originatingProjectId")

        share_type = ShareType(d.pop("shareType"))

        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:
            conditions_item = DatasetCondition.from_dict(conditions_item_data)

            conditions.append(conditions_item)

        classification_ids = cast(List[str], d.pop("classificationIds"))

        keywords = cast(List[str], d.pop("keywords"))

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        share = cls(
            id=id,
            name=name,
            description=description,
            originating_project_id=originating_project_id,
            share_type=share_type,
            conditions=conditions,
            classification_ids=classification_ids,
            keywords=keywords,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
        )

        share.additional_properties = d
        return share

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
