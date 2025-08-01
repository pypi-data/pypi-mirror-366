"""
Main Chemical Analyzer Module

Provides the primary interface for molecular analysis with Discovery Studio accuracy.
"""

from typing import List, Optional, Union
import logging
from pathlib import Path

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski, QED
    from rdkit.Chem.rdMolDescriptors import CalcTPSA, CalcNumRotatableBonds
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logging.warning("RDKit not available. Some features will be limited.")

from .properties import MolecularProperties
from .rules import ADMETRules
from .results import AnalysisResult, BatchResult
from .utils import smiles_to_mol, validate_smiles


class ChemicalAnalyzer:
    """
    Main chemical analyzer class providing comprehensive molecular analysis.
    
    Features:
    - Accurate molecular property calculations
    - Complete ADMET rules analysis
    - Batch processing capabilities
    - Discovery Studio-level accuracy
    """
    
    def __init__(self, use_cached_descriptors: bool = True):
        """
        Initialize the ChemicalAnalyzer.
        
        Args:
            use_cached_descriptors: Whether to cache descriptor calculations for performance
        """
        if not RDKIT_AVAILABLE:
            raise ImportError(
                "RDKit is required for ChemicalAnalyzer. "
                "Install with: pip install rdkit-pypi"
            )
        
        self.properties_calculator = MolecularProperties()
        self.rules_analyzer = ADMETRules()
        self.use_cached_descriptors = use_cached_descriptors
        self._descriptor_cache = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_smiles(self, smiles: str) -> AnalysisResult:
        """
        Analyze a single SMILES string.
        
        Args:
            smiles: SMILES notation string
            
        Returns:
            AnalysisResult object containing all calculated properties and rules
            
        Raises:
            ValueError: If SMILES is invalid
        """
        if not validate_smiles(smiles):
            raise ValueError(f"Invalid SMILES string: {smiles}")
        
        mol = smiles_to_mol(smiles)
        if mol is None:
            raise ValueError(f"Could not parse SMILES: {smiles}")
        
        return self.analyze_mol(mol, smiles)
    
    def analyze_mol(self, mol: 'Chem.Mol', smiles: Optional[str] = None) -> AnalysisResult:
        """
        Analyze an RDKit Mol object.
        
        Args:
            mol: RDKit Mol object
            smiles: Optional SMILES string (will be generated if not provided)
            
        Returns:
            AnalysisResult object containing all calculated properties and rules
        """
        if mol is None:
            raise ValueError("Invalid molecule object")
        
        if smiles is None:
            smiles = Chem.MolToSmiles(mol)
        
        # Calculate molecular properties
        properties = self.properties_calculator.calculate_all(mol)
        
        # Analyze ADMET rules
        rules = self.rules_analyzer.analyze_all(properties)
        
        # Create result object
        result = AnalysisResult(
            smiles=smiles,
            mol=mol,
            properties=properties,
            rules=rules
        )
        
        return result
    
    def analyze_batch(self, smiles_list: List[str], 
                     progress_bar: bool = True) -> BatchResult:
        """
        Analyze multiple SMILES strings.
        
        Args:
            smiles_list: List of SMILES strings
            progress_bar: Whether to show progress bar
            
        Returns:
            BatchResult object containing all analysis results
        """
        results = []
        failed = []
        
        if progress_bar:
            try:
                from tqdm import tqdm
                iterator = tqdm(smiles_list, desc="Analyzing compounds")
            except ImportError:
                iterator = smiles_list
                self.logger.info(f"Analyzing {len(smiles_list)} compounds...")
        else:
            iterator = smiles_list
        
        for i, smiles in enumerate(iterator):
            try:
                result = self.analyze_smiles(smiles)
                results.append(result)
            except Exception as e:
                self.logger.warning(f"Failed to analyze SMILES {smiles}: {e}")
                failed.append((i, smiles, str(e)))
        
        return BatchResult(
            results=results,
            failed=failed,
            total_processed=len(smiles_list)
        )
    
    def analyze_sdf(self, sdf_file: Union[str, Path]) -> BatchResult:
        """
        Analyze compounds from an SDF file.
        
        Args:
            sdf_file: Path to SDF file
            
        Returns:
            BatchResult object containing all analysis results
        """
        sdf_file = Path(sdf_file)
        if not sdf_file.exists():
            raise FileNotFoundError(f"SDF file not found: {sdf_file}")
        
        results = []
        failed = []
        
        try:
            supplier = Chem.SDMolSupplier(str(sdf_file))
            
            for i, mol in enumerate(supplier):
                if mol is None:
                    failed.append((i, "N/A", "Could not parse molecule"))
                    continue
                
                try:
                    result = self.analyze_mol(mol)
                    results.append(result)
                except Exception as e:
                    smiles = Chem.MolToSmiles(mol) if mol else "N/A"
                    failed.append((i, smiles, str(e)))
        
        except Exception as e:
            raise ValueError(f"Error reading SDF file: {e}")
        
        return BatchResult(
            results=results,
            failed=failed,
            total_processed=len(results) + len(failed)
        )
    
    def calculate_drug_likeness_score(self, result: AnalysisResult) -> float:
        """
        Calculate overall drug-likeness score based on multiple rules.
        
        Args:
            result: AnalysisResult object
            
        Returns:
            Drug-likeness score (0-1, higher is better)
        """
        # Weight different rules based on importance
        weights = {
            'lipinski': 0.25,
            'veber': 0.20,
            'ghose': 0.15,
            'egan': 0.15,
            'muegge': 0.10,
            'cns_mpo': 0.10,
            'reos': 0.05
        }
        
        score = 0.0
        for rule_name, weight in weights.items():
            if hasattr(result.rules, rule_name):
                rule_result = getattr(result.rules, rule_name)
                # Convert pass/fail to score (1.0 for pass, 0.0 for fail)
                rule_score = 1.0 if rule_result.passed else 0.0
                score += weight * rule_score
        
        return score
    
    def get_violation_summary(self, result: AnalysisResult) -> dict:
        """
        Get summary of rule violations.
        
        Args:
            result: AnalysisResult object
            
        Returns:
            Dictionary with violation counts and details
        """
        violations = {}
        total_violations = 0
        
        for rule_name in ['lipinski', 'veber', 'ghose', 'egan', 'muegge', 
                         'rule_of_3', 'cns_mpo', 'bro5', 'pfizer_3_75', 
                         'gsk_4_400', 'lead_likeness', 'reos']:
            if hasattr(result.rules, rule_name):
                rule_result = getattr(result.rules, rule_name)
                violations[rule_name] = {
                    'passed': rule_result.passed,
                    'violations': rule_result.violations,
                    'details': rule_result.details
                }
                total_violations += rule_result.violations
        
        return {
            'total_violations': total_violations,
            'rules_failed': sum(1 for v in violations.values() if not v['passed']),
            'rules_passed': sum(1 for v in violations.values() if v['passed']),
            'details': violations
        }