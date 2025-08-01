from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MoveDatasetInput")


@_attrs_define
class MoveDatasetInput:
    """
    Attributes:
        dataset_id (str):
        source_project_id (str):
        target_project_id (str):
    """

    dataset_id: str
    source_project_id: str
    target_project_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_id = self.dataset_id

        source_project_id = self.source_project_id

        target_project_id = self.target_project_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datasetId": dataset_id,
                "sourceProjectId": source_project_id,
                "targetProjectId": target_project_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_id = d.pop("datasetId")

        source_project_id = d.pop("sourceProjectId")

        target_project_id = d.pop("targetProjectId")

        move_dataset_input = cls(
            dataset_id=dataset_id,
            source_project_id=source_project_id,
            target_project_id=target_project_id,
        )

        move_dataset_input.additional_properties = d
        return move_dataset_input

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
