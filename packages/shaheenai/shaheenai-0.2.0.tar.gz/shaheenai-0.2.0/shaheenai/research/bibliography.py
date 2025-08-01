"""
BibliographyManager Module
=========================

This module provides functionality for managing bibliographic data and integrating
citation management systems like BibTeX.
"""

from typing import List, Dict

class BibliographyManager:
    """
    Class for managing bibliography and citations.
    """

    def __init__(self):
        self.entries: List[Dict[str, str]] = []

    def add_entry(self, entry: Dict[str, str]) -> None:
        """
        Add a bibliographic entry.
        """
        self.entries.append(entry)

    def get_entries(self) -> List[Dict[str, str]]:
        """
        Get all bibliographic entries.
        """
        return self.entries

    def export_bibtex(self, file_path: str) -> None:
        """
        Export the bibliography to a BibTeX file.
        """
        with open(file_path, 'w') as bibfile:
            for entry in self.entries:
                bibfile.write(f"@{entry['type']}{{{entry['key']},\n")
                for key, value in entry.items():
                    if key not in ['type', 'key']:
                        bibfile.write(f"  {key} = {{{value}}},\n")
                bibfile.write("}\n\n")

