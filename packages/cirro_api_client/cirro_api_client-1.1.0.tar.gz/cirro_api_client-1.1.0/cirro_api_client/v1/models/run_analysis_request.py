from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_analysis_request_params import RunAnalysisRequestParams
    from ..models.run_analysis_request_source_sample_files_map import RunAnalysisRequestSourceSampleFilesMap


T = TypeVar("T", bound="RunAnalysisRequest")


@_attrs_define
class RunAnalysisRequest:
    """
    Attributes:
        name (str): Name of the dataset
        process_id (str): Process ID of the workflow Example: process-nf-core-rnaseq-3_8.
        source_dataset_ids (List[str]): These datasets contain files that are inputs to this workflow.
        params (RunAnalysisRequestParams): Parameters used in workflow (can be empty)
        notification_emails (List[str]): Emails to notify upon workflow success or failure
        description (Union[None, Unset, str]): Description of the dataset (optional)
        source_sample_ids (Union[List[str], None, Unset]): Samples within the source datasets that will be used as
            inputs to this workflow. If not specified, all samples will be used.
        source_sample_files_map (Union['RunAnalysisRequestSourceSampleFilesMap', None, Unset]): Files containing samples
            used to define source data input to this workflow. If not specified, all files will be used. Keys are sampleIds,
            and the lists are file paths to include.
        resume_dataset_id (Union[None, Unset, str]): Used for caching task execution. If the parameters are the same as
            the dataset specified here, it will re-use the output to minimize duplicate work
        compute_environment_id (Union[None, Unset, str]): The compute environment where to run the workflow, if not
            specified, it will run in AWS
    """

    name: str
    process_id: str
    source_dataset_ids: List[str]
    params: "RunAnalysisRequestParams"
    notification_emails: List[str]
    description: Union[None, Unset, str] = UNSET
    source_sample_ids: Union[List[str], None, Unset] = UNSET
    source_sample_files_map: Union["RunAnalysisRequestSourceSampleFilesMap", None, Unset] = UNSET
    resume_dataset_id: Union[None, Unset, str] = UNSET
    compute_environment_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.run_analysis_request_source_sample_files_map import RunAnalysisRequestSourceSampleFilesMap

        name = self.name

        process_id = self.process_id

        source_dataset_ids = self.source_dataset_ids

        params = self.params.to_dict()

        notification_emails = self.notification_emails

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        source_sample_ids: Union[List[str], None, Unset]
        if isinstance(self.source_sample_ids, Unset):
            source_sample_ids = UNSET
        elif isinstance(self.source_sample_ids, list):
            source_sample_ids = self.source_sample_ids

        else:
            source_sample_ids = self.source_sample_ids

        source_sample_files_map: Union[Dict[str, Any], None, Unset]
        if isinstance(self.source_sample_files_map, Unset):
            source_sample_files_map = UNSET
        elif isinstance(self.source_sample_files_map, RunAnalysisRequestSourceSampleFilesMap):
            source_sample_files_map = self.source_sample_files_map.to_dict()
        else:
            source_sample_files_map = self.source_sample_files_map

        resume_dataset_id: Union[None, Unset, str]
        if isinstance(self.resume_dataset_id, Unset):
            resume_dataset_id = UNSET
        else:
            resume_dataset_id = self.resume_dataset_id

        compute_environment_id: Union[None, Unset, str]
        if isinstance(self.compute_environment_id, Unset):
            compute_environment_id = UNSET
        else:
            compute_environment_id = self.compute_environment_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "processId": process_id,
                "sourceDatasetIds": source_dataset_ids,
                "params": params,
                "notificationEmails": notification_emails,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if source_sample_ids is not UNSET:
            field_dict["sourceSampleIds"] = source_sample_ids
        if source_sample_files_map is not UNSET:
            field_dict["sourceSampleFilesMap"] = source_sample_files_map
        if resume_dataset_id is not UNSET:
            field_dict["resumeDatasetId"] = resume_dataset_id
        if compute_environment_id is not UNSET:
            field_dict["computeEnvironmentId"] = compute_environment_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.run_analysis_request_params import RunAnalysisRequestParams
        from ..models.run_analysis_request_source_sample_files_map import RunAnalysisRequestSourceSampleFilesMap

        d = src_dict.copy()
        name = d.pop("name")

        process_id = d.pop("processId")

        source_dataset_ids = cast(List[str], d.pop("sourceDatasetIds"))

        params = RunAnalysisRequestParams.from_dict(d.pop("params"))

        notification_emails = cast(List[str], d.pop("notificationEmails"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_source_sample_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                source_sample_ids_type_0 = cast(List[str], data)

                return source_sample_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        source_sample_ids = _parse_source_sample_ids(d.pop("sourceSampleIds", UNSET))

        def _parse_source_sample_files_map(
            data: object,
        ) -> Union["RunAnalysisRequestSourceSampleFilesMap", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_sample_files_map_type_0 = RunAnalysisRequestSourceSampleFilesMap.from_dict(data)

                return source_sample_files_map_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunAnalysisRequestSourceSampleFilesMap", None, Unset], data)

        source_sample_files_map = _parse_source_sample_files_map(d.pop("sourceSampleFilesMap", UNSET))

        def _parse_resume_dataset_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        resume_dataset_id = _parse_resume_dataset_id(d.pop("resumeDatasetId", UNSET))

        def _parse_compute_environment_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        compute_environment_id = _parse_compute_environment_id(d.pop("computeEnvironmentId", UNSET))

        run_analysis_request = cls(
            name=name,
            process_id=process_id,
            source_dataset_ids=source_dataset_ids,
            params=params,
            notification_emails=notification_emails,
            description=description,
            source_sample_ids=source_sample_ids,
            source_sample_files_map=source_sample_files_map,
            resume_dataset_id=resume_dataset_id,
            compute_environment_id=compute_environment_id,
        )

        run_analysis_request.additional_properties = d
        return run_analysis_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
