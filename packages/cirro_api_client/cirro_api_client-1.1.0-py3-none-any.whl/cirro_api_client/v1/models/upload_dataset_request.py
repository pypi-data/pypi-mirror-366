from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tag import Tag


T = TypeVar("T", bound="UploadDatasetRequest")


@_attrs_define
class UploadDatasetRequest:
    """
    Attributes:
        name (str): Name of the dataset
        process_id (str): ID of the ingest process Example: paired_dnaseq.
        expected_files (List[str]):
        description (Union[Unset, str]): Description of the dataset
        tags (Union[List['Tag'], None, Unset]): List of tags to apply to the dataset
    """

    name: str
    process_id: str
    expected_files: List[str]
    description: Union[Unset, str] = UNSET
    tags: Union[List["Tag"], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        process_id = self.process_id

        expected_files = self.expected_files

        description = self.description

        tags: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = []
            for tags_type_0_item_data in self.tags:
                tags_type_0_item = tags_type_0_item_data.to_dict()
                tags.append(tags_type_0_item)

        else:
            tags = self.tags

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "processId": process_id,
                "expectedFiles": expected_files,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.tag import Tag

        d = src_dict.copy()
        name = d.pop("name")

        process_id = d.pop("processId")

        expected_files = cast(List[str], d.pop("expectedFiles"))

        description = d.pop("description", UNSET)

        def _parse_tags(data: object) -> Union[List["Tag"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = []
                _tags_type_0 = data
                for tags_type_0_item_data in _tags_type_0:
                    tags_type_0_item = Tag.from_dict(tags_type_0_item_data)

                    tags_type_0.append(tags_type_0_item)

                return tags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["Tag"], None, Unset], data)

        tags = _parse_tags(d.pop("tags", UNSET))

        upload_dataset_request = cls(
            name=name,
            process_id=process_id,
            expected_files=expected_files,
            description=description,
            tags=tags,
        )

        upload_dataset_request.additional_properties = d
        return upload_dataset_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
