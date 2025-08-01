from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_settings import UserSettings


T = TypeVar("T", bound="UpdateUserRequest")


@_attrs_define
class UpdateUserRequest:
    """
    Attributes:
        name (str): Display name of the user
        email (str): Email address of the user
        phone (Union[Unset, str]): Phone number of the user
        department (Union[Unset, str]): Department or lab the user belongs to
        job_title (Union[Unset, str]): Job title or role of the user
        organization (Union[Unset, str]): The organization the user belongs to, only editable by administrators
        settings (Union['UserSettings', None, Unset]):
        groups (Union[Unset, List[str]]): Groups the user belongs to, only editable by administrators
    """

    name: str
    email: str
    phone: Union[Unset, str] = UNSET
    department: Union[Unset, str] = UNSET
    job_title: Union[Unset, str] = UNSET
    organization: Union[Unset, str] = UNSET
    settings: Union["UserSettings", None, Unset] = UNSET
    groups: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.user_settings import UserSettings

        name = self.name

        email = self.email

        phone = self.phone

        department = self.department

        job_title = self.job_title

        organization = self.organization

        settings: Union[Dict[str, Any], None, Unset]
        if isinstance(self.settings, Unset):
            settings = UNSET
        elif isinstance(self.settings, UserSettings):
            settings = self.settings.to_dict()
        else:
            settings = self.settings

        groups: Union[Unset, List[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "email": email,
            }
        )
        if phone is not UNSET:
            field_dict["phone"] = phone
        if department is not UNSET:
            field_dict["department"] = department
        if job_title is not UNSET:
            field_dict["jobTitle"] = job_title
        if organization is not UNSET:
            field_dict["organization"] = organization
        if settings is not UNSET:
            field_dict["settings"] = settings
        if groups is not UNSET:
            field_dict["groups"] = groups

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user_settings import UserSettings

        d = src_dict.copy()
        name = d.pop("name")

        email = d.pop("email")

        phone = d.pop("phone", UNSET)

        department = d.pop("department", UNSET)

        job_title = d.pop("jobTitle", UNSET)

        organization = d.pop("organization", UNSET)

        def _parse_settings(data: object) -> Union["UserSettings", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                settings_type_1 = UserSettings.from_dict(data)

                return settings_type_1
            except:  # noqa: E722
                pass
            return cast(Union["UserSettings", None, Unset], data)

        settings = _parse_settings(d.pop("settings", UNSET))

        groups = cast(List[str], d.pop("groups", UNSET))

        update_user_request = cls(
            name=name,
            email=email,
            phone=phone,
            department=department,
            job_title=job_title,
            organization=organization,
            settings=settings,
            groups=groups,
        )

        update_user_request.additional_properties = d
        return update_user_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
