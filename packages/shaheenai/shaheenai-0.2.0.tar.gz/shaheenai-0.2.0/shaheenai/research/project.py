"""
ResearchProject Module
=====================

This module provides functionality for managing research projects, 
including project metadata, milestones, and deliverables.
"""

from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json
import os

@dataclass
class Milestone:
    """Represents a research milestone."""
    name: str
    description: str
    due_date: datetime
    completed: bool = False
    completion_date: Optional[datetime] = None

@dataclass 
class ResearchProject:
    """Main class for managing a research project."""
    
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    milestones: List[Milestone] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def add_milestone(self, name: str, description: str, due_date: datetime) -> None:
        """Add a new milestone to the project."""
        milestone = Milestone(name=name, description=description, due_date=due_date)
        self.milestones.append(milestone)
    
    def complete_milestone(self, milestone_name: str) -> bool:
        """Mark a milestone as completed."""
        for milestone in self.milestones:
            if milestone.name == milestone_name:
                milestone.completed = True
                milestone.completion_date = datetime.now()
                return True
        return False
    
    def add_note(self, note: str) -> None:
        """Add a research note to the project."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes.append(f"[{timestamp}] {note}")
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the project."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def get_progress(self) -> float:
        """Calculate project progress as percentage of completed milestones."""
        if not self.milestones:
            return 0.0
        completed = sum(1 for m in self.milestones if m.completed)
        return (completed / len(self.milestones)) * 100
    
    def get_upcoming_milestones(self, days: int = 7) -> List[Milestone]:
        """Get milestones due in the next specified days."""
        from datetime import timedelta
        cutoff_date = datetime.now() + timedelta(days=days)
        return [m for m in self.milestones 
                if not m.completed and m.due_date <= cutoff_date]
    
    def save_to_file(self, filepath: str) -> None:
        """Save project to JSON file."""
        project_dict = {
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'milestones': [
                {
                    'name': m.name,
                    'description': m.description,
                    'due_date': m.due_date.isoformat(),
                    'completed': m.completed,
                    'completion_date': m.completion_date.isoformat() if m.completion_date else None
                }
                for m in self.milestones
            ],
            'notes': self.notes,
            'tags': self.tags
        }
        
        with open(filepath, 'w') as f:
            json.dump(project_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'ResearchProject':
        """Load project from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        project = cls(
            name=data['name'],
            description=data['description'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            notes=data.get('notes', []),
            tags=data.get('tags', [])
        )
        
        for m_data in data.get('milestones', []):
            milestone = Milestone(
                name=m_data['name'],
                description=m_data['description'],
                due_date=datetime.fromisoformat(m_data['due_date']),
                completed=m_data.get('completed', False),
                completion_date=datetime.fromisoformat(m_data['completion_date']) 
                                if m_data.get('completion_date') else None
            )
            project.milestones.append(milestone)
        
        return project
    
    def generate_report(self) -> str:
        """Generate a comprehensive project report."""
        report = f"# Research Project Report: {self.name}\n\n"
        report += f"**Description:** {self.description}\n\n"
        report += f"**Duration:** {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}\n\n"
        report += f"**Progress:** {self.get_progress():.1f}% complete\n\n"
        
        if self.tags:
            report += f"**Tags:** {', '.join(self.tags)}\n\n"
        
        report += "## Milestones\n\n"
        for milestone in self.milestones:
            status = "✅" if milestone.completed else "⏳"
            report += f"- {status} **{milestone.name}** (Due: {milestone.due_date.strftime('%Y-%m-%d')})\n"
            report += f"  {milestone.description}\n"
            if milestone.completed and milestone.completion_date:
                report += f"  Completed: {milestone.completion_date.strftime('%Y-%m-%d')}\n"
            report += "\n"
        
        if self.notes:
            report += "## Research Notes\n\n"
            for note in self.notes[-10:]:  # Show last 10 notes
                report += f"- {note}\n"
            report += "\n"
        
        upcoming = self.get_upcoming_milestones()
        if upcoming:
            report += "## Upcoming Milestones (Next 7 Days)\n\n"
            for milestone in upcoming:
                report += f"- **{milestone.name}** - Due: {milestone.due_date.strftime('%Y-%m-%d')}\n"
        
        return report
