"""
Parser for extracting account details from pubstype_detail pages.

This module parses account information from fraud relief public notice detail pages.
Supports different page types with specific parsing logic for each type.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import hashlib
import json


def parse_accounts(soup: BeautifulSoup, form: str) -> List[Dict[str, Any]]:
    """
    Parse account details from various types of pubstype_detail pages.
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        List of account dictionaries
    """
    try:
        if form == 'k_pubstype_01_detail.php':
            accounts = _parse_k_pubstype_01(soup)
        elif form == 'k_pubstype_04_detail.php':
            accounts = _parse_k_pubstype_04(soup)
        elif form == 'k_pubstype_05_detail.php':
            accounts = _parse_k_pubstype_05(soup)
        elif form == 'k_pubstype_07_detail.php':
            accounts = _parse_k_pubstype_07(soup)
        elif form == 'k_pubstype_09_detail.php':
            accounts = _parse_k_pubstype_09(soup)
        elif form == 'k_pubstype_10_detail.php':
            accounts = _parse_k_pubstype_10(soup)
        else:
            accounts = [{"error": f"Unknown form type: {form}"}]
    except Exception as e:
        return [{"error": f"Failed to parse account details: {str(e)}"}]

    return accounts

def _parse_k_pubstype_01(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Parse k_pubstype_01_detail pages - 消滅手続が開始された対象預金等債権"""
    accounts = []
    containers = soup.select('div.container')
    
    for i, container in enumerate(containers, start=1):
        account = {}

        # ゆうちょ銀行（テーブルが6つ）の場合、ゆうちょ銀行固有のテーブルを削除する
        if len(container.select('table')) == 6:
            # Create a temporary container for jpb_tables parsing
            jpb_container = BeautifulSoup('<div></div>', 'html.parser').div
            for table in container.select('table')[1:3]:
                jpb_container.append(table.extract())  # move table to jpb_container and remove from original
            # Extract specific fields for Japan Post Bank           
            account['branch_code_jpb'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(2) td.data')
            account['account_jpb'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(3) td.data')
            account['name_alias'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(4) td.data').replace('\u3000', ' ')

        # Extract
        account['seq_no'] = str(i)
        account['role'] = _parse(container, 'td.cat5').replace('■', '')
        account['bank_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(1) td.data')
        account['branch_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(2) td.data')
        account['branch_code'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(3) td.data')
        account['account_type'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(4) td.data')
        account['account'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(5) td.data')
        account['name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(6) td.data').replace('\u3000', ' ')
        account['amount'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(1) td.data2').replace(',', '')
        account['effective_from'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(3)')
        account['effective_to'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(5)')
        account['effective_method'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(3) td.data')
        account['payment_period'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(4) td.data')
        account['suspend_date'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(5) td.data')
        account['notes'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(7) td.data')

        accounts.append(account)
    
    return accounts

def _parse_k_pubstype_04(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Parse k_pubstype_04_detail pages - 消滅手続が終了した対象預金等債権"""
    accounts = []
    containers = soup.select('div.container')
    
    for i, container in enumerate(containers, start=1):
        account = {}

        # ゆうちょ銀行（テーブルが6つ）の場合、ゆうちょ銀行固有のテーブルを削除する
        if len(container.select('table')) == 6:
            # Create a temporary container for jpb_tables parsing
            jpb_container = BeautifulSoup('<div></div>', 'html.parser').div
            for table in container.select('table')[1:3]:
                jpb_container.append(table.extract())  # move table to jpb_container and remove from original
            # Extract specific fields for Japan Post Bank           
            account['branch_code_jpb'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(2) td.data')
            account['account_jpb'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(3) td.data')
            account['name_alias'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(4) td.data').replace('\u3000', ' ')

        # Extract
        account['seq_no'] = str(i)
        account['role'] = _parse(container, 'td.cat5').replace('■', '')
        account['bank_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(1) td.data')
        account['branch_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(2) td.data')
        account['branch_code'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(3) td.data')
        account['account_type'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(4) td.data')
        account['account'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(5) td.data')
        account['name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(6) td.data').replace('\u3000', ' ')
        account['amount'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(1) td.data2').replace(',', '')
        account['notice_date'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(2) td.data')
        account['notes'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(4) td.data')

        accounts.append(account)

    return accounts

def _parse_k_pubstype_05(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Parse k_pubstype_05_detail pages - 消滅手続が終了した対象預金等債権"""
    accounts = []
    containers = soup.select('div.container')
    
    for i, container in enumerate(containers, start=1):
        account = {}

        # Extract
        account['seq_no'] = str(i)
        account['role'] = _parse(container, 'td.cat5').replace('■', '')
        account['bank_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(1) td.data')
        
        if len(container.select('table:nth-of-type(2) > tbody > tr')) == 6:
            account['branch_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(2) td.data')
            account['branch_code'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(3) td.data')
            account['account_type'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(4) td.data')
            account['account'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(5) td.data')
            account['name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(6) td.data').replace('\u3000', ' ')
        elif len(container.select('table:nth-of-type(2) > tbody > tr')) == 4:
            account['branch_code_jpb'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(2) td.data')
            account['account_jpb'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(3) td.data')
            account['name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(4) td.data').replace('\u3000', ' ')

        account['amount'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(1) td.data2').replace(',', '')
        account['notice_date'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(2) td.data')
        account['delete_date'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(3) td.data')

        accounts.append(account)

    return accounts


def _parse_k_pubstype_07(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Parse k_pubstype_07_detail pages - 支払手続開始"""
    accounts = []
    containers = soup.select('div.container')
    
    for i, container in enumerate(containers, start=1):
        account = {}

        # ゆうちょ銀行（テーブルが6つ）の場合、ゆうちょ銀行固有のテーブルを削除する
        if len(container.select('table')) == 6:
            # Create a temporary container for jpb_tables parsing
            jpb_container = BeautifulSoup('<div></div>', 'html.parser').div
            for table in container.select('table')[1:3]:
                jpb_container.append(table.extract())  # move table to jpb_container and remove from original
            # Extract specific fields for Japan Post Bank           
            account['branch_code_jpb'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(2) td.data')
            account['account_jpb'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(3) td.data')
            account['name_alias'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(4) td.data').replace('\u3000', ' ')

        # Extract
        account['seq_no'] = str(i)
        account['role'] = _parse(container, 'td.cat5').replace('■', '')
        account['bank_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(1) td.data')
        account['branch_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(2) td.data')
        account['branch_code'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(3) td.data')
        account['account_type'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(4) td.data')
        account['account'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(5) td.data')
        account['name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(6) td.data').replace('\u3000', ' ')
        account['amount'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(1) td.data2').replace(',', '')
        account['effective_from'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(3)')
        account['effective_to'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(5)')
        account['effective_method'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(3) td.data')
        account['payment_period'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(4) td.data')
        account['suspend_date'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(5) td.data')
        account['reason'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(6) td.data')
        account['notes'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(7) td.data')

        accounts.append(account)

    return accounts


def _parse_k_pubstype_09(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Parse k_pubstype_09_detail pages - 決定書の送付が不可能"""
    accounts = []
    containers = soup.select('div.container')
    
    for i, container in enumerate(containers, start=1):
        account = {}

        # ゆうちょ銀行（テーブルが6つ）の場合、ゆうちょ銀行固有のテーブルを削除する
        if len(container.select('table')) == 6:
            # Create a temporary container for jpb_tables parsing
            jpb_container = BeautifulSoup('<div></div>', 'html.parser').div
            for table in container.select('table')[1:3]:
                jpb_container.append(table.extract())  # move table to jpb_container and remove from original
            # Extract specific fields for Japan Post Bank           
            account['branch_code_jpb'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(2) td.data')
            account['account_jpb'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(3) td.data')
            account['name_alias'] = _parse(jpb_container, 'table:nth-of-type(1) tr:nth-of-type(4) td.data').replace('\u3000', ' ')

        # Extract
        account['seq_no'] = str(i)
        account['role'] = _parse(container, 'td.cat5').replace('■', '')
        account['bank_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(1) td.data')
        account['branch_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(2) td.data')
        account['branch_code'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(3) td.data')
        account['account_type'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(4) td.data')
        account['account'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(5) td.data')
        account['name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(6) td.data').replace('\u3000', ' ')
        account['amount'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(1) td.data2').replace(',', '')
        account['notes'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(3) td.data')

        accounts.append(account)

    return accounts

def _parse_k_pubstype_10(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Parse k_pubstype_10_detail pages - 金融機関が決定表に記載"""
    accounts = []
    containers = soup.select('div.container')
    
    for i, container in enumerate(containers, start=1):
        account = {}

        # Extract
        account['seq_no'] = str(i)
        account['role'] = _parse(container, 'td.cat5').replace('■', '')
        account['bank_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(1) td.data')
        
        if len(container.select('table:nth-of-type(2) > tbody > tr')) == 6:
            account['branch_name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(2) td.data')
            account['branch_code'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(3) td.data')
            account['account_type'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(4) td.data')
            account['account'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(5) td.data')
            account['name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(6) td.data').replace('\u3000', ' ')
        elif len(container.select('table:nth-of-type(2) > tbody > tr')) == 4:
            account['branch_code_jpb'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(2) td.data')
            account['account_jpb'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(3) td.data')
            account['name'] = _parse(container, 'table:nth-of-type(2) tr:nth-of-type(4) td.data').replace('\u3000', ' ')

        account['amount'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(1) td.data2').replace(',', '')
        account['notice_date'] = _parse(container, 'table:nth-of-type(3) tr:nth-of-type(2) td.data2')

        accounts.append(account)

    return accounts


def _parse(soup: BeautifulSoup, selector: str) -> str:
    """Extract and normalize role from a BeautifulSoup element."""
    elem = soup.select_one(selector)
    if elem:
        role = elem.get_text(strip=True)
        return role.lstrip('■★').strip()
    else:
        return ''

