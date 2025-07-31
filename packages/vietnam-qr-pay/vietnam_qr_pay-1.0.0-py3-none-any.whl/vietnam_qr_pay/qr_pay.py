from typing import Optional, Dict, Union
from .constants import (
    FieldID,
    QRProvider,
    QRProviderGUID,
    ProviderFieldID,
    VietQRService,
    VietQRConsumerFieldID,
    AdditionalDataID,
    Provider,
    AdditionalData,
    Consumer,
    Merchant,
    EVMCoFieldID,
    UnreservedFieldID,
)
from .crc16 import crc16ccitt


class QRPay:
    """Vietnam QR Pay encoder/decoder supporting VietQR and VNPay standards."""
    
    def __init__(self, content: Optional[str] = None):
        self.is_valid = True
        self.version: Optional[str] = None
        self.init_method: Optional[str] = None
        self.provider = Provider()
        self.merchant = Merchant()
        self.consumer = Consumer()
        self.category: Optional[str] = None
        self.currency: Optional[str] = None
        self.amount: Optional[str] = None
        self.tip_and_fee_type: Optional[str] = None
        self.tip_and_fee_amount: Optional[str] = None
        self.tip_and_fee_percent: Optional[str] = None
        self.nation: Optional[str] = None
        self.city: Optional[str] = None
        self.zip_code: Optional[str] = None
        self.additional_data = AdditionalData()
        self.crc: Optional[str] = None
        
        self.evm_co: Dict[str, str] = {}
        self.unreserved: Dict[str, str] = {}
        
        if content:
            self.parse(content)
    
    def parse(self, content: str) -> None:
        """Parse QR content string."""
        if len(content) < 4:
            self._invalid()
            return
            
        # Verify CRC
        if not self._verify_crc(content):
            self._invalid()
            return
            
        # Parse content
        self._parse_root_content(content)
    
    def build(self) -> str:
        """Build QR content string from current data."""
        version = self._gen_field_data(FieldID.VERSION.value, self.version or "01")
        init_method = self._gen_field_data(FieldID.INIT_METHOD.value, self.init_method or "11")
        
        guid = self._gen_field_data(ProviderFieldID.GUID.value, self.provider.guid)
        
        provider_data_content = ""
        if self.provider.guid == QRProviderGUID.VIETQR.value:
            bank_bin = self._gen_field_data(
                VietQRConsumerFieldID.BANK_BIN.value, self.consumer.bank_bin
            )
            bank_number = self._gen_field_data(
                VietQRConsumerFieldID.BANK_NUMBER.value, self.consumer.bank_number
            )
            provider_data_content = bank_bin + bank_number
        elif self.provider.guid == QRProviderGUID.VNPAY.value:
            provider_data_content = self.merchant.id or ""
        else:
            provider_data_content = self.provider.data or ""
        
        provider = self._gen_field_data(ProviderFieldID.DATA.value, provider_data_content)
        service = self._gen_field_data(ProviderFieldID.SERVICE.value, self.provider.service)
        provider_data = self._gen_field_data(self.provider.field_id, guid + provider + service)
        
        category = self._gen_field_data(FieldID.CATEGORY.value, self.category)
        currency = self._gen_field_data(FieldID.CURRENCY.value, self.currency or "704")
        amount_str = self._gen_field_data(FieldID.AMOUNT.value, self.amount)
        tip_and_fee_type = self._gen_field_data(FieldID.TIP_AND_FEE_TYPE.value, self.tip_and_fee_type)
        tip_and_fee_amount = self._gen_field_data(FieldID.TIP_AND_FEE_AMOUNT.value, self.tip_and_fee_amount)
        tip_and_fee_percent = self._gen_field_data(FieldID.TIP_AND_FEE_PERCENT.value, self.tip_and_fee_percent)
        nation = self._gen_field_data(FieldID.NATION.value, self.nation or "VN")
        merchant_name = self._gen_field_data(FieldID.MERCHANT_NAME.value, self.merchant.name)
        city = self._gen_field_data(FieldID.CITY.value, self.city)
        zip_code = self._gen_field_data(FieldID.ZIP_CODE.value, self.zip_code)
        
        # Build additional data
        bill_number = self._gen_field_data(AdditionalDataID.BILL_NUMBER.value, self.additional_data.bill_number)
        mobile_number = self._gen_field_data(AdditionalDataID.MOBILE_NUMBER.value, self.additional_data.mobile_number)
        store_label = self._gen_field_data(AdditionalDataID.STORE_LABEL.value, self.additional_data.store)
        loyalty_number = self._gen_field_data(AdditionalDataID.LOYALTY_NUMBER.value, self.additional_data.loyalty_number)
        reference = self._gen_field_data(AdditionalDataID.REFERENCE_LABEL.value, self.additional_data.reference)
        customer_label = self._gen_field_data(AdditionalDataID.CUSTOMER_LABEL.value, self.additional_data.customer_label)
        terminal = self._gen_field_data(AdditionalDataID.TERMINAL_LABEL.value, self.additional_data.terminal)
        purpose = self._gen_field_data(AdditionalDataID.PURPOSE_OF_TRANSACTION.value, self.additional_data.purpose)
        data_request = self._gen_field_data(
            AdditionalDataID.ADDITIONAL_CONSUMER_DATA_REQUEST.value, self.additional_data.data_request
        )
        
        additional_data_content = (
            bill_number + mobile_number + store_label + loyalty_number + 
            reference + customer_label + terminal + purpose + data_request
        )
        additional_data = self._gen_field_data(FieldID.ADDITIONAL_DATA.value, additional_data_content)
        
        # Build EVMCo and unreserved fields
        evm_co_content = "".join(
            self._gen_field_data(key, value) 
            for key, value in sorted(self.evm_co.items())
        )
        unreserved_content = "".join(
            self._gen_field_data(key, value) 
            for key, value in sorted(self.unreserved.items())
        )
        
        content = (
            f"{version}{init_method}{provider_data}{category}{currency}{amount_str}"
            f"{tip_and_fee_type}{tip_and_fee_amount}{tip_and_fee_percent}{nation}"
            f"{merchant_name}{city}{zip_code}{additional_data}{evm_co_content}"
            f"{unreserved_content}{FieldID.CRC.value}04"
        )
        
        crc = self._gen_crc_code(content)
        return content + crc
    
    @classmethod
    def init_viet_qr(
        cls,
        bank_bin: str,
        bank_number: str,
        amount: Optional[str] = None,
        purpose: Optional[str] = None,
        service: Optional[VietQRService] = None,
    ) -> "QRPay":
        """Initialize a VietQR instance."""
        qr = cls()
        qr.init_method = "12" if amount else "11"
        qr.provider.field_id = FieldID.VIETQR.value
        qr.provider.guid = QRProviderGUID.VIETQR.value
        qr.provider.name = QRProvider.VIETQR
        qr.provider.service = (service or VietQRService.BY_ACCOUNT_NUMBER).value
        qr.consumer.bank_bin = bank_bin
        qr.consumer.bank_number = bank_number
        qr.amount = amount
        qr.additional_data.purpose = purpose
        return qr
    
    @classmethod
    def init_vnpay_qr(
        cls,
        merchant_id: str,
        merchant_name: str,
        store: str,
        terminal: str,
        amount: Optional[str] = None,
        purpose: Optional[str] = None,
        bill_number: Optional[str] = None,
        mobile_number: Optional[str] = None,
        loyalty_number: Optional[str] = None,
        reference: Optional[str] = None,
        customer_label: Optional[str] = None,
    ) -> "QRPay":
        """Initialize a VNPay QR instance."""
        qr = cls()
        # VNPAY always uses init method 11, unlike VietQR
        qr.merchant.id = merchant_id
        qr.merchant.name = merchant_name
        qr.provider.field_id = FieldID.VNPAYQR.value
        qr.provider.guid = QRProviderGUID.VNPAY.value
        qr.provider.name = QRProvider.VNPAY
        qr.amount = amount
        qr.additional_data.purpose = purpose
        qr.additional_data.bill_number = bill_number
        qr.additional_data.mobile_number = mobile_number
        qr.additional_data.store = store
        qr.additional_data.terminal = terminal
        qr.additional_data.loyalty_number = loyalty_number
        qr.additional_data.reference = reference
        qr.additional_data.customer_label = customer_label
        return qr
    
    def set_evm_co_field(self, field_id: EVMCoFieldID, value: str) -> None:
        """Set an EVMCo field value."""
        self.evm_co[field_id] = value
    
    def set_unreserved_field(self, field_id: UnreservedFieldID, value: str) -> None:
        """Set an unreserved field value."""
        self.unreserved[field_id] = value
    
    def _parse_root_content(self, content: str) -> None:
        """Parse root level QR content."""
        field_id, length, value, next_value = self._slice_content(content)
        
        if len(value) != length:
            self._invalid()
            return
        
        if field_id == FieldID.VERSION.value:
            self.version = value
        elif field_id == FieldID.INIT_METHOD.value:
            self.init_method = value
        elif field_id == FieldID.VIETQR.value or field_id == FieldID.VNPAYQR.value:
            self.provider.field_id = field_id
            self._parse_provider_info(value)
        elif field_id == FieldID.CATEGORY.value:
            self.category = value
        elif field_id == FieldID.CURRENCY.value:
            self.currency = value
        elif field_id == FieldID.AMOUNT.value:
            self.amount = value
        elif field_id == FieldID.TIP_AND_FEE_TYPE.value:
            self.tip_and_fee_type = value
        elif field_id == FieldID.TIP_AND_FEE_AMOUNT.value:
            self.tip_and_fee_amount = value
        elif field_id == FieldID.TIP_AND_FEE_PERCENT.value:
            self.tip_and_fee_percent = value
        elif field_id == FieldID.NATION.value:
            self.nation = value
        elif field_id == FieldID.MERCHANT_NAME.value:
            self.merchant.name = value
        elif field_id == FieldID.CITY.value:
            self.city = value
        elif field_id == FieldID.ZIP_CODE.value:
            self.zip_code = value
        elif field_id == FieldID.ADDITIONAL_DATA.value:
            self._parse_additional_data(value)
        elif field_id == FieldID.CRC.value:
            self.crc = value
        else:
            # Handle EVMCo and unreserved fields
            try:
                id_num = int(field_id)
                if 65 <= id_num <= 79:
                    self.evm_co[field_id] = value
                elif 80 <= id_num <= 99:
                    self.unreserved[field_id] = value
            except ValueError:
                pass
        
        if len(next_value) > 4:
            self._parse_root_content(next_value)
    
    def _parse_provider_info(self, content: str) -> None:
        """Parse provider information."""
        field_id, _, value, next_value = self._slice_content(content)
        
        if field_id == ProviderFieldID.GUID.value:
            self.provider.guid = value
        elif field_id == ProviderFieldID.DATA.value:
            if self.provider.guid == QRProviderGUID.VNPAY.value:
                self.provider.name = QRProvider.VNPAY
                self.merchant.id = value
            elif self.provider.guid == QRProviderGUID.VIETQR.value:
                self.provider.name = QRProvider.VIETQR
                self._parse_viet_qr_consumer(value)
            self.provider.data = value
        elif field_id == ProviderFieldID.SERVICE.value:
            self.provider.service = value
        
        if len(next_value) > 4:
            self._parse_provider_info(next_value)
    
    def _parse_viet_qr_consumer(self, content: str) -> None:
        """Parse VietQR consumer information."""
        field_id, _, value, next_value = self._slice_content(content)
        
        if field_id == VietQRConsumerFieldID.BANK_BIN.value:
            self.consumer.bank_bin = value
        elif field_id == VietQRConsumerFieldID.BANK_NUMBER.value:
            self.consumer.bank_number = value
        
        if len(next_value) > 4:
            self._parse_viet_qr_consumer(next_value)
    
    def _parse_additional_data(self, content: str) -> None:
        """Parse additional data fields."""
        field_id, _, value, next_value = self._slice_content(content)
        
        if field_id == AdditionalDataID.BILL_NUMBER.value:
            self.additional_data.bill_number = value
        elif field_id == AdditionalDataID.MOBILE_NUMBER.value:
            self.additional_data.mobile_number = value
        elif field_id == AdditionalDataID.STORE_LABEL.value:
            self.additional_data.store = value
        elif field_id == AdditionalDataID.LOYALTY_NUMBER.value:
            self.additional_data.loyalty_number = value
        elif field_id == AdditionalDataID.REFERENCE_LABEL.value:
            self.additional_data.reference = value
        elif field_id == AdditionalDataID.CUSTOMER_LABEL.value:
            self.additional_data.customer_label = value
        elif field_id == AdditionalDataID.TERMINAL_LABEL.value:
            self.additional_data.terminal = value
        elif field_id == AdditionalDataID.PURPOSE_OF_TRANSACTION.value:
            self.additional_data.purpose = value
        elif field_id == AdditionalDataID.ADDITIONAL_CONSUMER_DATA_REQUEST.value:
            self.additional_data.data_request = value
        
        if len(next_value) > 4:
            self._parse_additional_data(next_value)
    
    @staticmethod
    def _verify_crc(content: str) -> bool:
        """Verify CRC checksum."""
        check_content = content[:-4]
        crc_code = content[-4:].upper()
        gen_crc_code = QRPay._gen_crc_code(check_content)
        return crc_code == gen_crc_code
    
    @staticmethod
    def _gen_crc_code(content: str) -> str:
        """Generate CRC code for content."""
        crc_code = crc16ccitt(content)
        return f"{crc_code:04X}"
    
    @staticmethod
    def _slice_content(content: str) -> tuple[str, int, str, str]:
        """Slice content into field components."""
        field_id = content[:2]
        length = int(content[2:4])
        value = content[4:4 + length]
        next_value = content[4 + length:]
        return field_id, length, value, next_value
    
    def _invalid(self) -> None:
        """Mark QR as invalid."""
        self.is_valid = False
    
    @staticmethod
    def _gen_field_data(field_id: Optional[str], value: Optional[str]) -> str:
        """Generate field data string."""
        if not field_id or len(field_id) != 2 or not value:
            return ""
        
        length = f"{len(value):02d}"
        return f"{field_id}{length}{value}"