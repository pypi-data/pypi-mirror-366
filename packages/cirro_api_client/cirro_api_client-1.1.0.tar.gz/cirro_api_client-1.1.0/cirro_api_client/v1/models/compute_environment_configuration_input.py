from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.compute_environment_configuration_input_properties import (
        ComputeEnvironmentConfigurationInputProperties,
    )


T = TypeVar("T", bound="ComputeEnvironmentConfigurationInput")


@_attrs_define
class ComputeEnvironmentConfigurationInput:
    """
    Attributes:
        name (str):
        agent_id (Union[None, Unset, str]):
        properties (Union['ComputeEnvironmentConfigurationInputProperties', None, Unset]):
    """

    name: str
    agent_id: Union[None, Unset, str] = UNSET
    properties: Union["ComputeEnvironmentConfigurationInputProperties", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.compute_environment_configuration_input_properties import (
            ComputeEnvironmentConfigurationInputProperties,
        )

        name = self.name

        agent_id: Union[None, Unset, str]
        if isinstance(self.agent_id, Unset):
            agent_id = UNSET
        else:
            agent_id = self.agent_id

        properties: Union[Dict[str, Any], None, Unset]
        if isinstance(self.properties, Unset):
            properties = UNSET
        elif isinstance(self.properties, ComputeEnvironmentConfigurationInputProperties):
            properties = self.properties.to_dict()
        else:
            properties = self.properties

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if agent_id is not UNSET:
            field_dict["agentId"] = agent_id
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.compute_environment_configuration_input_properties import (
            ComputeEnvironmentConfigurationInputProperties,
        )

        d = src_dict.copy()
        name = d.pop("name")

        def _parse_agent_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        agent_id = _parse_agent_id(d.pop("agentId", UNSET))

        def _parse_properties(data: object) -> Union["ComputeEnvironmentConfigurationInputProperties", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                properties_type_0 = ComputeEnvironmentConfigurationInputProperties.from_dict(data)

                return properties_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ComputeEnvironmentConfigurationInputProperties", None, Unset], data)

        properties = _parse_properties(d.pop("properties", UNSET))

        compute_environment_configuration_input = cls(
            name=name,
            agent_id=agent_id,
            properties=properties,
        )

        compute_environment_configuration_input.additional_properties = d
        return compute_environment_configuration_input

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
