#!/usr/bin/env python

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from crewai.flow.flow import Flow, listen, router, start, or_
from crewai import Agent, Task, Crew, Process, LLM

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
    max_iterations: int = 100
    
    collected_publications: str = ""
    filtered_publications: str = ""
    processed_content: str = ""
    first_draft: str = ""
    evaluation: QualityAssessment = Field(default_factory=lambda: QualityAssessment())
    final_chapter: str = ""
    
    target_score: float = 100.0


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
        self._ensure_logs_directory()
        self.llm=LLM(model="gemini/gemini-2.0-flash", temperature=0.3)
        
    def _ensure_logs_directory(self):
        import os
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            print(f"Created logs directory: {logs_dir}")
        
    @start()
    def initialize_research_parameters(self):
        
        self.state.topic = "Conformance Testing of REST-based Web Services"
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
            depending on topic scope.""",
            agent=publication_collector
        )
        
        # Create and run crew
        collection_crew = Crew(
            agents=[publication_collector],
            tasks=[collect_task],
            process=Process.sequential,
            verbose=True,
            output_log_file="output/publication_collection.json"
        )
        
        result = collection_crew.kickoff()
        
        self.state.current_step = "filtering"

    @listen(collect_publications)
    def filter_publications(self):
        """Step 2: Filtern der Publikationen"""
        print("Step 2: Filtering and quality assessment of publications...")
        
        # Create publication filter agent
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
        
        # Create filtering task
        filter_task = Task(
            description=f"""Review and filter the collected publications based on relevance, quality,
            and methodological rigor. Evaluate each publication using criteria such as:
            journal impact factor, citation count, peer review status, methodology
            quality, relevance to {self.state.topic}, and publication recency. Exclude any publication
            that you find not relevant to the topic {self.state.topic}""",
            expected_output="""A curated list of 10-15 high-quality, relevant publications with quality
            ratings and brief justifications for inclusion. Include ranking based on
            relevance and impact.""",
            agent=publication_filter
        )
        
        # Create and run crew
        filtering_crew = Crew(
            agents=[publication_filter],
            tasks=[filter_task],
            process=Process.sequential,
            verbose=True,
            output_log_file="logs/publication_filtering.json"
        )
        
        result = filtering_crew.kickoff()

        self.state.current_step = "processing"

        return f"Filtered to {len(self.state.filtered_publications)} publications"

    @listen(filter_publications)
    def process_publications(self):
        """Step 3: Aufbereiten der Publikationen"""
        print("Step 3: Processing and synthesizing publication content...")
        
        # Create content processor agent
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
        
        # Create processing task
        process_task = Task(
            description=f"""Extract and synthesize key information from the filtered publications.
            For each publication, identify: main research questions, methodologies,
            key findings, limitations, implications, and relevance to {self.state.topic}.
            Organize the information thematically and identify patterns, trends,
            and knowledge gaps across the literature.""",
            expected_output="""A well-organized synthesis document containing: thematic categorization
            of research, key findings summary, methodological approaches overview,
            identified research gaps, and emerging trends in the field. Include
            proper citations for all referenced material.""",
            agent=content_processor
        )
        
        # Create and run crew
        processing_crew = Crew(
            agents=[content_processor],
            tasks=[process_task],
            process=Process.sequential,
            verbose=True,
            output_log_file="logs/content_processing.json"
        )
        
        result = processing_crew.kickoff()
        
        self.state.processed_content = result.raw
        self.state.current_step = "writing"

        print("Publications processed and synthesized")
        return "Publications processed and synthesized"

    @listen(or_(process_publications, "continue_writing"))
    def write_chapter(self):
        """Step 4: Write or revise the chapter based on feedback"""
        
        # Check if this is initial writing or revision
        is_revision = self.state.iteration_count > 0
        
        if is_revision:
            print(f"Revision {self.state.iteration_count}: Improving chapter based on feedback...")
        else:
            print("Step 4: Writing the related works chapter...")
        
        # Create chapter writer agent
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
        
        # Build task description based on whether this is revision or initial writing
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
            log_file = f"logs/chapter_revision_iteration_{self.state.iteration_count}.md"
        else:
            task_description = f"""Write a concise academic Related Works chapter on {self.state.topic} based on the 
            processed research findings. The chapter should include: a short introduction that 
            outlines the purpose and scope of the chapter, a thematically organized comparison 
            of relevant literature, a critical discussion of the current state of the art of the topic 
            {self.state.topic}. Compare the authors' approaches, results, and limitations, and an explicit 
            identification of research gaps. Conclude with a synthesis that highlights how the
            highlighted works inform the present study and point to directions for future research.
            Follow academic writing standards with proper citations and references conforming to APA Standards
            Always include the DOI or URL, if it's a web resource. Only answer with the final result."""
            expected_output = """A complete academic related works chapter between 800 and 1000 words with proper structure:
            introduction, thematic main sections with subsections, conclusions,
            and references. Written in formal academic style with clear argumentation
            and comprehensive coverage of {self.state.topic}."""
            log_file = "logs/chapter_writing.json"
        
        # Create writing task
        write_task = Task(
            description=task_description,
            expected_output=expected_output,
            agent=chapter_writer
        )
        
        # Create and run crew
        writing_crew = Crew(
            agents=[chapter_writer],
            tasks=[write_task],
            process=Process.sequential,
            verbose=True,
            output_log_file=log_file
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
        
        # Store previous score for comparison
        previous_score = self.state.evaluation.score if self.state.iteration_count > 0 else 0.0
        
        # Build iteration context
        iteration_context = ""
        if self.state.iteration_count > 0:
            iteration_context = f"This is iteration {self.state.iteration_count} of the revision process.\nPrevious score was: {previous_score}/10\n"
        
        # Create evaluation prompt
        evaluation_prompt = f"""
            You are a senior academic editor with decades of experience in scholarly publishing and peer review.
            Evaluate the following academic related works chapter on the topic "{self.state.topic}".
            {iteration_context}
            Evaluate based on these criteria (score each 0-10):
            1. Academic Writing Quality (clarity, flow, style)
            2. Literature Coverage (comprehensiveness, relevance)
            3. Critical Analysis (depth of analysis, comparison)
            4. Structure and Organization (logical flow, clear sections)
            5. Citation Quality (proper format, complete references)
            6. Research Gap Identification (clear gaps identified)
            7. Coherence and Argumentation (logical consistency)

            Calculate the overall_score as the average of all criteria scores.
            Set passed to true if overall_score >= 9.0, otherwise false.
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
            # Get structured evaluation - parse the response as QualityAssessment
            import json
            evaluation_result = evaluator_llm.call(evaluation_prompt)
            
            # Parse the response into QualityAssessment model
            if isinstance(evaluation_result, str):
                eval_data = json.loads(evaluation_result)
                self.state.evaluation = QualityAssessment(**eval_data)
            else:
                # If it's already parsed (some LLM clients do this)
                self.state.evaluation = QualityAssessment(**evaluation_result)
            
            # Save evaluation for audit
            try:
                with open("logs/evaluation.json", "a", encoding="utf-8") as f:
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
                import os, datetime
                os.makedirs("logs", exist_ok=True)
                with open("logs/iteration_count.log", "a", encoding="utf-8") as lf:
                    lf.write(f"iteration #{self.state.iteration_count}, score: {self.state.evaluation.score}\n")
            except Exception:
                # Don't let logging interfere with flow logic
                pass
            return "continue_writing"

    @listen("finalize")
    def finalize_chapter(self):
        
        print("Finalizing chapter...")
        
        
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
    """Main function to run the scientific research flow"""
    print("Starting Scientific Research Flow with Evaluator-Optimizer Loop")
    flow = ResearchFlow()
    result = flow.kickoff()
    print(f"\nFlow completed with result: {result}")
    return result


def plot():
    """Generate flow diagram"""
    flow = ResearchFlow()
    flow.plot("research_flow_diagram")
    print("Flow diagram saved as research_flow_diagram.html")


if __name__ == "__main__":
    kickoff()
