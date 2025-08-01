"""
Optimus Chem - Comprehensive Chemical Analysis Package

A Python package for accurate molecular property calculations and ADMET rules analysis.
Provides Discovery Studio-level accuracy for drug discovery applications.
"""

__version__ = "1.0.0"
__author__ = "Pritam"
__email__ = "pritam@stanford.edu"

from .analyzer import ChemicalAnalyzer
from .properties import MolecularProperties
from .rules import ADMETRules
from .results import AnalysisResult, BatchResult, RuleResult
from .utils import smiles_to_mol, mol_to_smiles, standardize_smiles

__all__ = [
    "ChemicalAnalyzer",
    "MolecularProperties", 
    "ADMETRules",
    "AnalysisResult",
    "BatchResult", 
    "RuleResult",
    "smiles_to_mol",
    "mol_to_smiles",
    "standardize_smiles",
]