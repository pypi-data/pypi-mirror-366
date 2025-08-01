"""
Utility Functions

Helper functions for molecular processing and validation.
"""

from typing import Optional, List, Union
import logging
import re

try:
    from rdkit import Chem
    try:
        from rdkit.Chem import rdMolStandardize
        STANDARDIZE_AVAILABLE = True
    except ImportError:
        STANDARDIZE_AVAILABLE = False
    RDKIT_AVAILABLE = True
except ImportError as e:
    print(f"RDKit import error in utils: {e}")
    RDKIT_AVAILABLE = False
    STANDARDIZE_AVAILABLE = False


def smiles_to_mol(smiles: str, sanitize: bool = True) -> Optional['Chem.Mol']:
    """
    Convert SMILES string to RDKit Mol object.
    
    Args:
        smiles: SMILES notation string
        sanitize: Whether to sanitize the molecule
        
    Returns:
        RDKit Mol object or None if conversion fails
    """
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for SMILES processing")
    
    try:
        mol = Chem.MolFromSmiles(smiles, sanitize=sanitize)
        return mol
    except Exception as e:
        logging.warning(f"Failed to convert SMILES '{smiles}': {e}")
        return None


def mol_to_smiles(mol: 'Chem.Mol', canonical: bool = True) -> Optional[str]:
    """
    Convert RDKit Mol object to SMILES string.
    
    Args:
        mol: RDKit Mol object
        canonical: Whether to generate canonical SMILES
        
    Returns:
        SMILES string or None if conversion fails
    """
    if not RDKIT_AVAILABLE:
        raise ImportError("RDKit is required for SMILES processing")
    
    if mol is None:
        return None
    
    try:
        if canonical:
            return Chem.MolToSmiles(mol)
        else:
            return Chem.MolToSmiles(mol, canonical=False)
    except Exception as e:
        logging.warning(f"Failed to convert Mol to SMILES: {e}")
        return None


def validate_smiles(smiles: str) -> bool:
    """
    Validate SMILES string.
    
    Args:
        smiles: SMILES notation string
        
    Returns:
        True if valid, False otherwise
    """
    if not smiles or not isinstance(smiles, str):
        return False
    
    # Basic character validation - include all common SMILES characters
    valid_chars = set('CNOSPFClBrI[]()=#+-0123456789cnospfl@HBSiTe\\/.:')
    if not all(c in valid_chars for c in smiles):
        # If character validation fails, still try RDKit parsing as it's more reliable
        pass
    
    # Try to parse with RDKit if available
    if RDKIT_AVAILABLE:
        mol = smiles_to_mol(smiles, sanitize=False)
        return mol is not None
    
    # Basic validation without RDKit
    # Check for balanced brackets
    brackets = {'(': ')', '[': ']'}
    stack = []
    for char in smiles:
        if char in brackets:
            stack.append(brackets[char])
        elif char in brackets.values():
            if not stack or stack.pop() != char:
                return False
    
    return len(stack) == 0


def standardize_smiles(smiles: str) -> Optional[str]:
    """
    Standardize SMILES string using RDKit.
    
    Args:
        smiles: Input SMILES string
        
    Returns:
        Standardized canonical SMILES or None if processing fails
    """
    if not RDKIT_AVAILABLE:
        logging.warning("RDKit not available for SMILES standardization")
        return smiles
    
    try:
        mol = smiles_to_mol(smiles)
        if mol is None:
            return None
        
        # Standardize the molecule if available
        if STANDARDIZE_AVAILABLE:
            normalizer = rdMolStandardize.Normalizer()
            mol = normalizer.normalize(mol)
        
        # Remove stereochemistry if needed
        try:
            Chem.RemoveStereochemistry(mol)
        except:
            pass  # Some RDKit versions may not have this function
        
        # Generate canonical SMILES
        return Chem.MolToSmiles(mol)
        
    except Exception as e:
        logging.warning(f"Failed to standardize SMILES '{smiles}': {e}")
        return None


def clean_smiles_list(smiles_list: List[str], 
                     remove_duplicates: bool = True,
                     standardize: bool = True) -> List[str]:
    """
    Clean and standardize a list of SMILES.
    
    Args:
        smiles_list: List of SMILES strings
        remove_duplicates: Whether to remove duplicate SMILES
        standardize: Whether to standardize SMILES
        
    Returns:
        Cleaned list of SMILES strings
    """
    cleaned = []
    seen = set()
    
    for smiles in smiles_list:
        if not validate_smiles(smiles):
            continue
        
        if standardize:
            std_smiles = standardize_smiles(smiles)
            if std_smiles is None:
                continue
            smiles = std_smiles
        
        if remove_duplicates:
            if smiles in seen:
                continue
            seen.add(smiles)
        
        cleaned.append(smiles)
    
    return cleaned


def read_smiles_file(filename: str, 
                    smiles_column: Union[int, str] = 0,
                    name_column: Optional[Union[int, str]] = None,
                    delimiter: str = '\t',
                    skip_header: bool = False) -> List[Union[str, tuple]]:
    """
    Read SMILES from a file.
    
    Args:
        filename: Path to file containing SMILES
        smiles_column: Column index or name containing SMILES
        name_column: Column index or name containing compound names
        delimiter: Field delimiter
        skip_header: Whether to skip the first line
        
    Returns:
        List of SMILES strings or (SMILES, name) tuples
    """
    results = []
    
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        if skip_header and lines:
            lines = lines[1:]
        
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            fields = line.split(delimiter)
            
            try:
                if isinstance(smiles_column, int):
                    smiles = fields[smiles_column]
                else:
                    # Assume first line is header for string column names
                    if line_num == 1:
                        header = fields
                        continue
                    smiles_idx = header.index(smiles_column)
                    smiles = fields[smiles_idx]
                
                if not validate_smiles(smiles):
                    logging.warning(f"Invalid SMILES on line {line_num}: {smiles}")
                    continue
                
                if name_column is not None:
                    if isinstance(name_column, int):
                        name = fields[name_column] if len(fields) > name_column else f"Compound_{line_num}"
                    else:
                        name_idx = header.index(name_column)
                        name = fields[name_idx] if len(fields) > name_idx else f"Compound_{line_num}"
                    results.append((smiles, name))
                else:
                    results.append(smiles)
                    
            except (IndexError, ValueError) as e:
                logging.warning(f"Error processing line {line_num}: {e}")
                continue
    
    except FileNotFoundError:
        raise FileNotFoundError(f"SMILES file not found: {filename}")
    except Exception as e:
        raise ValueError(f"Error reading SMILES file: {e}")
    
    return results


def calculate_molecular_formula(mol: 'Chem.Mol') -> str:
    """
    Calculate molecular formula from RDKit Mol object.
    
    Args:
        mol: RDKit Mol object
        
    Returns:
        Molecular formula string (e.g., "C8H10N4O2")
    """
    if not RDKIT_AVAILABLE or mol is None:
        return ""
    
    try:
        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
        return formula
    except Exception as e:
        logging.warning(f"Failed to calculate molecular formula: {e}")
        return ""


def get_atom_counts(mol: 'Chem.Mol') -> dict:
    """
    Get atom counts for each element in the molecule.
    
    Args:
        mol: RDKit Mol object
        
    Returns:
        Dictionary mapping element symbols to counts
    """
    if not RDKIT_AVAILABLE or mol is None:
        return {}
    
    atom_counts = {}
    for atom in mol.GetAtoms():
        symbol = atom.GetSymbol()
        atom_counts[symbol] = atom_counts.get(symbol, 0) + 1
    
    return atom_counts


def neutralize_molecule(mol: 'Chem.Mol') -> Optional['Chem.Mol']:
    """
    Neutralize charged molecule by removing common salt forms.
    
    Args:
        mol: RDKit Mol object
        
    Returns:
        Neutralized Mol object or None if neutralization fails
    """
    if not RDKIT_AVAILABLE or mol is None:
        return None
    
    if not STANDARDIZE_AVAILABLE:
        logging.warning("rdMolStandardize not available, returning original molecule")
        return mol
    
    try:
        # Use RDKit's standardization tools
        uncharger = rdMolStandardize.Uncharger()
        mol_neutral = uncharger.uncharge(mol)
        return mol_neutral
    except Exception as e:
        logging.warning(f"Failed to neutralize molecule: {e}")
        return mol


def remove_salts(mol: 'Chem.Mol') -> Optional['Chem.Mol']:
    """
    Remove salt components and keep the largest fragment.
    
    Args:
        mol: RDKit Mol object
        
    Returns:
        Desalted Mol object or None if desalting fails
    """
    if not RDKIT_AVAILABLE or mol is None:
        return None
    
    if not STANDARDIZE_AVAILABLE:
        logging.warning("rdMolStandardize not available, returning original molecule")
        return mol
    
    try:
        # Choose largest fragment
        largest_fragment = rdMolStandardize.LargestFragmentChooser()
        mol_desalted = largest_fragment.choose(mol)
        return mol_desalted
    except Exception as e:
        logging.warning(f"Failed to remove salts: {e}")
        return mol


def preprocess_molecule(smiles: str, 
                       neutralize: bool = True,
                       remove_salt: bool = True,
                       standardize: bool = True) -> Optional[str]:
    """
    Comprehensive molecule preprocessing.
    
    Args:
        smiles: Input SMILES string
        neutralize: Whether to neutralize charges
        remove_salt: Whether to remove salt components
        standardize: Whether to standardize the molecule
        
    Returns:
        Processed SMILES string or None if processing fails
    """
    if not validate_smiles(smiles):
        return None
    
    mol = smiles_to_mol(smiles)
    if mol is None:
        return None
    
    try:
        # Remove salts first
        if remove_salt:
            mol = remove_salts(mol)
            if mol is None:
                return None
        
        # Neutralize charges
        if neutralize:
            mol = neutralize_molecule(mol)
            if mol is None:
                return None
        
        # Standardize if requested
        if standardize and STANDARDIZE_AVAILABLE:
            normalizer = rdMolStandardize.Normalizer()
            mol = normalizer.normalize(mol)
        
        # Convert back to SMILES
        return mol_to_smiles(mol)
        
    except Exception as e:
        logging.warning(f"Failed to preprocess molecule '{smiles}': {e}")
        return None