from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02"


@dataclass
class ReportParameter1:
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "required": True,
            "min_length": 1,
            "max_length": 70,
        },
    )
    val: Optional[str] = field(
        default=None,
        metadata={
            "name": "Val",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "required": True,
            "min_length": 1,
            "max_length": 350,
        },
    )


@dataclass
class SupplementaryDataEnvelope1:
    any_element: Optional[object] = field(
        default=None,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
        },
    )


@dataclass
class RequestDetails4:
    key: Optional[str] = field(
        default=None,
        metadata={
            "name": "Key",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    rpt_data: list[ReportParameter1] = field(
        default_factory=list,
        metadata={
            "name": "RptData",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
        },
    )


@dataclass
class SupplementaryData1:
    plc_and_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "PlcAndNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "min_length": 1,
            "max_length": 350,
        },
    )
    envlp: Optional[SupplementaryDataEnvelope1] = field(
        default=None,
        metadata={
            "name": "Envlp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "required": True,
        },
    )


@dataclass
class RequestDetails5:
    tp: Optional[str] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    req_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "ReqRef",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    rpt_key: list[RequestDetails4] = field(
        default_factory=list,
        metadata={
            "name": "RptKey",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "min_occurs": 1,
        },
    )


@dataclass
class StaticDataReportV02:
    msg_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MsgId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    sttlm_ssn_idr: Optional[str] = field(
        default=None,
        metadata={
            "name": "SttlmSsnIdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "pattern": r"[a-zA-Z0-9]{4}",
        },
    )
    rpt_dtls: Optional[RequestDetails5] = field(
        default=None,
        metadata={
            "name": "RptDtls",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
            "required": True,
        },
    )
    splmtry_data: list[SupplementaryData1] = field(
        default_factory=list,
        metadata={
            "name": "SplmtryData",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02",
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:iso:std:iso:20022:tech:xsd:admi.010.001.02"

    statc_data_rpt: Optional[StaticDataReportV02] = field(
        default=None,
        metadata={
            "name": "StatcDataRpt",
            "type": "Element",
            "required": True,
        },
    )
