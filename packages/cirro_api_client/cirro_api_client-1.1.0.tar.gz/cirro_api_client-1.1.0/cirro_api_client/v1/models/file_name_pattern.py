from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileNamePattern")


@_attrs_define
class FileNamePattern:
    """
    Attributes:
        example_name (str): User-readable name for the file type used for display.
        sample_matching_pattern (str): File name pattern, formatted as a valid regex, to extract sample name and other
            metadata.
        description (Union[None, Unset, str]): File description.
    """

    example_name: str
    sample_matching_pattern: str
    description: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        example_name = self.example_name

        sample_matching_pattern = self.sample_matching_pattern

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "exampleName": example_name,
                "sampleMatchingPattern": sample_matching_pattern,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        example_name = d.pop("exampleName")

        sample_matching_pattern = d.pop("sampleMatchingPattern")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        file_name_pattern = cls(
            example_name=example_name,
            sample_matching_pattern=sample_matching_pattern,
            description=description,
        )

        file_name_pattern.additional_properties = d
        return file_name_pattern

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
