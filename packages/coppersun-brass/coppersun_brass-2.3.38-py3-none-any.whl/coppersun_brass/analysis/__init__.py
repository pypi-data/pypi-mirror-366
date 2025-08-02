"""
Analysis module for Copper Sun Brass.

Contains report generators for executive analysis and dashboards.
"""

from .brass_analysis_generator import BrassAnalysisGenerator
from .brass_yaml_generator import BrassYamlGenerator

__all__ = ['BrassAnalysisGenerator', 'BrassYamlGenerator']