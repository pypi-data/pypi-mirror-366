"""
Command Line Interface for Optimus Chem

Provides command-line access to chemical analysis functionality.
"""

import click
import sys
import json
from pathlib import Path
from typing import List, Optional

from .analyzer import ChemicalAnalyzer
from .utils import read_smiles_file, validate_smiles


@click.group()
@click.version_option(version="1.0.0")
def main():
    """Optimus Chem - Comprehensive Chemical Analysis Package"""
    pass


@main.command()
@click.argument('smiles')
@click.option('--output', '-o', type=click.File('w'), default=sys.stdout,
              help='Output file (default: stdout)')
@click.option('--format', '-f', type=click.Choice(['json', 'table']), default='table',
              help='Output format')
@click.option('--rules', '-r', multiple=True,
              help='Specific rules to analyze (default: all)')
def analyze(smiles: str, output, format: str, rules: tuple):
    """Analyze a single SMILES string."""
    if not validate_smiles(smiles):
        click.echo(f"Error: Invalid SMILES string: {smiles}", err=True)
        sys.exit(1)
    
    try:
        analyzer = ChemicalAnalyzer()
        result = analyzer.analyze_smiles(smiles)
        
        if format == 'json':
            output.write(result.to_json())
        else:
            # Table format
            _print_analysis_table(result, output, rules)
            
    except Exception as e:
        click.echo(f"Error analyzing compound: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), 
              help='Output file (CSV format)')
@click.option('--smiles-column', '-s', default=0,
              help='SMILES column index or name (default: 0)')
@click.option('--name-column', '-n', type=str,
              help='Name column index or name')  
@click.option('--delimiter', '-d', default='\t',
              help='Field delimiter (default: tab)')
@click.option('--skip-header', is_flag=True,
              help='Skip header line')
@click.option('--progress/--no-progress', default=True,
              help='Show progress bar')
def batch(input_file: str, output: Optional[str], smiles_column, 
          name_column: Optional[str], delimiter: str, skip_header: bool, progress: bool):
    """Analyze multiple compounds from a file."""
    
    try:
        # Read SMILES from file
        click.echo(f"Reading SMILES from {input_file}...")
        smiles_data = read_smiles_file(
            input_file,
            smiles_column=smiles_column,
            name_column=name_column,
            delimiter=delimiter,
            skip_header=skip_header
        )
        
        if not smiles_data:
            click.echo("Error: No valid SMILES found in input file", err=True)
            sys.exit(1)
        
        # Extract SMILES strings
        if isinstance(smiles_data[0], tuple):
            smiles_list = [item[0] for item in smiles_data]
        else:
            smiles_list = smiles_data
        
        click.echo(f"Found {len(smiles_list)} compounds to analyze")
        
        # Analyze compounds
        analyzer = ChemicalAnalyzer()
        results = analyzer.analyze_batch(smiles_list, progress_bar=progress)
        
        click.echo(f"Successfully analyzed {len(results.results)} compounds")
        if results.failed:
            click.echo(f"Failed to analyze {len(results.failed)} compounds")
        
        # Output results
        if output:
            results.to_csv(output)
            click.echo(f"Results saved to {output}")
        else:
            # Print summary to stdout
            _print_batch_summary(results)
            
    except Exception as e:
        click.echo(f"Error processing batch: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output HTML file')
@click.option('--template', '-t', type=click.Choice(['detailed', 'summary']), 
              default='detailed', help='Report template')
def report(input_file: str, output: str, template: str):
    """Generate HTML report from analysis results."""
    
    try:
        # Read and analyze compounds
        click.echo(f"Generating report from {input_file}...")
        
        smiles_data = read_smiles_file(input_file)
        if isinstance(smiles_data[0], tuple):
            smiles_list = [item[0] for item in smiles_data]
        else:
            smiles_list = smiles_data
        
        analyzer = ChemicalAnalyzer()
        results = analyzer.analyze_batch(smiles_list, progress_bar=True)
        
        # Generate HTML report
        html_content = _generate_html_report(results, template)
        
        with open(output, 'w') as f:
            f.write(html_content)
        
        click.echo(f"Report saved to {output}")
        
    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('smiles')
def validate(smiles: str):
    """Validate a SMILES string."""
    if validate_smiles(smiles):
        click.echo("✓ Valid SMILES")
        
        # Show basic info
        try:
            analyzer = ChemicalAnalyzer()
            result = analyzer.analyze_smiles(smiles)
            click.echo(f"Molecular Weight: {result.molecular_weight:.2f}")
            click.echo(f"LogP: {result.logp:.2f}")
            click.echo(f"TPSA: {result.tpsa:.1f}")
        except Exception as e:
            click.echo(f"Warning: Could not analyze SMILES: {e}")
    else:
        click.echo("✗ Invalid SMILES")
        sys.exit(1)


def _print_analysis_table(result, output, rules_filter: tuple):
    """Print analysis results in table format."""
    output.write(f"SMILES: {result.smiles}\n")
    output.write("=" * 60 + "\n")
    
    # Molecular properties
    output.write("MOLECULAR PROPERTIES:\n")
    output.write(f"  Molecular Weight: {result.molecular_weight:.2f} Da\n")
    output.write(f"  LogP: {result.logp:.2f}\n")
    output.write(f"  TPSA: {result.tpsa:.1f} Ų\n")
    output.write(f"  HBD: {result.hbd_count}\n")
    output.write(f"  HBA: {result.hba_count}\n")
    output.write(f"  Rotatable Bonds: {result.rotatable_bonds}\n")
    output.write("\n")
    
    # Rules analysis
    output.write("ADMET RULES:\n")
    for rule_name, rule_result in result.rules.items():
        if rules_filter and rule_name not in rules_filter:
            continue
        
        status = "PASS" if rule_result.passed else "FAIL"
        output.write(f"  {rule_result.name}: {status}")
        if rule_result.violations > 0:
            output.write(f" ({rule_result.violations} violations)")
        output.write("\n")
    
    output.write("\n")
    output.write("SUMMARY:\n")
    output.write(f"  Drug-likeness Score: {result.drug_likeness_score:.3f}\n")
    output.write(f"  Total Violations: {result.total_violations}\n")
    output.write(f"  Is Drug-like: {'Yes' if result.is_drug_like() else 'No'}\n")


def _print_batch_summary(results):
    """Print batch analysis summary."""
    print(f"\nBATCH ANALYSIS SUMMARY:")
    print(f"Total compounds processed: {len(results)}")
    
    if not results.results:
        print("No successful analyses to summarize.")
        return
    
    stats = results.get_summary_stats()
    
    print(f"\nProperty Statistics:")
    print(f"  Molecular Weight: {stats['property_stats']['molecular_weight']['mean']:.1f} ± {stats['property_stats']['molecular_weight']['max'] - stats['property_stats']['molecular_weight']['min']:.1f}")
    print(f"  LogP: {stats['property_stats']['logp']['mean']:.2f}")
    print(f"  TPSA: {stats['property_stats']['tpsa']['mean']:.1f}")
    
    print(f"\nRule Compliance:")
    print(f"  Lipinski Pass Rate: {stats['rule_stats']['lipinski_pass_rate']:.1%}")
    print(f"  Drug-like Fraction: {stats['rule_stats']['drug_like_fraction']:.1%}")
    print(f"  Average Violations: {stats['rule_stats']['avg_violations']:.1f}")


def _generate_html_report(results, template: str) -> str:
    """Generate HTML report from batch results."""
    
    # Simple HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Optimus Chem Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; overflow-x: auto; }}
            th, td {{ border: 1px solid #ddd; padding: 6px; text-align: center; font-size: 12px; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .pass {{ color: green; font-weight: bold; }}
            .fail {{ color: red; font-weight: bold; }}
            .na {{ color: gray; font-style: italic; }}
            .smiles {{ font-family: monospace; text-align: left; }}
            .summary-table {{ width: 50%; }}
            .summary-table th, .summary-table td {{ text-align: left; padding: 8px; }}
        </style>
    </head>
    <body>
        <h1>Optimus Chem Chemical Analysis Report</h1>
        <p>Generated for {len(results)} compounds</p>
        
        <h2>Summary Statistics</h2>
        <table class="summary-table">
            <tr><th>Metric</th><th>Value</th></tr>
    """
    
    if results.results:
        stats = results.get_summary_stats()
        
        # Calculate pass rates for all rules
        rule_pass_rates = {}
        rule_names = ['lipinski', 'veber', 'ghose', 'egan', 'muegge', 'rule_of_3', 
                     'cns_mpo', 'bro5', 'pains', 'pfizer_3_75', 'gsk_4_400', 
                     'lead_likeness', 'brenk', 'reos']
        
        for rule_name in rule_names:
            passed_count = sum(1 for r in results.results 
                             if rule_name in r.rules and r.rules[rule_name].passed)
            total_count = sum(1 for r in results.results if rule_name in r.rules)
            rule_pass_rates[rule_name] = passed_count / total_count if total_count > 0 else 0
        
        html += f"""
            <tr><td>Total Compounds</td><td>{len(results)}</td></tr>
            <tr><td>Success Rate</td><td>{results.success_rate:.1%}</td></tr>
            <tr><td>Average MW</td><td>{stats['property_stats']['molecular_weight']['mean']:.1f} Da</td></tr>
            <tr><td>Average LogP</td><td>{stats['property_stats']['logp']['mean']:.2f}</td></tr>
            <tr><td>Average TPSA</td><td>{stats['property_stats']['tpsa']['mean']:.1f} Ų</td></tr>
            <tr><td>Drug-like Fraction</td><td>{stats['rule_stats']['drug_like_fraction']:.1%}</td></tr>
        </table>
        
        <h2>Rule Pass Rates</h2>
        <table class="summary-table">
            <tr><th>Rule</th><th>Pass Rate</th></tr>
            <tr><td>Lipinski (Ro5)</td><td>{rule_pass_rates['lipinski']:.1%}</td></tr>
            <tr><td>Veber</td><td>{rule_pass_rates['veber']:.1%}</td></tr>
            <tr><td>Ghose</td><td>{rule_pass_rates['ghose']:.1%}</td></tr>
            <tr><td>Egan</td><td>{rule_pass_rates['egan']:.1%}</td></tr>
            <tr><td>Muegge</td><td>{rule_pass_rates['muegge']:.1%}</td></tr>
            <tr><td>Rule of 3</td><td>{rule_pass_rates['rule_of_3']:.1%}</td></tr>
            <tr><td>CNS MPO</td><td>{rule_pass_rates['cns_mpo']:.1%}</td></tr>
            <tr><td>bRo5</td><td>{rule_pass_rates['bro5']:.1%}</td></tr>
            <tr><td>PAINS</td><td>{rule_pass_rates['pains']:.1%}</td></tr>
            <tr><td>Pfizer 3/75</td><td>{rule_pass_rates['pfizer_3_75']:.1%}</td></tr>
            <tr><td>GSK 4/400</td><td>{rule_pass_rates['gsk_4_400']:.1%}</td></tr>
            <tr><td>Lead-likeness</td><td>{rule_pass_rates['lead_likeness']:.1%}</td></tr>
            <tr><td>Brenk filters</td><td>{rule_pass_rates['brenk']:.1%}</td></tr>
            <tr><td>REOS</td><td>{rule_pass_rates['reos']:.1%}</td></tr>
        """
    
    html += """
        </table>
        
        <h2>Individual Results</h2>
        <table>
            <tr>
                <th>SMILES</th>
                <th>MW</th>
                <th>LogP</th>
                <th>TPSA</th>
                <th>Lipinski</th>
                <th>Veber</th>
                <th>Ghose</th>
                <th>Egan</th>
                <th>Muegge</th>
                <th>Rule of 3</th>
                <th>CNS MPO</th>
                <th>bRo5</th>
                <th>PAINS</th>
                <th>Pfizer 3/75</th>
                <th>GSK 4/400</th>
                <th>Lead-like</th>
                <th>Brenk</th>
                <th>REOS</th>
                <th>Drug-like</th>
                <th>Total Violations</th>
            </tr>
    """
    
    for result in results.results[:100]:  # Limit to first 100 for performance
        # Helper function to get rule status
        def get_rule_status(rule_name):
            rule = result.rules.get(rule_name)
            if rule is None:
                return "N/A", "na"
            return ("PASS" if rule.passed else "FAIL"), ("pass" if rule.passed else "fail")
        
        # Get all rule statuses
        lipinski_status, lipinski_class = get_rule_status('lipinski')
        veber_status, veber_class = get_rule_status('veber')
        ghose_status, ghose_class = get_rule_status('ghose')
        egan_status, egan_class = get_rule_status('egan')
        muegge_status, muegge_class = get_rule_status('muegge')
        rule_of_3_status, rule_of_3_class = get_rule_status('rule_of_3')
        cns_mpo_status, cns_mpo_class = get_rule_status('cns_mpo')
        bro5_status, bro5_class = get_rule_status('bro5')
        pains_status, pains_class = get_rule_status('pains')
        pfizer_status, pfizer_class = get_rule_status('pfizer_3_75')
        gsk_status, gsk_class = get_rule_status('gsk_4_400')
        lead_status, lead_class = get_rule_status('lead_likeness')
        brenk_status, brenk_class = get_rule_status('brenk')
        reos_status, reos_class = get_rule_status('reos')
        
        drug_like = "Yes" if result.is_drug_like() else "No"
        
        html += f"""
            <tr>
                <td class="smiles">{result.smiles[:50]}{'...' if len(result.smiles) > 50 else ''}</td>
                <td>{result.molecular_weight:.1f}</td>
                <td>{result.logp:.2f}</td>
                <td>{result.tpsa:.1f}</td>
                <td class="{lipinski_class}">{lipinski_status}</td>
                <td class="{veber_class}">{veber_status}</td>
                <td class="{ghose_class}">{ghose_status}</td>
                <td class="{egan_class}">{egan_status}</td>
                <td class="{muegge_class}">{muegge_status}</td>
                <td class="{rule_of_3_class}">{rule_of_3_status}</td>
                <td class="{cns_mpo_class}">{cns_mpo_status}</td>
                <td class="{bro5_class}">{bro5_status}</td>
                <td class="{pains_class}">{pains_status}</td>
                <td class="{pfizer_class}">{pfizer_status}</td>
                <td class="{gsk_class}">{gsk_status}</td>
                <td class="{lead_class}">{lead_status}</td>
                <td class="{brenk_class}">{brenk_status}</td>
                <td class="{reos_class}">{reos_status}</td>
                <td>{drug_like}</td>
                <td>{result.total_violations}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return html


if __name__ == '__main__':
    main()