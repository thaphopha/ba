#!/usr/bin/env python

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json

from crewai.flow.flow import Flow, listen, router, start, or_
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import TavilySearchTool

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
    
    current_step: str = "initialized"
    iteration_count: int = 0
    max_iterations: int = 5
    
    collected_publications: str = ""
    filtered_publications: str = ""
    processed_content: str = ""
    first_draft: str = ""
    evaluation: QualityAssessment = Field(default_factory=lambda: QualityAssessment())
    final_chapter: str = ""
    
    target_score: float = 8.0


class ResearchFlow(Flow[ScientificResearchState]):
    """
    Workflow:
    1. Sammeln von wissenschaftlichen Publikationen (Collect Publications)
    2. Filtern der Publikationen (Filter Publications)
    3. Aufbereiten der Publikationen (Process Publications)
    4. Schreiben des Kapitels (Write Chapter)
    5. Bewertung des Kapitels (Evaluate Chapter)
    6. Letzter Feinschliff (Final Revision) - with feedback loop
    """

    def __init__(self):
        super().__init__()
        self.llm=LLM(model="gemini/gemini-2.0-flash", temperature=0.3)
        self._ensure_output_directories()
        
    def _ensure_output_directories(self):
        import os
        for directory in ["logs", "output"]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
           
    @start()
    def initialize_research_parameters(self):
        
        self.state.topic = "Model Context Protocol (MCP)"
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
            backstory="""You are an experienced research librarian with expertise in academic databases.
            You excel at finding comprehensive sets of scientific publications using
            advanced search strategies across multiple platforms like PubMed, IEEE,
            ACM Digital Library, Google Scholar, and specialized domain databases.""",
            verbose=True,
            tools=[TavilySearchTool()],
            max_rpm=14
        )
        
        collect_task = Task(
            description=f"""Conduct a comprehensive search for scientific publications related to {self.state.topic}.
            Search across multiple academic databases including PubMed, IEEE Xplore,
            ACM Digital Library, Google Scholar, and relevant domain-specific databases.
            Use advanced search strategies with appropriate keywords, Boolean operators,
            and filters. Focus on publications from the last {self.state.timeframe} years.""",
            expected_output="""A comprehensive list of relevant scientific publications with complete
            bibliographic information including titles, authors, journals, publication
            years, DOIs, abstracts, and access links. Minimum 25 publications
            depending on topic scope. Return as a JSON list of publications.""",
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
            max_rpm=14
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
            output_file="output/02_filtered_publications.json"
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

        print(f"Publications filtered")
        print(f"Stored {len(self.state.filtered_publications)} characters in filtered state")
        return f"Filtered publications stored"

    @listen(filter_publications)
    def process_publications(self):

        content_processor = Agent(
            role="Academic Content Processor and Synthesizer",
            goal=f"Extract, organize, and synthesize key information from filtered publications on {self.state.topic}",
            backstory="""You are a research analyst specialized in academic content processing.
            You excel at extracting key findings, methodologies, and insights from
            scientific papers and organizing them into coherent, well-structured
            summaries that capture the essence of complex research.""",
            verbose=True,
            max_rpm=14
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

        is_revision = self.state.iteration_count > 0
        
        if is_revision:
            print(f"Revision {self.state.iteration_count}: Improving chapter based on feedback...")
        else:
            print("Step 4: Writing the related works chapter...")
        
        chapter_writer = Agent(
            role="Academic Chapter Writer and Reviser" if is_revision else "Academic Chapter Writer",
            goal=f"Write comprehensive, well-structured related works chapter on {self.state.topic} based on processed research findings",
            backstory="""You are an accomplished academic writer with extensive experience in
            scholarly publishing. You have a talent for synthesizing complex research
            into clear, coherent narrative that follows academic writing standards
            and engages readers while maintaining scientific rigor.""",
            verbose=True,
            max_rpm=14
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
            introduction, thematic main sections with subsections, conclusions,
            and references. Written in formal academic style with clear argumentation
            and comprehensive coverage of the topic.
            
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
        
        result = writing_crew.kickoff()
        
        self.state.first_draft = result.raw
        self.state.current_step = "evaluation"
        
        if is_revision:
            print(f"Chapter revised (Iteration {self.state.iteration_count})")
            return f"Chapter revised - iteration {self.state.iteration_count}"
        else:
            print("First draft of chapter completed")
            return "Chapter first draft completed"

    @listen(write_chapter)
    def evaluate_chapter(self):   
        if self.state.iteration_count == 0:
            print("Step 5: Evaluating chapter quality...")
        else:
            print(f"Re-evaluating revised chapter (Iteration {self.state.iteration_count})...")
        
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
            
            Evaluation Criteria:
            Comprehensiveness (1–10):
            How well does the chapter cover the breadth of relevant literature? Are important works included?
            Relevance (1–10):
            Are the cited works clearly related to the research problem? Does the chapter avoid irrelevant or tangential references?
            Organization & Structure (1–10):
            Is the literature grouped logically (e.g., by theme, method, or chronology)? Does the flow help the reader understand the research landscape?
            Critical Analysis (1–10):
            Does the author go beyond summarizing papers to compare, contrast, and highlight gaps or trends?
            Clarity & Readability (1–10):
            Is the writing clear, concise, and accessible? Does it avoid unnecessary jargon or confusion?
            Citation Quality & Accuracy (1–10):
            Are sources reliable, up-to-date, and cited correctly? Are key foundational and recent works included?
            Final Steps:
            Compute the average score across all criteria.
            Set passed to true if overall_score >= {self.state.target_score}, otherwise false.
            Provide detailed, actionable feedback for improvement.

            Chapter to evaluate:
            {self.state.first_draft}
        """
        
        evaluator_llm = LLM(
            model="gemini/gemini-2.0-flash",
            temperature=0.3,
            response_format=QualityAssessment
        )
        
        try:
            import json
            evaluation_result = evaluator_llm.call(evaluation_prompt)
            
            if isinstance(evaluation_result, str):
                eval_data = json.loads(evaluation_result)
                self.state.evaluation = QualityAssessment(**eval_data)
            else:
                self.state.evaluation = QualityAssessment(**evaluation_result)
            
            try:
                with open("output/evaluation.json", "a", encoding="utf-8") as f:
                    f.write(f"Iteration {self.state.iteration_count}:\n")
                    json.dump(self.state.evaluation.model_dump(), f, indent=2)
                    f.write("\n" + "-" * 50 + "\n")
            except:
                pass
            
            print(f"Structured evaluation received - Score: {self.state.evaluation.score}/10")
            
        except Exception as e:

            fallback_score = max(previous_score + 0.5, 6.5) if self.state.iteration_count > 0 else 6.5
            self.state.evaluation = QualityAssessment(
                score=min(fallback_score, 10.0),
                feedback=f"Structured evaluation failed: {str(e)}. Using fallback score.",
                passed=False
            )
        
        self.state.current_step = "decision"
        
        if self.state.iteration_count > 0:
            print(f"Score improvement: {previous_score} -> {self.state.evaluation.score}")

        print(f"Chapter evaluated - Score: {self.state.evaluation.score}/10")
        print(f"Target: {self.state.target_score}/10")
        
        return f"Chapter evaluated with score {self.state.evaluation.score}"

    @router(evaluate_chapter)
    def quality_decision_router(self):
        """Router to decide next action based on evaluation"""
        print(f"Quality Decision - Current Score: {self.state.evaluation.score}")
        print(f"Iteration: {self.state.iteration_count}/{self.state.max_iterations}")
        
        if self.state.evaluation.score >= self.state.target_score:
            print("Target quality achieved!")
            return "finalize"
        elif self.state.iteration_count >= self.state.max_iterations:
            print("Max iterations reached - finalizing with current score")
            return "finalize"
        else:
            print("Quality improvement needed - routing back to write_chapter for revision")
            self.state.iteration_count += 1
            print(f"Routing to revision: iteration set to {self.state.iteration_count}")
            try:
                import os
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
    print("Starting Scientific Research Flow with Evaluator-Optimizer Loop")
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
