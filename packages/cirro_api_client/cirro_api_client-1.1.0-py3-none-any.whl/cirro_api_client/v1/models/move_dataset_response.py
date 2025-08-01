from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MoveDatasetResponse")


@_attrs_define
class MoveDatasetResponse:
    """
    Attributes:
        s_3_copy_command (str):
        s_3_delete_command (str):
        samples_not_moved (List[str]):
    """

    s_3_copy_command: str
    s_3_delete_command: str
    samples_not_moved: List[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        s_3_copy_command = self.s_3_copy_command

        s_3_delete_command = self.s_3_delete_command

        samples_not_moved = self.samples_not_moved

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "s3CopyCommand": s_3_copy_command,
                "s3DeleteCommand": s_3_delete_command,
                "samplesNotMoved": samples_not_moved,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        s_3_copy_command = d.pop("s3CopyCommand")

        s_3_delete_command = d.pop("s3DeleteCommand")

        samples_not_moved = cast(List[str], d.pop("samplesNotMoved"))

        move_dataset_response = cls(
            s_3_copy_command=s_3_copy_command,
            s_3_delete_command=s_3_delete_command,
            samples_not_moved=samples_not_moved,
        )

        move_dataset_response.additional_properties = d
        return move_dataset_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
