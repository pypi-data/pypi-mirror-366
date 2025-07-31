from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional

from xsdata.models.datatype import XmlDate, XmlDateTime

__NAMESPACE__ = "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04"


@dataclass
class AccountSchemeName1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class ActiveOrHistoricCurrencyAndAmount:
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


class CancellationIndividualStatus1Code(Enum):
    RJCR = "RJCR"
    ACCR = "ACCR"
    PDCR = "PDCR"


@dataclass
class CashAccountType2Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
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
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class ChargeBearerType1Code(Enum):
    DEBT = "DEBT"
    CRED = "CRED"
    SHAR = "SHAR"
    SLEV = "SLEV"


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
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 5,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class ClearingSystemIdentification3Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 3,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class CorrectiveGroupInformation1:
    msg_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MsgId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    msg_nm_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MsgNmId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
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
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


class CreditDebitCode(Enum):
    CRDT = "CRDT"
    DBIT = "DBIT"


@dataclass
class DateAndPlaceOfBirth:
    birth_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "BirthDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    prvc_of_birth: Optional[str] = field(
        default=None,
        metadata={
            "name": "PrvcOfBirth",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    city_of_birth: Optional[str] = field(
        default=None,
        metadata={
            "name": "CityOfBirth",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    ctry_of_birth: Optional[str] = field(
        default=None,
        metadata={
            "name": "CtryOfBirth",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "pattern": r"[A-Z]{2,2}",
        },
    )


@dataclass
class DiscountAmountType1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class DocumentType3Code(Enum):
    RADM = "RADM"
    RPIN = "RPIN"
    FXDR = "FXDR"
    DISP = "DISP"
    PUOR = "PUOR"
    SCOR = "SCOR"


class DocumentType5Code(Enum):
    MSIN = "MSIN"
    CNFA = "CNFA"
    DNFA = "DNFA"
    CINV = "CINV"
    CREN = "CREN"
    DEBN = "DEBN"
    HIRI = "HIRI"
    SBIN = "SBIN"
    CMCN = "CMCN"
    SOAC = "SOAC"
    DISP = "DISP"
    BOLD = "BOLD"
    VCHR = "VCHR"
    AROI = "AROI"
    TSUT = "TSUT"


@dataclass
class FinancialIdentificationSchemeName1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class Frequency6Code(Enum):
    YEAR = "YEAR"
    MNTH = "MNTH"
    QURT = "QURT"
    MIAN = "MIAN"
    WEEK = "WEEK"
    DAIL = "DAIL"
    ADHO = "ADHO"
    INDA = "INDA"
    FRTN = "FRTN"


@dataclass
class GenericIdentification3:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class GroupCancellationStatus1Code(Enum):
    PACR = "PACR"
    RJCR = "RJCR"
    ACCR = "ACCR"
    PDCR = "PDCR"


class InvestigationExecutionConfirmation3Code(Enum):
    CNCL = "CNCL"
    MODI = "MODI"
    IPAY = "IPAY"
    ICOV = "ICOV"
    MCOV = "MCOV"
    INFO = "INFO"
    CONF = "CONF"
    CWFW = "CWFW"
    MWFW = "MWFW"
    UWFW = "UWFW"
    PECR = "PECR"
    PDCR = "PDCR"
    RJCR = "RJCR"
    SMTC = "SMTC"
    SMTI = "SMTI"
    CHRG = "CHRG"
    PURP = "PURP"
    IDUP = "IDUP"


@dataclass
class LocalInstrument2Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class ModificationRejection2Code(Enum):
    UM01 = "UM01"
    UM02 = "UM02"
    UM03 = "UM03"
    UM04 = "UM04"
    UM05 = "UM05"
    UM06 = "UM06"
    UM07 = "UM07"
    UM08 = "UM08"
    UM09 = "UM09"
    UM10 = "UM10"
    UM11 = "UM11"
    UM12 = "UM12"
    UM13 = "UM13"
    UM14 = "UM14"
    UM15 = "UM15"
    UM16 = "UM16"
    UM17 = "UM17"
    UM18 = "UM18"
    UM19 = "UM19"
    UM20 = "UM20"
    UM21 = "UM21"
    UM22 = "UM22"
    UM23 = "UM23"
    UM24 = "UM24"
    UM25 = "UM25"
    UM26 = "UM26"
    UM27 = "UM27"


class NamePrefix1Code(Enum):
    DOCT = "DOCT"
    MIST = "MIST"
    MISS = "MISS"
    MADM = "MADM"


@dataclass
class OrganisationIdentificationSchemeName1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class OriginalGroupInformation3:
    orgnl_msg_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlMsgId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_msg_nm_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlMsgNmId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_cre_dt_tm: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "OrgnlCreDtTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


class PaymentCancellationRejection2Code(Enum):
    LEGL = "LEGL"
    AGNT = "AGNT"
    CUST = "CUST"
    ARDT = "ARDT"
    NOAS = "NOAS"
    NOOR = "NOOR"
    AC04 = "AC04"
    AM04 = "AM04"


class PaymentMethod4Code(Enum):
    CHK = "CHK"
    TRF = "TRF"
    DD = "DD"
    TRA = "TRA"


@dataclass
class PersonIdentificationSchemeName1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class Priority2Code(Enum):
    HIGH = "HIGH"
    NORM = "NORM"


@dataclass
class Purpose2Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class SequenceType3Code(Enum):
    FRST = "FRST"
    RCUR = "RCUR"
    FNAL = "FNAL"
    OOFF = "OOFF"
    RPRE = "RPRE"


@dataclass
class ServiceLevel8Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class SettlementMethod1Code(Enum):
    INDA = "INDA"
    INGA = "INGA"
    COVE = "COVE"
    CLRG = "CLRG"


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
class TaxAmountType1Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


class TransactionIndividualStatus1Code(Enum):
    ACTC = "ACTC"
    RJCT = "RJCT"
    PDNG = "PDNG"
    ACCP = "ACCP"
    ACSP = "ACSP"
    ACSC = "ACSC"
    ACCR = "ACCR"
    ACWC = "ACWC"


@dataclass
class CancellationStatusReason2Choice:
    cd: Optional[PaymentCancellationRejection2Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class ChargeType3Choice:
    cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    prtry: Optional[GenericIdentification3] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class ClearingSystemMemberIdentification2:
    clr_sys_id: Optional[ClearingSystemIdentification2Choice] = field(
        default=None,
        metadata={
            "name": "ClrSysId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    mmb_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MmbId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class ContactDetails2:
    nm_prfx: Optional[NamePrefix1Code] = field(
        default=None,
        metadata={
            "name": "NmPrfx",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 140,
        },
    )
    phne_nb: Optional[str] = field(
        default=None,
        metadata={
            "name": "PhneNb",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"\+[0-9]{1,3}-[0-9()+\-]{1,30}",
        },
    )
    mob_nb: Optional[str] = field(
        default=None,
        metadata={
            "name": "MobNb",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"\+[0-9]{1,3}-[0-9()+\-]{1,30}",
        },
    )
    fax_nb: Optional[str] = field(
        default=None,
        metadata={
            "name": "FaxNb",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"\+[0-9]{1,3}-[0-9()+\-]{1,30}",
        },
    )
    email_adr: Optional[str] = field(
        default=None,
        metadata={
            "name": "EmailAdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 2048,
        },
    )
    othr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Othr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class CorrectiveInterbankTransaction1:
    grp_hdr: Optional[CorrectiveGroupInformation1] = field(
        default=None,
        metadata={
            "name": "GrpHdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    instr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "InstrId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    end_to_end_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "EndToEndId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    tx_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "TxId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    intr_bk_sttlm_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    intr_bk_sttlm_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )


@dataclass
class CorrectivePaymentInitiation1:
    grp_hdr: Optional[CorrectiveGroupInformation1] = field(
        default=None,
        metadata={
            "name": "GrpHdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    pmt_inf_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "PmtInfId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    instr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "InstrId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    end_to_end_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "EndToEndId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    instd_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "InstdAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    reqd_exctn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "ReqdExctnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    reqd_colltn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "ReqdColltnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class CreditorReferenceType1Choice:
    cd: Optional[DocumentType3Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class DiscountAmountAndType1:
    tp: Optional[DiscountAmountType1Choice] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )


@dataclass
class DocumentAdjustment1:
    amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    cdt_dbt_ind: Optional[CreditDebitCode] = field(
        default=None,
        metadata={
            "name": "CdtDbtInd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rsn: Optional[str] = field(
        default=None,
        metadata={
            "name": "Rsn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 4,
        },
    )
    addtl_inf: Optional[str] = field(
        default=None,
        metadata={
            "name": "AddtlInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 140,
        },
    )


@dataclass
class EquivalentAmount2:
    amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    ccy_of_trf: Optional[str] = field(
        default=None,
        metadata={
            "name": "CcyOfTrf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "pattern": r"[A-Z]{3,3}",
        },
    )


@dataclass
class GenericAccountIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
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
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
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
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
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
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class GenericOrganisationIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    schme_nm: Optional[OrganisationIdentificationSchemeName1Choice] = field(
        default=None,
        metadata={
            "name": "SchmeNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class GenericPersonIdentification1:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    schme_nm: Optional[PersonIdentificationSchemeName1Choice] = field(
        default=None,
        metadata={
            "name": "SchmeNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class NumberOfCancellationsPerStatus1:
    dtld_nb_of_txs: Optional[str] = field(
        default=None,
        metadata={
            "name": "DtldNbOfTxs",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "pattern": r"[0-9]{1,15}",
        },
    )
    dtld_sts: Optional[CancellationIndividualStatus1Code] = field(
        default=None,
        metadata={
            "name": "DtldSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    dtld_ctrl_sum: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "DtldCtrlSum",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "total_digits": 18,
            "fraction_digits": 17,
        },
    )


@dataclass
class NumberOfTransactionsPerStatus1:
    dtld_nb_of_txs: Optional[str] = field(
        default=None,
        metadata={
            "name": "DtldNbOfTxs",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "pattern": r"[0-9]{1,15}",
        },
    )
    dtld_sts: Optional[TransactionIndividualStatus1Code] = field(
        default=None,
        metadata={
            "name": "DtldSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    dtld_ctrl_sum: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "DtldCtrlSum",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "total_digits": 18,
            "fraction_digits": 17,
        },
    )


@dataclass
class PaymentTypeInformation25:
    instr_prty: Optional[Priority2Code] = field(
        default=None,
        metadata={
            "name": "InstrPrty",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    clr_chanl: Optional[ClearingChannel2Code] = field(
        default=None,
        metadata={
            "name": "ClrChanl",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    svc_lvl: Optional[ServiceLevel8Choice] = field(
        default=None,
        metadata={
            "name": "SvcLvl",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    lcl_instrm: Optional[LocalInstrument2Choice] = field(
        default=None,
        metadata={
            "name": "LclInstrm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    seq_tp: Optional[SequenceType3Code] = field(
        default=None,
        metadata={
            "name": "SeqTp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    ctgy_purp: Optional[CategoryPurpose1Choice] = field(
        default=None,
        metadata={
            "name": "CtgyPurp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class PostalAddress6:
    adr_tp: Optional[AddressType2Code] = field(
        default=None,
        metadata={
            "name": "AdrTp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    dept: Optional[str] = field(
        default=None,
        metadata={
            "name": "Dept",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 70,
        },
    )
    sub_dept: Optional[str] = field(
        default=None,
        metadata={
            "name": "SubDept",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 70,
        },
    )
    strt_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "StrtNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 70,
        },
    )
    bldg_nb: Optional[str] = field(
        default=None,
        metadata={
            "name": "BldgNb",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 16,
        },
    )
    pst_cd: Optional[str] = field(
        default=None,
        metadata={
            "name": "PstCd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 16,
        },
    )
    twn_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "TwnNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    ctry_sub_dvsn: Optional[str] = field(
        default=None,
        metadata={
            "name": "CtrySubDvsn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    ctry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Ctry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"[A-Z]{2,2}",
        },
    )
    adr_line: list[str] = field(
        default_factory=list,
        metadata={
            "name": "AdrLine",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "max_occurs": 7,
            "min_length": 1,
            "max_length": 70,
        },
    )


@dataclass
class ReferredDocumentType1Choice:
    cd: Optional[DocumentType5Code] = field(
        default=None,
        metadata={
            "name": "Cd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    prtry: Optional[str] = field(
        default=None,
        metadata={
            "name": "Prtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class ResolutionInformation1:
    intr_bk_sttlm_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    intr_bk_sttlm_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    clr_chanl: Optional[ClearingChannel2Code] = field(
        default=None,
        metadata={
            "name": "ClrChanl",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class SupplementaryData1:
    plc_and_nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "PlcAndNm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 350,
        },
    )
    envlp: Optional[SupplementaryDataEnvelope1] = field(
        default=None,
        metadata={
            "name": "Envlp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )


@dataclass
class TaxAmountAndType1:
    tp: Optional[TaxAmountType1Choice] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )


@dataclass
class TaxCharges2:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    rate: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Rate",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "total_digits": 11,
            "fraction_digits": 10,
        },
    )
    amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class AccountIdentification4Choice:
    iban: Optional[str] = field(
        default=None,
        metadata={
            "name": "IBAN",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"[A-Z]{2,2}[0-9]{2,2}[a-zA-Z0-9]{1,30}",
        },
    )
    othr: Optional[GenericAccountIdentification1] = field(
        default=None,
        metadata={
            "name": "Othr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class AmountType3Choice:
    instd_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "InstdAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    eqvt_amt: Optional[EquivalentAmount2] = field(
        default=None,
        metadata={
            "name": "EqvtAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class BranchData2:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 140,
        },
    )
    pstl_adr: Optional[PostalAddress6] = field(
        default=None,
        metadata={
            "name": "PstlAdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class CorrectiveTransaction1Choice:
    initn: Optional[CorrectivePaymentInitiation1] = field(
        default=None,
        metadata={
            "name": "Initn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    intr_bk: Optional[CorrectiveInterbankTransaction1] = field(
        default=None,
        metadata={
            "name": "IntrBk",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class CreditorReferenceType2:
    cd_or_prtry: Optional[CreditorReferenceType1Choice] = field(
        default=None,
        metadata={
            "name": "CdOrPrtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class FinancialInstitutionIdentification8:
    bicfi: Optional[str] = field(
        default=None,
        metadata={
            "name": "BICFI",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"[A-Z]{6,6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3,3}){0,1}",
        },
    )
    clr_sys_mmb_id: Optional[ClearingSystemMemberIdentification2] = field(
        default=None,
        metadata={
            "name": "ClrSysMmbId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 140,
        },
    )
    pstl_adr: Optional[PostalAddress6] = field(
        default=None,
        metadata={
            "name": "PstlAdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    othr: Optional[GenericFinancialIdentification1] = field(
        default=None,
        metadata={
            "name": "Othr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class OrganisationIdentification8:
    any_bic: Optional[str] = field(
        default=None,
        metadata={
            "name": "AnyBIC",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"[A-Z]{6,6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3,3}){0,1}",
        },
    )
    othr: list[GenericOrganisationIdentification1] = field(
        default_factory=list,
        metadata={
            "name": "Othr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class PersonIdentification5:
    dt_and_plc_of_birth: Optional[DateAndPlaceOfBirth] = field(
        default=None,
        metadata={
            "name": "DtAndPlcOfBirth",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    othr: list[GenericPersonIdentification1] = field(
        default_factory=list,
        metadata={
            "name": "Othr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class ReferredDocumentType2:
    cd_or_prtry: Optional[ReferredDocumentType1Choice] = field(
        default=None,
        metadata={
            "name": "CdOrPrtry",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    issr: Optional[str] = field(
        default=None,
        metadata={
            "name": "Issr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class RemittanceAmount2:
    due_pybl_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "DuePyblAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    dscnt_apld_amt: list[DiscountAmountAndType1] = field(
        default_factory=list,
        metadata={
            "name": "DscntApldAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cdt_note_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "CdtNoteAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    tax_amt: list[TaxAmountAndType1] = field(
        default_factory=list,
        metadata={
            "name": "TaxAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    adjstmnt_amt_and_rsn: list[DocumentAdjustment1] = field(
        default_factory=list,
        metadata={
            "name": "AdjstmntAmtAndRsn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rmtd_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "RmtdAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class BranchAndFinancialInstitutionIdentification5:
    fin_instn_id: Optional[FinancialInstitutionIdentification8] = field(
        default=None,
        metadata={
            "name": "FinInstnId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    brnch_id: Optional[BranchData2] = field(
        default=None,
        metadata={
            "name": "BrnchId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class CashAccount24:
    id: Optional[AccountIdentification4Choice] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    tp: Optional[CashAccountType2Choice] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    ccy: Optional[str] = field(
        default=None,
        metadata={
            "name": "Ccy",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"[A-Z]{3,3}",
        },
    )
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 70,
        },
    )


@dataclass
class CreditorReferenceInformation2:
    tp: Optional[CreditorReferenceType2] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "Ref",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )


@dataclass
class Party11Choice:
    org_id: Optional[OrganisationIdentification8] = field(
        default=None,
        metadata={
            "name": "OrgId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    prvt_id: Optional[PersonIdentification5] = field(
        default=None,
        metadata={
            "name": "PrvtId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class ReferredDocumentInformation3:
    tp: Optional[ReferredDocumentType2] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    nb: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nb",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    rltd_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "RltdDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class ChargesRecord1:
    amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    cdt_dbt_ind: Optional[CreditDebitCode] = field(
        default=None,
        metadata={
            "name": "CdtDbtInd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    tp: Optional[ChargeType3Choice] = field(
        default=None,
        metadata={
            "name": "Tp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rate: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Rate",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "total_digits": 11,
            "fraction_digits": 10,
        },
    )
    br: Optional[ChargeBearerType1Code] = field(
        default=None,
        metadata={
            "name": "Br",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    agt: Optional[BranchAndFinancialInstitutionIdentification5] = field(
        default=None,
        metadata={
            "name": "Agt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    tax: Optional[TaxCharges2] = field(
        default=None,
        metadata={
            "name": "Tax",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class PartyIdentification43:
    nm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Nm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 140,
        },
    )
    pstl_adr: Optional[PostalAddress6] = field(
        default=None,
        metadata={
            "name": "PstlAdr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    id: Optional[Party11Choice] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    ctry_of_res: Optional[str] = field(
        default=None,
        metadata={
            "name": "CtryOfRes",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"[A-Z]{2,2}",
        },
    )
    ctct_dtls: Optional[ContactDetails2] = field(
        default=None,
        metadata={
            "name": "CtctDtls",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class SettlementInstruction4:
    sttlm_mtd: Optional[SettlementMethod1Code] = field(
        default=None,
        metadata={
            "name": "SttlmMtd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    sttlm_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "SttlmAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    clr_sys: Optional[ClearingSystemIdentification3Choice] = field(
        default=None,
        metadata={
            "name": "ClrSys",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    instg_rmbrsmnt_agt: Optional[
        BranchAndFinancialInstitutionIdentification5
    ] = field(
        default=None,
        metadata={
            "name": "InstgRmbrsmntAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    instg_rmbrsmnt_agt_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "InstgRmbrsmntAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    instd_rmbrsmnt_agt: Optional[
        BranchAndFinancialInstitutionIdentification5
    ] = field(
        default=None,
        metadata={
            "name": "InstdRmbrsmntAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    instd_rmbrsmnt_agt_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "InstdRmbrsmntAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    thrd_rmbrsmnt_agt: Optional[
        BranchAndFinancialInstitutionIdentification5
    ] = field(
        default=None,
        metadata={
            "name": "ThrdRmbrsmntAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    thrd_rmbrsmnt_agt_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "ThrdRmbrsmntAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class AmendmentInformationDetails8:
    orgnl_mndt_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlMndtId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_cdtr_schme_id: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "OrgnlCdtrSchmeId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_cdtr_agt: Optional[BranchAndFinancialInstitutionIdentification5] = (
        field(
            default=None,
            metadata={
                "name": "OrgnlCdtrAgt",
                "type": "Element",
                "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            },
        )
    )
    orgnl_cdtr_agt_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "OrgnlCdtrAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_dbtr: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "OrgnlDbtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_dbtr_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "OrgnlDbtrAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_dbtr_agt: Optional[BranchAndFinancialInstitutionIdentification5] = (
        field(
            default=None,
            metadata={
                "name": "OrgnlDbtrAgt",
                "type": "Element",
                "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            },
        )
    )
    orgnl_dbtr_agt_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "OrgnlDbtrAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_fnl_colltn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "OrgnlFnlColltnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_frqcy: Optional[Frequency6Code] = field(
        default=None,
        metadata={
            "name": "OrgnlFrqcy",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class CancellationStatusReason2:
    orgtr: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "Orgtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rsn: Optional[CancellationStatusReason2Choice] = field(
        default=None,
        metadata={
            "name": "Rsn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    addtl_inf: list[str] = field(
        default_factory=list,
        metadata={
            "name": "AddtlInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 105,
        },
    )


@dataclass
class Charges3:
    ttl_chrgs_and_tax_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "TtlChrgsAndTaxAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rcrd: list[ChargesRecord1] = field(
        default_factory=list,
        metadata={
            "name": "Rcrd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class Party12Choice:
    pty: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "Pty",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    agt: Optional[BranchAndFinancialInstitutionIdentification5] = field(
        default=None,
        metadata={
            "name": "Agt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class StructuredRemittanceInformation9:
    rfrd_doc_inf: list[ReferredDocumentInformation3] = field(
        default_factory=list,
        metadata={
            "name": "RfrdDocInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rfrd_doc_amt: Optional[RemittanceAmount2] = field(
        default=None,
        metadata={
            "name": "RfrdDocAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cdtr_ref_inf: Optional[CreditorReferenceInformation2] = field(
        default=None,
        metadata={
            "name": "CdtrRefInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    invcr: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "Invcr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    invcee: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "Invcee",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    addtl_rmt_inf: list[str] = field(
        default_factory=list,
        metadata={
            "name": "AddtlRmtInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "max_occurs": 3,
            "min_length": 1,
            "max_length": 140,
        },
    )


@dataclass
class Case3:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    cretr: Optional[Party12Choice] = field(
        default=None,
        metadata={
            "name": "Cretr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    reop_case_indctn: Optional[bool] = field(
        default=None,
        metadata={
            "name": "ReopCaseIndctn",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class CaseAssignment3:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    assgnr: Optional[Party12Choice] = field(
        default=None,
        metadata={
            "name": "Assgnr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    assgne: Optional[Party12Choice] = field(
        default=None,
        metadata={
            "name": "Assgne",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    cre_dt_tm: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "CreDtTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )


@dataclass
class MandateRelatedInformation8:
    mndt_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "MndtId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    dt_of_sgntr: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "DtOfSgntr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    amdmnt_ind: Optional[bool] = field(
        default=None,
        metadata={
            "name": "AmdmntInd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    amdmnt_inf_dtls: Optional[AmendmentInformationDetails8] = field(
        default=None,
        metadata={
            "name": "AmdmntInfDtls",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    elctrnc_sgntr: Optional[str] = field(
        default=None,
        metadata={
            "name": "ElctrncSgntr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 1025,
        },
    )
    frst_colltn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "FrstColltnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    fnl_colltn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "FnlColltnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    frqcy: Optional[Frequency6Code] = field(
        default=None,
        metadata={
            "name": "Frqcy",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class RemittanceInformation7:
    ustrd: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Ustrd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 140,
        },
    )
    strd: list[StructuredRemittanceInformation9] = field(
        default_factory=list,
        metadata={
            "name": "Strd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class StatementResolutionEntry2:
    orgnl_grp_inf: Optional[OriginalGroupInformation3] = field(
        default=None,
        metadata={
            "name": "OrgnlGrpInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_stmt_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlStmtId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    acct_svcr_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "AcctSvcrRef",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    crrctd_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "CrrctdAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    chrgs: list[Charges3] = field(
        default_factory=list,
        metadata={
            "name": "Chrgs",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    purp: Optional[Purpose2Choice] = field(
        default=None,
        metadata={
            "name": "Purp",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class InvestigationStatus3Choice:
    conf: Optional[InvestigationExecutionConfirmation3Code] = field(
        default=None,
        metadata={
            "name": "Conf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rjctd_mod: list[ModificationRejection2Code] = field(
        default_factory=list,
        metadata={
            "name": "RjctdMod",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    dplct_of: Optional[Case3] = field(
        default=None,
        metadata={
            "name": "DplctOf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    assgnmt_cxl_conf: Optional[bool] = field(
        default=None,
        metadata={
            "name": "AssgnmtCxlConf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class OriginalGroupHeader5:
    orgnl_grp_cxl_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlGrpCxlId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    rslvd_case: Optional[Case3] = field(
        default=None,
        metadata={
            "name": "RslvdCase",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_msg_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlMsgId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_msg_nm_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlMsgNmId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_cre_dt_tm: Optional[XmlDateTime] = field(
        default=None,
        metadata={
            "name": "OrgnlCreDtTm",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_nb_of_txs: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlNbOfTxs",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"[0-9]{1,15}",
        },
    )
    orgnl_ctrl_sum: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "OrgnlCtrlSum",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "total_digits": 18,
            "fraction_digits": 17,
        },
    )
    grp_cxl_sts: Optional[GroupCancellationStatus1Code] = field(
        default=None,
        metadata={
            "name": "GrpCxlSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cxl_sts_rsn_inf: list[CancellationStatusReason2] = field(
        default_factory=list,
        metadata={
            "name": "CxlStsRsnInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    nb_of_txs_per_cxl_sts: list[NumberOfTransactionsPerStatus1] = field(
        default_factory=list,
        metadata={
            "name": "NbOfTxsPerCxlSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class OriginalTransactionReference16:
    intr_bk_sttlm_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    amt: Optional[AmountType3Choice] = field(
        default=None,
        metadata={
            "name": "Amt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    intr_bk_sttlm_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "IntrBkSttlmDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    reqd_colltn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "ReqdColltnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    reqd_exctn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "ReqdExctnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cdtr_schme_id: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "CdtrSchmeId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    sttlm_inf: Optional[SettlementInstruction4] = field(
        default=None,
        metadata={
            "name": "SttlmInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    pmt_tp_inf: Optional[PaymentTypeInformation25] = field(
        default=None,
        metadata={
            "name": "PmtTpInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    pmt_mtd: Optional[PaymentMethod4Code] = field(
        default=None,
        metadata={
            "name": "PmtMtd",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    mndt_rltd_inf: Optional[MandateRelatedInformation8] = field(
        default=None,
        metadata={
            "name": "MndtRltdInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rmt_inf: Optional[RemittanceInformation7] = field(
        default=None,
        metadata={
            "name": "RmtInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    ultmt_dbtr: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "UltmtDbtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    dbtr: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "Dbtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    dbtr_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "DbtrAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    dbtr_agt: Optional[BranchAndFinancialInstitutionIdentification5] = field(
        default=None,
        metadata={
            "name": "DbtrAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    dbtr_agt_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "DbtrAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cdtr_agt: Optional[BranchAndFinancialInstitutionIdentification5] = field(
        default=None,
        metadata={
            "name": "CdtrAgt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cdtr_agt_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "CdtrAgtAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cdtr: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "Cdtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cdtr_acct: Optional[CashAccount24] = field(
        default=None,
        metadata={
            "name": "CdtrAcct",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    ultmt_cdtr: Optional[PartyIdentification43] = field(
        default=None,
        metadata={
            "name": "UltmtCdtr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class PaymentTransaction39:
    cxl_sts_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CxlStsId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    rslvd_case: Optional[Case3] = field(
        default=None,
        metadata={
            "name": "RslvdCase",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_instr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlInstrId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_end_to_end_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlEndToEndId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    tx_cxl_sts: Optional[CancellationIndividualStatus1Code] = field(
        default=None,
        metadata={
            "name": "TxCxlSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cxl_sts_rsn_inf: list[CancellationStatusReason2] = field(
        default_factory=list,
        metadata={
            "name": "CxlStsRsnInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_instd_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = field(
        default=None,
        metadata={
            "name": "OrgnlInstdAmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_reqd_exctn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "OrgnlReqdExctnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_reqd_colltn_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "OrgnlReqdColltnDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_tx_ref: Optional[OriginalTransactionReference16] = field(
        default=None,
        metadata={
            "name": "OrgnlTxRef",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class PaymentTransaction40:
    cxl_sts_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CxlStsId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    rslvd_case: Optional[Case3] = field(
        default=None,
        metadata={
            "name": "RslvdCase",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_grp_inf: Optional[OriginalGroupInformation3] = field(
        default=None,
        metadata={
            "name": "OrgnlGrpInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_instr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlInstrId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_end_to_end_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlEndToEndId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_tx_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlTxId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_clr_sys_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlClrSysRef",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    tx_cxl_sts: Optional[CancellationIndividualStatus1Code] = field(
        default=None,
        metadata={
            "name": "TxCxlSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cxl_sts_rsn_inf: list[CancellationStatusReason2] = field(
        default_factory=list,
        metadata={
            "name": "CxlStsRsnInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rsltn_rltd_inf: Optional[ResolutionInformation1] = field(
        default=None,
        metadata={
            "name": "RsltnRltdInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_intr_bk_sttlm_amt: Optional[ActiveOrHistoricCurrencyAndAmount] = (
        field(
            default=None,
            metadata={
                "name": "OrgnlIntrBkSttlmAmt",
                "type": "Element",
                "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            },
        )
    )
    orgnl_intr_bk_sttlm_dt: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "OrgnlIntrBkSttlmDt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    assgnr: Optional[Party12Choice] = field(
        default=None,
        metadata={
            "name": "Assgnr",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    assgne: Optional[Party12Choice] = field(
        default=None,
        metadata={
            "name": "Assgne",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_tx_ref: Optional[OriginalTransactionReference16] = field(
        default=None,
        metadata={
            "name": "OrgnlTxRef",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class OriginalPaymentInstruction3:
    orgnl_pmt_inf_cxl_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlPmtInfCxlId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "min_length": 1,
            "max_length": 35,
        },
    )
    rslvd_case: Optional[Case3] = field(
        default=None,
        metadata={
            "name": "RslvdCase",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_pmt_inf_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlPmtInfId",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
            "min_length": 1,
            "max_length": 35,
        },
    )
    orgnl_grp_inf: Optional[OriginalGroupInformation3] = field(
        default=None,
        metadata={
            "name": "OrgnlGrpInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_nb_of_txs: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrgnlNbOfTxs",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "pattern": r"[0-9]{1,15}",
        },
    )
    orgnl_ctrl_sum: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "OrgnlCtrlSum",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "total_digits": 18,
            "fraction_digits": 17,
        },
    )
    pmt_inf_cxl_sts: Optional[GroupCancellationStatus1Code] = field(
        default=None,
        metadata={
            "name": "PmtInfCxlSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    cxl_sts_rsn_inf: list[CancellationStatusReason2] = field(
        default_factory=list,
        metadata={
            "name": "CxlStsRsnInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    nb_of_txs_per_cxl_sts: list[NumberOfCancellationsPerStatus1] = field(
        default_factory=list,
        metadata={
            "name": "NbOfTxsPerCxlSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    tx_inf_and_sts: list[PaymentTransaction39] = field(
        default_factory=list,
        metadata={
            "name": "TxInfAndSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class UnderlyingTransaction4:
    orgnl_grp_inf_and_sts: Optional[OriginalGroupHeader5] = field(
        default=None,
        metadata={
            "name": "OrgnlGrpInfAndSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    orgnl_pmt_inf_and_sts: list[OriginalPaymentInstruction3] = field(
        default_factory=list,
        metadata={
            "name": "OrgnlPmtInfAndSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    tx_inf_and_sts: list[PaymentTransaction40] = field(
        default_factory=list,
        metadata={
            "name": "TxInfAndSts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class ResolutionOfInvestigationV04:
    assgnmt: Optional[CaseAssignment3] = field(
        default=None,
        metadata={
            "name": "Assgnmt",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    rslvd_case: Optional[Case3] = field(
        default=None,
        metadata={
            "name": "RslvdCase",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    sts: Optional[InvestigationStatus3Choice] = field(
        default=None,
        metadata={
            "name": "Sts",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
            "required": True,
        },
    )
    cxl_dtls: list[UnderlyingTransaction4] = field(
        default_factory=list,
        metadata={
            "name": "CxlDtls",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    stmt_dtls: Optional[StatementResolutionEntry2] = field(
        default=None,
        metadata={
            "name": "StmtDtls",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    crrctn_tx: Optional[CorrectiveTransaction1Choice] = field(
        default=None,
        metadata={
            "name": "CrrctnTx",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    rsltn_rltd_inf: Optional[ResolutionInformation1] = field(
        default=None,
        metadata={
            "name": "RsltnRltdInf",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )
    splmtry_data: list[SupplementaryData1] = field(
        default_factory=list,
        metadata={
            "name": "SplmtryData",
            "type": "Element",
            "namespace": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04",
        },
    )


@dataclass
class Document:
    class Meta:
        namespace = "urn:iso:std:iso:20022:tech:xsd:camt.029.001.04"

    rsltn_of_invstgtn: Optional[ResolutionOfInvestigationV04] = field(
        default=None,
        metadata={
            "name": "RsltnOfInvstgtn",
            "type": "Element",
            "required": True,
        },
    )
