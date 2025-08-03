from typing import Any, Dict, List
import unicodedata
import re
from jpdatetime import jpdatetime

# 正規表現パターンをコンパイル（パフォーマンス向上）
LONG_VOWEL_PATTERN = re.compile(r'[-˗ᅳ᭸‐‑‒–—―⁃⁻−▬─━➖ーㅡ﹘﹣－ｰ𐄐𐆑]')
NAME_SPLIT_PATTERN = re.compile(r'^([A-Za-z0-9 ]+)\s*\（([\u30A0-\u30FF\s]{3,})\）$|^([\u30A0-\u30FF\s]{3,})\s*\（([A-Za-z0-9 ]+)\）$')
DATE_PATTERN = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
ACCOUNT_TYPE_BRACKET_PATTERN = re.compile(r'^([A-Za-z0-9]+)〔(.+)〕$')
ACCOUNT_BRACKET_PATTERN = re.compile(r'^([0-9]+)〔([0-9]+)〕$')

# 定数定義
NAME_FIELDS = ('name', 'name_alias')
DATE_FIELDS = ('notice_date', 'suspend_date', 'delete_date')
KANJI_DIGITS = {
    '0': '〇', '1': '一', '2': '二', '3': '三', '4': '四',
    '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
}

# Unicode正規化用の置換テーブル
UNICODE_REPLACEMENTS = [
    ('\u309B', '\u3099'),  # 濁点
    ('\u309C', '\u309A'),  # 半濁点
    ('(', '（'),
    (')', '）'),
    ('〔', '（'),
    ('〕', '）')
]


def _normalize_text_field(text: str) -> str:
    """テキストフィールドの正規化処理"""
    # 濁点と半濁点を合成可能な濁点と半濁点に標準化
    for old, new in UNICODE_REPLACEMENTS[:2]:
        text = text.replace(old, new)
    
    # 長音を標準化
    text = LONG_VOWEL_PATTERN.sub('ー', text)
    
    # 括弧以外の文字列を標準化
    text = unicodedata.normalize('NFKC', text)
    for old, new in UNICODE_REPLACEMENTS[2:]:
        text = text.replace(old, new)
    
    return text


def _process_name_field(account: Dict[str, Any]) -> None:
    """名前フィールドの処理（分割とエイリアス設定）"""
    name = account.get('name')
    if not isinstance(name, str):
        return
    
    match = NAME_SPLIT_PATTERN.match(name)
    if match:
        if match.group(1) and match.group(2):
            # パターン1: アルファベット名（日本語名）
            account['name'] = match.group(2).strip()
            account['name_alias'] = match.group(1).strip()
        elif match.group(3) and match.group(4):
            # パターン2: 日本語名（アルファベット名）
            account['name'] = match.group(3).strip()
            account['name_alias'] = match.group(4).strip()


def _convert_date_fields(account: Dict[str, Any]) -> None:
    """日付フィールドの変換処理"""
    for date_field in DATE_FIELDS:
        date_value = account.get(date_field)
        if not isinstance(date_value, str):
            continue
        
        try:
            match = DATE_PATTERN.match(date_value)
            if match:
                year, month, day = match.groups()
                account[date_field] = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        except (ValueError, AttributeError):
            # 日付変換に失敗した場合は元の値を保持
            continue


def _split_account_type_field(account: Dict[str, Any]) -> None:
    """口座タイプフィールドの分割処理（異常値修正対応）"""
    account_type = account.get('account_type')
    if not isinstance(account_type, str):
        return
    
    # 〔〕で囲まれたパターンをチェック
    bracket_match = ACCOUNT_TYPE_BRACKET_PATTERN.match(account_type)
    if bracket_match:
        account['branch_code_jpb'] = bracket_match.group(1).strip()
        account['account_type'] = bracket_match.group(2).strip()
        return
    
    # スペース区切りのパターンをチェック
    parts = account_type.split()
    if len(parts) == 2:
        account['branch_code_jpb'] = parts[0].strip()
        account['account_type'] = parts[1].strip()


def _split_account_field(account: Dict[str, Any]) -> None:
    """口座フィールドの分割処理"""
    account_value = account.get('account')
    if not isinstance(account_value, str):
        return
    
    # 〔〕で囲まれたパターンをチェック
    bracket_match = ACCOUNT_BRACKET_PATTERN.match(account_value)
    if bracket_match:
        account['account_jpb'] = bracket_match.group(1).strip().zfill(8)
        account['account'] = bracket_match.group(2).strip().zfill(7)
        return
    
    # スペース区切りのパターンをチェック
    parts = account_value.split()
    if len(parts) == 2:
        account['account_jpb'] = parts[0].strip().zfill(8)
        account['account'] = parts[1].strip().zfill(7)


def _process_jpb_branch_code(account: Dict[str, Any]) -> None:
    """ゆうちょ銀行支店コードの処理"""
    # 既に支店コードがある場合は処理しない
    if account.get('branch_code'):
        return
    
    branch_code_jpb = account.get('branch_code_jpb')
    if not branch_code_jpb or len(branch_code_jpb) < 3:
        return
    
    first_digit = branch_code_jpb[0]
    branch_code = ''
    
    if first_digit == '1':
        branch_code = f"{branch_code_jpb[1:3]}8"
        account['account_type'] = '普通預金'
    elif first_digit == '0':
        branch_code = f"{branch_code_jpb[1:3]}9"
        account['account_type'] = '振替口座'
    
    if branch_code:
        account['branch_code'] = branch_code.zfill(3)
        # 漢数字変換
        account['branch_name'] = ''.join(
            KANJI_DIGITS.get(digit, digit) for digit in account['branch_code']
        )


def _process_jpb_account_number(account: Dict[str, Any]) -> None:
    """ゆうちょ銀行口座番号の処理"""
    # 既に口座番号がある場合は処理しない
    if account.get('account'):
        return
    
    account_jpb = account.get('account_jpb')
    if account_jpb:
        account['account'] = account_jpb[:7].zfill(7)


def _process_notice_date(account: Dict[str, Any]) -> None:
    """通知日付の処理"""
    notice_date = account.get('notice_date')
    if isinstance(notice_date, str):
        try:
            account['notice_date'] = jpdatetime.strptime(notice_date, '%G年%m月%d日').strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            # 日付パース失敗時は元の値を保持
            pass


def normalize_accounts(account: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    口座データの正規化処理
    
    Args:
        account (Dict[str, Any]): 口座データの辞書
        
    Returns:
        List[Dict[str, Any]]: 正規化された口座データのリスト
    """
    if 'error' in account:
        return [account]  # エラーがある場合はそのまま返す

    # テキストフィールドの正規化
    for field in NAME_FIELDS:
        if field in account and isinstance(account[field], str):
            account[field] = _normalize_text_field(account[field])
    
    # 各種フィールドの処理
    _process_name_field(account)
    _convert_date_fields(account)
    _split_account_type_field(account)
    _split_account_field(account)
    _process_jpb_branch_code(account)
    _process_jpb_account_number(account)
    _process_notice_date(account)

    return [account]