# Vietnam QR Pay - Python

Python library for encoding/decoding QR codes for Vietnamese banks, supporting VietQR (bank transfer QR) and VNPayQR standards, as well as multi-purpose QR codes for e-wallets like MoMo and ZaloPay.

This is the Python version of the vietnam-qr-pay library, separated from the original TypeScript/JavaScript implementation.

## Features

- ✅ Decode VietQR and VNPay QR codes
- ✅ Create static QR codes (no amount specified)
- ✅ Create dynamic QR codes (with amount)
- ✅ Support for 60+ Vietnamese banks
- ✅ E-wallet QR support (MoMo, ZaloPay via VietQR)
- ✅ CRC16 checksum validation
- ✅ Fully typed with Python type hints

## Installation

```bash
pip install vietnam-qr-pay
```

Or using uv:

```bash
uv add vietnam-qr-pay
```

## Quick Start

### Decode a QR Code

```python
from vietnam_qr_pay import QRPay

# Decode a VietQR code
qr_content = "00020101021238530010A0000007270123000697041601092576788590208QRIBFTTA5303704540410005802VN62150811Chuyen tien6304BBB8"
qr_pay = QRPay(qr_content)

print(qr_pay.is_valid)  # True
print(qr_pay.provider.name)  # QRProvider.VIETQR
print(qr_pay.consumer.bank_bin)  # 970416
print(qr_pay.consumer.bank_number)  # 257678859
print(qr_pay.amount)  # 1000
print(qr_pay.additional_data.purpose)  # Chuyen tien
```

### Create a Static VietQR (No Amount)

```python
from vietnam_qr_pay import QRPay, BanksObject

# Create QR for ACB bank account
qr_pay = QRPay.init_viet_qr(
    bank_bin=BanksObject["acb"].bin,
    bank_number="257678859"
)
content = qr_pay.build()
print(content)
# 00020101021138530010A0000007270123000697041601092576788590208QRIBFTTA53037045802VN6304AE9F
```

### Create a Dynamic VietQR (With Amount)

```python
from vietnam_qr_pay import QRPay, BanksObject

qr_pay = QRPay.init_viet_qr(
    bank_bin=BanksObject["vietcombank"].bin,
    bank_number="1234567890",
    amount="100000",
    purpose="Thanh toan don hang"
)
content = qr_pay.build()
```

### Create a VNPay QR Code

```python
from vietnam_qr_pay import QRPay

qr_pay = QRPay.init_vnpay_qr(
    merchant_id="0102154778",
    merchant_name="TUGIACOMPANY",
    store="TU GIA COMPUTER",
    terminal="TUGIACO1"
)
content = qr_pay.build()
```

## E-Wallet Support

### MoMo QR Code

```python
from vietnam_qr_pay import QRPay, BanksObject

# MoMo account number from the app
account_number = "99MM24011M34875080"

momo_qr = QRPay.init_viet_qr(
    bank_bin=BanksObject["banviet"].bin,
    bank_number=account_number,
    amount="50000",  # Optional
    purpose="Chuyen tien"  # Optional
)

# Add MoMo specific reference
momo_qr.additional_data.reference = "MOMOW2W" + account_number[10:]

# Add phone number's last 3 digits
momo_qr.set_unreserved_field("80", "046")

content = momo_qr.build()
```

### ZaloPay QR Code

```python
from vietnam_qr_pay import QRPay, BanksObject

# ZaloPay account number from the app
account_number = "99ZP24009M07248267"

zalopay_qr = QRPay.init_viet_qr(
    bank_bin=BanksObject["banviet"].bin,
    bank_number=account_number,
    amount="100000",  # Optional
    purpose="Thanh toan"  # Optional
)

content = zalopay_qr.build()
```

## Working with Banks

### List All Supported Banks

```python
from vietnam_qr_pay import BanksObject, VietQRStatus

# Get all banks
all_banks = BanksObject.values()

# Get banks supporting VietQR transfers
transfer_banks = [
    bank for bank in BanksObject.values() 
    if bank.viet_qr_status == VietQRStatus.TRANSFER_SUPPORTED
]

# Access specific bank info
vietcombank = BanksObject["vietcombank"]
print(vietcombank.name)  # Ngân hàng TMCP Ngoại Thương Việt Nam
print(vietcombank.short_name)  # Vietcombank
print(vietcombank.bin)  # 970436
```

### Bank Object Properties

```python
from vietnam_qr_pay import BanksObject

bank = BanksObject["acb"]
print(bank.key)  # BankKey.ACB
print(bank.code)  # BankCode.ACB
print(bank.name)  # Ngân hàng TMCP Á Châu
print(bank.short_name)  # ACB
print(bank.bin)  # 970416
print(bank.swift_code)  # ASCBVNVX
print(bank.viet_qr_status)  # VietQRStatus.TRANSFER_SUPPORTED
```

## Advanced Usage

### Modify and Rebuild QR

```python
# Parse existing QR
qr_pay = QRPay(qr_content)

# Modify fields
qr_pay.amount = "999999"
qr_pay.additional_data.purpose = "Updated purpose"

# Rebuild QR
new_content = qr_pay.build()
```

### Custom Fields

```python
# Set unreserved fields (80-99)
qr_pay.set_unreserved_field("85", "custom_value")

# Set EMVCo fields (65-79)
qr_pay.set_evm_co_field("70", "emv_value")
```

## API Reference

### QRPay Class

```python
class QRPay:
    # Properties
    is_valid: bool
    version: str
    init_method: str  # "11" = static, "12" = dynamic
    provider: Provider
    merchant: Merchant
    consumer: Consumer
    amount: Optional[str]
    currency: str  # "704" for VND
    nation: str  # "VN"
    additional_data: AdditionalData
    crc: str
    
    # Methods
    def __init__(content: Optional[str] = None)
    def parse(content: str) -> None
    def build() -> str
    
    # Class methods
    @classmethod
    def init_viet_qr(...) -> QRPay
    @classmethod
    def init_vnpay_qr(...) -> QRPay
```

### Bank Properties

```python
@dataclass
class Bank:
    key: BankKey
    code: BankCode
    name: str
    short_name: str
    bin: str
    viet_qr_status: VietQRStatus
    lookup_supported: Optional[int]
    swift_code: Optional[str]
    keywords: Optional[str]
    deprecated: Optional[bool]
```

## Testing

Run tests using pytest:

```bash
uv run pytest
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

This is a Python port of the original [vietnam-qr-pay](https://github.com/xuannghia/vietnam-qr-pay) JavaScript library.