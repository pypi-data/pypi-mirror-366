"""
Research Planning Module for ShaheenAI
=====================================

This module provides comprehensive research planning and management capabilities,
including project organization, literature management, and research workflows.
"""

from .planner import ResearchPlanner
from .bibliography import BibliographyManager
from .project import ResearchProject
from .templates import ResearchTemplates

__all__ = [
    "ResearchPlanner",
    "BibliographyManager", 
    "ResearchProject",
    "ResearchTemplates"
]
