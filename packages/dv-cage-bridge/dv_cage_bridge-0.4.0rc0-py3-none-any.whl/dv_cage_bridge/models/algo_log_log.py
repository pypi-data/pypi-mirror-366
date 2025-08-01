from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AlgoLogLog")


@_attrs_define
class AlgoLogLog:
    """
    Attributes:
        msg (str):
        library_version (str):
        event (Union[Unset, str]):
        event_stream (Union[Unset, str]):
    """

    msg: str
    library_version: str
    event: Union[Unset, str] = UNSET
    event_stream: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        msg = self.msg

        library_version = self.library_version

        event = self.event

        event_stream = self.event_stream

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "msg": msg,
                "libraryVersion": library_version,
            }
        )
        if event is not UNSET:
            field_dict["event"] = event
        if event_stream is not UNSET:
            field_dict["eventStream"] = event_stream

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        msg = d.pop("msg")

        library_version = d.pop("libraryVersion")

        event = d.pop("event", UNSET)

        event_stream = d.pop("eventStream", UNSET)

        algo_log_log = cls(
            msg=msg,
            library_version=library_version,
            event=event,
            event_stream=event_stream,
        )

        algo_log_log.additional_properties = d
        return algo_log_log

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
