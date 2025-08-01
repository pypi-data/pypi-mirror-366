"""
ResearchPlanner Module
=====================

This module is responsible for planning and organizing research tasks, timelines,
and methodologies.
"""

from typing import List, Dict

class ResearchPlanner:
    """
    Class for planning and organizing research tasks.
    """
    
    def __init__(self):
        self.tasks: List[str] = []
        self.timeline: Dict[str, str] = {}

    def add_task(self, task: str) -> None:
        """
        Add a research task to the planner.
        """
        self.tasks.append(task)

    def set_timeline(self, task: str, deadline: str) -> None:
        """
        Set a deadline for a specific task.
        """
        if task in self.tasks:
            self.timeline[task] = deadline

    def view_tasks(self) -> List[str]:
        """
        Return a list of all planned tasks.
        """
        return self.tasks

    def view_timeline(self) -> Dict[str, str]:
        """
        Return the timeline with deadlines for each task.
        """
        return self.timeline

