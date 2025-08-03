"""
Command-line interface for PyBrain
"""

import click
import logging
from typing import Optional
from pybrain.core.ai import AIEngine, ModelConfig
from pybrain.core.harmonizer import DataHarmonizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def main():
    """PyBrain - Unified Healthcare Intelligence Platform"""
    pass


@main.command()
@click.option('--model', '-m', default='clinical-bert', help='AI model to use')
@click.option('--text', '-t', required=True, help='Clinical text to analyze')
def analyze(model: str, text: str):
    """Analyze clinical text using AI"""
    click.echo(f"Analyzing text with {model}...")
    
    engine = AIEngine(ModelConfig(model_name=model, model_type="nlp"))
    entities = engine.extract_clinical_entities(text)
    
    click.echo("\nExtracted Entities:")
    for entity_type, values in entities.items():
        if values:
            click.echo(f"  {entity_type}: {', '.join(values)}")


@main.command()
@click.option('--input', '-i', required=True, type=click.File('r'), help='Input file')
@click.option('--format', '-f', required=True, 
              type=click.Choice(['hl7v2', 'csv', 'cda']), help='Input format')
@click.option('--resource', '-r', required=True,
              type=click.Choice(['Patient', 'Observation', 'MedicationRequest']),
              help='Target FHIR resource type')
@click.option('--output', '-o', type=click.File('w'), help='Output file')
def harmonize(input, format, resource, output):
    """Harmonize healthcare data to FHIR format"""
    click.echo(f"Harmonizing {format} data to FHIR {resource}...")
    
    harmonizer = DataHarmonizer()
    
    # Read input data
    import json
    data = json.load(input)
    
    # Harmonize to FHIR
    fhir_resource = harmonizer.harmonize_to_fhir(data, format, resource)
    
    if fhir_resource:
        result = json.dumps(fhir_resource, indent=2)
        if output:
            output.write(result)
        else:
            click.echo(result)
    else:
        click.echo("Harmonization failed!", err=True)


@main.command()
@click.option('--port', '-p', default=8000, help='Server port')
@click.option('--host', '-h', default='0.0.0.0', help='Server host')
def serve(port: int, host: str):
    """Start PyBrain API server"""
    click.echo(f"Starting PyBrain server on {host}:{port}...")
    click.echo("Server functionality would be implemented here")


if __name__ == '__main__':
    main()