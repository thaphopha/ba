from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Test1():
    """Academic Research and Chapter Writing Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def publication_collector(self) -> Agent:
        return Agent(
            config=self.agents_config['publication_collector'], # type: ignore[index]
            verbose=True
        )

    @agent
    def publication_filter(self) -> Agent:
        return Agent(
            config=self.agents_config['publication_filter'], # type: ignore[index]
            verbose=True
        )

    @agent
    def content_processor(self) -> Agent:
        return Agent(
            config=self.agents_config['content_processor'], # type: ignore[index]
            verbose=True
        )

    @agent
    def chapter_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['chapter_writer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def chapter_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['chapter_evaluator'], # type: ignore[index]
            verbose=True
        )

    @agent
    def chapter_reviser(self) -> Agent:
        return Agent(
            config=self.agents_config['chapter_reviser'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def collect_publications_task(self) -> Task:
        return Task(
            config=self.tasks_config['collect_publications_task'], # type: ignore[index]
        )

    @task
    def filter_publications_task(self) -> Task:
        return Task(
            config=self.tasks_config['filter_publications_task'], # type: ignore[index]
        )

    @task
    def process_publications_task(self) -> Task:
        return Task(
            config=self.tasks_config['process_publications_task'], # type: ignore[index]
        )

    @task
    def write_chapter_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_chapter_task'], # type: ignore[index]
        )

    @task
    def evaluate_chapter_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_chapter_task'], # type: ignore[index]
        )

    @task
    def revise_chapter_task(self) -> Task:
        return Task(
            config=self.tasks_config['revise_chapter_task'], # type: ignore[index]
            output_file='final_chapter.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Academic Research and Chapter Writing crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            # process=Process.sequential,
            verbose=True,
            process=Process.sequential,
            max_rpm=14, # 15 ist erlaubt mit gemini-2.0-flash
            output_log_file="logs/crew_execution_log.json",
        )
