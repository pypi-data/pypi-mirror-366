from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="ConnectionsAddToWorkspaceResponse401")


@_attrs_define
class ConnectionsAddToWorkspaceResponse401:
    """Error response.

    Attributes:
        msg (str):  Error message.
        code (int):  Status code for the error.
    """

    msg: str
    code: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        msg = self.msg

        code = self.code

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "msg": msg,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        msg = d.pop("msg")

        code = d.pop("code")

        connections_add_to_workspace_response_401 = cls(
            msg=msg,
            code=code,
        )

        connections_add_to_workspace_response_401.additional_properties = d
        return connections_add_to_workspace_response_401

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
