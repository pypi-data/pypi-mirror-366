from enum import Enum
from typing import Optional, Literal


class QRProvider(str, Enum):
    VIETQR = "VIETQR"
    VNPAY = "VNPAY"


class QRProviderGUID(str, Enum):
    VNPAY = "A000000775"
    VIETQR = "A000000727"


class FieldID(str, Enum):
    VERSION = "00"
    INIT_METHOD = "01"
    VNPAYQR = "26"
    VIETQR = "38"
    CATEGORY = "52"
    CURRENCY = "53"
    AMOUNT = "54"
    TIP_AND_FEE_TYPE = "55"
    TIP_AND_FEE_AMOUNT = "56"
    TIP_AND_FEE_PERCENT = "57"
    NATION = "58"
    MERCHANT_NAME = "59"
    CITY = "60"
    ZIP_CODE = "61"
    ADDITIONAL_DATA = "62"
    CRC = "63"


EVMCoFieldID = Literal[
    "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", 
    "75", "76", "77", "78", "79"
]

UnreservedFieldID = Literal[
    "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",
    "90", "91", "92", "93", "94", "95", "96", "97", "98", "99"
]


class ProviderFieldID(str, Enum):
    GUID = "00"
    DATA = "01"
    SERVICE = "02"


class VietQRService(str, Enum):
    BY_ACCOUNT_NUMBER = "QRIBFTTA"  # Dịch vụ chuyển nhanh NAPAS247 đến Tài khoản
    BY_CARD_NUMBER = "QRIBFTTC"     # Dịch vụ chuyển nhanh NAPAS247 đến Thẻ


class VietQRConsumerFieldID(str, Enum):
    BANK_BIN = "00"
    BANK_NUMBER = "01"


class AdditionalDataID(str, Enum):
    BILL_NUMBER = "01"  # Số hóa đơn
    MOBILE_NUMBER = "02"  # Số ĐT
    STORE_LABEL = "03"  # Mã cửa hàng
    LOYALTY_NUMBER = "04"  # Mã khách hàng thân thiết
    REFERENCE_LABEL = "05"  # Mã tham chiếu
    CUSTOMER_LABEL = "06"  # Mã khách hàng
    TERMINAL_LABEL = "07"  # Mã số điểm bán
    PURPOSE_OF_TRANSACTION = "08"  # Mục đích giao dịch
    ADDITIONAL_CONSUMER_DATA_REQUEST = "09"  # Yêu cầu dữ liệu KH bổ sung


class Provider:
    def __init__(self):
        self.field_id: Optional[str] = None
        self.name: Optional[QRProvider] = None
        self.guid: Optional[str] = None
        self.service: Optional[str] = None
        self.data: Optional[str] = None


class AdditionalData:
    def __init__(self):
        self.bill_number: Optional[str] = None
        self.mobile_number: Optional[str] = None
        self.store: Optional[str] = None
        self.loyalty_number: Optional[str] = None
        self.reference: Optional[str] = None
        self.customer_label: Optional[str] = None
        self.terminal: Optional[str] = None
        self.purpose: Optional[str] = None
        self.data_request: Optional[str] = None


class Consumer:
    def __init__(self):
        self.bank_bin: Optional[str] = None
        self.bank_number: Optional[str] = None


class Merchant:
    def __init__(self):
        self.id: Optional[str] = None
        self.name: Optional[str] = None