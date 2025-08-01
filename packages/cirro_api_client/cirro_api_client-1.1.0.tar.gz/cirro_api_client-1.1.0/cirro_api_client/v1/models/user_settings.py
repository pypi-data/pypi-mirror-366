from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserSettings")


@_attrs_define
class UserSettings:
    """Additional settings for the user

    Attributes:
        analysis_update_notifications_enabled (bool):
    """

    analysis_update_notifications_enabled: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        analysis_update_notifications_enabled = self.analysis_update_notifications_enabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "analysisUpdateNotificationsEnabled": analysis_update_notifications_enabled,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        analysis_update_notifications_enabled = d.pop("analysisUpdateNotificationsEnabled")

        user_settings = cls(
            analysis_update_notifications_enabled=analysis_update_notifications_enabled,
        )

        user_settings.additional_properties = d
        return user_settings

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
