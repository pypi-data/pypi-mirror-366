from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageInput")


@_attrs_define
class MessageInput:
    """
    Attributes:
        message (str):
        parent_message_id (Union[None, Unset, str]):
    """

    message: str
    parent_message_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        message = self.message

        parent_message_id: Union[None, Unset, str]
        if isinstance(self.parent_message_id, Unset):
            parent_message_id = UNSET
        else:
            parent_message_id = self.parent_message_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
            }
        )
        if parent_message_id is not UNSET:
            field_dict["parentMessageId"] = parent_message_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        message = d.pop("message")

        def _parse_parent_message_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_message_id = _parse_parent_message_id(d.pop("parentMessageId", UNSET))

        message_input = cls(
            message=message,
            parent_message_id=parent_message_id,
        )

        message_input.additional_properties = d
        return message_input

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
