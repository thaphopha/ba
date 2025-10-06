#!/usr/bin/env python

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from src.test2.research_flow import ResearchFlow

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="Scientific Research Server")

BASE_DIR = Path(__file__).resolve().parents[2]

@mcp.tool
async def do_scientific_research(
    ctx: Context,
    topic: str,
    timeframe: int = 5,
    max_pdfs_per_tool: int = 10,
    target_score: float = 8.0,
    max_iterations: int = 5
) -> dict:
    """
    Run a complete scientific research flow for literature review.
    
    Args:
        topic: Research topic to investigate
        timeframe: Years to look back for publications (default: 5)
        max_pdfs_per_tool: Maximum PDFs to collect per source tool (default: 10)
        target_score: Target quality score (0-10, default: 8.0)
        max_iterations: Maximum revision iterations (default: 5)
    
    Returns:
        dict with status, topic, score, and paths to outputs
    """
    
    try:
        logger.info(f"Starting research flow for topic: {topic}")
        
        flow = ResearchFlow()
        
        flow.state.topic = topic
        flow.state.timeframe = timeframe
        flow.state.max_pdfs_per_tool = max_pdfs_per_tool
        flow.state.target_score = target_score
        flow.state.max_iterations = max_iterations

        # Run synchronous flow.kickoff() in executor to avoid blocking async loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, flow.kickoff)

        logger.info(f"Final state: iterations={flow.state.iteration_count}, score={flow.state.evaluation.score}")
        
        output_dir = BASE_DIR / "output"
        final_chapter_path = output_dir / "final_related_work.md"
        
        return {
            "output_files": {
                "final_chapter": str(final_chapter_path),
            }
        }
        
    except Exception as e:
        logger.error(f"Research flow failed: {e}", exc_info=True)
        
        error_details = str(e)
        if hasattr(flow, 'state') and flow.state.final_chapter:
            error_details = flow.state.final_chapter
        
        return {
            "status": "failed",
            "error": str(e),
            "error_details": error_details,
            "topic": topic
        }


@mcp.resource("report://final_chapter")
async def get_final_chapter() -> str:
    """Get the final related work chapter (if available)"""
    chapter_path = BASE_DIR / "output" / "final_related_work.md"
    
    if not chapter_path.exists():
        return "No final chapter available yet."
    
    with open(chapter_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    logger.info("Starting Research MCP Server...")
    logger.info(f"Base directory: {BASE_DIR}")
    mcp.run(transport="http", host="0.0.0.0", port=9001)
