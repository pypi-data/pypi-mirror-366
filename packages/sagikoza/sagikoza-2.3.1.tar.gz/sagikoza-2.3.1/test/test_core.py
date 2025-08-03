import pytest
from sagikoza import core
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

@pytest.fixture
def sel_pubs_html():
    # テスト用HTMLを読み込む
    with open("test/pages/sel_pubs.php", encoding="utf-8") as f:
        return f.read()

def test_sel_pubs(sel_pubs_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(sel_pubs_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        result = core._sel_pubs("near3")
        assert isinstance(result, list)
        assert len(result) == 195
        # 指定した辞書が含まれるかどうか
        expected = {
            'notice_round': '24年度第20回', 
            'notice_type': '権利行使の届出等',
            'notice_number': '公告（07）第043号',
            'notice_date': '令和７年４月２３日',
            'doc_id': '15362'
        }
        assert result[1] == expected
        # 指定した辞書が含まれるかどうか
        expected_without_bracket = {
            'notice_round': '25年度第03回', 
            'notice_type': '債権消滅',
            'notice_number': '公告（07）第072号',
            'notice_date': '令和７年５月１日',
            'doc_id': '15402'
        }
        assert result[100] == expected_without_bracket

def test_sel_pubs_empty():
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_fetch_html.return_value = BeautifulSoup("<html></html>", "html.parser")
        result = core._sel_pubs("near3")
        assert result == []

def test_sel_pubs_exception():
    with patch("sagikoza.core.fetch_html", side_effect=core.FetchError("fail")):
        with pytest.raises(core.FetchError):
            core._sel_pubs("near3")

@pytest.fixture
def pubs_dispatcher_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubs_dispatcher.php", encoding="utf-8") as f:
        return f.read()

def test_pubs_dispatcher(pubs_dispatcher_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubs_dispatcher_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        notice = {'doc_id': '15362'}
        result = core._pubs_dispatcher(notice)
        assert isinstance(result, list)
        assert len(result) == 8
        # 指定した辞書が含まれるかどうか
        expected = {
            'inst_code': '0310', 
            'p_id': '03', 
            'pn': '365699', 
            're': '0', 
            'params': 'inst_code=0310&p_id=03&pn=365699&re=0', 
            'doc_id': '15362'
        }
        assert result[6] == expected

def test_pubs_dispatcher_empty():
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_fetch_html.return_value = BeautifulSoup("<html></html>", "html.parser")
        notice = {'doc_id': '15362'}
        result = core._pubs_dispatcher(notice)
        # リファクタリング後は空の場合エラーメッセージが返される
        assert len(result) == 1
        # 指定した辞書が含まれるかどうか
        expected = {'doc_id': '15362', 'error': 'No submit found'}
        assert result[0] == expected

def test_pubs_dispatcher_exception():
    with patch("sagikoza.core.fetch_html", side_effect=core.FetchError("fail")):
        notice = {'doc_id': '15362'}
        with pytest.raises(core.FetchError):
            core._pubs_dispatcher(notice)

@pytest.fixture
def pubs_basic_frame_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubs_basic_frame.php", encoding="utf-8") as f:
        return f.read()

def test_pubs_basic_frame(pubs_basic_frame_html):
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_soup = BeautifulSoup(pubs_basic_frame_html, "html.parser")
        mock_fetch_html.return_value = mock_soup
        submit = {'params': 'inst_code=0034&p_id=03&pn=365600&re=0'}
        result = core._pubs_basic_frame(submit)
        assert isinstance(result, list)
        assert len(result) == 94
        # 指定した辞書が含まれるかどうか
        expected = {
            'form': 'k_pubstype_01_detail.php', 
            'no': '2421-0034-0004', 
            'params': 'inst_code=0034&p_id=03&pn=365600&re=0'
        }
        assert result[3] == expected

def test_pubs_basic_frame_empty():
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_fetch_html.return_value = BeautifulSoup("<html></html>", "html.parser")
        submit = {'params': 'inst_code=0034&p_id=03&pn=365600&re=0'}
        result = core._pubs_basic_frame(submit)
        expected = {
            'error': 'No subjects found for submit params=inst_code=0034&p_id=03&pn=365600&re=0', 
            'params': 'inst_code=0034&p_id=03&pn=365600&re=0'
        }
        assert result[0] == expected

def test_pubs_basic_frame_exception():
    with patch("sagikoza.core.fetch_html", side_effect=core.FetchError("fail")):
        submit = {'params': 'inst_code=0034&p_id=03&pn=365600&re=0'}
        with pytest.raises(core.FetchError):
            core._pubs_basic_frame(submit)

def test_pubstype_detail_empty():
    with patch("sagikoza.core.fetch_html") as mock_fetch_html:
        mock_fetch_html.return_value = BeautifulSoup("<html></html>", "html.parser")
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2421-0034-0004",
            "pn": "365600",
            "p_id": "0034",
            "re": "0",
            "doc_id": "12345",
            "referer": '0'
        }
        result = core._pubstype_detail(subject)
        expected = {
            'error': 'No accounts found for subject no=2421-0034-0004',
            'uid': '12345-2421-0034-0004-0',
            "form": "k_pubstype_01_detail.php",
            "no": "2421-0034-0004",
            "pn": "365600",
            "p_id": "0034",
            "re": "0",
            "doc_id": "12345",
            "referer": '0'
        }
        assert result[0] == expected

def test_pubstype_detail_exception():
    with patch("sagikoza.core.fetch_html", side_effect=core.FetchError("fail")):
        subject = {
            "form": "k_pubstype_01_detail.php",
            "no": "2421-0034-0004",
            "pn": "365600",
            "p_id": "0034",
            "re": "0",
            "referer": '0'
        }
        with pytest.raises(core.FetchError):
            core._pubstype_detail(subject)

def test_fetch_empty():
    with patch("sagikoza.core._sel_pubs", return_value=[]):
        result = core.fetch("near3")
        assert result == []

@pytest.fixture
def pubs_basic_frame_pagination_html():
    # テスト用HTMLを読み込む
    with open("test/pages/pubs_basic_frame_pagination.php", encoding="utf-8") as f:
        return f.read()

def test_create_pagination_list_with_pagination(pubs_basic_frame_pagination_html):
    from sagikoza.parser.pubs_basic_frame import create_pagination_list
    soup = BeautifulSoup(pubs_basic_frame_pagination_html, "html.parser")
    result = create_pagination_list(soup)
    # 2から23までの数字のリストが返される（range(2, 24)は2から23まで）
    expected = list(range(2, 24))
    assert result == expected

def test_create_pagination_list_no_pagination(pubs_basic_frame_html):
    from sagikoza.parser.pubs_basic_frame import create_pagination_list
    soup = BeautifulSoup(pubs_basic_frame_html, "html.parser")
    result = create_pagination_list(soup)
    # ページネーションがない場合は空のリストが返される
    assert result == []