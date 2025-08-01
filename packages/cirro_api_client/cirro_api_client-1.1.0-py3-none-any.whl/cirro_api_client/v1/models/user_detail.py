import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_project_assignment import UserProjectAssignment
    from ..models.user_settings import UserSettings


T = TypeVar("T", bound="UserDetail")


@_attrs_define
class UserDetail:
    """
    Attributes:
        username (str):
        name (str):
        phone (str):
        email (str):
        organization (str):
        job_title (str):
        department (str):
        invited_by (str):
        project_assignments (List['UserProjectAssignment']):
        groups (List[str]):
        settings (UserSettings): Additional settings for the user
        sign_up_time (Union[None, Unset, datetime.datetime]):
        last_signed_in (Union[None, Unset, datetime.datetime]):
    """

    username: str
    name: str
    phone: str
    email: str
    organization: str
    job_title: str
    department: str
    invited_by: str
    project_assignments: List["UserProjectAssignment"]
    groups: List[str]
    settings: "UserSettings"
    sign_up_time: Union[None, Unset, datetime.datetime] = UNSET
    last_signed_in: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        name = self.name

        phone = self.phone

        email = self.email

        organization = self.organization

        job_title = self.job_title

        department = self.department

        invited_by = self.invited_by

        project_assignments = []
        for project_assignments_item_data in self.project_assignments:
            project_assignments_item = project_assignments_item_data.to_dict()
            project_assignments.append(project_assignments_item)

        groups = self.groups

        settings = self.settings.to_dict()

        sign_up_time: Union[None, Unset, str]
        if isinstance(self.sign_up_time, Unset):
            sign_up_time = UNSET
        elif isinstance(self.sign_up_time, datetime.datetime):
            sign_up_time = self.sign_up_time.isoformat()
        else:
            sign_up_time = self.sign_up_time

        last_signed_in: Union[None, Unset, str]
        if isinstance(self.last_signed_in, Unset):
            last_signed_in = UNSET
        elif isinstance(self.last_signed_in, datetime.datetime):
            last_signed_in = self.last_signed_in.isoformat()
        else:
            last_signed_in = self.last_signed_in

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "name": name,
                "phone": phone,
                "email": email,
                "organization": organization,
                "jobTitle": job_title,
                "department": department,
                "invitedBy": invited_by,
                "projectAssignments": project_assignments,
                "groups": groups,
                "settings": settings,
            }
        )
        if sign_up_time is not UNSET:
            field_dict["signUpTime"] = sign_up_time
        if last_signed_in is not UNSET:
            field_dict["lastSignedIn"] = last_signed_in

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user_project_assignment import UserProjectAssignment
        from ..models.user_settings import UserSettings

        d = src_dict.copy()
        username = d.pop("username")

        name = d.pop("name")

        phone = d.pop("phone")

        email = d.pop("email")

        organization = d.pop("organization")

        job_title = d.pop("jobTitle")

        department = d.pop("department")

        invited_by = d.pop("invitedBy")

        project_assignments = []
        _project_assignments = d.pop("projectAssignments")
        for project_assignments_item_data in _project_assignments:
            project_assignments_item = UserProjectAssignment.from_dict(project_assignments_item_data)

            project_assignments.append(project_assignments_item)

        groups = cast(List[str], d.pop("groups"))

        settings = UserSettings.from_dict(d.pop("settings"))

        def _parse_sign_up_time(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                sign_up_time_type_0 = isoparse(data)

                return sign_up_time_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        sign_up_time = _parse_sign_up_time(d.pop("signUpTime", UNSET))

        def _parse_last_signed_in(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_signed_in_type_0 = isoparse(data)

                return last_signed_in_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_signed_in = _parse_last_signed_in(d.pop("lastSignedIn", UNSET))

        user_detail = cls(
            username=username,
            name=name,
            phone=phone,
            email=email,
            organization=organization,
            job_title=job_title,
            department=department,
            invited_by=invited_by,
            project_assignments=project_assignments,
            groups=groups,
            settings=settings,
            sign_up_time=sign_up_time,
            last_signed_in=last_signed_in,
        )

        user_detail.additional_properties = d
        return user_detail

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
