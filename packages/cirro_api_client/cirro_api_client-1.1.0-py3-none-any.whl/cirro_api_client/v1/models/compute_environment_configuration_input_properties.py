from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ComputeEnvironmentConfigurationInputProperties")


@_attrs_define
class ComputeEnvironmentConfigurationInputProperties:
    """ """

    additional_properties: Dict[str, str] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        compute_environment_configuration_input_properties = cls()

        compute_environment_configuration_input_properties.additional_properties = d
        return compute_environment_configuration_input_properties

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
