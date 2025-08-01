from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.message import Message


T = TypeVar("T", bound="PaginatedResponseMessage")


@_attrs_define
class PaginatedResponseMessage:
    """
    Attributes:
        data (List['Message']):
        next_token (str):
    """

    data: List["Message"]
    next_token: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        next_token = self.next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.message import Message

        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = Message.from_dict(data_item_data)

            data.append(data_item)

        next_token = d.pop("nextToken")

        paginated_response_message = cls(
            data=data,
            next_token=next_token,
        )

        paginated_response_message.additional_properties = d
        return paginated_response_message

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
