"""
Text Extractor for RAG (Retrieval-Augmented Generation) Pipeline.

This module provides functions to extract text from various sources:
- File extraction (.txt, .pdf, .docx, .doc, .py, .php, etc.)
- REST API extraction
- Web URL extraction

The extracted text is processed and prepared for use with LangChain vector databases
and embedding models.
"""
import re
import json
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup, Tag


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    logger.warning("trafilatura not available. Using BeautifulSoup fallback for web extraction.")
from urllib3.exceptions import InsecureRequestWarning
import warnings

# Suppress SSL warnings for web scraping
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# File extensions supported for text extraction
SUPPORTED_FILE_EXTENSIONS = {
    # Text files
    '.txt': 'text',
    '.md': 'markdown',
    '.csv': 'csv',
    '.json': 'json',
    '.xml': 'xml',
    '.html': 'html',
    '.htm': 'html',
    
    # Code files
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.cs': 'csharp',
    '.php': 'php',
    '.rb': 'ruby',
    '.go': 'go',
    '.rs': 'rust',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.r': 'r',
    '.sql': 'sql',
    '.sh': 'bash',
    '.ps1': 'powershell',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.ini': 'ini',
    '.cfg': 'config',
    '.conf': 'config',
    
    # Document files (require additional libraries)
    '.pdf': 'pdf',
    '.docx': 'docx',
    '.doc': 'doc',
    '.rtf': 'rtf',
    '.odt': 'odt',
    '.epub': 'epub',
    
    # Data files
    '.xlsx': 'excel',
    '.xls': 'excel',
    '.parquet': 'parquet',
    '.avro': 'avro',
    '.pickle': 'pickle',
    '.pkl': 'pickle',
}

# MIME types for API responses
SUPPORTED_MIME_TYPES = {
    'text/plain': 'text',
    'text/html': 'html',
    'text/xml': 'xml',
    'application/json': 'json',
    'application/xml': 'xml',
    'text/csv': 'csv',
    'application/pdf': 'pdf',
}


class TextExtractor:
    """
    A comprehensive text extractor for various data sources.
    
    Supports file extraction, REST API calls, and web URL scraping
    with proper error handling and text preprocessing.
    """
    
    def __init__(self, 
                 max_workers: int = 10,
                 timeout: int = 30,
                 retry_attempts: int = 3,
                 user_agent: Optional[str] = None,
                 chunk_size: int = 1000,
                 overlap_size: int = 200,
                 **kwargs):
        """
        Initialize the TextExtractor.
        
        Args:
            max_workers: Maximum number of concurrent workers
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            user_agent: Custom user agent for web requests
            chunk_size: Size of text chunks for processing
            overlap_size: Overlap size between chunks
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        
        # Default user agent
        self.user_agent = user_agent if user_agent is not None else (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        # Session with retry strategy
        self.session = self._create_session()
        
        # Initialize optional dependencies
        self._init_optional_deps()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.retry_attempts,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        return session
    
    def _init_optional_deps(self):
        """Initialize optional dependencies for file processing."""
        self.pdf_available = False
        self.docx_available = False
        self.excel_available = False
        
        try:
            import PyPDF2
            self.pdf_available = True
        except ImportError:
            logger.warning("PyPDF2 not available. PDF extraction disabled.")
        
        try:
            from docx import Document
            self.docx_available = True
        except ImportError:
            logger.warning("python-docx not available. DOCX extraction disabled.")
        
        try:
            import pandas as pd
            self.excel_available = True
        except ImportError:
            logger.warning("pandas not available. Excel extraction disabled.")
    
    def extract_from_files(self, 
                          file_paths: List[str], 
                          encoding: str = 'utf-8',
                          include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Extract text from a list of files.
        
        Args:
            file_paths: List of file paths to extract text from
            encoding: File encoding (default: utf-8)
            include_metadata: Whether to include file metadata
            
        Returns:
            List of dictionaries containing extracted text and metadata
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._extract_single_file, file_path, encoding, include_metadata): file_path
                for file_path in file_paths
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error extracting from {file_path}: {str(e)}")
                    if include_metadata:
                        results.append({
                            'file_path': file_path,
                            'text': '',
                            'error': str(e),
                            'file_type': 'unknown',
                            'file_size': 0,
                            'extraction_time': 0
                        })
                    
                    
        
        return results
    
    def _extract_single_file(self, 
                           file_path: str, 
                           encoding: str = 'utf-8',
                           include_metadata: bool = True) -> Optional[Dict[str, Any]]:
        """Extract text from a single file."""
        start_time = time.time()
        
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_extension = path_obj.suffix.lower()
            file_type = SUPPORTED_FILE_EXTENSIONS.get(file_extension, 'unknown')
            
            if file_type == 'unknown':
                logger.warning(f"Unsupported file type: {file_extension}")
                return None
            
            # Extract text based on file type
            text = self._extract_text_by_type(path_obj, file_type, encoding)
            
            # Clean and preprocess text
            text = self._clean_text(text)
            
            # Chunk text if needed
            chunks = self._chunk_text(text)
            
            result = {
                'file_path': str(path_obj),
                'text': text,
                'chunks': chunks,
                'file_type': file_type,
                'file_size': path_obj.stat().st_size,
                'extraction_time': time.time() - start_time
            }
            
            if include_metadata:
                result.update(self._get_file_metadata(path_obj))
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from {file_path}: {str(e)}")
            raise
    
    def _extract_text_by_type(self, file_path: Path, file_type: str, encoding: str) -> str:
        """Extract text based on file type."""
        
        if file_type in ['text', 'markdown', 'csv', 'json', 'xml', 'html']:
            return self._extract_text_file(file_path, encoding)
        
        elif file_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 
                          'csharp', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 
                          'scala', 'r', 'sql', 'bash', 'powershell', 'yaml', 'toml', 
                          'ini', 'config']:
            return self._extract_code_file(file_path, encoding)
        
        elif file_type == 'pdf':
            return self._extract_pdf_file(file_path)
        
        elif file_type == 'docx':
            return self._extract_docx_file(file_path)
        
        elif file_type == 'doc':
            return self._extract_doc_file(file_path)
        
        elif file_type == 'excel':
            return self._extract_excel_file(file_path)
        
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _extract_text_file(self, file_path: Path, encoding: str) -> str:
        """Extract text from plain text files."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Could not decode file with any encoding: {file_path}")
    
    def _extract_code_file(self, file_path: Path, encoding: str) -> str:
        """Extract text from code files with syntax highlighting preservation."""
        text = self._extract_text_file(file_path, encoding)
        
        # Add file header comment for context
        file_name = file_path.name
        file_type = file_path.suffix[1:].upper()
        
        header = f"# File: {file_name}\n# Type: {file_type}\n# Content:\n\n"
        return header + text
    
    def _extract_pdf_file(self, file_path: Path) -> str:
        """Extract text from PDF files."""
        if not self.pdf_available:
            raise ImportError("PyPDF2 is required for PDF extraction")
        
        import PyPDF2
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
        
        return text
    
    def _extract_docx_file(self, file_path: Path) -> str:
        """Extract text from DOCX files."""
        if not self.docx_available:
            raise ImportError("python-docx is required for DOCX extraction")
        
        from docx import Document
        
        try:
            doc = Document(str(file_path))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {str(e)}")
    
    def _extract_doc_file(self, file_path: Path) -> str:
        """Extract text from DOC files (requires additional libraries)."""
        # Note: DOC extraction requires additional libraries like python-docx2txt
        # or antiword. This is a placeholder implementation.
        raise NotImplementedError("DOC file extraction not implemented. Consider converting to DOCX first.")
    
    def _extract_excel_file(self, file_path: Path) -> str:
        """Extract text from Excel files."""
        if not self.excel_available:
            raise ImportError("pandas is required for Excel extraction")
        
        import pandas as pd
        
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            text = f"Excel file: {file_path.name}\n"
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                text += f"\n--- Sheet: {sheet_name} ---\n"
                text += df.to_string(index=False) + "\n"
            
            return text
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def extract_from_apis(self, 
                         api_endpoints: List[Dict[str, Any]],
                         include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Extract text from REST API endpoints.
        
        Args:
            api_endpoints: List of API endpoint configurations
                Each dict should contain:
                - 'url': API endpoint URL
                - 'method': HTTP method (GET, POST, etc.)
                - 'headers': Optional request headers
                - 'params': Optional query parameters
                - 'data': Optional request body
                - 'auth': Optional authentication
            include_metadata: Whether to include response metadata
            
        Returns:
            List of dictionaries containing extracted text and metadata
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_endpoint = {
                executor.submit(self._extract_from_single_api, endpoint, include_metadata): endpoint
                for endpoint in api_endpoints
            }
            
            for future in as_completed(future_to_endpoint):
                endpoint = future_to_endpoint[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error extracting from API {endpoint.get('url', 'unknown')}: {str(e)}")
                    if include_metadata:
                        results.append({
                            'url': endpoint.get('url', 'unknown'),
                            'text': '',
                            'error': str(e),
                            'status_code': None,
                            'response_time': 0
                        })
        
        return results
    
    def _extract_from_single_api(self, 
                                endpoint: Dict[str, Any],
                                include_metadata: bool = True) -> Optional[Dict[str, Any]]:
        """Extract text from a single API endpoint."""
        start_time = time.time()
        
        try:
            url = endpoint['url']
            method = endpoint.get('method', 'GET').upper()
            headers = endpoint.get('headers', {})
            params = endpoint.get('params', {})
            data = endpoint.get('data', None)
            auth = endpoint.get('auth', None)
            
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                auth=auth,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Extract text based on content type
            content_type = response.headers.get('content-type', '').split(';')[0]
            text = self._extract_text_from_response(response, content_type)
            
            # Clean and preprocess text
            text = self._clean_text(text)
            
            # Chunk text if needed
            chunks = self._chunk_text(text)
            
            result = {
                'url': url,
                'method': method,
                'text': text,
                'chunks': chunks,
                'status_code': response.status_code,
                'content_type': content_type,
                'response_time': time.time() - start_time
            }
            
            if include_metadata:
                result.update(self._get_response_metadata(response))
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from API {endpoint.get('url', 'unknown')}: {str(e)}")
            raise
    
    def _extract_text_from_response(self, response: requests.Response, content_type: str) -> str:
        """Extract text from API response based on content type."""
        
        if content_type in ['application/json', 'text/json']:
            try:
                data = response.json()
                return json.dumps(data, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return response.text
        
        elif content_type in ['text/html', 'application/xhtml+xml']:
            return self._extract_text_from_html(response.text)
        
        elif content_type in ['text/xml', 'application/xml']:
            return self._extract_text_from_xml(response.text)
        
        elif content_type == 'text/csv':
            return response.text
        
        elif content_type == 'text/plain':
            return response.text
        
        else:
            # Try to extract as text
            return response.text
    
    def extract_from_urls(self, 
                         urls: List[str],
                         include_metadata: bool = True,
                         extract_links: bool = False) -> List[Dict[str, Any]]:
        """
        Extract text from web URLs.
        
        Args:
            urls: List of URLs to extract text from
            include_metadata: Whether to include page metadata
            extract_links: Whether to extract and include links
            
        Returns:
            List of dictionaries containing extracted text and metadata
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self._extract_from_single_url, url, include_metadata, extract_links): url
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error extracting from URL {url}: {str(e)}")
                    if include_metadata:
                        results.append({
                            'url': url,
                            'text': '',
                            'error': str(e),
                            'status_code': None,
                            'response_time': 0
                        })
        
        return results
    
    def _extract_from_single_url(self, 
                                url: str,
                                include_metadata: bool = True,
                                extract_links: bool = False) -> Optional[Dict[str, Any]]:
        """Extract text from a single URL."""
        start_time = time.time()
        
        try:
            # Make request
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Extract text using trafilatura (better than BeautifulSoup for main content)
            text = trafilatura.extract(response.text, include_links=extract_links)
            
            if not text:
                # Fallback to BeautifulSoup if trafilatura fails
                text = self._extract_text_from_html(response.text)
            
            # Clean and preprocess text
            text = self._clean_text(text)
            
            # Chunk text if needed
            chunks = self._chunk_text(text)
            
            result = {
                'url': url,
                'text': text,
                'chunks': chunks,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'response_time': time.time() - start_time
            }
            
            if include_metadata:
                result.update(self._get_page_metadata(response, url))
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from URL {url}: {str(e)}")
            raise
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract text from HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_text_from_xml(self, xml_content: str) -> str:
        """Extract text from XML content."""
        soup = BeautifulSoup(xml_content, 'xml')
        return soup.get_text()
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove special characters that might cause issues
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for processing."""
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + self.chunk_size * 0.7:  # At least 70% of chunk size
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start + self.chunk_size * 0.7:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.overlap_size
            if start >= len(text):
                break
        
        return chunks
    
    def _get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get metadata for a file."""
        stat = file_path.stat()
        return {
            'file_name': file_path.name,
            'file_extension': file_path.suffix,
            'file_size_bytes': stat.st_size,
            'created_time': stat.st_ctime,
            'modified_time': stat.st_mtime,
            'is_file': file_path.is_file(),
            'is_directory': file_path.is_dir(),
        }
    
    def _get_response_metadata(self, response: requests.Response) -> Dict[str, Any]:
        """Get metadata for an API response."""
        return {
            'headers': dict(response.headers),
            'encoding': response.encoding,
            'cookies': dict(response.cookies),
            'elapsed_time': response.elapsed.total_seconds(),
        }
    
    def _get_page_metadata(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """Get metadata for a web page."""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        metadata = {
            'title': soup.title.string if soup.title else '',
            'description': '',
            'keywords': '',
            'author': '',
            'language': response.headers.get('content-language', ''),
            'encoding': response.encoding,
            'headers': dict(response.headers),
            'cookies': dict(response.cookies),
            'elapsed_time': response.elapsed.total_seconds(),
        }
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if isinstance(tag, Tag):  # Type check for BeautifulSoup Tag
                name_attr = tag.get('name')
                content_attr = tag.get('content')
                
                # Handle potential None values and convert to string
                name = str(name_attr).lower() if name_attr is not None else ''
                content = str(content_attr) if content_attr is not None else ''
                
                if name == 'description':
                    metadata['description'] = content
                elif name == 'keywords':
                    metadata['keywords'] = content
                elif name == 'author':
                    metadata['author'] = content
        
        return metadata
    
    def close(self):
        """Close the session and cleanup resources."""
        if hasattr(self, 'session'):
            self.session.close()


# Convenience functions for easy usage
def extract_text_from_files(file_paths: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Convenience function to extract text from files."""
    extractor = TextExtractor(**kwargs)
    try:
        return extractor.extract_from_files(file_paths)
    finally:
        extractor.close()


def extract_text_from_apis(api_endpoints: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
    """Convenience function to extract text from APIs."""
    extractor = TextExtractor(**kwargs)
    try:
        return extractor.extract_from_apis(api_endpoints)
    finally:
        extractor.close()


def extract_text_from_urls(urls: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Convenience function to extract text from URLs."""
    extractor = TextExtractor(**kwargs)
    try:
        return extractor.extract_from_urls(urls)
    finally:
        extractor.close()


def extract_text_from_mixed_sources(sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
    """
    Extract text from mixed sources (files, APIs, URLs).
    
    Args:
        sources: List of source configurations
            Each dict should contain:
            - 'type': 'file', 'api', or 'url'
            - 'path'/'url'/'endpoint': The source location
            - Additional parameters specific to the source type
        **kwargs: Additional arguments for TextExtractor
    
    Returns:
        List of dictionaries containing extracted text and metadata
    """
    extractor = TextExtractor(**kwargs)
    results = []
    
    try:
        for source in sources:
            source_type = source.get('type', '').lower()
            
            if source_type == 'file':
                file_path = source.get('path')
                if file_path:
                    result = extractor.extract_from_files([file_path])
                    results.extend(result)
            
            elif source_type == 'api':
                endpoint = {k: v for k, v in source.items() if k != 'type'}
                result = extractor.extract_from_apis([endpoint])
                results.extend(result)
            
            elif source_type == 'url':
                url = source.get('url')
                if url:
                    result = extractor.extract_from_urls([url])
                    results.extend(result)
            
            else:
                logger.warning(f"Unknown source type: {source_type}")
    
    finally:
        extractor.close()
    
    return results 