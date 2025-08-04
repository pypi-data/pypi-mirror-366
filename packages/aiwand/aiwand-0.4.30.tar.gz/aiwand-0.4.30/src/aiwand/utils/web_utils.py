import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List
import httpx

from ..models import LinkContent
from .file_utils import is_remote_url


def fetch_all_data(
    links: List[str],
    timeout: int = 30
) -> List[LinkContent]:
    """
    Fetch content from multiple URLs with proper error handling.
    Args:
        links (List[str]): List of URLs to fetch content from
    Returns:
        List[LinkContent]: List of LinkContent        
    Raises:
        ValueError: If the URL is invalid
        urllib.error.URLError: If the URL can't be reached
        urllib.error.HTTPError: If the server returns an error status
    """
    all_data = []
    for link in links:
        try:
            if not is_remote_url(link):
                data = read_file_content(link)
            else:
                data = fetch_data(url=link, timeout=timeout)
            link_data = LinkContent(
                url=link,
                content=data
            )
            all_data.append(link_data)
        except Exception as e:
            print(f"Error fetching content from {link}: {str(e)}")
            continue
    return all_data


def fetch_doc(doc_url: str, timeout: int = 30) -> str:
    """
    Fetch a document from a URL.
    """
    try:
        return httpx.get(doc_url).content
    except Exception as e:
        raise ValueError(f"Error fetching document from {doc_url}: {str(e)}")


def get_soup(
        url: str, 
        timeout: int = 30,
        parser: str = 'html.parser',
        **kwargs
     ) -> BeautifulSoup:
    """
    Get a BeautifulSoup object for a given URL.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'AIWand/1.0 (Content Extraction Tool)'
        }
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return BeautifulSoup(response.read(), parser, **kwargs)


def fetch_data(url: str, timeout: int = 30) -> str:
    """
    Fetch content from a URL with proper error handling.
    
    Args:
        url (str): URL to fetch content from
        timeout (int): Request timeout in seconds (default: 30)        
    Returns:
        str: Content fetched from the URL        
    Raises:
        ValueError: If the URL is invalid
        urllib.error.URLError: If the URL can't be reached
        urllib.error.HTTPError: If the server returns an error status        
    Examples:
        >>> content = fetch_data("https://example.com")
        >>> print(f"Page content: {content[:100]}...")
    """
    try:
        soup = get_soup(url, timeout=timeout)
        
        title = soup.title.string
        text = soup.get_text(separator=" ")

        full_text = f"""Title: {title}\nURL Source: {url}\nContent:\n{text}"""
        
        return full_text
    except urllib.error.HTTPError as e:
        raise urllib.error.HTTPError(
            url, e.code, f"HTTP {e.code}: {e.reason}", e.headers, e.fp
        )
    except urllib.error.URLError as e:
        raise urllib.error.URLError(f"Failed to fetch URL {url}: {e.reason}")
    except Exception as e:
        raise ValueError(f"Error fetching content from {url}: {str(e)}")


def read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Read the content of a file with proper error handling.
    
    Args:
        file_path (str): Path to the file to read
        encoding (str): File encoding (default: 'utf-8')
        
    Returns:
        str: Content of the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read due to permissions
        UnicodeDecodeError: If the file can't be decoded with the specified encoding
        
    Examples:
        >>> content = read_file_content("document.txt")
        >>> print(f"File content: {content[:100]}...")
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        with open(path, 'r', encoding=encoding) as file:
            return file.read()
            
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(path, 'r', encoding='latin-1') as file:
                return file.read()
        except UnicodeDecodeError:
            raise UnicodeDecodeError(
                f"Could not decode file {file_path} with utf-8 or latin-1 encoding"
            )
    except PermissionError:
        raise PermissionError(f"Permission denied reading file: {file_path}")
