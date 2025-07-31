from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional

from xsdata.models.datatype import XmlDate, XmlDateTime, XmlTime

__NAMESPACE__ = "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03"


@dataclass
class AccountSchemeName1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class ActiveCurrencyAndAmount:
    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
            "total_digits": 18,
            "fraction_digits": 5,
        },
    )
    ccy: Optional[str] = field(
        default=None,
        metadata={
            "name": "Ccy",
            "type": "Attribute",
            "required": True,
            "pattern": r"[A-Z]{3,3}",
        },
    )


class AddressType2Code(Enum):
    ADDR = "ADDR"
    PBOX = "PBOX"
    HOME = "HOME"
    BIZZ = "BIZZ"
    MLTO = "MLTO"
    DLVY = "DLVY"


@dataclass
class CashAccountType2Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class CategoryPurpose1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


class ClearingChannel2Code(Enum):
    RTGS = "RTGS"
    RTNS = "RTNS"
    MPNS = "MPNS"
    BOOK = "BOOK"


@dataclass
class ClearingSystemIdentification2Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 5,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class FinancialIdentificationSchemeName1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class GenericIdentification30:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "pattern": r"[a-zA-Z0-9]{4}",
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    schme_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "SchmeNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


class Instruction5Code(Enum):
    PHOB = "PHOB"
    TELB = "TELB"


@dataclass
class LocalInstrument2Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class PaymentIdentification7:
    instr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "InstrId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    end_to_end_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "EndToEndId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    tx_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TxId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    uetr: Optional[str] = field(
        default=None,
        metadata={
            "name": "UETR",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "pattern": r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}",
        },
    )
    clr_sys_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "ClrSysRef",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


class Priority2Code(Enum):
    HIGH = "HIGH"
    NORM = "NORM"


class Priority3Code(Enum):
    URGT = "URGT"
    HIGH = "HIGH"
    NORM = "NORM"


@dataclass
class ProxyAccountType1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class Purpose2Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class RemittanceInformation2:
    ustrd: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Ustrd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 140,
        },
    )


@dataclass
class ServiceLevel8Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class SettlementDateTimeIndication1:
    dbt_dt_tm: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "DbtDtTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    cdt_dt_tm: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "CdtDtTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class SettlementTimeRequest2:
    clstm: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "CLSTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    till_tm: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "TillTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    fr_tm: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "FrTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    rjct_tm: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "RjctTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
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
class AddressType3Choice:
    cd: Optional[AddressType2Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    prtry: Optional[GenericIdentification30] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class ClearingSystemMemberIdentification2:
    clr_sys_id: Optional[ClearingSystemIdentification2Choice] = field(
        default=None,
        metadata={
            "name": "ClrSysId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    mmb_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MmbId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class GenericAccountIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "min_length": 1,
            "max_length": 34,
        },
    )
    schme_nm: Optional[AccountSchemeName1Choice] = field(
        default=None,
        metadata={
            "name": "SchmeNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class GenericFinancialIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    schme_nm: Optional[FinancialIdentificationSchemeName1Choice] = field(
        default=None,
        metadata={
            "name": "SchmeNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class InstructionForCreditorAgent2:
    cd: Optional[Instruction5Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    instr_inf: Optional[str] = field(
        default=None,
        metadata={
            "name": "InstrInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 140,
        },
    )


@dataclass
class PaymentTypeInformation28:
    instr_prty: Optional[Priority2Code] = field(
        default=None,
        metadata={
            "name": "InstrPrty",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    clr_chanl: Optional[ClearingChannel2Code] = field(
        default=None,
        metadata={
            "name": "ClrChanl",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    svc_lvl: list[ServiceLevel8Choice] = field(
        default_factory=list,
        metadata={
            "name": "SvcLvl",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    lcl_instrm: Optional[LocalInstrument2Choice] = field(
        default=None,
        metadata={
            "name": "LclInstrm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    ctgy_purp: Optional[CategoryPurpose1Choice] = field(
        default=None,
        metadata={
            "name": "CtgyPurp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class ProxyAccountIdentification1:
    tp: Optional[ProxyAccountType1Choice] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "min_length": 1,
            "max_length": 2048,
        },
    )


@dataclass
class SupplementaryData1:
    plc_and_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "PlcAndNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 350,
        },
    )
    envlp: Optional[SupplementaryDataEnvelope1] = field(
        default=None,
        metadata={
            "name": "Envlp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )


@dataclass
class AccountIdentification4Choice:
    iban: Optional[str] = field(
        default=None,
        metadata={
            "name": "IBAN",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "pattern": r"[A-Z]{2,2}[0-9]{2,2}[a-zA-Z0-9]{1,30}",
        },
    )
    othr: Optional[GenericAccountIdentification1] = field(
        default=None,
        metadata={
            "name": "Othr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class PostalAddress24:
    adr_tp: Optional[AddressType3Choice] = field(
        default=None,
        metadata={
            "name": "AdrTp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    dept: Optional[str] = field(
        default=None,
        metadata={
            "name": "Dept",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 70,
        },
    )
    sub_dept: Optional[str] = field(
        default=None,
        metadata={
            "name": "SubDept",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 70,
        },
    )
    strt_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "StrtNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 70,
        },
    )
    bldg_nb: Optional[str] = field(
        default=None,
        metadata={
            "name": "BldgNb",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 16,
        },
    )
    bldg_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "BldgNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    flr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Flr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 70,
        },
    )
    pst_bx: Optional[str] = field(
        default=None,
        metadata={
            "name": "PstBx",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 16,
        },
    )
    room: Optional[str] = field(
        default=None,
        metadata={
            "name": "Room",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 70,
        },
    )
    pst_cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "PstCd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 16,
        },
    )
    twn_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "TwnNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    twn_lctn_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "TwnLctnNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    dstrct_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "DstrctNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    ctry_sub_dvsn: Optional[str] = field(
        default=None,
        metadata={
            "name": "CtrySubDvsn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    ctry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Ctry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "pattern": r"[A-Z]{2,2}",
        },
    )
    adr_line: list[str] = field(
        default_factory=list,
        metadata={
            "name": "AdrLine",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "max_occurs": 7,
            "min_length": 1,
            "max_length": 70,
        },
    )


@dataclass
class BranchData3:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 35,
        },
    )
    lei: Optional[str] = field(
        default=None,
        metadata={
            "name": "LEI",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "pattern": r"[A-Z0-9]{18,18}[0-9]{2,2}",
        },
    )
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 140,
        },
    )
    pstl_adr: Optional[PostalAddress24] = field(
        default=None,
        metadata={
            "name": "PstlAdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class CashAccount38:
    id: Optional[AccountIdentification4Choice] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )
    tp: Optional[CashAccountType2Choice] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    ccy: Optional[str] = field(
        default=None,
        metadata={
            "name": "Ccy",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "pattern": r"[A-Z]{3,3}",
        },
    )
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 70,
        },
    )
    prxy: Optional[ProxyAccountIdentification1] = field(
        default=None,
        metadata={
            "name": "Prxy",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class FinancialInstitutionIdentification18:
    bicfi: Optional[str] = field(
        default=None,
        metadata={
            "name": "BICFI",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "pattern": r"[A-Z0-9]{4,4}[A-Z]{2,2}[A-Z0-9]{2,2}([A-Z0-9]{3,3}){0,1}",
        },
    )
    clr_sys_mmb_id: Optional[ClearingSystemMemberIdentification2] = field(
        default=None,
        metadata={
            "name": "ClrSysMmbId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    lei: Optional[str] = field(
        default=None,
        metadata={
            "name": "LEI",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "pattern": r"[A-Z0-9]{18,18}[0-9]{2,2}",
        },
    )
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 140,
        },
    )
    pstl_adr: Optional[PostalAddress24] = field(
        default=None,
        metadata={
            "name": "PstlAdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    othr: Optional[GenericFinancialIdentification1] = field(
        default=None,
        metadata={
            "name": "Othr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class BranchAndFinancialInstitutionIdentification6:
    fin_instn_id: Optional[FinancialInstitutionIdentification18] = field(
        default=None,
        metadata={
            "name": "FinInstnId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )
    brnch_id: Optional[BranchData3] = field(
        default=None,
        metadata={
            "name": "BrnchId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class DirectDebitTransactionInformation25:
    pmt_id: Optional[PaymentIdentification7] = field(
        default=None,
        metadata={
            "name": "PmtId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )
    pmt_tp_inf: Optional[PaymentTypeInformation28] = field(
        default=None,
        metadata={
            "name": "PmtTpInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    intr_bk_sttlm_amt: Optional[ActiveCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )
    intr_bk_sttlm_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    sttlm_prty: Optional[Priority3Code] = field(
        default=None,
        metadata={
            "name": "SttlmPrty",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    sttlm_tm_indctn: Optional[SettlementDateTimeIndication1] = field(
        default=None,
        metadata={
            "name": "SttlmTmIndctn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    sttlm_tm_req: Optional[SettlementTimeRequest2] = field(
        default=None,
        metadata={
            "name": "SttlmTmReq",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    ultmt_dbtr: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "UltmtDbtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    dbtr: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "Dbtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )
    dbtr_acct: Optional[CashAccount38] = field(
        default=None,
        metadata={
            "name": "DbtrAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    dbtr_agt: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "DbtrAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    dbtr_agt_acct: Optional[CashAccount38] = field(
        default=None,
        metadata={
            "name": "DbtrAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    instr_for_dbtr_agt: Optional[str] = field(
        default=None,
        metadata={
            "name": "InstrForDbtrAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_length": 1,
            "max_length": 210,
        },
    )
    purp: Optional[Purpose2Choice] = field(
        default=None,
        metadata={
            "name": "Purp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    rmt_inf: Optional[RemittanceInformation2] = field(
        default=None,
        metadata={
            "name": "RmtInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class GroupHeader92:
    msg_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MsgId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    cre_dt_tm: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "CreDtTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )
    nb_of_txs: Optional[str] = field(
        default=None,
        metadata={
            "name": "NbOfTxs",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "pattern": r"[0-9]{1,15}",
        },
    )
    ctrl_sum: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "CtrlSum",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "total_digits": 18,
            "fraction_digits": 17,
        },
    )
    instg_agt: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "InstgAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    instd_agt: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "InstdAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class CreditTransferTransaction38:
    cdt_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CdtId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    btch_bookg: Optional[bool] = field(
        default=None,
        metadata={
            "name": "BtchBookg",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    pmt_tp_inf: Optional[PaymentTypeInformation28] = field(
        default=None,
        metadata={
            "name": "PmtTpInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    ttl_intr_bk_sttlm_amt: Optional[ActiveCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "TtlIntrBkSttlmAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    intr_bk_sttlm_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    sttlm_tm_indctn: Optional[SettlementDateTimeIndication1] = field(
        default=None,
        metadata={
            "name": "SttlmTmIndctn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    instg_agt: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "InstgAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    instd_agt: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "InstdAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    intrmy_agt1: Optional[BranchAndFinancialInstitutionIdentification6] = (
        field(
            default=None,
            metadata={
                "name": "IntrmyAgt1",
                "type": "Element",
                "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            },
        )
    )
    intrmy_agt1_acct: Optional[CashAccount38] = field(
        default=None,
        metadata={
            "name": "IntrmyAgt1Acct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    intrmy_agt2: Optional[BranchAndFinancialInstitutionIdentification6] = (
        field(
            default=None,
            metadata={
                "name": "IntrmyAgt2",
                "type": "Element",
                "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            },
        )
    )
    intrmy_agt2_acct: Optional[CashAccount38] = field(
        default=None,
        metadata={
            "name": "IntrmyAgt2Acct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    intrmy_agt3: Optional[BranchAndFinancialInstitutionIdentification6] = (
        field(
            default=None,
            metadata={
                "name": "IntrmyAgt3",
                "type": "Element",
                "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            },
        )
    )
    intrmy_agt3_acct: Optional[CashAccount38] = field(
        default=None,
        metadata={
            "name": "IntrmyAgt3Acct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    cdtr_agt: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "CdtrAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    cdtr_agt_acct: Optional[CashAccount38] = field(
        default=None,
        metadata={
            "name": "CdtrAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    cdtr: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "Cdtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )
    cdtr_acct: Optional[CashAccount38] = field(
        default=None,
        metadata={
            "name": "CdtrAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    ultmt_cdtr: Optional[BranchAndFinancialInstitutionIdentification6] = field(
        default=None,
        metadata={
            "name": "UltmtCdtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    instr_for_cdtr_agt: list[InstructionForCreditorAgent2] = field(
        default_factory=list,
        metadata={
            "name": "InstrForCdtrAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )
    drct_dbt_tx_inf: list[DirectDebitTransactionInformation25] = field(
        default_factory=list,
        metadata={
            "name": "DrctDbtTxInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_occurs": 1,
        },
    )
    splmtry_data: list[SupplementaryData1] = field(
        default_factory=list,
        metadata={
            "name": "SplmtryData",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class FinancialInstitutionDirectDebitV03:
    grp_hdr: Optional[GroupHeader92] = field(
        default=None,
        metadata={
            "name": "GrpHdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "required": True,
        },
    )
    cdt_instr: list[CreditTransferTransaction38] = field(
        default_factory=list,
        metadata={
            "name": "CdtInstr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
            "min_occurs": 1,
        },
    )
    splmtry_data: list[SupplementaryData1] = field(
        default_factory=list,
        metadata={
            "name": "SplmtryData",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03",
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:iso:std:iso:20022:tech:xsd:pacs.010.001.03"

    fidrct_dbt: Optional[FinancialInstitutionDirectDebitV03] = field(
        default=None,
        metadata={
            "name": "FIDrctDbt",
            "type": "Element",
            "required": True,
        },
    )
