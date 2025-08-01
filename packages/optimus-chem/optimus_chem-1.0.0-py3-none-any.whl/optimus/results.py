"""
Results Classes

Data structures for storing and manipulating analysis results.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from rdkit import Chem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


@dataclass
class RuleResult:
    """Result of a single ADMET rule evaluation."""
    name: str
    purpose: str
    criteria: str
    passed: bool
    violations: int
    details: Dict[str, Any]
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'purpose': self.purpose,
            'criteria': self.criteria,
            'passed': self.passed,
            'violations': self.violations,
            'details': self.details,
            'score': self.score
        }


class AnalysisResult:
    """
    Complete analysis result for a single compound.
    
    Contains molecular properties, ADMET rule results, and convenience methods
    for accessing and interpreting the data.
    """
    
    def __init__(self, smiles: str, mol: Optional['Chem.Mol'], 
                 properties: Dict[str, Any], rules: Dict[str, RuleResult]):
        self.smiles = smiles
        self.mol = mol
        self.properties = properties
        self.rules = rules
        
        # Calculate derived properties
        self._calculate_summary_metrics()
    
    def _calculate_summary_metrics(self):
        """Calculate summary metrics and scores."""
        # Drug-likeness score (weighted combination of key rules)
        self.drug_likeness_score = self._calculate_drug_likeness_score()
        
        # Total violations across all rules
        self.total_violations = sum(rule.violations for rule in self.rules.values())
        
        # Rules passed/failed counts
        self.rules_passed = sum(1 for rule in self.rules.values() if rule.passed)
        self.rules_failed = sum(1 for rule in self.rules.values() if not rule.passed)
        
        # Key property shortcuts
        self.molecular_weight = self.properties.get('molecular_weight', 0)
        self.logp = self.properties.get('logp_crippen', 0)
        self.tpsa = self.properties.get('tpsa', 0)
        self.hbd_count = self.properties.get('hbd_count', 0)
        self.hba_count = self.properties.get('hba_count', 0)
        self.rotatable_bonds = self.properties.get('rotatable_bond_count', 0)
        
        # Rule shortcuts
        self.lipinski = self.rules.get('lipinski')
        self.veber = self.rules.get('veber')
        self.ghose = self.rules.get('ghose')
        self.lipinski_violations = self.lipinski.violations if self.lipinski else 0
    
    def _calculate_drug_likeness_score(self) -> float:
        """Calculate overall drug-likeness score (0-1, higher is better)."""
        # Weight different rules based on importance for drug-likeness
        weights = {
            'lipinski': 0.25,
            'veber': 0.20,
            'ghose': 0.15,
            'egan': 0.15,
            'muegge': 0.10,
            'reos': 0.10,
            'cns_mpo': 0.05
        }
        
        score = 0.0
        total_weight = 0.0
        
        for rule_name, weight in weights.items():
            if rule_name in self.rules:
                rule_result = self.rules[rule_name]
                rule_score = 1.0 if rule_result.passed else 0.0
                score += weight * rule_score
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def get_violations_summary(self) -> Dict[str, Any]:
        """Get detailed summary of all rule violations."""
        violations = {}
        
        for rule_name, rule_result in self.rules.items():
            if rule_result.violations > 0:
                violations[rule_name] = {
                    'violations': rule_result.violations,
                    'details': rule_result.details
                }
        
        return {
            'total_violations': self.total_violations,
            'rules_with_violations': len(violations),
            'violation_details': violations
        }
    
    def is_drug_like(self, strict: bool = False) -> bool:
        """
        Assess if compound is drug-like.
        
        Args:
            strict: If True, requires passing all major rules
            
        Returns:
            Boolean indicating drug-likeness
        """
        if strict:
            # Must pass Lipinski, Veber, and have no major violations
            return (self.lipinski.passed if self.lipinski else False) and \
                   (self.veber.passed if self.veber else False) and \
                   self.total_violations <= 2
        else:
            # More lenient: drug-likeness score > 0.6
            return self.drug_likeness_score > 0.6
    
    def is_lead_like(self) -> bool:
        """Check if compound satisfies lead-likeness criteria."""
        lead_rule = self.rules.get('lead_likeness')
        return lead_rule.passed if lead_rule else False
    
    def is_fragment_like(self) -> bool:
        """Check if compound satisfies fragment-likeness (Rule of 3)."""
        ro3_rule = self.rules.get('rule_of_3')
        return ro3_rule.passed if ro3_rule else False
    
    def has_structural_alerts(self) -> bool:
        """Check if compound has structural alerts (PAINS, Brenk)."""
        pains = self.rules.get('pains')
        brenk = self.rules.get('brenk')
        
        pains_alerts = pains.violations > 0 if pains else False
        brenk_alerts = brenk.violations > 0 if brenk else False
        
        return pains_alerts or brenk_alerts
    
    def get_cns_assessment(self) -> Dict[str, Any]:
        """Get CNS drug potential assessment."""
        cns_mpo = self.rules.get('cns_mpo')
        
        if not cns_mpo:
            return {'assessment': 'Not analyzed', 'score': 0}
        
        score = cns_mpo.score if hasattr(cns_mpo, 'score') else 0
        
        if score >= 0.8:
            assessment = 'Excellent CNS potential'
        elif score >= 0.6:
            assessment = 'Good CNS potential'
        elif score >= 0.4:
            assessment = 'Moderate CNS potential'
        else:
            assessment = 'Poor CNS potential'
        
        return {
            'assessment': assessment,
            'score': score,
            'details': cns_mpo.details
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'smiles': self.smiles,
            'properties': self.properties,
            'rules': {name: rule.to_dict() for name, rule in self.rules.items()},
            'summary': {
                'drug_likeness_score': self.drug_likeness_score,
                'total_violations': self.total_violations,
                'rules_passed': self.rules_passed,
                'rules_failed': self.rules_failed,
                'is_drug_like': self.is_drug_like(),
                'is_lead_like': self.is_lead_like(),
                'is_fragment_like': self.is_fragment_like(),
                'has_structural_alerts': self.has_structural_alerts()
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class BatchResult:
    """
    Results from batch analysis of multiple compounds.
    
    Provides convenient methods for analyzing and exporting batch results.
    """
    
    def __init__(self, results: List[AnalysisResult], 
                 failed: List[Tuple[int, str, str]], total_processed: int):
        self.results = results
        self.failed = failed
        self.total_processed = total_processed
        self.success_rate = len(results) / total_processed if total_processed > 0 else 0
    
    def __len__(self) -> int:
        return len(self.results)
    
    def __getitem__(self, index: int) -> AnalysisResult:
        return self.results[index]
    
    def __iter__(self):
        return iter(self.results)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the batch."""
        if not self.results:
            return {'error': 'No successful analyses'}
        
        # Property statistics
        mw_values = [r.molecular_weight for r in self.results]
        logp_values = [r.logp for r in self.results]
        tpsa_values = [r.tpsa for r in self.results]
        
        # Rule statistics
        lipinski_pass_rate = sum(1 for r in self.results if r.lipinski and r.lipinski.passed) / len(self.results)
        drug_like_count = sum(1 for r in self.results if r.is_drug_like())
        
        return {
            'total_compounds': len(self.results),
            'success_rate': self.success_rate,
            'property_stats': {
                'molecular_weight': {
                    'mean': sum(mw_values) / len(mw_values),
                    'min': min(mw_values),
                    'max': max(mw_values)
                },
                'logp': {
                    'mean': sum(logp_values) / len(logp_values),
                    'min': min(logp_values),
                    'max': max(logp_values)
                },
                'tpsa': {
                    'mean': sum(tpsa_values) / len(tpsa_values),
                    'min': min(tpsa_values),
                    'max': max(tpsa_values)
                }
            },
            'rule_stats': {
                'lipinski_pass_rate': lipinski_pass_rate,
                'drug_like_fraction': drug_like_count / len(self.results),
                'avg_violations': sum(r.total_violations for r in self.results) / len(self.results)
            }
        }
    
    def filter_by_rule(self, rule_name: str, passed_only: bool = True) -> 'BatchResult':
        """Filter results by specific rule compliance."""
        filtered_results = []
        
        for result in self.results:
            if rule_name in result.rules:
                rule_result = result.rules[rule_name]
                if passed_only and rule_result.passed:
                    filtered_results.append(result)
                elif not passed_only and not rule_result.passed:
                    filtered_results.append(result)
        
        return BatchResult(
            results=filtered_results,
            failed=self.failed,
            total_processed=len(filtered_results)
        )
    
    def filter_drug_like(self, strict: bool = False) -> 'BatchResult':
        """Filter to drug-like compounds only."""
        drug_like = [r for r in self.results if r.is_drug_like(strict=strict)]
        
        return BatchResult(
            results=drug_like,
            failed=self.failed,
            total_processed=len(drug_like)
        )
    
    def to_dataframe(self):
        """Convert results to pandas DataFrame."""
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas is required for DataFrame conversion. Install with: pip install pandas")
        
        if not self.results:
            return pd.DataFrame()
        
        data = []
        for result in self.results:
            row = {
                'SMILES': result.smiles,
                'MW': result.molecular_weight,
                'LogP': result.logp,
                'TPSA': result.tpsa,
                'HBD': result.hbd_count,
                'HBA': result.hba_count,
                'RotBonds': result.rotatable_bonds,
                'Drug_Likeness_Score': result.drug_likeness_score,
                'Total_Violations': result.total_violations,
                'Lipinski_Pass': result.lipinski.passed if result.lipinski else None,
                'Lipinski_Violations': result.lipinski_violations,
                'Veber_Pass': result.veber.passed if result.veber else None,
                'Is_Drug_Like': result.is_drug_like(),
                'Is_Lead_Like': result.is_lead_like(),
                'Is_Fragment_Like': result.is_fragment_like(),
                'Has_Structural_Alerts': result.has_structural_alerts()
            }
            
            # Add individual rule results
            for rule_name, rule_result in result.rules.items():
                row[f'{rule_name}_pass'] = rule_result.passed
                row[f'{rule_name}_violations'] = rule_result.violations
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def to_csv(self, filename: str, **kwargs):
        """Export results to CSV file."""
        df = self.to_dataframe()
        df.to_csv(filename, index=False, **kwargs)
    
    def to_excel(self, filename: str, **kwargs):
        """Export results to Excel file."""
        df = self.to_dataframe()
        df.to_excel(filename, index=False, **kwargs)
    
    def get_failed_compounds(self) -> List[Dict[str, Any]]:
        """Get information about compounds that failed analysis."""
        return [
            {
                'index': idx,
                'smiles': smiles,
                'error': error
            }
            for idx, smiles, error in self.failed
        ]