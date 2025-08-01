"""
ResearchTemplates Module
=======================

This module provides templates and guide generation for research methodologies, reports, and more.
"""

from typing import List

class ResearchTemplates:
    """
    Class for generating research templates and guides.
    """

    @staticmethod
    def generate_template(template_name: str) -> str:
        """
        Generate a research template based on the given name.
        """
        templates = {
            "proposal": """# Research Proposal Template

## Title

## Abstract

## Introduction

## Objectives

## Methodology

## Expected Results

## References
""",
            "report": """# Research Report Template

## Title

## Abstract

## Introduction

## Results

## Discussion

## Conclusion

## References
"""

            # More templates can be added here
        }

        return templates.get(template_name, "Template not found")

