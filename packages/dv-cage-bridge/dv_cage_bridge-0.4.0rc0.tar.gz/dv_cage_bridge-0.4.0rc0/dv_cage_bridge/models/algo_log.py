import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.algo_log_log import AlgoLogLog


T = TypeVar("T", bound="AlgoLog")


@_attrs_define
class AlgoLog:
    """
    Attributes:
        time (datetime.datetime):
        log (AlgoLogLog):
    """

    time: datetime.datetime
    log: "AlgoLogLog"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        time = self.time.isoformat()

        log = self.log.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time": time,
                "log": log,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.algo_log_log import AlgoLogLog

        d = dict(src_dict)
        time = isoparse(d.pop("time"))

        log = AlgoLogLog.from_dict(d.pop("log"))

        algo_log = cls(
            time=time,
            log=log,
        )

        algo_log.additional_properties = d
        return algo_log

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
