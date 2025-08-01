"""
Molecular Properties Calculator

Provides accurate molecular property calculations matching Discovery Studio standards.
"""

from typing import Dict, Any, Optional
import math
import logging

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski, QED
    from rdkit.Chem import rdMolDescriptors
    # Use direct imports with fallbacks
    CalcTPSA = getattr(rdMolDescriptors, 'CalcTPSA', None)
    CalcNumRotatableBonds = getattr(rdMolDescriptors, 'CalcNumRotatableBonds', None)
    CalcNumRings = getattr(rdMolDescriptors, 'CalcNumRings', None)
    CalcNumAromaticRings = getattr(rdMolDescriptors, 'CalcNumAromaticRings', None)
    CalcNumHBA = getattr(rdMolDescriptors, 'CalcNumHBA', None)
    CalcNumHBD = getattr(rdMolDescriptors, 'CalcNumHBD', None)
    CalcExactMolWt = getattr(rdMolDescriptors, 'CalcExactMolWt', None)
    CalcFractionCsp3 = getattr(rdMolDescriptors, 'CalcFractionCsp3', None)
    CalcNumAliphaticRings = getattr(rdMolDescriptors, 'CalcNumAliphaticRings', None)
    
    # Fallback to Descriptors if not available in rdMolDescriptors
    if CalcTPSA is None:
        CalcTPSA = getattr(Descriptors, 'TPSA', lambda mol: 0)
    if CalcNumRotatableBonds is None:
        CalcNumRotatableBonds = getattr(Descriptors, 'NumRotatableBonds', lambda mol: 0)
    if CalcNumRings is None:
        CalcNumRings = getattr(Descriptors, 'RingCount', lambda mol: 0)
    if CalcNumAromaticRings is None:
        CalcNumAromaticRings = getattr(Descriptors, 'NumAromaticRings', lambda mol: 0)
    if CalcNumHBA is None:
        CalcNumHBA = getattr(Descriptors, 'NumHAcceptors', lambda mol: 0)
    if CalcNumHBD is None:
        CalcNumHBD = getattr(Descriptors, 'NumHDonors', lambda mol: 0)
    if CalcExactMolWt is None:
        CalcExactMolWt = getattr(Descriptors, 'ExactMolWt', lambda mol: 0)
    if CalcFractionCsp3 is None:
        CalcFractionCsp3 = getattr(Descriptors, 'FractionCsp3', lambda mol: 0)
    if CalcNumAliphaticRings is None:
        CalcNumAliphaticRings = getattr(Descriptors, 'NumAliphaticRings', lambda mol: 0)
    
    RDKIT_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    RDKIT_AVAILABLE = False


class MolecularProperties:
    """
    Calculator for molecular properties with Discovery Studio accuracy.
    
    Provides comprehensive molecular descriptors including:
    - Basic properties (MW, LogP, etc.)
    - Hydrogen bonding descriptors
    - Structural descriptors
    - ADMET-relevant properties
    """
    
    def __init__(self):
        if not RDKIT_AVAILABLE:
            raise ImportError("RDKit is required for molecular property calculations")
        
        self.logger = logging.getLogger(__name__)
    
    def calculate_all(self, mol: 'Chem.Mol') -> Dict[str, Any]:
        """
        Calculate all molecular properties for a given molecule.
        
        Args:
            mol: RDKit Mol object
            
        Returns:
            Dictionary containing all calculated properties
        """
        if mol is None:
            raise ValueError("Invalid molecule object")
        
        properties = {}
        
        # Basic molecular properties
        properties.update(self._calculate_basic_properties(mol))
        
        # Structural descriptors
        properties.update(self._calculate_structural_descriptors(mol))
        
        # Hydrogen bonding descriptors
        properties.update(self._calculate_hydrogen_bonding(mol))
        
        # Lipophilicity descriptors
        properties.update(self._calculate_lipophilicity(mol))
        
        # Topological descriptors
        properties.update(self._calculate_topological_descriptors(mol))
        
        # ADMET-relevant properties
        properties.update(self._calculate_admet_properties(mol))
        
        return properties
    
    def _calculate_basic_properties(self, mol: 'Chem.Mol') -> Dict[str, float]:
        """Calculate basic molecular properties."""
        return {
            'molecular_weight': CalcExactMolWt(mol),
            'heavy_atom_count': mol.GetNumHeavyAtoms(),
            'atom_count': mol.GetNumAtoms(),
            'bond_count': mol.GetNumBonds(),
            'formal_charge': Chem.rdmolops.GetFormalCharge(mol),
        }
    
    def _calculate_structural_descriptors(self, mol: 'Chem.Mol') -> Dict[str, int]:
        """Calculate structural descriptors."""
        return {
            'ring_count': CalcNumRings(mol),
            'aromatic_ring_count': CalcNumAromaticRings(mol),
            'aliphatic_ring_count': CalcNumAliphaticRings(mol),
            'rotatable_bond_count': CalcNumRotatableBonds(mol),
            'sp3_fraction': CalcFractionCsp3(mol),
        }
    
    def _calculate_hydrogen_bonding(self, mol: 'Chem.Mol') -> Dict[str, int]:
        """Calculate hydrogen bonding descriptors."""
        return {
            'hbd_count': CalcNumHBD(mol),  # Hydrogen bond donors
            'hba_count': CalcNumHBA(mol),  # Hydrogen bond acceptors
            'hbd_lipinski': Lipinski.NumHDonors(mol),  # Lipinski HBD
            'hba_lipinski': Lipinski.NumHAcceptors(mol),  # Lipinski HBA
        }
    
    def _calculate_lipophilicity(self, mol: 'Chem.Mol') -> Dict[str, float]:
        """Calculate lipophilicity descriptors."""
        return {
            'logp_crippen': Crippen.MolLogP(mol),  # Crippen LogP
            'logp_wildman': Descriptors.MolLogP(mol),  # Wildman-Crippen LogP
            'molar_refractivity': Crippen.MolMR(mol),  # Molar refractivity
        }
    
    def _calculate_topological_descriptors(self, mol: 'Chem.Mol') -> Dict[str, float]:
        """Calculate topological descriptors."""
        return {
            'tpsa': CalcTPSA(mol),  # Topological Polar Surface Area
            'labute_asa': Descriptors.LabuteASA(mol),  # Labute ASA
            'balaban_j': Descriptors.BalabanJ(mol),  # Balaban J index
            'bertz_ct': Descriptors.BertzCT(mol),  # Bertz CT complexity
        }
    
    def _calculate_admet_properties(self, mol: 'Chem.Mol') -> Dict[str, float]:
        """Calculate ADMET-relevant properties."""
        properties = {}
        
        # QED (Quantitative Estimate of Drug-likeness)
        try:
            qed_properties = QED.properties(mol)
            properties.update({
                'qed_mw': qed_properties.MW,
                'qed_alogp': qed_properties.ALOGP,
                'qed_hba': qed_properties.HBA,
                'qed_hbd': qed_properties.HBD,
                'qed_psa': qed_properties.PSA,
                'qed_rotb': qed_properties.ROTB,
                'qed_arom': qed_properties.AROM,
                'qed_alerts': qed_properties.ALERTS,
                'qed_score': QED.qed(mol),
            })
        except Exception as e:
            self.logger.warning(f"Could not calculate QED properties: {e}")
        
        # Additional ADMET descriptors
        properties.update({
            'num_saturated_rings': Descriptors.NumSaturatedRings(mol),
            'num_aromatic_carbocycles': Descriptors.NumAromaticCarbocycles(mol),
            'num_aromatic_heterocycles': Descriptors.NumAromaticHeterocycles(mol),
            'num_aliphatic_carbocycles': Descriptors.NumAliphaticCarbocycles(mol),
            'num_aliphatic_heterocycles': Descriptors.NumAliphaticHeterocycles(mol),
        })
        
        return properties
    
    def estimate_pka(self, mol: 'Chem.Mol') -> Optional[float]:
        """
        Estimate pKa using simple heuristics.
        
        Note: For accurate pKa predictions, consider using specialized tools
        like ChemAxon's pKa plugin or ACD/pKa.
        """
        # Simple heuristic-based pKa estimation
        # This is a very rough approximation
        
        # Look for common ionizable groups
        carboxylic_acid = mol.HasSubstructMatch(Chem.MolFromSmarts('C(=O)O'))
        phenol = mol.HasSubstructMatch(Chem.MolFromSmarts('c[OH]'))
        primary_amine = mol.HasSubstructMatch(Chem.MolFromSmarts('[NH2]'))
        secondary_amine = mol.HasSubstructMatch(Chem.MolFromSmarts('[NH1]'))
        tertiary_amine = mol.HasSubstructMatch(Chem.MolFromSmarts('[NH0]'))
        
        if carboxylic_acid:
            return 4.5  # Typical carboxylic acid pKa
        elif phenol:
            return 10.0  # Typical phenol pKa
        elif primary_amine:
            return 9.5  # Typical primary amine pKa
        elif secondary_amine:
            return 10.0  # Typical secondary amine pKa
        elif tertiary_amine:
            return 9.8  # Typical tertiary amine pKa
        
        return None  # No ionizable groups detected
    
    def calculate_logd(self, mol: 'Chem.Mol', ph: float = 7.4) -> float:
        """
        Calculate LogD at specified pH.
        
        LogD accounts for ionization state at physiological pH.
        """
        logp = Crippen.MolLogP(mol)
        pka = self.estimate_pka(mol)
        
        if pka is None:
            return logp  # No ionizable groups, LogD = LogP
        
        # Henderson-Hasselbalch equation for basic compounds
        if pka > 7:  # Basic compound
            fraction_neutral = 1 / (1 + 10**(ph - pka))
        else:  # Acidic compound
            fraction_neutral = 1 / (1 + 10**(pka - ph))
        
        # Assume ionized form has LogP reduced by ~4 units
        logd = logp + math.log10(fraction_neutral + (1 - fraction_neutral) * 10**(-4))
        
        return logd
    
    def calculate_molecular_complexity(self, mol: 'Chem.Mol') -> float:
        """
        Calculate molecular complexity score.
        
        Combines multiple complexity measures into a single score.
        """
        # Bertz CT complexity (normalized)
        bertz_ct = Descriptors.BertzCT(mol)
        bertz_normalized = bertz_ct / 100.0  # Rough normalization
        
        # Ring complexity
        ring_complexity = (CalcNumRings(mol) + CalcNumAromaticRings(mol)) / 10.0
        
        # Branching complexity
        branch_complexity = mol.GetNumHeavyAtoms() / (mol.GetNumBonds() + 1)
        
        # Heteroatom complexity
        heteroatom_count = sum(1 for atom in mol.GetAtoms() 
                              if atom.GetAtomicNum() not in [1, 6])  # Not H or C
        hetero_complexity = heteroatom_count / mol.GetNumHeavyAtoms()
        
        # Combine measures
        complexity = (bertz_normalized + ring_complexity + 
                     branch_complexity + hetero_complexity) / 4.0
        
        return min(complexity, 1.0)  # Cap at 1.0
    
    def get_property_names(self) -> list:
        """Get list of all calculated property names."""
        return [
            'molecular_weight', 'heavy_atom_count', 'atom_count', 'bond_count',
            'formal_charge', 'ring_count', 'aromatic_ring_count', 
            'aliphatic_ring_count', 'rotatable_bond_count', 'sp3_fraction',
            'hbd_count', 'hba_count', 'hbd_lipinski', 'hba_lipinski',
            'logp_crippen', 'logp_wildman', 'molar_refractivity',
            'tpsa', 'labute_asa', 'balaban_j', 'bertz_ct',
            'qed_score', 'num_saturated_rings', 'num_aromatic_carbocycles',
            'num_aromatic_heterocycles', 'num_aliphatic_carbocycles',
            'num_aliphatic_heterocycles'
        ]