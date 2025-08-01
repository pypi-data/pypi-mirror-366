from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RunAnalysisRequestSourceSampleFilesMap")


@_attrs_define
class RunAnalysisRequestSourceSampleFilesMap:
    """Files containing samples used to define source data input to this workflow. If not specified, all files will be
    used. Keys are sampleIds, and the lists are file paths to include.

    """

    additional_properties: Dict[str, List[str]] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        run_analysis_request_source_sample_files_map = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = cast(List[str], prop_dict)

            additional_properties[prop_name] = additional_property

        run_analysis_request_source_sample_files_map.additional_properties = additional_properties
        return run_analysis_request_source_sample_files_map

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
