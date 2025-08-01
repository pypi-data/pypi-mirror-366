# Optimus Chem - Comprehensive Chemical Analysis Package

<div align="center">
  <img src="https://raw.githubusercontent.com/pritampanda15/Optimus_Chemical_Analyzer/main/logo.png" alt="Optimus Logo" width="300">
</div>

<img src="https://img.shields.io/badge/Python-3.7%2B-blue.svg" alt="Python 3.7+">
<img src="https://img.shields.io/badge/RDKit-Latest-green.svg" alt="RDKit">
<img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">

Optimus Chem is a comprehensive Python package for molecular property calculations and ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) rules analysis. It provides accurate calculations matching Discovery Studio standards for drug discovery applications.

## Features

###  Molecular Property Calculations
- **Accurate RDKit-based calculations** matching Discovery Studio standards
- Molecular weight, LogP, LogD, pKa predictions
- Hydrogen bond donors/acceptors
- Topological Polar Surface Area (TPSA)
- Rotatable bonds and ring analysis
- Molar refractivity and more

###  Complete ADMET Rules Analysis
Implementation of all 14 major drug screening rules:

1. **Lipinski (Ro5)** - Oral bioavailability
2. **Veber** - Permeability and solubility  
3. **Ghose** - Drug-likeness
4. **Egan** - Oral absorption
5. **Muegge** - Broad drug-likeness
6. **Rule of 3** - Fragment-based design
7. **CNS MPO** - CNS exposure potential
8. **bRo5** - Non-classical scaffolds
9. **PAINS** - False positive alerts
10. **Pfizer 3/75** - Promiscuity/toxicity alert
11. **GSK 4/400** - ADMET risk reduction
12. **Lead-likeness** - Lead compound transition
13. **Brenk filters** - Unstable/toxic groups
14. **REOS** - Rapid compound filtering

### 🔧 Easy-to-Use API
```python
from optimus import ChemicalAnalyzer

analyzer = ChemicalAnalyzer()
results = analyzer.analyze_smiles("CCO")  # Ethanol
print(results.lipinski_violations)  # 0
print(results.drug_likeness_score)  # 0.85
```

## Installation

```bash
pip install optimus-chem
```

### From Source
```bash
https://github.com/pritampanda15/Optimus_Chemical_Analyzer
cd Optimus_Chemical_Analyzer
pip install -e .
```

## Quick Start

### Basic Analysis
```python
from optimus import ChemicalAnalyzer

# Initialize analyzer
analyzer = ChemicalAnalyzer()

# Analyze a compound
results = analyzer.analyze_smiles("CC(=O)OC1=CC=CC=C1C(=O)O")  # Aspirin

# Access results
print(f"Molecular Weight: {results.molecular_weight:.2f}")
print(f"LogP: {results.logp:.2f}")
print(f"Lipinski Violations: {results.lipinski_violations}")
print(f"Drug-likeness Score: {results.drug_likeness_score:.2f}")
```

### Batch Analysis
```python
smiles_list = [
    "CCO",  # Ethanol
    "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"  # Caffeine
]

results = analyzer.analyze_batch(smiles_list)
df = results.to_dataframe()
print(df[['SMILES', 'MW', 'LogP', 'Lipinski_Violations']])
```

### Command Line Interface

#### Available Commands
```bash
optimus --help
```

**Options:**
- `--version`  Show the version and exit.
- `--help`     Show this message and exit.

**Commands:**
- `analyze`   Analyze a single SMILES string.
- `batch`     Analyze multiple compounds from a file.
- `report`    Generate HTML report from analysis results.
- `validate`  Validate a SMILES string.

#### Command Usage Examples
```bash
# Get help for specific commands
optimus analyze --help
optimus batch --help
optimus report --help
optimus validate --help

# Analyze single compound
optimus analyze "CCO"

# Analyze from file
optimus batch compounds.smi --output results.csv

# Generate report
optimus report compounds.smi --format html

# Validate SMILES
optimus validate "CCO"
```

## API Reference

### ChemicalAnalyzer Class

#### Methods
- `analyze_smiles(smiles: str) -> AnalysisResult`
- `analyze_batch(smiles_list: List[str]) -> BatchResult`
- `analyze_mol(mol: Mol) -> AnalysisResult`
- `analyze_sdf(sdf_file: str) -> BatchResult`

#### Properties Calculated
- `molecular_weight`: Molecular weight (Da)
- `logp`: Partition coefficient
- `logd`: Distribution coefficient at pH 7.4
- `pka`: Acid dissociation constant
- `hbd`: Hydrogen bond donors
- `hba`: Hydrogen bond acceptors
- `tpsa`: Topological polar surface area
- `rotatable_bonds`: Number of rotatable bonds
- `aromatic_rings`: Number of aromatic rings
- `molar_refractivity`: Molar refractivity

#### ADMET Rules
Each rule returns a `RuleResult` object with:
- `passed`: Boolean indicating if rule is satisfied
- `violations`: Number of violations
- `details`: Detailed breakdown of criteria


## HTML Report Generation

Optimus can generate comprehensive HTML reports with interactive visualizations and detailed analysis results:

```python
from optimus import ChemicalAnalyzer

analyzer = ChemicalAnalyzer()

# Analyze multiple compounds
smiles_list = [
    "CCO",  # Ethanol
    "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"  # Caffeine
]

# Generate HTML report
analyzer.generate_html_report(smiles_list, output_file="analysis_report.html")
```

### Command Line HTML Report
```bash
# Generate HTML report from SMILES file
optimus report compounds.smi --format html --output report.html
```

The HTML report includes:
- **Summary Statistics**: Total compounds, success rates, average properties
- **Rule Pass Rates**: Pass/fail statistics for all 14 ADMET rules
- **Individual Results**: Detailed breakdown for each compound with color-coded pass/fail indicators
- **Interactive Features**: Sortable tables and responsive design

### Sample HTML Output Features:
- ✅ **Pass/Fail Indicators**: Green for pass, red for fail, gray for N/A
-  **Summary Tables**: Key metrics and rule compliance rates
-  **Detailed Analysis**: Molecular properties and ADMET rule results
-  **Responsive Design**: Works on desktop and mobile devices

## Examples

### Drug-likeness Assessment
```python
from optimus import ChemicalAnalyzer
import pandas as pd

analyzer = ChemicalAnalyzer()

# FDA approved drugs
fda_drugs = [
    "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
    "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
]

results = []
for smiles in fda_drugs:
    result = analyzer.analyze_smiles(smiles)
    results.append({
        'SMILES': smiles,
        'MW': result.molecular_weight,
        'LogP': result.logp,
        'Lipinski_Pass': result.lipinski.passed,
        'Drug_Score': result.drug_likeness_score
    })

df = pd.DataFrame(results)
print(df)
```

### CNS Drug Analysis
```python
# Analyze CNS penetration potential
result = analyzer.analyze_smiles("CN1C=NC2=C1C(=O)N(C(=O)N2C)C")  # Caffeine

print(f"CNS MPO Score: {result.cns_mpo.score}")
print(f"BBB Permeability: {result.bbb_permeability}")
print(f"P-gp Substrate: {result.pgp_substrate}")
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Optimus in your research, please cite:

```
Optimus Chem: Comprehensive Chemical Analysis Package for Drug Discovery
P.K.Panda.et al. (2025)
```


## Support

- 📧 Email: pritam@stanford.edu
- 🐛 Issues: [GitHub Issues](https://github.com/pritampanda15/Optimus_Chemical_Analyzer)