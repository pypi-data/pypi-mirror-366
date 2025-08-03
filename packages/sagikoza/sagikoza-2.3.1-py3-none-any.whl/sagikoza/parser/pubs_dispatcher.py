from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_submit(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Extracts publication details from the BeautifulSoup object.

    Args:
        soup: BeautifulSoup object containing the HTML of the publication page.

    Returns:
        A list of dictionaries, each containing details of a publication.
    
    Raises:
        ValueError: HTMLパースエラーの場合
    """
    try:
        submit = []
        links = soup.select('tr > td.\\36 > a')
        
        for link in links:
            params = {}
            href = link.get('href')
            if not href:
                continue
                
            href = href.replace('./pubs_basic_frame.php?', '')
            for param in href.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            
            if params:  # Only add if we have valid parameters
                params['params'] = href
                submit.append(params)

        logger.debug(f"Parsed {len(submit)} submit details from HTML")
        return submit
    
    except Exception as e:
        logger.error(f"Error parsing submit details: {e}")
        return []

