import pytest
from vietnam_qr_pay import QRPay, BanksObject


class TestMoMoZaloPay:
    def test_create_momo_qr(self):
        """Test creating a MoMo QR code."""
        # MoMo account number
        account_number = "99MM24011M34875080"
        
        momo_qr = QRPay.init_viet_qr(
            bank_bin=BanksObject["banviet"].bin,
            bank_number=account_number
        )
        
        # MoMo specific fields
        momo_qr.additional_data.reference = "MOMOW2W" + account_number[10:]
        momo_qr.set_unreserved_field("80", "046")
        
        content = momo_qr.build()
        
        # Verify content includes MoMo specific data
        assert BanksObject["banviet"].bin in content
        assert account_number in content
        assert "MOMOW2W34875080" in content  # Reference
        assert "8003046" in content  # Unreserved field 80 with value 046

    def test_create_zalopay_qr(self):
        """Test creating a ZaloPay QR code."""
        # ZaloPay account number
        account_number = "99ZP24009M07248267"
        
        zalopay_qr = QRPay.init_viet_qr(
            bank_bin=BanksObject["banviet"].bin,
            bank_number=account_number
        )
        
        content = zalopay_qr.build()
        
        # Expected content
        expected = "00020101021138620010A00000072701320006970454011899ZP24009M072482670208QRIBFTTA53037045802VN6304073C"
        assert content == expected

    def test_momo_with_amount(self):
        """Test creating a MoMo QR code with amount."""
        account_number = "99MM24011M34875080"
        
        momo_qr = QRPay.init_viet_qr(
            bank_bin=BanksObject["banviet"].bin,
            bank_number=account_number,
            amount="50000",
            purpose="Test payment"
        )
        
        # MoMo specific fields
        momo_qr.additional_data.reference = "MOMOW2W" + account_number[10:]
        momo_qr.set_unreserved_field("80", "046")
        
        content = momo_qr.build()
        
        # Verify dynamic QR properties
        assert "540550000" in content  # Amount field with value 50000
        assert "Test payment" in content
        assert momo_qr.init_method == "12"  # Dynamic QR