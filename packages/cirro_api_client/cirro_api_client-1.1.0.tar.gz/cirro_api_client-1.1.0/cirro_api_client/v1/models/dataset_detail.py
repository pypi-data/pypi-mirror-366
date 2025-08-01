import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_detail_info import DatasetDetailInfo
    from ..models.dataset_detail_params import DatasetDetailParams
    from ..models.dataset_detail_source_sample_files_map import DatasetDetailSourceSampleFilesMap
    from ..models.named_item import NamedItem
    from ..models.tag import Tag


T = TypeVar("T", bound="DatasetDetail")


@_attrs_define
class DatasetDetail:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        s3 (str):
        process_id (str):
        project_id (str):
        source_dataset_ids (List[str]):
        source_datasets (List['NamedItem']):
        source_sample_ids (List[str]):
        source_sample_files_map (DatasetDetailSourceSampleFilesMap): Keys are sampleIds, and the lists are file paths to
            include.
        status (Status):
        status_message (str):
        tags (List['Tag']):
        params (DatasetDetailParams):
        info (DatasetDetailInfo):
        is_view_restricted (bool):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        originating_project_id (Union[Unset, str]): The originating project ID might be different if the dataset was
            shared from another project.
        share (Union['NamedItem', None, Unset]):
    """

    id: str
    name: str
    description: str
    s3: str
    process_id: str
    project_id: str
    source_dataset_ids: List[str]
    source_datasets: List["NamedItem"]
    source_sample_ids: List[str]
    source_sample_files_map: "DatasetDetailSourceSampleFilesMap"
    status: Status
    status_message: str
    tags: List["Tag"]
    params: "DatasetDetailParams"
    info: "DatasetDetailInfo"
    is_view_restricted: bool
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    originating_project_id: Union[Unset, str] = UNSET
    share: Union["NamedItem", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.named_item import NamedItem

        id = self.id

        name = self.name

        description = self.description

        s3 = self.s3

        process_id = self.process_id

        project_id = self.project_id

        source_dataset_ids = self.source_dataset_ids

        source_datasets = []
        for source_datasets_item_data in self.source_datasets:
            source_datasets_item = source_datasets_item_data.to_dict()
            source_datasets.append(source_datasets_item)

        source_sample_ids = self.source_sample_ids

        source_sample_files_map = self.source_sample_files_map.to_dict()

        status = self.status.value

        status_message = self.status_message

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        params = self.params.to_dict()

        info = self.info.to_dict()

        is_view_restricted = self.is_view_restricted

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        originating_project_id = self.originating_project_id

        share: Union[Dict[str, Any], None, Unset]
        if isinstance(self.share, Unset):
            share = UNSET
        elif isinstance(self.share, NamedItem):
            share = self.share.to_dict()
        else:
            share = self.share

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "s3": s3,
                "processId": process_id,
                "projectId": project_id,
                "sourceDatasetIds": source_dataset_ids,
                "sourceDatasets": source_datasets,
                "sourceSampleIds": source_sample_ids,
                "sourceSampleFilesMap": source_sample_files_map,
                "status": status,
                "statusMessage": status_message,
                "tags": tags,
                "params": params,
                "info": info,
                "isViewRestricted": is_view_restricted,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if originating_project_id is not UNSET:
            field_dict["originatingProjectId"] = originating_project_id
        if share is not UNSET:
            field_dict["share"] = share

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.dataset_detail_info import DatasetDetailInfo
        from ..models.dataset_detail_params import DatasetDetailParams
        from ..models.dataset_detail_source_sample_files_map import DatasetDetailSourceSampleFilesMap
        from ..models.named_item import NamedItem
        from ..models.tag import Tag

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        s3 = d.pop("s3")

        process_id = d.pop("processId")

        project_id = d.pop("projectId")

        source_dataset_ids = cast(List[str], d.pop("sourceDatasetIds"))

        source_datasets = []
        _source_datasets = d.pop("sourceDatasets")
        for source_datasets_item_data in _source_datasets:
            source_datasets_item = NamedItem.from_dict(source_datasets_item_data)

            source_datasets.append(source_datasets_item)

        source_sample_ids = cast(List[str], d.pop("sourceSampleIds"))

        source_sample_files_map = DatasetDetailSourceSampleFilesMap.from_dict(d.pop("sourceSampleFilesMap"))

        status = Status(d.pop("status"))

        status_message = d.pop("statusMessage")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        params = DatasetDetailParams.from_dict(d.pop("params"))

        info = DatasetDetailInfo.from_dict(d.pop("info"))

        is_view_restricted = d.pop("isViewRestricted")

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        originating_project_id = d.pop("originatingProjectId", UNSET)

        def _parse_share(data: object) -> Union["NamedItem", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                share_type_1 = NamedItem.from_dict(data)

                return share_type_1
            except:  # noqa: E722
                pass
            return cast(Union["NamedItem", None, Unset], data)

        share = _parse_share(d.pop("share", UNSET))

        dataset_detail = cls(
            id=id,
            name=name,
            description=description,
            s3=s3,
            process_id=process_id,
            project_id=project_id,
            source_dataset_ids=source_dataset_ids,
            source_datasets=source_datasets,
            source_sample_ids=source_sample_ids,
            source_sample_files_map=source_sample_files_map,
            status=status,
            status_message=status_message,
            tags=tags,
            params=params,
            info=info,
            is_view_restricted=is_view_restricted,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            originating_project_id=originating_project_id,
            share=share,
        )

        dataset_detail.additional_properties = d
        return dataset_detail

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
