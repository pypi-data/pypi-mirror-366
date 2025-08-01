from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.finished_summary import FinishedSummary
    from ..models.pending_report import PendingReport
    from ..models.status_error import StatusError
    from ..models.status_exported import StatusExported
    from ..models.status_exporting import StatusExporting
    from ..models.status_initialized import StatusInitialized
    from ..models.status_mounted import StatusMounted
    from ..models.status_unmounted import StatusUnmounted
    from ..models.status_writing import StatusWriting


T = TypeVar("T", bound="CollaboratorStatus")


@_attrs_define
class CollaboratorStatus:
    """
    Attributes:
        status (Union['StatusError', 'StatusExported', 'StatusExporting', 'StatusInitialized', 'StatusMounted',
            'StatusUnmounted', 'StatusWriting']):
        reports (list[Union['FinishedSummary', 'PendingReport']]): The summarized quality reports of the collaborator.
        has_server_secret (bool): Indicates if a secret has been loaded to push/pull the data.
    """

    status: Union[
        "StatusError",
        "StatusExported",
        "StatusExporting",
        "StatusInitialized",
        "StatusMounted",
        "StatusUnmounted",
        "StatusWriting",
    ]
    reports: list[Union["FinishedSummary", "PendingReport"]]
    has_server_secret: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.pending_report import PendingReport
        from ..models.status_exported import StatusExported
        from ..models.status_exporting import StatusExporting
        from ..models.status_initialized import StatusInitialized
        from ..models.status_mounted import StatusMounted
        from ..models.status_unmounted import StatusUnmounted
        from ..models.status_writing import StatusWriting

        status: dict[str, Any]
        if isinstance(self.status, StatusUnmounted):
            status = self.status.to_dict()
        elif isinstance(self.status, StatusInitialized):
            status = self.status.to_dict()
        elif isinstance(self.status, StatusWriting):
            status = self.status.to_dict()
        elif isinstance(self.status, StatusMounted):
            status = self.status.to_dict()
        elif isinstance(self.status, StatusExporting):
            status = self.status.to_dict()
        elif isinstance(self.status, StatusExported):
            status = self.status.to_dict()
        else:
            status = self.status.to_dict()

        reports = []
        for reports_item_data in self.reports:
            reports_item: dict[str, Any]
            if isinstance(reports_item_data, PendingReport):
                reports_item = reports_item_data.to_dict()
            else:
                reports_item = reports_item_data.to_dict()

            reports.append(reports_item)

        has_server_secret = self.has_server_secret

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "reports": reports,
                "hasServerSecret": has_server_secret,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finished_summary import FinishedSummary
        from ..models.pending_report import PendingReport
        from ..models.status_error import StatusError
        from ..models.status_exported import StatusExported
        from ..models.status_exporting import StatusExporting
        from ..models.status_initialized import StatusInitialized
        from ..models.status_mounted import StatusMounted
        from ..models.status_unmounted import StatusUnmounted
        from ..models.status_writing import StatusWriting

        d = dict(src_dict)

        def _parse_status(
            data: object,
        ) -> Union[
            "StatusError",
            "StatusExported",
            "StatusExporting",
            "StatusInitialized",
            "StatusMounted",
            "StatusUnmounted",
            "StatusWriting",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_0 = StatusUnmounted.from_dict(data)

                return componentsschemas_status_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_1 = StatusInitialized.from_dict(data)

                return componentsschemas_status_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_2 = StatusWriting.from_dict(data)

                return componentsschemas_status_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_3 = StatusMounted.from_dict(data)

                return componentsschemas_status_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_4 = StatusExporting.from_dict(data)

                return componentsschemas_status_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_5 = StatusExported.from_dict(data)

                return componentsschemas_status_type_5
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_status_type_6 = StatusError.from_dict(data)

            return componentsschemas_status_type_6

        status = _parse_status(d.pop("status"))

        reports = []
        _reports = d.pop("reports")
        for reports_item_data in _reports:

            def _parse_reports_item(data: object) -> Union["FinishedSummary", "PendingReport"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_quality_report_summary_type_0 = PendingReport.from_dict(data)

                    return componentsschemas_quality_report_summary_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_quality_report_summary_type_1 = FinishedSummary.from_dict(data)

                return componentsschemas_quality_report_summary_type_1

            reports_item = _parse_reports_item(reports_item_data)

            reports.append(reports_item)

        has_server_secret = d.pop("hasServerSecret")

        collaborator_status = cls(
            status=status,
            reports=reports,
            has_server_secret=has_server_secret,
        )

        collaborator_status.additional_properties = d
        return collaborator_status

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
