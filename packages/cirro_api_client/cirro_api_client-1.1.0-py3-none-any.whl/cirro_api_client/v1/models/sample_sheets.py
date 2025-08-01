from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SampleSheets")


@_attrs_define
class SampleSheets:
    """
    Attributes:
        samples (Union[Unset, str]): Written to samplesheet.csv, available as ds.samplesheet in preprocess
        files (Union[Unset, str]): Written to files.csv, available as ds.files in preprocess
    """

    samples: Union[Unset, str] = UNSET
    files: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        samples = self.samples

        files = self.files

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if samples is not UNSET:
            field_dict["samples"] = samples
        if files is not UNSET:
            field_dict["files"] = files

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        samples = d.pop("samples", UNSET)

        files = d.pop("files", UNSET)

        sample_sheets = cls(
            samples=samples,
            files=files,
        )

        sample_sheets.additional_properties = d
        return sample_sheets

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
