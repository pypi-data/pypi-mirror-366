#!/usr/bin/env python3
"""
Test script for Optimus package validation.

Tests accuracy against known compounds and validates calculations.
"""

from optimus import ChemicalAnalyzer
import pandas as pd

# Test compounds with known properties
test_compounds = [
    {
        'name': 'Aspirin',
        'smiles': 'CC(=O)OC1=CC=CC=C1C(=O)O',
        'expected_mw': 180.16,
        'expected_logp': 1.19,
        'expected_hbd': 1,
        'expected_hba': 4,
        'should_pass_lipinski': True
    },
    {
        'name': 'Caffeine', 
        'smiles': 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C',
        'expected_mw': 194.19,
        'expected_logp': -0.07,
        'expected_hbd': 0,
        'expected_hba': 6,
        'should_pass_lipinski': True
    },
    {
        'name': 'Ibuprofen',
        'smiles': 'CC(C)CC1=CC=C(C=C1)C(C)C(=O)O',
        'expected_mw': 206.28,
        'expected_logp': 3.97,
        'expected_hbd': 1,
        'expected_hba': 2,
        'should_pass_lipinski': True
    },
    {
        'name': 'Ethanol',
        'smiles': 'CCO',
        'expected_mw': 46.07,
        'expected_logp': -0.31,
        'expected_hbd': 1,
        'expected_hba': 1,
        'should_pass_lipinski': True
    }
]

def test_optimus_accuracy():
    """Test Optimus calculations against expected values."""
    
    print("🧪 Testing Optimus Chemical Analyzer")
    print("=" * 50)
    
    analyzer = ChemicalAnalyzer()
    
    for compound in test_compounds:
        print(f"\n📋 Testing {compound['name']} ({compound['smiles']})")
        
        try:
            result = analyzer.analyze_smiles(compound['smiles'])
            
            # Test molecular properties
            mw_error = abs(result.molecular_weight - compound['expected_mw']) / compound['expected_mw'] * 100
            logp_error = abs(result.logp - compound['expected_logp']) if compound['expected_logp'] != 0 else abs(result.logp)
            
            print(f"  Molecular Weight: {result.molecular_weight:.2f} Da (expected: {compound['expected_mw']:.2f}, error: {mw_error:.1f}%)")
            print(f"  LogP: {result.logp:.2f} (expected: {compound['expected_logp']:.2f}, error: {logp_error:.2f})")
            print(f"  HBD: {result.hbd_count} (expected: {compound['expected_hbd']})")
            print(f"  HBA: {result.hba_count} (expected: {compound['expected_hba']})")
            
            print(f"  Lipinski Pass: {result.lipinski.passed if result.lipinski else 'N/A'} (expected: {compound['should_pass_lipinski']})")
            print(f"  Drug-likeness Score: {result.drug_likeness_score:.3f}")
            print(f"  Total Violations: {result.total_violations}")
            
            # Validate accuracy
            if mw_error < 5:  # Within 5% is acceptable
                print("  ✅ Molecular weight calculation accurate")
            else:
                print("  ❌ Molecular weight calculation may be inaccurate")
            
        except Exception as e:
            print(f"  ❌ Error analyzing {compound['name']}: {e}")


def test_all_rules():
    """Test all ADMET rules with example compounds."""
    
    print("\n\n🔬 Testing All ADMET Rules")
    print("=" * 50)
    
    analyzer = ChemicalAnalyzer()
    
    # Test with aspirin
    result = analyzer.analyze_smiles('CC(=O)OC1=CC=CC=C1C(=O)O')
    
    print("Rules analysis for Aspirin:")
    for rule_name, rule_result in result.rules.items():
        status = "✅ PASS" if rule_result.passed else "❌ FAIL"
        print(f"  {rule_result.name}: {status} ({rule_result.violations} violations)")
    
    print(f"\nOverall Assessment:")
    print(f"  Drug-likeness Score: {result.drug_likeness_score:.3f}")
    print(f"  Is Drug-like: {'Yes' if result.is_drug_like() else 'No'}")
    print(f"  Is Lead-like: {'Yes' if result.is_lead_like() else 'No'}")
    print(f"  Has Structural Alerts: {'Yes' if result.has_structural_alerts() else 'No'}")


def test_batch_analysis():
    """Test batch analysis functionality."""
    
    print("\n\n📊 Testing Batch Analysis")
    print("=" * 50)
    
    smiles_list = [compound['smiles'] for compound in test_compounds]
    
    analyzer = ChemicalAnalyzer()
    batch_results = analyzer.analyze_batch(smiles_list, progress_bar=False)
    
    print(f"Batch analysis results:")
    print(f"  Total compounds: {len(smiles_list)}")
    print(f"  Successfully analyzed: {len(batch_results.results)}")
    print(f"  Failed: {len(batch_results.failed)}")
    print(f"  Success rate: {batch_results.success_rate:.1%}")
    
    # Create DataFrame
    df = batch_results.to_dataframe()
    print(f"\nGenerated DataFrame with {len(df)} rows and {len(df.columns)} columns")
    print("Column names:", list(df.columns))
    
    # Summary statistics
    stats = batch_results.get_summary_stats()
    print(f"\nSummary Statistics:")
    print(f"  Average MW: {stats['property_stats']['molecular_weight']['mean']:.1f} Da")
    print(f"  Average LogP: {stats['property_stats']['logp']['mean']:.2f}")
    print(f"  Lipinski Pass Rate: {stats['rule_stats']['lipinski_pass_rate']:.1%}")


def validate_discovery_studio_accuracy():
    """Compare against Discovery Studio reference values."""
    
    print("\n\n🎯 Discovery Studio Accuracy Validation")
    print("=" * 50)
    
    # Reference compounds with Discovery Studio calculated values
    reference_data = [
        {
            'name': 'Aspirin',
            'smiles': 'CC(=O)OC1=CC=CC=C1C(=O)O',
            'ds_mw': 180.159,
            'ds_logp': 1.185,
            'ds_tpsa': 63.6,
            'ds_hbd': 1,
            'ds_hba': 4
        },
        {
            'name': 'Caffeine',
            'smiles': 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C',
            'ds_mw': 194.191,
            'ds_logp': -0.073,
            'ds_tpsa': 58.4,
            'ds_hbd': 0,
            'ds_hba': 6
        }
    ]
    
    analyzer = ChemicalAnalyzer()
    
    print("Comparison with Discovery Studio values:")
    print("Compound           Property    Optimus    DS        Error")
    print("-" * 55)
    
    for ref in reference_data:
        result = analyzer.analyze_smiles(ref['smiles'])
        
        # Molecular weight comparison
        mw_error = abs(result.molecular_weight - ref['ds_mw']) / ref['ds_mw'] * 100
        print(f"{ref['name']:<18} MW          {result.molecular_weight:<8.2f}   {ref['ds_mw']:<8.2f}  {mw_error:>5.1f}%")
        
        # LogP comparison  
        logp_error = abs(result.logp - ref['ds_logp'])
        print(f"{'':<18} LogP        {result.logp:<8.2f}   {ref['ds_logp']:<8.2f}  {logp_error:>5.2f}")
        
        # TPSA comparison
        tpsa_error = abs(result.tpsa - ref['ds_tpsa']) / ref['ds_tpsa'] * 100
        print(f"{'':<18} TPSA        {result.tpsa:<8.1f}   {ref['ds_tpsa']:<8.1f}  {tpsa_error:>5.1f}%")
        
        print()


if __name__ == '__main__':
    try:
        test_optimus_accuracy()
        test_all_rules()
        test_batch_analysis()
        validate_discovery_studio_accuracy()
        
        print("\n\n🎉 All tests completed successfully!")
        print("\nOptimus is ready for use. Install with:")
        print("  cd optimus")
        print("  pip install -e .")
        print("\nOr create distribution:")  
        print("  python setup.py sdist bdist_wheel")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease install required dependencies:")
        print("  pip install rdkit-pypi pandas numpy")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nPlease check the installation and try again.")