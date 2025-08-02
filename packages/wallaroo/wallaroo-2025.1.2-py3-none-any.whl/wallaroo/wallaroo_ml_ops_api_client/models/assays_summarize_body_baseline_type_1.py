from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.assays_summarize_body_baseline_type_1_fixed_window import (
        AssaysSummarizeBodyBaselineType1FixedWindow,
    )


T = TypeVar("T", bound="AssaysSummarizeBodyBaselineType1")


@_attrs_define
class AssaysSummarizeBodyBaselineType1:
    """
    Attributes:
        fixed_window (AssaysSummarizeBodyBaselineType1FixedWindow):  Assay window.
    """

    fixed_window: "AssaysSummarizeBodyBaselineType1FixedWindow"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        fixed_window = self.fixed_window.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fixed_window": fixed_window,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_summarize_body_baseline_type_1_fixed_window import (
            AssaysSummarizeBodyBaselineType1FixedWindow,
        )

        d = src_dict.copy()
        fixed_window = AssaysSummarizeBodyBaselineType1FixedWindow.from_dict(
            d.pop("fixed_window")
        )

        assays_summarize_body_baseline_type_1 = cls(
            fixed_window=fixed_window,
        )

        assays_summarize_body_baseline_type_1.additional_properties = d
        return assays_summarize_body_baseline_type_1

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
