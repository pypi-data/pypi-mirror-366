"""
Core module for sagikoza library - Refactored version.

This module provides functions to fetch public notices under Japan's Furikome Sagi Relief Act.
Supports both full data extraction and incremental updates.
"""

import logging
from typing import Literal, Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from time import sleep
from dataclasses import dataclass
from enum import Enum

from bs4 import BeautifulSoup
import requests

from sagikoza.parser.sel_pubs import parse_notices
from sagikoza.parser.pubs_dispatcher import parse_submit
from sagikoza.parser.pubs_basic_frame import parse_subject, create_pagination_list
from sagikoza.parser.pubstype_detail import parse_accounts
from sagikoza.normalize import normalize_accounts

# Constants
DOMAIN = "https://furikomesagi.dic.go.jp"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}
DEFAULT_TIMEOUT = 5.0
DEFAULT_MAX_WORKERS = 5
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

logger = logging.getLogger(__name__)

# Global session
SESSION = requests.Session()
SESSION.trust_env = False
SESSION.headers.update(DEFAULT_HEADERS)


class ErrorType(Enum):
    """エラーの種類を定義する列挙型."""
    NETWORK = "network"
    HTTP = "http"
    TIMEOUT = "timeout"
    PARSE = "parse"
    VALIDATION = "validation"


@dataclass
class ProcessingStats:
    """処理統計データクラス."""
    total: int
    successful: int
    failed: int
    
    @property
    def success_rate(self) -> float:
        """成功率を計算."""
        return self.successful / self.total if self.total > 0 else 0.0


class SagiKozaError(Exception):
    """Base exception for sagikoza library."""
    def __init__(self, message: str, error_type: ErrorType = ErrorType.NETWORK):
        super().__init__(message)
        self.error_type = error_type


class FetchError(SagiKozaError):
    """Exception for HTML fetch errors."""
    pass


class ValidationError(SagiKozaError):
    """Exception for data validation errors."""
    def __init__(self, message: str):
        super().__init__(message, ErrorType.VALIDATION)


def validate_year_parameter(year: str) -> str:
    """年パラメータの妥当性を検証."""
    if not isinstance(year, str):
        raise ValidationError(f"Year must be a string, got {type(year)}")
    
    if year == "near3":
        return year
    
    # 年形式の基本的な検証
    if len(year) == 4 and year.isdigit():
        year_int = int(year)
        if 2008 <= year_int <= 2025:  # 合理的な年の範囲
            return year

    raise ValidationError(f"Invalid year format: {year}. Expected 'near3' or YYYY format (2008-2025)")


def validate_required_fields(data: Dict[str, Any], required_fields: List[str], context: str = "") -> None:
    """必須フィールドの存在を検証."""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        context_str = f" in {context}" if context else ""
        raise ValidationError(f"Missing required fields {missing_fields}{context_str}: {data}")


def retry_on_error(max_retries: int = DEFAULT_MAX_RETRIES, delay: float = DEFAULT_RETRY_DELAY):
    """関数の失敗時にリトライを行うデコレータ。重複エラーメッセージは抑制される。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            error_logged = set()
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    err_msg = str(e)
                    
                    # 同じエラーメッセージは一回だけログに記録
                    if err_msg not in error_logged:
                        if attempt < max_retries - 1:
                            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}")
                        else:
                            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
                        error_logged.add(err_msg)
                    else:
                        if attempt < max_retries - 1:
                            logger.debug(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e} (suppressed duplicate error)")
                    
                    if attempt < max_retries - 1:
                        sleep(delay * (2 ** attempt))
            
            raise last_exception
        return wrapper
    return decorator


def process_items_with_error_handling(
    items: List[Dict[str, Any]], 
    processor_func: callable, 
    item_name: str,
    max_workers: int = DEFAULT_MAX_WORKERS
) -> tuple[List[Dict[str, Any]], ProcessingStats]:
    """エラーハンドリングとロギングを備えたマルチスレッド処理でアイテムのリストを処理する。"""
    results = []
    successful = 0
    failed = 0
    
    if not items:
        logger.debug(f"No {item_name}s to process")
        return results, ProcessingStats(0, 0, 0)
    
    logger.debug(f"Processing {len(items)} {item_name}s with {max_workers} workers")
    
    # ThreadPoolExecutorを使用して並列処理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 全てのタスクを投入
        future_to_item = {executor.submit(processor_func, item): item for item in items}
        
        # 完了したタスクを処理
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                processed = future.result()
                if processed:  # 空でない結果のみ追加
                    results.extend(processed)
                successful += 1
                logger.debug(f"Successfully processed {item_name}: {item.get('doc_id', item.get('no', 'unknown'))}")
            except Exception as e:
                failed += 1
                logger.error(f"Error processing {item_name}: {item} | {e}")
    
    stats = ProcessingStats(len(items), successful, failed)
    logger.debug(f"Processed {stats.total} {item_name}s: {stats.successful} successful, {stats.failed} failed (success rate: {stats.success_rate:.2%})")
    
    return results, stats


@retry_on_error(max_retries=DEFAULT_MAX_RETRIES, delay=DEFAULT_RETRY_DELAY)
def fetch_html(
    url: str,
    method: Literal['GET', 'POST'] = 'GET',
    data: Optional[Dict[str, Any]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> BeautifulSoup:
    """
    HTMLを取得しBeautifulSoupオブジェクトを返す。

    Args:
        url: 対象URL
        method: HTTPメソッド ('GET' または 'POST')
        data: GETのパラメータまたはPOSTのボディ
        timeout: リクエストタイムアウト（秒）

    Raises:
        FetchError: ネットワーク、HTTP、またはタイムアウトエラー時
    """
    logger.debug(f"Fetching HTML: url={url}, method={method}, data={data}")
    
    try:
        if method == 'GET':
            resp = SESSION.get(url, params=data, timeout=timeout)
        else:
            resp = SESSION.post(url, data=data, timeout=timeout)
            resp.encoding = resp.apparent_encoding
        
        resp.raise_for_status()
        
    except requests.exceptions.Timeout as e:
        logger.warning(f'Timeout error fetching HTML from {url}: {e}')
        raise FetchError(f'Request timeout for {url}', ErrorType.TIMEOUT) from e
    except requests.exceptions.ConnectionError as e:
        logger.warning(f'Connection error fetching HTML from {url}: {e}')
        raise FetchError(f'Connection failed for {url}', ErrorType.NETWORK) from e
    except requests.exceptions.HTTPError as e:
        logger.warning(f'HTTP error fetching HTML from {url}: {e}')
        raise FetchError(f'HTTP error {resp.status_code} for {url}', ErrorType.HTTP) from e
    except requests.exceptions.RequestException as e:
        logger.warning(f'Request error fetching HTML from {url}: {e}')
        raise FetchError(f'Failed to fetch HTML from {url}', ErrorType.NETWORK) from e
    
    return BeautifulSoup(resp.text, 'html.parser')


def _generate_uid(data: Dict[str, Any]) -> str:
    """
    データ辞書からUIDを生成する。
    
    Args:
        data: doc_id, no, seq_noを含むデータ辞書
        
    Returns:
        doc_id-no-seq_no形式のUID文字列
        
    Note:
        - noが空白の場合は '0000-0000-0000' を使用
        - seq_noが空白の場合は '0' を使用
    """
    doc_id = data.get('doc_id', '')
    no_value = data.get('no', '').strip() or '0000-0000-0000'
    seq_no_value = str(data.get('seq_no', '')).strip() or '0'
    return f"{doc_id}-{no_value}-{seq_no_value}"


def _sel_pubs(year: str = "near3") -> List[Dict[str, Any]]:
    """指定された年の公告通知を取得する。"""
    year = validate_year_parameter(year)
    logger.debug(f"Getting publication notices for year={year}")

    url = f"{DOMAIN}/sel_pubs.php"
    payload = {
        "search_term": year,
        "search_no": "none",
        "search_pubs_type": "none",
        "sort_id": "5"
    }
    
    try:
        soup = fetch_html(url, "POST", payload)
        notices = parse_notices(soup)
        
        if not notices:
            logger.warning(f"No notices found for year={year}")
        else:
            logger.debug(f"Fetched {len(notices)} notices for year={year}")

        return notices
    except Exception as e:
        logger.error(f"Exception in _sel_pubs: {e} | year={year}")
        raise


def _pubs_dispatcher(notice: Dict[str, Any]) -> List[Dict[str, Any]]:
    """通知の公告詳細を取得する。"""
    # エラーキーがある場合は直接返す
    if "error" in notice:
        return [notice]
    
    validate_required_fields(notice, ['doc_id'], 'notice')
    doc_id = notice['doc_id']
    
    logger.debug(f"Getting publication details for notice doc_id={doc_id}")
    
    url = f"{DOMAIN}/pubs_dispatcher.php"
    payload = {"head_line": "", "doc_id": doc_id}
    
    try:
        soup = fetch_html(url, "POST", payload)
        details = parse_submit(soup)
        
        if not details:
            details = [{'error': 'No submit found'}]
            logger.warning(f"No submit details found for doc_id={doc_id}")
        else:
            logger.debug(f"Fetched {len(details)} details for doc_id={doc_id}")
        
        return [{**detail, **notice} for detail in details]
    except Exception as e:
        logger.error(f"Exception in _pubs_dispatcher: {e} | notice={notice}")
        raise


def _pubs_basic_frame(submit: Dict[str, Any]) -> List[Dict[str, Any]]:
    """投稿の基本公告情報を取得する。"""
    # エラーキーがある場合は直接返す
    if "error" in submit:
        return [submit]
    
    validate_required_fields(submit, ['params'], 'submit')
    params = submit['params']
    
    logger.debug(f"Getting basic publication info for submit params={params}")
    
    url = f"{DOMAIN}/pubs_basic_frame.php"
    
    try:
        soup = fetch_html(url, "GET", submit['params'])
        details = parse_subject(soup)
        # Pagination handling
        for page in create_pagination_list(soup):
            soup = fetch_html(url, "GET", submit['params'] + f"&page={page}")
            details.extend(parse_subject(soup))

        if not details:
            details = [{"error": f"No subjects found for submit params={params}"}]
            logger.warning(f"No subjects found for submit params={params}")
        else:
            logger.debug(f"Fetched {len(details)} subjects for submit params={params}")
        
        return [{**detail, **submit} for detail in details]
    except Exception as e:
        logger.error(f"Exception in _pubs_basic_frame: {e} | submit={submit}")
        raise


def _pubstype_detail(subject: Dict[str, Any]) -> List[Dict[str, Any]]:
    """件名の口座詳細を取得する。"""
    # エラーキーがある場合は直接返す
    if "error" in subject:
        return [subject]
    
    validate_required_fields(subject, ['form', 'no'], 'subject')
    form = subject['form']
    no = subject['no']
    
    logger.debug(f"Getting account details for subject no={no}, form={form}")
    
    url = f"{DOMAIN}/" + form
    payload = {
        "r_no": no,
        "pn": subject.get('pn', ''),
        "p_id": subject.get('p_id', ''),
        "re": subject.get('re', ''),
        "referer": '0'
    }
    
    try:
        soup = fetch_html(url, "POST", payload)
        details = parse_accounts(soup, form)
        
        if not details:
            details = [{"error": f"No accounts found for subject no={no}"}]
            logger.warning(f"No accounts found for subject no={no}")
        else:
            logger.debug(f"Fetched {len(details)} accounts for subject no={no}")
        
        # UIDを生成して各詳細に追加
        result = []
        for detail in details:
            combined = {**detail, **subject}
            combined['uid'] = _generate_uid(combined)
            result.append(combined)
        
        return result
    except Exception as e:
        logger.error(f"Exception in _pubstype_detail: {e} | subject={subject}")
        raise


def fetch(year: str = "near3", normalize: bool = False, max_workers: int = DEFAULT_MAX_WORKERS) -> List[Dict[str, Any]]:
    """
    指定された年のすべての公告データを取得する。
    
    Args:
        year: データを取得する年、または最新3か月の場合は "near3"
        max_workers: 並列処理の最大スレッド数
        
    Returns:
        完全な情報を含む口座辞書のリスト
        
    Raises:
        ValidationError: 無効なパラメータの場合
        FetchError: データ取得エラーの場合
    """
    year = validate_year_parameter(year)
    
    if max_workers < 1:
        raise ValidationError(f"max_workers must be >= 1, got {max_workers}")
    
    logger.info(f"Starting fetch for year={year} with max_workers={max_workers}")
    
    try:
        # ステップ 1: 通知取得
        notices = _sel_pubs(year)
        if not notices:
            logger.warning(f"No notices found for year={year}")
            return []
        
        # ステップ 2: エラーハンドリングと並列処理で投稿取得
        submits, submits_stats = process_items_with_error_handling(
            notices, _pubs_dispatcher, "notice", max_workers
        )
        logger.info(f"Total submits fetched: {len(submits)}")
        
        # ステップ 3: エラーハンドリングと並列処理で件名取得
        subjects, subjects_stats = process_items_with_error_handling(
            submits, _pubs_basic_frame, "submit", max_workers
        )
        logger.info(f"Total subjects fetched: {len(subjects)}")
        
        # ステップ 4: エラーハンドリングと並列処理で口座取得
        accounts, accounts_stats = process_items_with_error_handling(
            subjects, _pubstype_detail, "subject", max_workers
        )
        logger.info(f"Total accounts fetched: {len(accounts)}")
        
        # ステップ 5: 取得データの正規化
        if normalize:
            accounts, records_stats = process_items_with_error_handling(
                accounts, normalize_accounts, "accounts", max_workers * 2
            )
            logger.info(f"Total normalized records: {len(accounts)}")

        # 処理統計をログ出力
        logger.info(f"Processing summary for year={year}:")
        logger.info(f"  Notices: {len(notices)}")
        logger.info(f"  Submits: {submits_stats.successful}/{submits_stats.total} (success rate: {submits_stats.success_rate:.2%})")
        logger.info(f"  Subjects: {subjects_stats.successful}/{subjects_stats.total} (success rate: {subjects_stats.success_rate:.2%})")
        logger.info(f"  Accounts: {accounts_stats.successful}/{accounts_stats.total} (success rate: {accounts_stats.success_rate:.2%})")
        if normalize:
            logger.info(f"  Normalized: {records_stats.successful}/{records_stats.total} (success rate: {records_stats.success_rate:.2%})")

        logger.info(f"Fetch completed for year={year}")

        return accounts

    except Exception as e:
        logger.error(f"Exception in fetch: {e} | year={year}")
        raise

if __name__ == "__main__":
    import pandas as pd
    
    # ログレベルを設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s'
    )
    
    try:
        data = fetch("near3", normalize=True)
        df = pd.DataFrame(data)
        df.to_parquet("accounts.parquet", index=False)
        print(f"Successfully saved {len(data)} records to accounts.parquet")
    except Exception as e:
        print(f"Error: {e}")
        raise