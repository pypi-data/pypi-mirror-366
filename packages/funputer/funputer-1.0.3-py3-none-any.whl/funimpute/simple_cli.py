"""
Simple command-line interface focused on core functionality.
"""

import click
import logging
import sys
from pathlib import Path

from .simple_analyzer import analyze_imputation_requirements
from .models import AnalysisConfig
from .io import save_suggestions


@click.command()
@click.option('--metadata', '-m', 
              required=True,
              help='Path to metadata CSV file')
@click.option('--data', '-d',
              required=True, 
              help='Path to data CSV file')
@click.option('--output', '-o',
              help='Output path for suggestions CSV (default: suggestions.csv)')
@click.option('--config', '-c',
              help='Path to configuration YAML file')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose logging')
def main(metadata, data, output, config, verbose):
    """
    Analyze dataset and suggest imputation methods.
    
    Examples:
    
    # Basic usage
    funimpute -m metadata.csv -d data.csv
    
    # With custom output
    funimpute -m metadata.csv -d data.csv -o my_suggestions.csv
    
    # With configuration
    funimpute -m metadata.csv -d data.csv -c config.yml
    """
    
    # Setup logging
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s',
        stream=sys.stdout
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration if provided
        analysis_config = AnalysisConfig()
        if config:
            from .io import load_configuration
            analysis_config = load_configuration(config)
        
        logger.info(f"Analyzing {data} with metadata {metadata}")
        
        # Run analysis
        suggestions = analyze_imputation_requirements(
            metadata_path=metadata,
            data_path=data,
            config=analysis_config
        )
        
        # Save results
        output_path = output or "suggestions.csv"
        save_suggestions(suggestions, output_path)
        
        # Display summary
        click.echo(f"\n✓ Analysis complete!")
        click.echo(f"  Columns analyzed: {len(suggestions)}")
        click.echo(f"  Total missing values: {sum(s.missing_count for s in suggestions):,}")
        click.echo(f"  Average confidence: {sum(s.confidence_score for s in suggestions) / len(suggestions):.3f}")
        click.echo(f"  Results saved to: {output_path}")
        
        # Show method distribution
        from collections import Counter
        methods = Counter(s.proposed_method for s in suggestions)
        click.echo(f"\n  Proposed methods:")
        for method, count in methods.most_common():
            click.echo(f"    {method}: {count}")
        
    except FileNotFoundError as e:
        click.echo(f"Error: File not found - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        click.echo(f"Error: Analysis failed - {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()