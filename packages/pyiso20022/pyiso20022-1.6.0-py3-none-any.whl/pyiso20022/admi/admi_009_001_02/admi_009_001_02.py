from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02"


@dataclass
class RequestDetails3:
    tp: Optional[str] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    key: Optional[str] = field(
        default=None,
        metadata={
            "name": "Key",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02",
            "min_length": 1,
            "max_length": 35,
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
class SupplementaryData1:
    plc_and_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "PlcAndNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02",
            "min_length": 1,
            "max_length": 350,
        },
    )
    envlp: Optional[SupplementaryDataEnvelope1] = field(
        default=None,
        metadata={
            "name": "Envlp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02",
            "required": True,
        },
    )


@dataclass
class StaticDataRequestV02:
    msg_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MsgId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02",
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
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02",
            "pattern": r"[a-zA-Z0-9]{4}",
        },
    )
    data_req_dtls: Optional[RequestDetails3] = field(
        default=None,
        metadata={
            "name": "DataReqDtls",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02",
            "required": True,
        },
    )
    splmtry_data: list[SupplementaryData1] = field(
        default_factory=list,
        metadata={
            "name": "SplmtryData",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02",
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:iso:std:iso:20022:tech:xsd:admi.009.001.02"

    statc_data_req: Optional[StaticDataRequestV02] = field(
        default=None,
        metadata={
            "name": "StatcDataReq",
            "type": "Element",
            "required": True,
        },
    )
