from dataclasses import dataclass
from enum import IntEnum
from typing import Optional
from .bank_key import BankKey
from .bank_code import BankCode


class VietQRStatus(IntEnum):
    NOT_SUPPORTED = -1
    RECEIVE_ONLY = 0
    TRANSFER_SUPPORTED = 1


@dataclass
class Bank:
    key: BankKey
    code: BankCode
    name: str
    short_name: str
    bin: str
    viet_qr_status: VietQRStatus
    lookup_supported: Optional[int] = None
    swift_code: Optional[str] = None
    keywords: Optional[str] = None
    deprecated: Optional[bool] = None


BanksObject = {
    BankKey.ABBANK: Bank(
        key=BankKey.ABBANK,
        code=BankCode.ABBANK,
        name="Ngân hàng TMCP An Bình",
        bin="970425",
        short_name="AB Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="ABBKVNVX",
        keywords="anbinh"
    ),
    BankKey.ACB: Bank(
        key=BankKey.ACB,
        code=BankCode.ACB,
        name="Ngân hàng TMCP Á Châu",
        bin="970416",
        short_name="ACB",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="ASCBVNVX",
        keywords="achau"
    ),
    BankKey.AGRIBANK: Bank(
        key=BankKey.AGRIBANK,
        code=BankCode.AGRIBANK,
        name="Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam",
        bin="970405",
        short_name="Agribank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="VBAAVNVX",
        keywords="nongnghiep, nongthon, agribank, agri"
    ),
    BankKey.BAC_A_BANK: Bank(
        key=BankKey.BAC_A_BANK,
        code=BankCode.BAC_A_BANK,
        name="Ngân hàng TMCP Bắc Á",
        bin="970409",
        short_name="BacA Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="NASCVNVX",
        keywords="baca, NASB"
    ),
    BankKey.BAOVIET_BANK: Bank(
        key=BankKey.BAOVIET_BANK,
        code=BankCode.BAOVIET_BANK,
        name="Ngân hàng TMCP Bảo Việt",
        bin="970438",
        short_name="BaoViet Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="BVBVVNVX",
        keywords="baoviet, BVB"
    ),
    BankKey.BANVIET: Bank(
        key=BankKey.BANVIET,
        code=BankCode.BANVIET,
        name="Ngân hàng TMCP Bản Việt",
        bin="970454",
        short_name="BVBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="VCBCVNVX",
        keywords="banviet, vietcapitalbank"
    ),
    BankKey.BIDC: Bank(
        key=BankKey.BIDC,
        code=BankCode.BIDC,
        name="Ngân hàng TMCP Đầu tư và Phát triển Campuchia",
        bin="",
        short_name="BIDC",
        viet_qr_status=VietQRStatus.NOT_SUPPORTED
    ),
    BankKey.BIDV: Bank(
        key=BankKey.BIDV,
        code=BankCode.BIDV,
        name="Ngân hàng TMCP Đầu tư và Phát triển Việt Nam",
        bin="970418",
        short_name="BIDV",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="BIDVVNVX"
    ),
    BankKey.CAKE: Bank(
        key=BankKey.CAKE,
        code=BankCode.CAKE,
        name="Ngân hàng số CAKE by VPBank - Ngân hàng TMCP Việt Nam Thịnh Vượng",
        bin="546034",
        short_name="CAKE by VPBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code=None
    ),
    BankKey.CBBANK: Bank(
        key=BankKey.CBBANK,
        code=BankCode.CBBANK,
        name="Ngân hàng Thương mại TNHH MTV Xây dựng Việt Nam",
        bin="970444",
        short_name="CB Bank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code="GTBAVNVX",
        keywords="xaydungvn, xaydung"
    ),
    BankKey.CIMB: Bank(
        key=BankKey.CIMB,
        code=BankCode.CIMB,
        name="Ngân hàng TNHH MTV CIMB Việt Nam",
        bin="422589",
        short_name="CIMB Bank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code="CIBBVNVN",
        keywords="cimbvn"
    ),
    BankKey.COOP_BANK: Bank(
        key=BankKey.COOP_BANK,
        code=BankCode.COOP_BANK,
        name="Ngân hàng Hợp tác xã Việt Nam",
        bin="970446",
        short_name="Co-op Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code=None,
        keywords="hoptacxa, coop"
    ),
    BankKey.DBS_BANK: Bank(
        key=BankKey.DBS_BANK,
        code=BankCode.DBS_BANK,
        name="NH TNHH MTV Phát triển Singapore - Chi nhánh TP. Hồ Chí Minh",
        bin="796500",
        short_name="DBS Bank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=0,
        swift_code="DBSSVNVX",
        keywords="dbshcm"
    ),
    BankKey.DONG_A_BANK: Bank(
        key=BankKey.DONG_A_BANK,
        code=BankCode.DONG_A_BANK,
        name="Ngân hàng TMCP Đông Á",
        bin="970406",
        short_name="DongA Bank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code="EACBVNVX",
        keywords="donga, DAB",
        deprecated=True
    ),
    BankKey.EXIMBANK: Bank(
        key=BankKey.EXIMBANK,
        code=BankCode.EXIMBANK,
        name="Ngân hàng TMCP Xuất Nhập khẩu Việt Nam",
        bin="970431",
        short_name="Eximbank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="EBVIVNVX"
    ),
    BankKey.GPBANK: Bank(
        key=BankKey.GPBANK,
        code=BankCode.GPBANK,
        name="Ngân hàng Thương mại TNHH MTV Dầu Khí Toàn Cầu",
        bin="970408",
        short_name="GPBank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code="GBNKVNVX",
        keywords="daukhi"
    ),
    BankKey.HDBANK: Bank(
        key=BankKey.HDBANK,
        code=BankCode.HDBANK,
        name="Ngân hàng TMCP Phát triển TP. Hồ Chí Minh",
        bin="970437",
        short_name="HDBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="HDBCVNVX"
    ),
    BankKey.HONGLEONG_BANK: Bank(
        key=BankKey.HONGLEONG_BANK,
        code=BankCode.HONGLEONG_BANK,
        name="Ngân hàng TNHH MTV Hong Leong Việt Nam",
        bin="970442",
        short_name="HongLeong Bank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code="HLBBVNVX",
        keywords="HLBVN"
    ),
    BankKey.HSBC: Bank(
        key=BankKey.HSBC,
        code=BankCode.HSBC,
        name="Ngân hàng TNHH MTV HSBC (Việt Nam)",
        bin="458761",
        short_name="HSBC Vietnam",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code="HSBCVNVX"
    ),
    BankKey.IBK_HCM: Bank(
        key=BankKey.IBK_HCM,
        code=BankCode.IBK_HCM,
        name="Ngân hàng Công nghiệp Hàn Quốc - Chi nhánh TP. Hồ Chí Minh",
        bin="970456",
        short_name="IBK HCM",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=0,
        swift_code=None,
        keywords="congnghiep"
    ),
    BankKey.IBK_HN: Bank(
        key=BankKey.IBK_HN,
        code=BankCode.IBK_HN,
        name="Ngân hàng Công nghiệp Hàn Quốc - Chi nhánh Hà Nội",
        bin="970455",
        short_name="IBK HN",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=0,
        swift_code=None,
        keywords="congnghiep"
    ),
    BankKey.INDOVINA_BANK: Bank(
        key=BankKey.INDOVINA_BANK,
        code=BankCode.INDOVINA_BANK,
        name="Ngân hàng TNHH Indovina",
        bin="970434",
        short_name="Indovina Bank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code=None
    ),
    BankKey.KASIKORN_BANK: Bank(
        key=BankKey.KASIKORN_BANK,
        code=BankCode.KASIKORN_BANK,
        name="Ngân hàng Đại chúng TNHH KASIKORNBANK - CN TP. Hồ Chí Minh",
        bin="668888",
        short_name="Kasikornbank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="KASIVNVX"
    ),
    BankKey.KIENLONG_BANK: Bank(
        key=BankKey.KIENLONG_BANK,
        code=BankCode.KIENLONG_BANK,
        name="Ngân hàng TMCP Kiên Long",
        bin="970452",
        short_name="KienlongBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="KLBKVNVX"
    ),
    BankKey.KOOKMIN_BANK_HCM: Bank(
        key=BankKey.KOOKMIN_BANK_HCM,
        code=BankCode.KOOKMIN_BANK_HCM,
        name="Ngân hàng Kookmin - Chi nhánh TP. Hồ Chí Minh",
        bin="970463",
        short_name="Kookmin Bank HCM",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=0,
        swift_code=None
    ),
    BankKey.KOOKMIN_BANK_HN: Bank(
        key=BankKey.KOOKMIN_BANK_HN,
        code=BankCode.KOOKMIN_BANK_HN,
        name="Ngân hàng Kookmin - Chi nhánh Hà Nội",
        bin="970462",
        short_name="Kookmin Bank HN",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=0,
        swift_code=None
    ),
    BankKey.LIENVIETPOST_BANK: Bank(
        key=BankKey.LIENVIETPOST_BANK,
        code=BankCode.LPBANK,
        name="Ngân hàng TMCP Bưu Điện Liên Việt",
        bin="970449",
        short_name="LienVietPostBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="LVBKVNVX",
        keywords="lienvietbank",
        deprecated=True
    ),
    BankKey.LPBANK: Bank(
        key=BankKey.LPBANK,
        code=BankCode.LPBANK,
        name="Ngân hàng TMCP Lộc Phát Việt Nam",
        bin="970449",
        short_name="LPBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="LVBKVNVX",
        keywords="lienvietbank, loc phat"
    ),
    BankKey.LIOBANK: Bank(
        key=BankKey.LIOBANK,
        code=BankCode.LIOBANK,
        name="Ngân hàng số Liobank - Ngân hàng TMCP Phương Đông",
        bin="963369",
        short_name="Liobank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code=None
    ),
    BankKey.MBBANK: Bank(
        key=BankKey.MBBANK,
        code=BankCode.MBBANK,
        name="Ngân hàng TMCP Quân đội",
        bin="970422",
        short_name="MB Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="MSCBVNVX"
    ),
    BankKey.MBV: Bank(
        key=BankKey.MBV,
        code=BankCode.MBV,
        name="Ngân hàng TNHH MTV Việt Nam Hiện Đại",
        bin="970414",
        short_name="MBV",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="OCBKUS3M",
        keywords="daiduong, mbv"
    ),
    BankKey.MSB: Bank(
        key=BankKey.MSB,
        code=BankCode.MSB,
        name="Ngân hàng TMCP Hàng Hải",
        bin="970426",
        short_name="MSB",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="MCOBVNVX",
        keywords="hanghai"
    ),
    BankKey.NAM_A_BANK: Bank(
        key=BankKey.NAM_A_BANK,
        code=BankCode.NAM_A_BANK,
        name="Ngân hàng TMCP Nam Á",
        bin="970428",
        short_name="Nam A Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="NAMAVNVX",
        keywords="namabank"
    ),
    BankKey.NCB: Bank(
        key=BankKey.NCB,
        code=BankCode.NCB,
        name="Ngân hàng TMCP Quốc Dân",
        bin="970419",
        short_name="NCB Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="NVBAVNVX",
        keywords="quocdan"
    ),
    BankKey.NONGHYUP_BANK_HN: Bank(
        key=BankKey.NONGHYUP_BANK_HN,
        code=BankCode.NONGHYUP_BANK_HN,
        name="Ngân hàng Nonghyup - Chi nhánh Hà Nội",
        bin="801011",
        short_name="Nonghyup Bank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=0,
        swift_code=None
    ),
    BankKey.OCB: Bank(
        key=BankKey.OCB,
        code=BankCode.OCB,
        name="Ngân hàng TMCP Phương Đông",
        bin="970448",
        short_name="OCB Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="ORCOVNVX",
        keywords="phuongdong"
    ),
    BankKey.OCEANBANK: Bank(
        key=BankKey.OCEANBANK,
        code=BankCode.OCEANBANK,
        name="Ngân hàng Thương mại TNHH MTV Đại Dương",
        bin="970414",
        short_name="Ocean Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="OCBKUS3M",
        keywords="daiduong",
        deprecated=True
    ),
    BankKey.PGBANK: Bank(
        key=BankKey.PGBANK,
        code=BankCode.PGBANK,
        name="Ngân hàng TMCP Xăng dầu Petrolimex",
        bin="970430",
        short_name="PG Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="PGBLVNVX"
    ),
    BankKey.PUBLIC_BANK: Bank(
        key=BankKey.PUBLIC_BANK,
        code=BankCode.PUBLIC_BANK,
        name="Ngân hàng TNHH MTV Public Việt Nam",
        bin="970439",
        short_name="Public Bank Vietnam",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code="VIDPVNVX",
        keywords="publicvn"
    ),
    BankKey.PVCOM_BANK: Bank(
        key=BankKey.PVCOM_BANK,
        code=BankCode.PVCOM_BANK,
        name="Ngân hàng TMCP Đại Chúng Việt Nam",
        bin="970412",
        short_name="PVcomBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="WBVNVNVX",
        keywords="daichung"
    ),
    BankKey.SACOMBANK: Bank(
        key=BankKey.SACOMBANK,
        code=BankCode.SACOMBANK,
        name="Ngân hàng TMCP Sài Gòn Thương Tín",
        bin="970403",
        short_name="Sacombank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="SGTTVNVX"
    ),
    BankKey.SAIGONBANK: Bank(
        key=BankKey.SAIGONBANK,
        code=BankCode.SAIGONBANK,
        name="Ngân hàng TMCP Sài Gòn Công Thương",
        bin="970400",
        short_name="SaigonBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="SBITVNVX",
        keywords="saigoncongthuong, saigonbank"
    ),
    BankKey.SCB: Bank(
        key=BankKey.SCB,
        code=BankCode.SCB,
        name="Ngân hàng TMCP Sài Gòn",
        bin="970429",
        short_name="SCB",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="SACLVNVX",
        keywords="saigon"
    ),
    BankKey.SEA_BANK: Bank(
        key=BankKey.SEA_BANK,
        code=BankCode.SEA_BANK,
        name="Ngân hàng TMCP Đông Nam Á",
        bin="970440",
        short_name="SeABank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="SEAVVNVX"
    ),
    BankKey.SHB: Bank(
        key=BankKey.SHB,
        code=BankCode.SHB,
        name="Ngân hàng TMCP Sài Gòn - Hà Nội",
        bin="970443",
        short_name="SHB",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="SHBAVNVX",
        keywords="saigonhanoi, sghn"
    ),
    BankKey.SHINHAN_BANK: Bank(
        key=BankKey.SHINHAN_BANK,
        code=BankCode.SHINHAN_BANK,
        name="Ngân hàng TNHH MTV Shinhan Việt Nam",
        bin="970424",
        short_name="Shinhan Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="SHBKVNVX"
    ),
    BankKey.STANDARD_CHARTERED_BANK: Bank(
        key=BankKey.STANDARD_CHARTERED_BANK,
        code=BankCode.STANDARD_CHARTERED_BANK,
        name="Ngân hàng TNHH MTV Standard Chartered Bank Việt Nam",
        bin="970410",
        short_name="Standard Chartered Vietnam",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code="SCBLVNVX"
    ),
    BankKey.TECHCOMBANK: Bank(
        key=BankKey.TECHCOMBANK,
        code=BankCode.TECHCOMBANK,
        name="Ngân hàng TMCP Kỹ thương Việt Nam",
        bin="970407",
        short_name="Techcombank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="VTCBVNVX"
    ),
    BankKey.TIMO: Bank(
        key=BankKey.TIMO,
        code=BankCode.TIMO,
        name="Ngân hàng số Timo by Bản Việt Bank",
        bin="963388",
        short_name="Timo",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=0,
        swift_code=None,
        keywords="banviet"
    ),
    BankKey.TPBANK: Bank(
        key=BankKey.TPBANK,
        code=BankCode.TPBANK,
        name="Ngân hàng TMCP Tiên Phong",
        bin="970423",
        short_name="TPBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="TPBVVNVX",
        keywords="tienphong"
    ),
    BankKey.UBANK: Bank(
        key=BankKey.UBANK,
        code=BankCode.UBANK,
        name="Ngân hàng số Ubank by VPBank - Ngân hàng TMCP Việt Nam Thịnh Vượng",
        bin="546035",
        short_name="Ubank by VPBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code=None
    ),
    BankKey.UNITED_OVERSEAS_BANK: Bank(
        key=BankKey.UNITED_OVERSEAS_BANK,
        code=BankCode.UNITED_OVERSEAS_BANK,
        name="Ngân hàng United Overseas Bank Việt Nam",
        bin="970458",
        short_name="United Overseas Bank Vietnam",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code=None
    ),
    BankKey.VIB: Bank(
        key=BankKey.VIB,
        code=BankCode.VIB,
        name="Ngân hàng TMCP Quốc tế Việt Nam",
        bin="970441",
        short_name="VIB",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="VNIBVNVX",
        keywords="quocte"
    ),
    BankKey.VIET_A_BANK: Bank(
        key=BankKey.VIET_A_BANK,
        code=BankCode.VIET_A_BANK,
        name="Ngân hàng TMCP Việt Á",
        bin="970427",
        short_name="VietABank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="VNACVNVX"
    ),
    BankKey.VIETBANK: Bank(
        key=BankKey.VIETBANK,
        code=BankCode.VIETBANK,
        name="Ngân hàng TMCP Việt Nam Thương Tín",
        bin="970433",
        short_name="VietBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="VNTTVNVX",
        keywords="vietnamthuongtin, vnthuongtin"
    ),
    BankKey.VIETCOMBANK: Bank(
        key=BankKey.VIETCOMBANK,
        code=BankCode.VIETCOMBANK,
        name="Ngân hàng TMCP Ngoại Thương Việt Nam",
        bin="970436",
        short_name="Vietcombank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="BFTVVNVX"
    ),
    BankKey.VIETINBANK: Bank(
        key=BankKey.VIETINBANK,
        code=BankCode.VIETINBANK,
        name="Ngân hàng TMCP Công thương Việt Nam",
        bin="970415",
        short_name="VietinBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="ICBVVNVX",
        keywords="viettin"
    ),
    BankKey.VIKKI: Bank(
        key=BankKey.VIKKI,
        code=BankCode.VIKKI,
        name="Ngân hàng TNHH MTV Số Vikki",
        bin="970406",
        short_name="Vikki Bank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="EACBVNVX",
        keywords="vikki, dongabank, dong a"
    ),
    BankKey.VPBANK: Bank(
        key=BankKey.VPBANK,
        code=BankCode.VPBANK,
        name="Ngân hàng TMCP Việt Nam Thịnh Vượng",
        bin="970432",
        short_name="VPBank",
        viet_qr_status=VietQRStatus.TRANSFER_SUPPORTED,
        lookup_supported=1,
        swift_code="VPBKVNVX",
        keywords="vnthinhvuong"
    ),
    BankKey.VRB: Bank(
        key=BankKey.VRB,
        code=BankCode.VRB,
        name="Ngân hàng Liên doanh Việt - Nga",
        bin="970421",
        short_name="VietNgaBank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code=None,
        keywords="vietnam-russia, vrbank"
    ),
    BankKey.WOORI_BANK: Bank(
        key=BankKey.WOORI_BANK,
        code=BankCode.WOORI_BANK,
        name="Ngân hàng TNHH MTV Woori Việt Nam",
        bin="970457",
        short_name="Woori Bank",
        viet_qr_status=VietQRStatus.RECEIVE_ONLY,
        lookup_supported=1,
        swift_code=None
    )
}