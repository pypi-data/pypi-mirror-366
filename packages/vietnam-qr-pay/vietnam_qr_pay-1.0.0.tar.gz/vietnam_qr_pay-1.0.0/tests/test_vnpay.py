import pytest
from vietnam_qr_pay import QRPay, QRProvider


class TestVNPay:
    def test_decode_vnpay(self):
        """Test decoding a VNPay QR code."""
        qr_content = "00020101021126280010A0000007750110010531314453037045408210900005802VN5910CELLPHONES62600312CPSHN ONLINE0517021908061613127850705ONLHN0810CellphoneS63047685"
        qr_pay = QRPay(qr_content)
        
        assert qr_pay.is_valid is True
        assert qr_pay.provider.name == QRProvider.VNPAY
        assert qr_pay.merchant.id == "0105313144"
        assert qr_pay.amount == "21090000"
        assert qr_pay.additional_data.store == "CPSHN ONLINE"
        assert qr_pay.additional_data.terminal == "ONLHN"
        assert qr_pay.additional_data.purpose == "CellphoneS"
        assert qr_pay.additional_data.reference == "02190806161312785"

    def test_create_vnpay_qr(self):
        """Test creating a VNPay QR code."""
        qr_pay = QRPay.init_vnpay_qr(
            merchant_id="0102154778",
            merchant_name="TUGIACOMPANY",
            store="TU GIA COMPUTER",
            terminal="TUGIACO1"
        )
        content = qr_pay.build()
        
        # Build the expected content step by step for verification
        # The content should include version, init method, provider data, currency, nation, merchant name, and additional data
        assert content.startswith("00020101021126280010A000000775")  # Version, init method, provider start
        assert "0102154778" in content  # Merchant ID
        assert "TUGIACOMPANY" in content  # Merchant name
        assert "TU GIA COMPUTER" in content  # Store
        assert "TUGIACO1" in content  # Terminal