from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_condition import DatasetCondition


T = TypeVar("T", bound="ShareInput")


@_attrs_define
class ShareInput:
    """
    Attributes:
        name (str):
        description (str):
        classification_ids (List[str]): Data classification IDs for the share
        conditions (List['DatasetCondition']): The conditions under which the dataset is shared
        keywords (Union[Unset, List[str]]): Search keywords for the share
        shared_project_ids (Union[Unset, List[str]]): The project IDs that can access this share
        is_view_restricted (Union[Unset, bool]): Whether files within the share are restricted from viewing or
            downloading Default: False.
    """

    name: str
    description: str
    classification_ids: List[str]
    conditions: List["DatasetCondition"]
    keywords: Union[Unset, List[str]] = UNSET
    shared_project_ids: Union[Unset, List[str]] = UNSET
    is_view_restricted: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        description = self.description

        classification_ids = self.classification_ids

        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        keywords: Union[Unset, List[str]] = UNSET
        if not isinstance(self.keywords, Unset):
            keywords = self.keywords

        shared_project_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.shared_project_ids, Unset):
            shared_project_ids = self.shared_project_ids

        is_view_restricted = self.is_view_restricted

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "classificationIds": classification_ids,
                "conditions": conditions,
            }
        )
        if keywords is not UNSET:
            field_dict["keywords"] = keywords
        if shared_project_ids is not UNSET:
            field_dict["sharedProjectIds"] = shared_project_ids
        if is_view_restricted is not UNSET:
            field_dict["isViewRestricted"] = is_view_restricted

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.dataset_condition import DatasetCondition

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        classification_ids = cast(List[str], d.pop("classificationIds"))

        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:
            conditions_item = DatasetCondition.from_dict(conditions_item_data)

            conditions.append(conditions_item)

        keywords = cast(List[str], d.pop("keywords", UNSET))

        shared_project_ids = cast(List[str], d.pop("sharedProjectIds", UNSET))

        is_view_restricted = d.pop("isViewRestricted", UNSET)

        share_input = cls(
            name=name,
            description=description,
            classification_ids=classification_ids,
            conditions=conditions,
            keywords=keywords,
            shared_project_ids=shared_project_ids,
            is_view_restricted=is_view_restricted,
        )

        share_input.additional_properties = d
        return share_input

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
