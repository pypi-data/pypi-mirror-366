from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ValidateFileNamePatternsRequest")


@_attrs_define
class ValidateFileNamePatternsRequest:
    """
    Attributes:
        file_names (List[str]):
        file_name_patterns (List[str]):
    """

    file_names: List[str]
    file_name_patterns: List[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        file_names = self.file_names

        file_name_patterns = self.file_name_patterns

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fileNames": file_names,
                "fileNamePatterns": file_name_patterns,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        file_names = cast(List[str], d.pop("fileNames"))

        file_name_patterns = cast(List[str], d.pop("fileNamePatterns"))

        validate_file_name_patterns_request = cls(
            file_names=file_names,
            file_name_patterns=file_name_patterns,
        )

        validate_file_name_patterns_request.additional_properties = d
        return validate_file_name_patterns_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
