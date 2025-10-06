# -----------------------------------------------------------------------------------------------------------------------
# Arxiv: von https://github.com/crewAIInc/crewAI-tools/blob/main/crewai_tools/tools/arxiv_paper_tool/arxiv_paper_tool.py
# modifiziert um sortierung hinzuzufügen und filterung nach datum zu ermöglichen
# -----------------------------------------------------------------------------------------------------------------------

import re
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import json
from typing import Type, List, Optional, ClassVar
from pydantic import BaseModel, Field
from crewai.tools import BaseTool, EnvVar
import logging
from pathlib import Path
from utils.citation import format_apa_citation

logger = logging.getLogger(__file__)

class ArxivToolInput(BaseModel):
    search_query: str = Field(..., description="Search query for Arxiv, e.g., 'transformer neural network'")
    max_results: int = Field(25, ge=1, le=100, description="Max results to fetch; must be between 1 and 100")
    sort_by: str = Field(..., description="Field to sort by, either 'relevance' or 'submittedDate'")
    sort_order: str = Field(..., description="Order to sort results, either 'ascending' or 'descending'")
    submitted_date: Optional[str] = Field(None, description="Date range filter in format [YYYYMMDDTTTT+TO+YYYYMMDDTTTT] for submitted dates in GMT, e.g., '[20200101+TO+20231231]'")

class ArxivTool(BaseTool):
    BASE_API_URL: ClassVar[str] = "http://export.arxiv.org/api/query"
    SLEEP_DURATION: ClassVar[int] = 1
    SUMMARY_TRUNCATE_LENGTH: ClassVar[int] = 300
    ATOM_NAMESPACE: ClassVar[str] = "{http://www.w3.org/2005/Atom}"
    REQUEST_TIMEOUT: ClassVar[int] = 10  
    name: str = "Arxiv Paper Fetcher and Downloader"
    description: str = "Fetches metadata from Arxiv based on a search query and optionally downloads PDFs."
    args_schema: Type[BaseModel] = ArxivToolInput
    model_config = {"extra": "allow"} 
    package_dependencies: List[str] = ["pydantic"]
    env_vars: List[EnvVar] = []

    download_pdfs: bool = True
    save_dir: str = "./pdfs"
    search_terms: List[str] = []
    use_title_as_filename: bool = False
    default_max_results: int = 10
    
    def __init__(self, download_pdfs: bool = True, save_dir: str = "./pdfs", search_terms: Optional[List[str]] = None, use_title_as_filename: bool = False, default_max_results: int = 10, **kwargs):
        super().__init__(
            download_pdfs=download_pdfs,
            save_dir=save_dir,
            search_terms=search_terms if search_terms is not None else [],
            use_title_as_filename=use_title_as_filename,
            default_max_results=int(default_max_results) if default_max_results is not None else 10,
            **kwargs
        )

    def _run(self, search_query: str, max_results: int = -1, sort_by: str = "relevance", sort_order: str = "descending", submitted_date: Optional[str] = None) -> List[dict]:
        try:
            if isinstance(max_results, int) and max_results <= 0:
                max_results = self.default_max_results
            args = ArxivToolInput(search_query=search_query, max_results=max_results, sort_by=sort_by, sort_order=sort_order, submitted_date=submitted_date)
            logger.info(f"Running Arxiv tool: query='{args.search_query}', max_results={args.max_results}, "
                        f"download_pdfs={self.download_pdfs}, save_dir='{self.save_dir}', "
                        f"use_title_as_filename={self.use_title_as_filename}")

            combined_query = args.search_query.strip() if args.search_query else ""
      
            if self.search_terms:
                additional_terms = []
                for term in self.search_terms:
                    t = term.strip()
                    if t and t not in combined_query:
                        additional_terms.append(t)
                
                if additional_terms:
                    if combined_query:
                        combined_query = f"{combined_query} {' '.join(additional_terms)}"
                    else:
                        combined_query = ' '.join(additional_terms)

            logger.info(f"Final ArXiv query: '{combined_query}'")
            papers = self.fetch_arxiv_data(combined_query, args.max_results, args.sort_by, args.sort_order, args.submitted_date)

            if self.download_pdfs:
                save_dir = self._validate_save_path(self.save_dir)
                mapping = {}
                for paper in papers:
                    if paper['pdf_url']:
                        if self.use_title_as_filename:
                            safe_title = re.sub(r'[\\/*?:"<>|]', "_", paper['title']).strip()
                            filename_base = safe_title or paper['arxiv_id']
                        else:
                            filename_base = paper['arxiv_id']
                        filename = f"{filename_base[:500]}.pdf"
                        save_path = Path(save_dir) / filename
                        save_path.parent.mkdir(parents=True, exist_ok=True)

                        try:
                            self.download_pdf(paper['pdf_url'], str(save_path))
                            time.sleep(self.SLEEP_DURATION)
                            paper['pdf_filename'] = filename
                            mapping[filename] = {
                                'title': paper['title'],
                                'authors': paper['authors'],
                                'year': paper['year'],
                                'journal': paper['journal'],
                                'doi': paper['doi'],
                                'arxiv_id': paper['arxiv_id'],
                                'pdf_url': paper['pdf_url'],
                                'citation': paper['citation'],
                                'screening_result': 'None'
                            }
                        except Exception as e:
                            logger.warning(f"Failed to download PDF for {paper['title']}: {e}")

                if mapping:
                    mapping_path = Path(save_dir) / "sources.json"
        
                    existing_mapping = {}
                    if mapping_path.exists():
                        try:
                            with open(mapping_path, 'r', encoding='utf-8') as f:
                                existing_mapping = json.load(f)
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse existing {mapping_path}, starting fresh")
     
                    existing_mapping.update(mapping)
                    with open(mapping_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_mapping, f, indent=2)

            return papers

        except Exception as e:
            logger.error(f"ArxivTool Error: {str(e)}")
            return []

    def fetch_arxiv_data(self, search_query: str, max_results: int, sort_by: str, sort_order: str, submitted_date: Optional[str] = None) -> List[dict]:
        """Fetch data from ArXiv API with improved error handling"""

        if not search_query or not search_query.strip():
            logger.warning("Empty search query provided to ArXiv API")
            return []

        api_url = f"{self.BASE_API_URL}?search_query={urllib.parse.quote(search_query)}&start=0&max_results={max_results}&sortBy={sort_by}&sortOrder={sort_order}"
        
        if submitted_date:
            api_url += f"&submittedDate={urllib.parse.quote(submitted_date)}"
            
        logger.info(f"Fetching data from Arxiv API: {api_url}")

        try:
            with urllib.request.urlopen(api_url, timeout=self.REQUEST_TIMEOUT) as response:
                logger.info(f"ArXiv API response status: {response.status}")
                if response.status != 200:
                    logger.error(f"Error: HTTP {response.status}")
                    return []
                data = response.read().decode('utf-8')
                logger.info(f"Received {len(data)} characters from ArXiv API")
        except urllib.error.URLError as e:
            logger.error(f"Error fetching from ArXiv API: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching from ArXiv API: {e}")
            return []

        try:
            root = ET.fromstring(data)
        except ET.ParseError as e:
            logger.error(f"Error parsing XML response: {e}")
            logger.debug(f"Raw response: {data[:1000]}...")
            return []

        papers = []
        entries = root.findall(self.ATOM_NAMESPACE + "entry")
        logger.info(f"Found {len(entries)} entries in ArXiv response")

        for entry in entries:
            raw_id = self._get_element_text(entry, "id")
            arxiv_id = raw_id.split('/')[-1].replace('.', '_') if raw_id else "unknown"

            title = self._get_element_text(entry, "title") or "No Title"
            summary = self._get_element_text(entry, "summary") or "No Summary"
            published = self._get_element_text(entry, "published") or "No Publish Date"
            authors = [
                self._get_element_text(author, "name") or "Unknown"
                for author in entry.findall(self.ATOM_NAMESPACE + "author")
            ]
            journal = self._get_element_text(entry, "journal-ref") or None
            pdf_url = self._extract_pdf_url(entry)
            doi_elem = entry.find("{http://arxiv.org/schemas/atom}doi")
            doi = doi_elem.text.strip() if doi_elem is not None and doi_elem.text else None

            year_val: Optional[int] = None
            year_val = int(published[:4]) if published and published[:4].isdigit() else None

            citation = format_apa_citation(authors=authors, year=year_val, title=title, publisher=(journal or "arXiv"), doi=(doi or f"https://arxiv.org/abs/{arxiv_id.replace('_', '.')}" if arxiv_id else None))

            papers.append({
                "arxiv_id": arxiv_id,
                "title": title,
                "summary": summary,
                "authors": authors,
                "published_date": published,
                "pdf_url": pdf_url,
                "citation": citation,
                "year": year_val,
                "journal": journal,
                "doi": doi
            })

        logger.info(f"Successfully parsed {len(papers)} papers from ArXiv")
        return papers

    @staticmethod
    def _get_element_text(entry: ET.Element, element_name: str) -> Optional[str]:
        elem = entry.find(f'{ArxivTool.ATOM_NAMESPACE}{element_name}')
        return elem.text.strip() if elem is not None and elem.text else None

    def _extract_pdf_url(self, entry: ET.Element) -> Optional[str]:
        for link in entry.findall(self.ATOM_NAMESPACE + "link"):
            if link.attrib.get('title', '').lower() == 'pdf':
                return link.attrib.get('href')
        for link in entry.findall(self.ATOM_NAMESPACE + "link"):
            href = link.attrib.get('href')
            if href and 'pdf' in href:
                return href
        return None

    def _format_paper_result(self, paper: dict) -> str:
        summary = (paper['summary'][:self.SUMMARY_TRUNCATE_LENGTH] + '...') \
            if len(paper['summary']) > self.SUMMARY_TRUNCATE_LENGTH else paper['summary']
        authors_str = ', '.join(paper['authors'])
        return (f"Title: {paper['title']}\n"
                f"Authors: {authors_str}\n"
                f"Published: {paper['published_date']}\n"
                f"PDF: {paper['pdf_url'] or 'N/A'}\n"
                f"Summary: {summary}")

    @staticmethod
    def _validate_save_path(path: str) -> Path:
        save_path = Path(path).resolve()
        save_path.mkdir(parents=True, exist_ok=True)
        return save_path

    def download_pdf(self, pdf_url: str, save_path: str):
        try:
            logger.info(f"Downloading PDF from {pdf_url} to {save_path}")
            urllib.request.urlretrieve(pdf_url, str(save_path))
            logger.info(f"PDF saved: {save_path}")
        except urllib.error.URLError as e:
            logger.error(f"Network error occurred while downloading {pdf_url}: {e}")
            raise
        except OSError as e:
            logger.error(f"File save error for {save_path}: {e}")
            raise
