from bs4 import BeautifulSoup
import pytest
from unittest.mock import patch

from sagikoza import core

@pytest.fixture
def k_pubstype_01_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_01_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_01_detail_1(k_pubstype_01_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_01_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2505-9900-0335",
            "pn": "375438",
            "p_id": "03",
            "re": "0",
            "doc_id": "15931",
            "referer": '0',
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 3
        
        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '15931-2505-9900-0335-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'branch_name': '二二八', 
            'branch_code': '228', 
            'account_type': '普通預金', 
            'account': '3084648', 
            'name': 'リードバンク（ド', 
            'amount': '853305', 
            'effective_from': '2025年6月3日 0時', 
            'effective_to': '2025年8月4日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '2024年10月21日', 
            'notes': '', 
            'branch_code_jpb': '12250',
            'account_jpb': '30846481',
            'name_alias': 'リードバンク 合同会社',
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            "doc_id": "15931",
            'referer': '0'
        }
        assert result[0] == expected

        # 青木信用金庫ケースの確認
        expected = {
            'uid': '15931-2505-9900-0335-2',
            'seq_no': '2',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': '青木信用金庫', 
            'branch_name': '越谷支店', 
            'branch_code': '014', 
            'account_type': '普通預金', 
            'account': '5032277', 
            'name': 'カ）パレット', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            "doc_id": "15931",
            'referer': '0'
        }
        assert result[1] == expected

        # 京葉銀行ケースの確認
        expected = {
            'uid': '15931-2505-9900-0335-3',
            'seq_no': '3',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': '京葉銀行', 
            'branch_name': '鎌取支店', 
            'branch_code': '418', 
            'account_type': '普通預金', 
            'account': '5569011', 
            'name': 'ド）シュガーラッシュ', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '２０２４年１０月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-9900-0335', 
            'pn': '375438', 
            'p_id': '03', 
            're': '0', 
            "doc_id": "15931",
            'referer': '0'
        }
        assert result[2] == expected

@pytest.fixture
def k_pubstype_01_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_01_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_01_detail_2(k_pubstype_01_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_01_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2506-0001-0894",
            "pn": "375331",
            "p_id": "03",
            "re": "0",
            "doc_id": "15937",
            "referer": '1'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        
        # みずほ銀行（外国人）ケースの確認
        expected = {
            'uid': '15937-2506-0001-0894-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '山形支店', 
            'branch_code': '728', 
            'account_type': '普通預金', 
            'account': '3056028', 
            'name': 'ＰＨＡＭ ＶＡＮ ＭＡＮＨ （フアン ヴアン マイン）', 
            'amount': '2599', 
            'effective_from': '2025年6月17日 0時', 
            'effective_to': '2025年8月18日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '2024年08月頃', 
            'suspend_date': '2024年8月16日', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2506-0001-0894', 
            'pn': '375331', 
            'p_id': '03', 
            're': '0', 
            "doc_id": "15937",
            'referer': '1'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_01_detail_3():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_01_detail_3.html", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_01_detail_3(k_pubstype_01_detail_3):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_01_detail_3, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2505-0543-0040",
            "pn": "369281",
            "p_id": "01",
            "re": "0",
            "doc_id": "15442",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 3
        
        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '15442-2505-0543-0040-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': '名古屋銀行', 
            'branch_name': '安城支店', 
            'branch_code': '287', 
            'account_type': '普通預金', 
            'account': '3438687', 
            'name': 'サワイ ケイコ', 
            'amount': '3021', 
            'effective_from': '2025年6月3日 0時', 
            'effective_to': '2025年8月4日 15時', 
            'effective_method': '所定の届出書を提出（詳細は照会先へご連絡下さい）', 
            'payment_period': '2025年2月', 
            'suspend_date': '2025年2月20日', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-0543-0040', 
            'pn': '369281', 
            'p_id': '01', 
            're': '0', 
            "doc_id": "15442",
            'referer': '0'
        }
        assert result[0] == expected

        # 異常値ケースの確認
        expected = {
            'uid': '15442-2505-0543-0040-2',
            'seq_no': '2',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'branch_name': '四〇八', 
            'branch_code': '408', 
            'account_type': '14000　　　　普通預金', 
            'account': '7555041 755504', 
            'name': 'ミヤモト マサユキ', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '2025年2月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-0543-0040', 
            'pn': '369281', 
            'p_id': '01', 
            're': '0', 
            "doc_id": "15442",
            'referer': '0'
        }
        assert result[1] == expected

        # 異常値ケースの確認
        expected = {
            'uid': '15442-2505-0543-0040-3',
            'seq_no': '3',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'branch_name': '四〇八', 
            'branch_code': '408', 
            'account_type': '14060　　　　普通預金', 
            'account': '14881151 1488115', 
            'name': 'ミヤモト マサユキ', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '2025年2月', 
            'suspend_date': '', 
            'notes': '', 
            'form': 'k_pubstype_01_detail.php', 
            'no': '2505-0543-0040', 
            'pn': '369281', 
            'p_id': '01', 
            're': '0', 
            "doc_id": "15442",
            'referer': '0'
        }
        assert result[2] == expected

@pytest.fixture
def k_pubstype_04_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_04_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_04_detail_1(k_pubstype_04_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_04_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_04_detail.php",
            "no": "2503-9900-0475",
            "pn": "368470",
            "p_id": "05",
            "re": "0",
            "doc_id": "15606",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        
        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '15606-2503-9900-0475-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る',
            'bank_name': 'ゆうちょ銀行',
            'branch_name': '五一八',
            'branch_code': '518',
            'account_type': '普通預金',
            'account': '6211644', 
            'name': 'フャン ティ カイン リー', 
            'amount': '602827', 
            'notice_date': '2025年5月1日',
            'notes': '法第六条第一項（権利行使の届出等あり）',
            'branch_code_jpb': '15150',
            'account_jpb': '62116441',
            'name_alias': 'ＰＨＡＮ ＴＨＩ ＫＨＡＮＨ ＬＹ',
            "form": "k_pubstype_04_detail.php",
            "no": "2503-9900-0475",
            "pn": "368470",
            "p_id": "05",
            "re": "0",
            "doc_id": "15606",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_04_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_04_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_04_detail_2(k_pubstype_04_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_04_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_04_detail.php",
            "no": "2507-0310-0051",
            "pn": "372840",
            "p_id": "05",
            "re": "0",
            "doc_id": "15842",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1
        
        # ＧＭＯあおぞらネット銀行ケースの確認
        expected = {
            'uid': '15842-2507-0310-0051-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ＧＭＯあおぞらネット銀行', 
            'branch_name': 'フリー支店', 
            'branch_code': '125', 
            'account_type': '普通預金', 
            'account': '1121426', 
            'name': 'カ）フアイナンシヤルラグジユアリ－', 
            'amount': '8676', 
            'notice_date': '2025年7月1日',
            'notes': '法第六条第一項（権利行使の届出等あり）',
            "form": "k_pubstype_04_detail.php",
            "no": "2507-0310-0051",
            "pn": "372840",
            "p_id": "05",
            "re": "0",
            "doc_id": "15842",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_05_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_05_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_05_detail_1(k_pubstype_05_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_05_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_05_detail.php",
            "no": "2503-9900-0011",
            "pn": "373302",
            "p_id": "07",
            "re": "0",
            "doc_id": "15802",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # みずほ銀行ケースの確認
        expected = {
            'uid': '15802-2503-9900-0011-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'name': 'ＢＵＩ ＶＡＮ ＢＩＮＨ（ブイ ウ゛ァン ビン）', 
            'amount': '773', 
            'notice_date': '2025年5月1日',
            'delete_date': '2025年7月1日',
            'branch_code_jpb': '19730',
            'account_jpb': '16099061',
            "form": "k_pubstype_05_detail.php",
            "no": "2503-9900-0011",
            "pn": "373302",
            "p_id": "07",
            "re": "0",
            "doc_id": "15802",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_05_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_05_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_05_detail_2(k_pubstype_05_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_05_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_05_detail.php",
            "no": "2502-0001-0034",
            "pn": "371209",
            "p_id": "07",
            "re": "0",
            "doc_id": "15712",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # みずほ銀行ケースの確認
        expected = {
            'uid': '15712-2502-0001-0034-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '春日部支店', 
            'branch_code': '223', 
            'account_type': '普通預金', 
            'account': '3075321', 
            'name': 'ＰＲＥＳＥＮＴＡＣＩＯＮ ＡＬＩＣＥ ＶＩＣＴＯＲＩＡ （プレセンタシオン アリス ヴイクトリア）', 
            'amount': '151797', 
            'notice_date': '2025年4月16日',
            'delete_date': '2025年6月16日',
            "form": "k_pubstype_05_detail.php",
            "no": "2502-0001-0034",
            "pn": "371209",
            "p_id": "07",
            "re": "0",
            "doc_id": "15712",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_07_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_07_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_07_detail_1(k_pubstype_07_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_07_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "doc_id": "15713",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 2

        # 三菱ＵＦＪ銀行ケースの確認
        expected = {
            'uid': '15713-2502-0005-0027-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': '三菱ＵＦＪ銀行', 
            'branch_name': '町田支店', 
            'branch_code': '228', 
            'account_type': '普通預金', 
            'account': '2549964', 
            'name': 'グエン ダン ビン', 
            'amount': '22004', 
            'effective_from': '2025年7月17日 0時', 
            'effective_to': '2025年10月15日 15時', 
            'effective_method': '被害回復分配金支払申請書を店頭に提出又は郵送（詳細は照会先へご連絡下さい）', 
            'payment_period': '2024年5月頃', 
            'suspend_date': '2025年7月1日', 
            'reason': 'オレオレ詐欺',
            'notes': '', 
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "doc_id": "15713",
            "referer": '0'
        }
        assert result[0] == expected

        # 資金の移転元となった預金口座等に係る
        expected = {
            'uid': '15713-2502-0005-0027-2',
            'seq_no': '2',
            'role': '資金の移転元となった預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '柏支店', 
            'branch_code': '329', 
            'account_type': '普通預金', 
            'account': '4157068', 
            'name': 'ＥＢＡＲＤＡＬＯＺＡ ＶＥＲＥＧＩＬＩＯ', 
            'amount': '', 
            'effective_from': '', 
            'effective_to': '', 
            'effective_method': '', 
            'payment_period': '2024年5月頃', 
            'suspend_date': '', 
            'reason': 'オレオレ詐欺',
            'notes': '', 
            "form": "k_pubstype_07_detail.php",
            "no": "2502-0005-0027",
            "pn": "373593",
            "p_id": "08",
            "re": "0",
            "doc_id": "15713",
            "referer": '0'
        }
        assert result[1] == expected

@pytest.fixture
def k_pubstype_09_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_09_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_09_detail_1(k_pubstype_09_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_09_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_09_detail.php",
            "no": "2411-0038-0042",
            "pn": "370345",
            "p_id": "12",
            "re": "0",
            "doc_id": "15692",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # 住信ＳＢＩネット銀行ケースの確認
        expected = {
            'uid': '15692-2411-0038-0042-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': '住信ＳＢＩネット銀行', 
            'branch_name': '法人第一支店', 
            'branch_code': '106', 
            'account_type': '普通預金', 
            'account': '2088276', 
            'name': 'ド） エース', 
            'amount': '237019', 
            'notes': '', 
            "form": "k_pubstype_09_detail.php",
            "no": "2411-0038-0042",
            "pn": "370345",
            "p_id": "12",
            "re": "0",
            "doc_id": "15692",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_10_detail_1():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_10_detail_1.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_10_detail_1(k_pubstype_10_detail_1):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_10_detail_1, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_10_detail.php",
            "no": "2415-9900-0114",
            "pn": "371720",
            "p_id": "11",
            "re": "0",
            "doc_id": "15707",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '15707-2415-9900-0114-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'ゆうちょ銀行', 
            'name': 'ＴＲＡＮ ＶＡＮ ＣＡＮＨ（チャン ウ゛ァン カイン）', 
            'amount': '20153', 
            'notice_date': '2025年1月16日',
            'branch_code_jpb': '10330',
            'account_jpb': '89857121',
            "form": "k_pubstype_10_detail.php",
            "no": "2415-9900-0114",
            "pn": "371720",
            "p_id": "11",
            "re": "0",
            "doc_id": "15707",
            "referer": '0'
        }
        assert result[0] == expected

@pytest.fixture
def k_pubstype_10_detail_2():
    # テスト用HTMLを読み込む
    with open("test/pages/k_pubstype_10_detail_2.php", encoding="utf-8") as f:
        return f.read()

def test_k_pubstype_10_detail_2(k_pubstype_10_detail_2):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(k_pubstype_10_detail_2, "html.parser")
        mock_fetch_html.return_value = mock_soup
        subject = {
            "form": "k_pubstype_10_detail.php",
            "no": "2412-0001-0028",
            "pn": "369725",
            "p_id": "11",
            "re": "0",
            "doc_id": "15643",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        assert isinstance(result, list)
        assert len(result) == 1

        # ゆうちょ銀行ケースの確認
        expected = {
            'uid': '15643-2412-0001-0028-1',
            'seq_no': '1',
            'role': '対象預金口座等に係る', 
            'bank_name': 'みずほ銀行', 
            'branch_name': '赤羽支店', 
            'branch_code': '203', 
            'account_type': '普通預金', 
            'account': '3118190', 
            'name': 'ＮＧＵＹＥＮ ＴＨＩ ＨＯＡＩ ＮＨＩＥＮ （グエン テイ ホアイ ニエン）', 
            'amount': '450709', 
            'notice_date': '2024年12月2日',
            "form": "k_pubstype_10_detail.php",
            "no": "2412-0001-0028",
            "pn": "369725",
            "p_id": "11",
            "re": "0",
            "doc_id": "15643",
            "referer": '0'
        }
        assert result[0] == expected