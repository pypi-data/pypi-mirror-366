import pytest
from vietnam_qr_pay import QRPay, QRProvider, QRProviderGUID, BanksObject


class TestVietQR:
    def test_decode_vietqr(self):
        """Test decoding a VietQR code."""
        qr_content = "00020101021238530010A0000007270123000697041601092576788590208QRIBFTTA5303704540410005802VN62150811Chuyen tien6304BBB8"
        qr_pay = QRPay(qr_content)
        
        assert qr_pay.is_valid is True
        assert qr_pay.version == "01"
        assert qr_pay.provider.name == QRProvider.VIETQR
        assert qr_pay.provider.guid == QRProviderGUID.VIETQR.value
        assert qr_pay.consumer.bank_bin == "970416"
        assert qr_pay.consumer.bank_number == "257678859"
        assert qr_pay.amount == "1000"
        assert qr_pay.additional_data.purpose == "Chuyen tien"
        assert qr_pay.build() == qr_content

    def test_crc_with_three_byte(self):
        """Test CRC with three-byte value."""
        qr_content = "00020101021138580010A000000727012800069704070114190304136010180208QRIBFTTA53037045802VN63040283"
        qr_pay = QRPay(qr_content)
        
        assert qr_pay.is_valid is True
        assert qr_pay.version == "01"
        assert qr_pay.provider.name == QRProvider.VIETQR
        assert qr_pay.provider.guid == QRProviderGUID.VIETQR.value
        assert qr_pay.consumer.bank_bin == "970407"
        assert qr_pay.consumer.bank_number == "19030413601018"
        assert qr_pay.build() == qr_content

    def test_invalid_crc(self):
        """Test invalid CRC VietQR."""
        qr_pay = QRPay("00020101021238530010A0000007270123000697041601092576788590208QRIBFTTA5303704540410005802VN62150811Chuyen tien6304BBB5")
        assert qr_pay.is_valid is False

    def test_mbbank_qr_with_lowercase_crc(self):
        """Test MBBank QR with lowercase CRC."""
        qr_content = "00020101021138540010A00000072701240006970422011003523509170208QRIBFTTA53037045802VN630479db"
        qr_pay = QRPay(qr_content)
        
        assert qr_pay.is_valid is True
        assert qr_pay.version == "01"
        assert qr_pay.provider.name == QRProvider.VIETQR
        assert qr_pay.provider.guid == QRProviderGUID.VIETQR.value
        assert qr_pay.consumer.bank_bin == "970422"
        assert qr_pay.consumer.bank_number == "0352350917"
        assert qr_pay.build()[-4:] == qr_content[-4:].upper()

    def test_create_static_vietqr(self):
        """Test creating a static VietQR code."""
        qr_pay = QRPay.init_viet_qr(
            bank_bin=BanksObject["acb"].bin,
            bank_number="257678859"
        )
        content = qr_pay.build()
        
        assert content == "00020101021138530010A0000007270123000697041601092576788590208QRIBFTTA53037045802VN6304AE9F"

    def test_create_dynamic_vietqr(self):
        """Test creating a dynamic VietQR code with amount and purpose."""
        qr_pay = QRPay.init_viet_qr(
            bank_bin=BanksObject["acb"].bin,
            bank_number="257678859",
            amount="10000",
            purpose="Chuyen tien"
        )
        content = qr_pay.build()
        
        assert content == "00020101021238530010A0000007270123000697041601092576788590208QRIBFTTA53037045405100005802VN62150811Chuyen tien630453E6"

    def test_modify_and_rebuild_qr(self):
        """Test modifying QR data and rebuilding."""
        qr_content = "00020101021238530010A0000007270123000697041601092576788590208QRIBFTTA5303704540410005802VN62150811Chuyen tien6304BBB8"
        qr_pay = QRPay(qr_content)
        
        # Verify original values
        assert qr_pay.amount == "1000"
        assert qr_pay.additional_data.purpose == "Chuyen tien"
        
        # Modify values
        qr_pay.amount = "999999"
        qr_pay.additional_data.purpose = "Cam on nhe"
        
        new_content = qr_pay.build()
        assert new_content == "00020101021238530010A0000007270123000697041601092576788590208QRIBFTTA530370454069999995802VN62140810Cam on nhe6304E786"