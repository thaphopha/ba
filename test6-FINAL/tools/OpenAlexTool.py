# OpenAlex[1]PaperTool für die Suche nach wissenschaftlichen Arbeiten. Stark inspiriert vom ArxivPaperTool von CrewAI (s. ./ArxivTool.py).
# 
# Quellen:
# [1] Priem, J., Piwowar, H., & Orr, R. (2022). 
# OpenAlex: A fully-open index of scholarly works, authors, publisher, institutions, and concepts. 
# ArXiv. https://arxiv.org/abs/2205.01833

import re
import os
import time
import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import logging
from pathlib import Path
from pypdf import PdfReader
from utils.citation import format_apa_citation

logger = logging.getLogger(__file__)

class OpenAlexToolInput(BaseModel):
    query: str = Field(..., description="Search query for OpenAlex, e.g., 'machine learning'")
    max_results: int = Field(25, ge=1, le=100, description="Max results to fetch; must be between 1 and 100")
    from_publication_date: Optional[str] = Field(None, description="Filter for publications from this date onwards in format YYYY-MM-DD, e.g., '2020-01-01'")

class OpenAlexTool(BaseTool):
    SLEEP_DURATION: int = 1
    REQUEST_TIMEOUT: int = 30
    name: str = "OpenAlexTool Paper Fetcher and Downloader"
    description: str = "Search OpenAlex for papers and return basic metadata and download pdfs if available."
    args_schema: Type[BaseModel] = OpenAlexToolInput
    
    download_pdfs: bool = True
    save_dir: str = "./pdfs"
    default_max_results: int = 10
    
    def __init__(self, download_pdfs: bool = True, save_dir: str = "./pdfs", default_max_results: int = 10, **kwargs):
        super().__init__(
            download_pdfs=download_pdfs,
            save_dir=save_dir,
            default_max_results=default_max_results,
            **kwargs
        )

    def _run(self, query: str, max_results: int = -1, from_publication_date: Optional[str] = None) -> List[dict]:
        try:
            if isinstance(max_results, int) and max_results <= 0:
                max_results = self.default_max_results
            args = OpenAlexToolInput(query=query, max_results=max_results, from_publication_date=from_publication_date)
            logger.info(f"Running OpenAlex tool: query='{args.query}', max_results={args.max_results}, "
                        f"from_publication_date={args.from_publication_date}")

            filter_parts = ["best_oa_location.is_oa:true", "type:book|journal|article|repository"]
            if args.from_publication_date:
                filter_parts.append(f"from_publication_date:{args.from_publication_date}")
            else:
                filter_parts.append("from_publication_date:2018-01-01")
            
            params = {
                "select": "id,doi,display_name,authorships,best_oa_location,open_access,publication_year,locations,primary_location",
                "search": args.query,
                "per-page": str(min(args.max_results, 50)),
                "sort": "publication_year:desc,relevance_score:desc",
                "filter": ",".join(filter_parts),
            }
            
            url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
            logger.info(f"Fetching data from OpenAlex API: {url}")
            
            try:
                with urllib.request.urlopen(url, timeout=self.REQUEST_TIMEOUT) as response:
                    if response.status != 200:
                        logger.error(f"Error: HTTP {response.status}")
                        return []
                    data = json.loads(response.read().decode('utf-8'))
            except urllib.error.URLError as e:
                logger.error(f"Error fetching from OpenAlex API: {e}")
                return []
            except Exception as e:
                logger.error(f"Error fetching from OpenAlex API: {e}")
                return []

            papers = []
            works = data.get("results", [])
            total_works = len(works)
            
            for i, work in enumerate(works):            
                if not work or not isinstance(work, dict):
                    logger.warning(f"Skipping unexpected work entry (not a dict): {work}")
                    continue

                pdf_url = None

                best_oa_location = work.get("best_oa_location") or {}
                if best_oa_location.get("pdf_url"):
                    pdf_url = best_oa_location.get("pdf_url")

                if not pdf_url:
                    primary_location = work.get("primary_location") or {}
                    if primary_location.get("pdf_url"):
                        pdf_url = primary_location.get("pdf_url")

                if not pdf_url:
                    open_access = work.get("open_access") or {}
                    if open_access.get("oa_url"):
                        pdf_url = open_access.get("oa_url")

                if not pdf_url:
                    for location in (work.get("locations") or []):
                        if not location or not isinstance(location, dict):
                            continue
                        if location.get("pdf_url"):
                            pdf_url = location.get("pdf_url")
                            break

                authors = []
                for auth in (work.get("authorships") or []) if isinstance(work.get("authorships"), list) else []:
                    if not auth or not isinstance(auth, dict):
                        continue
                    author = auth.get("author") or {}
                    if isinstance(author, dict) and author.get("display_name"):
                        authors.append(author.get("display_name"))
                
                year = work.get("publication_year") or None
                title = work.get("display_name", "Untitled")
                
                if not title:
                    logger.warning(f"Skipping entry with missing title: {work}")
                    continue

                best_oa_location = work.get("best_oa_location")
                if not isinstance(best_oa_location, dict):
                    best_oa_location = {}
                source_obj = best_oa_location.get("source") if isinstance(best_oa_location.get("source"), dict) else {}
                journal = source_obj.get("display_name") if isinstance(source_obj, dict) else None

                doi_val = work.get("doi")
                doi = ""
                if isinstance(doi_val, str) and doi_val:
                    doi = doi_val.replace("https://doi.org/", "")

                arxiv_val = work.get("arxiv_id", "")
                arxiv_id = ""
                if isinstance(arxiv_val, str) and arxiv_val:
                    arxiv_id = arxiv_val.replace("https://arxiv.org/abs/", "")
                citation = format_apa_citation(authors=authors, year=year, title=title, publisher=journal, doi=doi, url=pdf_url)

                papers.append({
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "journal": journal,
                    "doi": doi,
                    "arxiv_id": arxiv_id,
                    "pdf_url": pdf_url,
                    "citation": citation,
                    "screening_result": None
                })

            logger.info("Finished processing API results")

            if self.download_pdfs:
                save_dir = self._validate_save_path(self.save_dir)
                mapping = {}
                for paper in papers:
                    if paper['pdf_url']:
                        if paper['arxiv_id']:
                            filename_base = paper['arxiv_id']
                        elif paper['doi']:
                            filename_base = re.sub(r'[\\/:\s]+', '_', paper['doi'])
                        else:
                            filename_base = re.sub(r'[\\/*?:"<>|\s]+', '_', paper['title']).strip()

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
                    # Merge mappings
                    existing_mapping.update(mapping)
                    with open(mapping_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_mapping, f, indent=2)

            return papers

        except Exception as e:
            logger.error(f"OpenAlexTool Error: {str(e)}")
            return []

    @staticmethod
    def _validate_save_path(path: str) -> Path:
        save_path = Path(path).resolve()
        save_path.mkdir(parents=True, exist_ok=True)
        return save_path

    def download_pdf(self, pdf_url: str, save_path: str):
        try:
            logger.info(f"Downloading PDF from {pdf_url} to {save_path}")
            urllib.request.urlretrieve(pdf_url, str(save_path))
            
            # Validate PDF content
            try:
                PdfReader(save_path)
                logger.info(f"PDF saved and validated: {save_path}")
            except Exception as e:
                os.remove(save_path)
                logger.error(f"Downloaded file is not a valid PDF: {e}")
                raise Exception("Downloaded content is not a valid PDF")
                
        except urllib.error.URLError as e:
            logger.error(f"Network error occurred while downloading {pdf_url}: {e}")
            raise
        except OSError as e:
            logger.error(f"File save error for {save_path}: {e}")
            raise
