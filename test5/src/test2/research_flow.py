#!/usr/bin/env python

import os
import json
import getpass
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from crewai.flow.flow import Flow, listen, router, start, or_
from crewai import Agent, Task, Crew, Process, LLM
import sys
from langchain_community.document_loaders import PyPDFium2Loader
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.OpenAlexTool import OpenAlexTool
from tools.ArxivTool import ArxivTool
from tools.RetrievalTool import RetrievalTool
from langchain_chroma import Chroma
import chromadb
from chroma_manager import ChromaManager
import json

ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

class EvaluationCriteria(BaseModel):
    
    comprehensiveness: float = Field(default=0.0, ge=0.0, le=10.0, description="How well does the chapter cover the breadth of relevant literature? Are important works included?")
    relevance: float = Field(default=0.0, ge=0.0, le=10.0, description="Are the cited works clearly related to the research problem? Does the chapter avoid irrelevant or tangential references?")
    organization_and_structure: float = Field(default=0.0, ge=0.0, le=10.0, description="Is the literature grouped logically (e.g., by theme, method, or chronology)? Does the flow help the reader understand the research landscape?")
    critical_analysis: float = Field(default=0.0, ge=0.0, le=10.0, description="Does the author go beyond summarizing papers to compare, contrast, and highlight gaps or trends?")
    clarity_and_readability: float = Field(default=0.0, ge=0.0, le=10.0, description="Is the writing clear, concise, and accessible? Does it avoid unnecessary jargon or confusion?")
    citation_quality_and_accuracy: float = Field(default=0.0, ge=0.0, le=10.0, description="Are sources reliable, up-to-date, and cited correctly? Are key foundational and recent works included?")


class QualityAssessment(BaseModel):

    score: float = Field(default=0.0, ge=0.0, le=10.0, description="Overall score (average of all criteria)")
    criteria: EvaluationCriteria = Field(default_factory=EvaluationCriteria, description="Individual criteria scores")
    feedback: str = Field(default="", description="Detailed feedback for improvement")
    passed: bool = Field(default=False, description="True if score >= 8.0, otherwise False")


class ScientificResearchState(BaseModel):
    topic: str = ""
    timeframe: int = 5
    max_pdfs_per_tool: int = 10
    pdf_save_dir: str = str((Path(__file__).parent.parent.parent / "pdfs").resolve())
    current_step: str = "initialized"
    iteration_count: int = 0
    max_iterations: int = 5

    chroma_persist_directory: str = str((Path(__file__).parent.parent.parent / "chroma_db").resolve())

    collected_publications: str = ""
    filtered_publications: str = ""
    processed_content: str = ""
    first_draft: str = ""
    evaluation: QualityAssessment = Field(default_factory=lambda: QualityAssessment())
    final_chapter: str = ""
    target_score: float = 8.0


class ResearchFlow(Flow[ScientificResearchState]):
    """
    Workflow steps:
    1. Sammeln von wissenschaftlichen Publikationen (Collect Publications)
    2. Filtern der Publikationen (Filter Publications)
    3. Aufbereiten der Publikationen (Process Publications)
    4. Schreiben des Kapitels (Write Chapter)
    5. Bewertung des Kapitels (Evaluate Chapter)
    6. Letzter Feinschliff (Final Revision) - with feedback loop
    """

    def __init__(self):
        super().__init__()
        
        # Using Google AI Studio (standard Gemini API)
        # API Key should start with AIza (not AQ. which is Vertex AI)
        # self.llm = LLM(model="gemini/gemini-1.5-flash", temperature=0.3)
        # working: "nvidia_nim/meta/llama-3.3-70b-instruct"
        # not working: "nvidia_nim/openai/gpt-oss-120b"
        self.llm = llm
        # LLM("gemini/gemini-2.0-flash", temperature=0.3)

        self._ensure_output_directories()

        self.vector_store = Chroma(
            collection_name="scientific_publications",
            embedding_function=embeddings,
            persist_directory=self.state.chroma_persist_directory
        )
        
    def _ensure_output_directories(self):
        """Ensure the output, logs, and pdfs directories exist"""
        import os
        for directory in ["logs", "output", "pdfs"]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
        
        pdf_dir = Path(self.state.pdf_save_dir)
        if not pdf_dir.exists():
            pdf_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created PDF directory: {pdf_dir}")
           
    @start()
    def initialize_research_parameters(self):
        

        self.state.topic = "Deep Learning in Resource and Data Constrained Edge Computing Systems"
        self.state.timeframe = 5
        self.state.current_step = "collection"

        print(f"Research Topic: {self.state.topic}")
        print(f"Timeframe: {self.state.timeframe} years")

        return "Research parameters initialized"

    @listen(initialize_research_parameters)
    def collect_publications(self):

        publication_collector = Agent(
            role="Scientific Publication Collector",
            goal=f"Systematically collect relevant scientific publications on {self.state.topic} from various academic databases and sources",
            backstory=f"""You are an experienced research librarian with expertise in academic databases.
            You have two specialized tools:
            
            1. ArxivTool - For preprints and recent research:
               - Use EXACT technical terms and acronyms from the topic
               - For "{self.state.topic}", search with the full term or key technical keywords
               - Filter by submission date for last {self.state.timeframe} years
               - Example: search_query="{self.state.topic}", submitted_date="[20200101+TO+20250101]"
               
            2. OpenAlexTool - For peer-reviewed publications:
               - Use precise queries with specific terminology
               - For "{self.state.topic}", include ALL key terms and technical names
               - Add context words like "protocol", "framework", "system", "architecture" if relevant
               - Filter by publication date: from_publication_date="2020-01-01"
               - Example: query="{self.state.topic} protocol implementation"
            
            CRITICAL: Use the EXACT topic name in your searches. Don't substitute with generic terms.
            If a topic has an acronym, use BOTH the full name AND acronym in separate searches.
            Always filter by date to get publications from last {self.state.timeframe} years.""",
            verbose=True,
            tools=[
                ArxivTool(download_pdfs=True, save_dir=self.state.pdf_save_dir, default_max_results=self.state.max_pdfs_per_tool),
                OpenAlexTool(download_pdfs=True, save_dir=self.state.pdf_save_dir, default_max_results=self.state.max_pdfs_per_tool)
            ],
            llm=self.llm,
            max_rpm=10,
            max_iter=2
        )
        
        collect_task = Task(
            description=f"""Use ArxivTool and OpenAlexTool to search for publications about "{self.state.topic}".
            
            SEARCH STRATEGY:
            1. Use ArxivTool with search_query="{self.state.topic}" and date filter for last {self.state.timeframe} years
            2. Use OpenAlexTool with precise query including full topic name and related technical terms
            3. Try variations if needed: acronyms, full names, related technical terminology
            
            REQUIREMENTS:
            - Must use the EXACT topic name "{self.state.topic}" in searches
            - Filter all searches to last {self.state.timeframe} years (from 2020 onwards)
            - Collect up to {self.state.max_pdfs_per_tool} publications per tool (total ~20)
            - Verify publications are actually about "{self.state.topic}" specifically
            
            Return results with complete metadata: title, authors, year, journal, DOI, abstract, URL.""",
            expected_output="""A comprehensive JSON list of scientific publications specifically about 
            "{self.state.topic}" with complete bibliographic information: titles, authors, journals, 
            publication years, DOIs, abstracts, and access links. All publications must be from 
            the last {self.state.timeframe} years and directly relevant to the topic.""",
            agent=publication_collector,
            output_file="output/collected_publications.json"
        )
        
        collection_crew = Crew(
            agents=[publication_collector],
            tasks=[collect_task],
            process=Process.sequential,
            verbose=True,
            
        )
        
        result = collection_crew.kickoff()
        self.state.collected_publications = result.raw
        self.state.current_step = "filtering"


    @listen(collect_publications)
    def filter_publications(self):
        publication_filter = Agent(
            role="Scientific Publication Filter and Quality Assessor",
            goal=f"Filter and evaluate collected publications based on relevance, quality, and methodological rigor for {self.state.topic}",
            backstory="""You are a senior academic with extensive experience in peer review and
            research methodology. You have a keen eye for identifying high-quality
            research and can quickly assess the relevance and credibility of scientific
            publications based on citation metrics, journal impact factors, and methodological soundness.""",
            verbose=True,
            llm=self.llm,
            max_rpm=10
        )
        
        publications_text = self.state.collected_publications if self.state.collected_publications else "No publications collected yet."
        
        task_description = f"""HERE ARE THE COLLECTED PUBLICATIONS TO FILTER:
            {publications_text}

            YOUR TASK:
            Review and filter ONLY the publications listed above based on relevance, quality,
            and methodological rigor. Evaluate each publication using criteria such as:
            journal impact factor, citation count, peer review status, methodology
            quality, relevance to {self.state.topic}, and publication recency.

            CRITICAL INSTRUCTIONS:
            - You MUST use ONLY the publications provided above
            - Do NOT make up or invent any new publications
            - Do NOT add publications not in the list above
            - Select the 10-15 most relevant publications from the list above
            - Exclude publications not relevant to {self.state.topic}"""
        
        filter_task = Task(
            description=task_description,
            expected_output="""A curated list of 10-15 high-quality, relevant publications selected
            FROM THE PROVIDED LIST ONLY, with quality ratings and brief justifications 
            for inclusion. Include ranking based on relevance and impact.
            DO NOT INVENT NEW PUBLICATIONS.""",
            agent=publication_filter,
            output_json="output/02_filtered_publications.json",
        )
        
        filtering_crew = Crew(
            agents=[publication_filter],
            tasks=[filter_task],
            process=Process.sequential,
            verbose=True,
        )
        
        result = filtering_crew.kickoff()
        
        self.state.filtered_publications = result.raw
        self.state.current_step = "processing"

        self._cleanup_and_upsert_filtered_publications()
        
        return f"Filtered publications stored"


    def _cleanup_and_upsert_filtered_publications(self):
        try:
            import json
            from pathlib import Path

            collected_pubs = json.loads(self.state.collected_publications)
            filtered_pubs = json.loads(self.state.filtered_publications)
            
            filtered_ids = set()
            for pub in filtered_pubs:
                doi = pub.get('doi', '').strip()
                arxiv_id = pub.get('arxiv_id', '').strip()
                title = pub.get('title', '').strip()
                if doi:
                    filtered_ids.add(doi)
                if arxiv_id:
                    filtered_ids.add(arxiv_id)
                if title:
                    filtered_ids.add(title)
            
            pdf_dir = Path(self.state.pdf_save_dir)
            deleted_count = 0
            kept_count = 0
            
            if pdf_dir.exists():
                for pub in collected_pubs:
                    doi = pub.get('doi', '').strip()
                    arxiv_id = pub.get('arxiv_id', '').strip()
                    title = pub.get('title', '').strip()
    
                    is_filtered = any([
                        doi and doi in filtered_ids,
                        arxiv_id and arxiv_id in filtered_ids,
                        title and title in filtered_ids
                    ])
                    
                    pdf_filename = pub.get('pdf_filename')
                    if pdf_filename:
                        pdf_path = pdf_dir / pdf_filename
                        if pdf_path.exists():
                            if not is_filtered:
                                pdf_path.unlink()
                                deleted_count += 1
                                print(f"Deleted: {pdf_filename}")
                            else:
                                kept_count += 1
                                print(f" Kept: {pdf_filename}")

            if len(filtered_pubs) == 0:
                print("\nNo filtered publications to upsert")
                return
            
            manager = ChromaManager(persist_directory=self.state.chroma_persist_directory)
            manager.connect()
            
            documents = []
            metadatas = []
            base_ids = []
            
            for idx, pub in enumerate(filtered_pubs):
                title = pub.get('title', '')
                
                pdf_filename = pub.get('pdf_filename')
                doc_text = None
                
                if pdf_filename:
                    pdf_path = pdf_dir / pdf_filename
                    if pdf_path.exists():
                        try:
                            print(f"Loading PDF: {pdf_filename}")
                            loader = PyPDFium2Loader(str(pdf_path))
                            pages = loader.load()
         
                            doc_text = "\n\n".join([page.page_content for page in pages])
                            
                        except Exception as e:
                            print(f"Failed to load PDF: {e}")
                
                if not doc_text or len(doc_text.strip()) < 100:
                    abstract = pub.get('abstract', '')
                    doc_text = f"Title: {title}\n\nAbstract: {abstract}"
                
                documents.append(doc_text)
                
                metadata = {
                    'title': title or '',
                    'authors': pub.get('authors', '') if isinstance(pub.get('authors'), str) else ', '.join(pub.get('authors', []) if pub.get('authors') else []),
                    'year': pub.get('year') or 0,
                    'journal': pub.get('journal') or '',
                    'doi': pub.get('doi') or '',
                    'arxiv_id': pub.get('arxiv_id') or '',
                    'pdf_url': pub.get('pdf_url') or '',
                    'source': 'arxiv' if pub.get('arxiv_id') else 'openalex',
                    'quality_rating': pub.get('quality_rating') or '',
                    'filtered': 'true' 
                }
                metadatas.append(metadata)
  
                paper_id = pub.get('doi') or pub.get('arxiv_id') or f"paper_{idx}"
                paper_id = paper_id.replace('/', '_').replace(':', '_').replace('.', '_')
                base_ids.append(paper_id)
            
            manager.add_chunked_documents(
                collection_name="scientific_publications",
                documents=documents,
                metadatas=metadatas,
                base_ids=base_ids,
                chunk_size=1000,
                chunk_overlap=200
            )
            
            info = manager.get_collection_info("scientific_publications")
            print(f"\nVector store now contains {info.get('count')} chunks from {len(filtered_pubs)} filtered publications")
            print("="*60 + "\n")
        except Exception as e:
            raise

    @listen(filter_publications)
    def process_publications(self):
        content_processor = Agent(
            role="Academic Content Processor and Synthesizer",
            goal=f"Extract, organize, and synthesize key information from filtered publications on {self.state.topic}",
            backstory="""You are a research analyst specialized in academic content processing.
            You excel at extracting key findings, methodologies, and insights from
            scientific papers and organizing them into coherent, well-structured
            summaries that capture the essence of complex research.
            
            You have access to a Multi-Strategy Retrieval tool with THREE search methods:
            1. DENSE (semantic): Use for conceptual queries, understanding meaning
            2. SPARSE (BM25): Use for exact terms, acronyms, specific keywords  
            3. HYBRID: Best of both - recommended for most searches
            
            Use strategy='hybrid' by default for balanced results.""",
            verbose=True,
            max_rpm=10,
            llm=self.llm,
            tools=[RetrievalTool(chroma_persist_directory=self.state.chroma_persist_directory)]
        )
        
        filtered_pubs = self.state.filtered_publications if self.state.filtered_publications else "No filtered publications available."
        
        process_task = Task(
            description=f"""HERE ARE THE FILTERED PUBLICATIONS TO PROCESS:
                {filtered_pubs}

                YOUR TASK:
                Extract and synthesize key information from ONLY the filtered publications listed above.
                For each publication, identify: main research questions, methodologies,
                key findings, limitations, implications, and relevance to {self.state.topic}.
                Organize the information thematically and identify patterns, trends,
                and knowledge gaps across the literature.

                CRITICAL: Use ONLY the publications provided above. Do NOT add or invent new publications.""",
            expected_output="""A well-organized synthesis document containing: thematic categorization
            of research, key findings summary, methodological approaches overview,
            identified research gaps, and emerging trends in the field. Include
            proper citations for all referenced material.
            
            IMPORTANT: Reference ONLY the publications that were provided in the task description.""",
            agent=content_processor,
            output_file="output/03_processed_content.md"
        )
        
        processing_crew = Crew(
            agents=[content_processor],
            tasks=[process_task],
            process=Process.sequential,
            verbose=True,
            
        )
        
        result = processing_crew.kickoff()
        
        self.state.processed_content = result.raw
        self.state.current_step = "writing"

        print("Publications processed and synthesized")
        return "Publications processed and synthesized"

    @listen(or_(process_publications, "continue_writing"))
    def write_chapter(self):
        """Step 4: Write or revise the chapter based on feedback"""
        
        is_revision = self.state.iteration_count > 0
        
        chapter_writer = Agent(
            role="Academic Chapter Writer and Reviser" if is_revision else "Academic Chapter Writer",
            goal=f"Write comprehensive, well-structured related works chapter on {self.state.topic} based on processed research findings",
            backstory="""You are an accomplished academic writer with extensive experience in
            scholarly publishing. You have a talent for synthesizing complex research
            into clear, coherent narrative that follows academic writing standards
            and engages readers while maintaining scientific rigor.
            
            You have access to a Multi-Strategy Retrieval tool with THREE search methods:
            1. DENSE (semantic): For conceptual/thematic searches
            2. SPARSE (BM25): For exact terms, author names, specific keywords
            3. HYBRID: Best results combining both (RECOMMENDED)
            
            When looking up citations, use strategy='sparse' for exact author/title matching.
            For broader topics, use strategy='hybrid'.""",
            verbose=True,
            allow_delegation=False,
            max_iter=15,
            max_rpm=10,
            llm=self.llm,
            tools=[RetrievalTool(chroma_persist_directory=self.state.chroma_persist_directory)]
        )
        
        if is_revision:
            task_description = f"""Revise and improve the chapter based on the evaluation feedback.
            Address all identified issues including: improving argumentation,
            enhancing clarity, adding missing information, missing citations, 
            missing references, strengthening conclusions, improving transitions 
            between sections, and ensuring proper academic tone throughout. Implement 
            all constructive feedback while maintaining the chapter's core contribution. 
            Keep it short and concise, ideally within the initial word count of 800-1000 words.
            
            Current Score: {self.state.evaluation.score}/10
            Target Score: {self.state.target_score}/10
            
            Specific Feedback to Address:
            {self.state.evaluation.feedback}
            
            Chapter to Revise:
            {self.state.first_draft}"""
            expected_output = f"""A revised, high-quality academic related works chapter that addresses all evaluation
            feedback and aims to achieve a score of {self.state.target_score}/10. Return only the final result."""
            output_file = f"output/05_chapter_revision_iteration_{self.state.iteration_count}.md"
        else:
            task_description = f"""HERE IS THE PROCESSED RESEARCH CONTENT TO USE:
                {self.state.processed_content}

                YOUR TASK:
                Write a concise academic Related Works chapter on {self.state.topic} based ONLY on the 
                processed research findings provided above. The chapter should include: a short introduction that 
                outlines the purpose and scope of the chapter, a thematically organized comparison 
                of relevant literature, a critical discussion of the current state of the art of the topic 
                {self.state.topic}. Compare the authors' approaches, results, and limitations, and an explicit 
                identification of research gaps. Conclude with a synthesis that highlights how the
                highlighted works inform the present study and point to directions for future research.
                Add a bibliography with full citations in APA format only at the end.

                CRITICAL: Use ONLY the publications and information from the processed content above.
                Do NOT add new publications or sources that were not in the processed content.
                Follow academic writing standards with proper citations and references conforming to APA Standards.
                Always include the DOI-URL or URL, if it's a web resource. Only answer with the final result."""
            expected_output = """A complete academic related works chapter between 800 and 1000 words with proper structure:
                introduction, thematic main sections with subsections, proper inline citations in APA, conclusions,
                and bibliography. Written in formal academic style with clear argumentation
                and comprehensive coverage of the topic.
                Start with #Related Work and end with #Bibliography.
                IMPORTANT: Reference ONLY publications from the provided processed content. 
                Do NOT add or cite publications that were not in the processed content."""
            output_file = "output/chapter_initial_draft.md"
  
        write_task = Task(
            description=task_description,
            expected_output=expected_output,
            agent=chapter_writer,
            output_file=output_file
        )
        
        writing_crew = Crew(
            agents=[chapter_writer],
            tasks=[write_task],
            process=Process.sequential,
            verbose=True,
            
        )
        
        try:
           
            result = writing_crew.kickoff()
         
            if not result or not result.raw or len(result.raw.strip()) < 100:
                raise ValueError("Writing crew returned empty result")
                
            self.state.first_draft = result.raw
        except Exception as e:
            raise
        self.state.current_step = "evaluation"
        
        if is_revision:
            return f"Chapter revised - iteration {self.state.iteration_count}"
        else:
            return "Chapter first draft completed"

    @listen(write_chapter)
    def evaluate_chapter(self):
        
        previous_score = self.state.evaluation.score if self.state.iteration_count > 0 else 0.0
   
        iteration_context = ""
        if self.state.iteration_count > 0:
            iteration_context = f"This is iteration {self.state.iteration_count} of the revision process.\nPrevious score was: {previous_score}/10\n"
        
        evaluation_prompt = f"""
            You are an academic reviewer evaluating the Related Work chapter of a research paper.
            Your goal is to assess the quality of the chapter on the topic "{self.state.topic}" according to the criteria below.
            {iteration_context}
            For each criterion:
            Provide a numerical rating (1–10), where 1 = very poor and 10 = excellent.
            Add a short justification (2–3 sentences).
            At the end, calculate the average score and provide a final summary (5–7 sentences) that synthesizes your evaluation.
            
            IMPORTANT: Format your response EXACTLY as follows:
            
            COMPREHENSIVENESS: [score 1-10]
            [justification]
            
            RELEVANCE: [score 1-10]
            [justification]
            
            ORGANIZATION: [score 1-10]
            [justification]
            
            CRITICAL_ANALYSIS: [score 1-10]
            [justification]
            
            CLARITY: [score 1-10]
            [justification]
            
            CITATION_QUALITY: [score 1-10]
            [justification]
            
            OVERALL_SCORE: [average score]
            PASSED: [true/false - True if score >= 8.0]
            
            SUMMARY:
            [Your detailed summary and recommendations]

            Chapter to evaluate:
            {self.state.first_draft}
        """
        
        evaluator_llm = self.llm
        
        try:
            import re
            evaluation_result = evaluator_llm.call(evaluation_prompt)

            if isinstance(evaluation_result, str):
                response_text = evaluation_result
            else:
                response_text = str(evaluation_result)
            
            score_match = re.search(r'OVERALL_SCORE:\s*(\d+(?:\.\d+)?)', response_text)
            passed_match = re.search(r'PASSED:\s*(true|false)', response_text, re.IGNORECASE)
            summary_match = re.search(r'SUMMARY:\s*(.*?)$', response_text, re.DOTALL | re.MULTILINE)
            
            if score_match:
                score = float(score_match.group(1))
                passed = passed_match.group(1).lower() == 'true' if passed_match else score >= 9.0
                feedback = summary_match.group(1).strip() if summary_match else "Evaluation completed"
                
                self.state.evaluation = QualityAssessment(
                    score=min(max(score, 0.0), 10.0),
                    feedback=feedback,
                    passed=passed
                )
            else:
                raise ValueError("Could not parse OVERALL_SCORE from response")
            try:
                with open("output/evaluation.json", "a", encoding="utf-8") as f:
                    f.write(f"Iteration {self.state.iteration_count}:\n")
                    f.write(f"Score: {self.state.evaluation.score}\n")
                    f.write(f"Passed: {self.state.evaluation.passed}\n")
                    f.write(f"Feedback: {self.state.evaluation.feedback}\n")
                    f.write("\n" + "-" * 50 + "\n")
            except:
                pass
            
        except Exception as e:
            fallback_score = max(previous_score + 0.5, 6.5) if self.state.iteration_count > 0 else 6.5
            self.state.evaluation = QualityAssessment(
                score=min(fallback_score, 10.0),
                feedback=f"Text evaluation failed: {str(e)}. Using fallback score.",
                passed=False
            )
        
        self.state.current_step = "decision"
        


        print(f"Chapter evaluated - Score: {self.state.evaluation.score}/10")
        print(f"Target: {self.state.target_score}/10")
        
        return f"Chapter evaluated with score {self.state.evaluation.score}"

    @router(evaluate_chapter)
    def quality_decision_router(self):    
        if self.state.evaluation.score >= self.state.target_score:
            return "finalize"
        elif self.state.iteration_count >= self.state.max_iterations:
            return "finalize"
        else:
            self.state.iteration_count += 1
            try:
                import os, datetime
                os.makedirs("output", exist_ok=True)
                with open("output/iteration_count.json", "a", encoding="utf-8") as lf:
                    lf.write(f"iteration #{self.state.iteration_count}, score: {self.state.evaluation.score}\n")
            except Exception:
                pass
            return "continue_writing"

    @listen("finalize")
    def finalize_chapter(self):
        self.state.final_chapter = self.state.first_draft
        self._save_chapter("output/final_related_work.md", self.state.final_chapter)

        if self.state.evaluation.score >= self.state.target_score:
            print(f"SUCCESS! Target achieved - Score: {self.state.evaluation.score}/10")
        else:
            print(f"Max iterations reached - Final score: {self.state.evaluation.score}/10")
        
        self.state.current_step = "completed"
        return "Chapter finalized"

    def _save_chapter(self, filename: str, content: str):
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Chapter saved to {filename}")

def kickoff():
    flow = ResearchFlow()
    result = flow.kickoff()
    print(f"\nFlow completed with result: {result}")
    return result


def plot():
    flow = ResearchFlow()
    flow.plot("research_flow_diagram")
    print("Flow diagram saved as research_flow_diagram.html")

if __name__ == "__main__":
    kickoff()
