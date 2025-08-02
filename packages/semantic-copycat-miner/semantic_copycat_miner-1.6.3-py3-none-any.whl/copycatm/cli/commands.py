"""
CLI command implementations for CopycatM.
"""

import json
import sys
from pathlib import Path

import click

from .. import __version__
from ..core.analyzer import CopycatAnalyzer
from ..core.config import AnalysisConfig
from ..core.exceptions import CopycatError
from .utils import setup_logging, get_verbosity_level


@click.command()
@click.version_option(version=__version__, prog_name="copycatm")
@click.argument("path", type=click.Path(exists=True))
@click.option("--verbose", "-v", count=True, help="Verbose output (can be repeated: -v, -vv, -vvv)")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors")
@click.option("--debug", is_flag=True, help="Enable debug mode with intermediate representations")
@click.option("--output", "-o", type=click.Path(), help="Output JSON file path (default: stdout)")
@click.option("--complexity-threshold", "-c", type=int, default=3, 
              help="Cyclomatic complexity threshold (default: 3)")
@click.option("--min-lines", type=int, default=20, 
              help="Minimum lines for algorithm analysis (default: 20)")
@click.option("--include-intermediates", is_flag=True, 
              help="Include AST and control flow graphs in output")
@click.option("--hash-algorithms", help="Comma-separated hash types (default: sha256,tlsh,minhash)")
@click.option("--confidence-threshold", type=float, default=0.0, 
              help="Minimum confidence score to include (0.0-1.0)")
@click.option("--only-algorithms", is_flag=True, help="Only output algorithmic signatures")
@click.option("--only-metadata", is_flag=True, help="Only output file metadata")
@click.option("--parallel", "-p", type=int, help="Number of parallel workers (default: CPU count)")
@click.option("--chunk-size", type=int, default=100, 
              help="Files per chunk for batch processing (default: 100)")
@click.option("--languages", help="Comma-separated list of languages to analyze")
@click.option("--enable-swhid", is_flag=True, help="Generate Software Heritage IDs")
@click.option("--swhid-include-directory", is_flag=True, help="Include directory SWHID (performance impact)")
@click.pass_context
def cli(ctx, path, verbose, quiet, debug, output, complexity_threshold, min_lines, include_intermediates,
        hash_algorithms, confidence_threshold, only_algorithms, only_metadata,
        parallel, chunk_size, languages, enable_swhid, swhid_include_directory):
    """Analyze a file or directory to extract hashes, algorithms, and structural features."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["debug"] = debug
    ctx.obj["output"] = output
    
    # Setup logging
    verbosity = get_verbosity_level(verbose, quiet, debug)
    setup_logging(verbosity)
    
    try:
        path_obj = Path(path)
        
        if path_obj.is_file():
            # Single file analysis
            if not quiet:
                click.echo(f"Analyzing file: {path}")
            
            # Build configuration for single file
            config = AnalysisConfig(
                complexity_threshold=complexity_threshold,
                min_lines=min_lines,
                include_intermediates=include_intermediates,
                hash_algorithms=hash_algorithms.split(",") if hash_algorithms else None,
                confidence_threshold=confidence_threshold,
                parallel_workers=parallel,
                chunk_size=chunk_size,
                languages=languages.split(",") if languages else None,
                enable_swhid=enable_swhid,
                swhid_include_directory=swhid_include_directory
            )
            
            # Initialize analyzer
            analyzer = CopycatAnalyzer(config)
            
            # Analyze file using enhanced three-tier analyzer for control blocks
            result = analyzer.analyze_file_enhanced(path)
            
            # Filter output if requested
            if only_algorithms:
                result = {"algorithms": result.get("algorithms", [])}
            elif only_metadata:
                result = {
                    "file_metadata": result.get("file_metadata", {}),
                    "file_properties": result.get("file_properties", {})
                }
            
            # Output results
            output_json(result, output)
            
        elif path_obj.is_dir():
            # Directory analysis
            if not quiet:
                click.echo(f"Analyzing directory: {path}")
            
            # Build configuration for batch processing
            config = AnalysisConfig(
                complexity_threshold=complexity_threshold,
                min_lines=min_lines,
                include_intermediates=include_intermediates,
                hash_algorithms=hash_algorithms.split(",") if hash_algorithms else None,
                confidence_threshold=confidence_threshold,
                parallel_workers=parallel,
                chunk_size=chunk_size,
                languages=languages.split(",") if languages else None,
                enable_swhid=enable_swhid,
                swhid_include_directory=swhid_include_directory
            )
            
            # Initialize analyzer
            analyzer = CopycatAnalyzer(config)
            
            # Analyze directory
            results = analyzer.analyze_directory(path)
            
            # Output results
            output_json({"results": results}, output)
            
        else:
            raise click.BadParameter(f"Path {path} is neither a file nor directory")
        
    except CopycatError as e:
        error_output = {
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "path": path,
                "timestamp": get_timestamp()
            }
        }
        output_json(error_output, output)
        sys.exit(1)
    except Exception as e:
        error_output = {
            "error": {
                "type": "UnexpectedError",
                "message": str(e),
                "path": path,
                "timestamp": get_timestamp()
            }
        }
        output_json(error_output, output)
        sys.exit(1)











def main():
    """Main CLI entry point."""
    return cli()


def output_json(data, output_path):
    """Output JSON data to file or stdout."""
    json_str = json.dumps(data, indent=2, default=str)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(json_str)
    else:
        click.echo(json_str)


def get_timestamp():
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z" 