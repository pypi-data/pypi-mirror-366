from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="StatusGetDeploymentResponse200EnginesItemPipelineStatusesType0")


@_attrs_define
class StatusGetDeploymentResponse200EnginesItemPipelineStatusesType0:
    """Statuses of pipelines serviced by the engine."""

    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status_get_deployment_response_200_engines_item_pipeline_statuses_type_0 = cls()

        status_get_deployment_response_200_engines_item_pipeline_statuses_type_0.additional_properties = d
        return status_get_deployment_response_200_engines_item_pipeline_statuses_type_0

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
