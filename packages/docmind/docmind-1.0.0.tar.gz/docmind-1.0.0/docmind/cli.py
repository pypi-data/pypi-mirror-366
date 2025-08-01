"""Enhanced CLI for DocMind with comprehensive options."""

import argparse
import sys
import glob
from pathlib import Path
from typing import List, Optional

from .config import DocMindConfig, load_config, save_config, get_preset_config, QUALITY_PRESETS
from .converter import DocMind
from .exceptions import *

def create_parser() -> argparse.ArgumentParser:
    """Create comprehensive argument parser."""
    parser = argparse.ArgumentParser(
        prog='docmind',
        description='DocMind: Universal AI-optimized document converter for PDFs and DOCX files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  docmind document.pdf                          # Basic conversion
  docmind document.docx -o results/             # Custom output directory
  docmind *.pdf --batch                         # Batch process all PDFs
  docmind doc.pdf --quality ai_optimized        # Use AI-optimized preset
  docmind doc.pdf --ocr --ocr-lang eng+fra      # Enable OCR with multiple languages
  docmind doc.pdf --config custom.yaml          # Use custom configuration
  docmind doc.pdf --dry-run                     # Preview what would be done
  docmind --create-config high > config.yaml    # Generate config file

Quality Presets:
  fast         - Quick conversion, lower quality
  balanced     - Default quality and speed (default)
  high         - High quality, slower processing  
  ai_optimized - Maximum quality for LLM consumption

Supported formats: PDF, DOCX
Output formats: Markdown (GitHub/GitLab flavored)
        """
    )
    
    # Input files
    parser.add_argument(
        'input_files',
        nargs='*',
        help='Input PDF/DOCX files or glob patterns'
    )
    
    # Output options
    output_group = parser.add_argument_group('output options')
    output_group.add_argument(
        '-o', '--output',
        type=Path,
        default='output',
        help='Output directory (default: output)'
    )
    output_group.add_argument(
        '--format',
        choices=['markdown', 'html'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    output_group.add_argument(
        '--flavor',
        choices=['github', 'gitlab', 'standard'],
        default='github',
        help='Markdown flavor (default: github)'
    )
    
    # Quality and performance
    quality_group = parser.add_argument_group('quality and performance')
    quality_group.add_argument(
        '--quality',
        choices=list(QUALITY_PRESETS.keys()),
        default='balanced',
        help='Quality preset (default: balanced)'
    )
    quality_group.add_argument(
        '--image-quality',
        type=int,
        metavar='N',
        help='Image quality 1-100 (overrides preset)'
    )
    quality_group.add_argument(
        '--image-min-size',
        metavar='WxH',
        help='Minimum image size, e.g., 800x600'
    )
    quality_group.add_argument(
        '--max-file-size',
        type=int,
        metavar='MB',
        help='Maximum file size in MB'
    )
    quality_group.add_argument(
        '--chunk-size',
        type=int,
        metavar='N',
        help='Pages per processing chunk (memory optimization)'
    )
    quality_group.add_argument(
        '--workers',
        type=int,
        metavar='N',
        help='Number of worker threads'
    )
    
    # Features
    features_group = parser.add_argument_group('features')
    features_group.add_argument(
        '--ocr',
        action='store_true',
        help='Enable OCR for scanned content'
    )
    features_group.add_argument(
        '--ocr-lang',
        default='eng',
        help='OCR language(s), e.g., eng, eng+fra (default: eng)'
    )
    features_group.add_argument(
        '--extract-tables',
        action='store_true',
        default=True,
        help='Extract tables (default: enabled)'
    )
    features_group.add_argument(
        '--no-extract-tables',
        action='store_false',
        dest='extract_tables',
        help='Disable table extraction'
    )
    features_group.add_argument(
        '--include-toc',
        action='store_true',
        help='Generate table of contents'
    )
    features_group.add_argument(
        '--include-metadata',
        action='store_true',
        default=True,
        help='Include document metadata (default: enabled)'
    )
    features_group.add_argument(
        '--no-metadata',
        action='store_false',
        dest='include_metadata',
        help='Exclude document metadata'
    )
    
    # Processing options
    processing_group = parser.add_argument_group('processing options')
    processing_group.add_argument(
        '--batch',
        action='store_true',
        help='Enable batch processing mode'
    )
    processing_group.add_argument(
        '--resume',
        action='store_true',
        default=True,
        help='Resume interrupted conversions (default: enabled)'
    )
    processing_group.add_argument(
        '--no-resume',
        action='store_false',
        dest='resume',
        help='Disable resume capability'
    )
    processing_group.add_argument(
        '--cache',
        action='store_true',
        default=True,
        help='Enable caching (default: enabled)'
    )
    processing_group.add_argument(
        '--no-cache',
        action='store_false',
        dest='cache',
        help='Disable caching'
    )
    processing_group.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite existing output'
    )
    
    # Configuration
    config_group = parser.add_argument_group('configuration')
    config_group.add_argument(
        '--config',
        type=Path,
        help='Configuration file (YAML or JSON)'
    )
    config_group.add_argument(
        '--save-config',
        type=Path,
        help='Save current settings to config file'
    )
    config_group.add_argument(
        '--create-config',
        choices=list(QUALITY_PRESETS.keys()),
        help='Output config for preset (use with > file.yaml)'
    )
    
    # Utility options
    utility_group = parser.add_argument_group('utility options')
    utility_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without processing'
    )
    utility_group.add_argument(
        '--check-deps',
        action='store_true',
        help='Check system dependencies'
    )
    utility_group.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    utility_group.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet output (errors only)'
    )
    utility_group.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser

def expand_file_patterns(patterns: List[str]) -> List[Path]:
    """Expand glob patterns to file paths."""
    files = []
    for pattern in patterns:
        if '*' in pattern or '?' in pattern:
            expanded = glob.glob(pattern)
            files.extend([Path(f) for f in expanded])
        else:
            files.append(Path(pattern))
    return files

def validate_args(args) -> None:
    """Validate command line arguments."""
    if not args.input_files and not args.check_deps and not args.create_config:
        raise ValueError("No input files specified. Use --help for usage information.")
    
    if args.image_min_size:
        try:
            w, h = map(int, args.image_min_size.split('x'))
            if w <= 0 or h <= 0:
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError("Invalid image size format. Use WxH, e.g., 800x600")

def args_to_config(args) -> DocMindConfig:
    """Convert command line arguments to configuration."""
    # Start with preset or default config
    if args.config:
        config = load_config(args.config)
    else:
        config = get_preset_config(args.quality)
    
    # Apply command line overrides
    if args.image_quality is not None:
        config.image.quality = args.image_quality
    
    if args.image_min_size:
        w, h = map(int, args.image_min_size.split('x'))
        config.image.min_width = w
        config.image.min_height = h
    
    if args.max_file_size is not None:
        config.performance.max_file_size_mb = args.max_file_size
    
    if args.chunk_size is not None:
        config.performance.chunk_size_pages = args.chunk_size
    
    if args.workers is not None:
        config.performance.max_workers = args.workers
    
    # Feature flags
    config.conversion.ocr_enabled = args.ocr
    config.conversion.ocr_language = args.ocr_lang
    config.conversion.extract_tables = args.extract_tables
    config.conversion.include_metadata = args.include_metadata
    
    config.output.format = args.format
    config.output.flavor = args.flavor
    config.output.include_toc = args.include_toc
    
    config.performance.enable_resume = args.resume
    config.performance.cache_enabled = args.cache
    
    return config

def check_dependencies() -> None:
    """Check and report system dependencies."""
    print("🔧 Checking DocMind Dependencies")
    print("=" * 35)
    
    # Create temporary converter to check tools
    converter = DocMind()
    
    required_tools = {
        'pandoc': 'Essential for high-quality text conversion',
        'imagemagick': 'Recommended for advanced image processing',
        'tesseract': 'Required for OCR functionality',
        'tesseract_py': 'Python OCR library'
    }
    
    optional_tools = {
        'libreoffice': 'For advanced EMF/WMF conversion',
        'tqdm': 'For progress bars'
    }
    
    print("\nRequired/Recommended:")
    for tool, description in required_tools.items():
        status = "✅" if converter.tools.get(tool, False) else "❌"
        print(f"  {status} {tool:<12} - {description}")
    
    print("\nOptional:")
    for tool, description in optional_tools.items():
        status = "✅" if converter.tools.get(tool, False) else "⚪"
        print(f"  {status} {tool:<12} - {description}")
    
    print("\nInstallation commands:")
    print("  pandoc:     brew install pandoc (macOS) | apt install pandoc (Linux)")
    print("  imagemagick: brew install imagemagick | apt install imagemagick")
    print("  tesseract:   brew install tesseract | apt install tesseract-ocr")
    print("  Python deps: pip install pytesseract tqdm")

def create_config_output(preset: str) -> None:
    """Output configuration for a preset."""
    try:
        config = get_preset_config(preset)
        from .config import save_config
        import tempfile
        import yaml
        
        # Convert to dict and output as YAML
        from dataclasses import asdict
        config_dict = asdict(config)
        
        print("# DocMind Configuration")
        print(f"# Preset: {preset}")
        print(f"# Generated by DocMind v1.0.0")
        print()
        print(yaml.dump(config_dict, indent=2, default_flow_style=False))
        
    except Exception as e:
        print(f"Error generating config: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Handle utility commands
        if args.create_config:
            create_config_output(args.create_config)
            return
        
        if args.check_deps:
            check_dependencies()
            return
        
        # Validate arguments
        validate_args(args)
        
        # Expand file patterns
        input_files = expand_file_patterns(args.input_files)
        
        if not input_files:
            print("❌ No files found matching the patterns", file=sys.stderr)
            sys.exit(1)
        
        # Filter existing files
        existing_files = [f for f in input_files if f.exists()]
        if len(existing_files) != len(input_files):
            missing = set(input_files) - set(existing_files)
            print(f"⚠️  Warning: {len(missing)} files not found: {missing}")
        
        if not existing_files:
            print("❌ No valid input files found", file=sys.stderr)
            sys.exit(1)
        
        # Create configuration
        config = args_to_config(args)
        
        # Save config if requested
        if args.save_config:
            save_config(config, args.save_config)
            print(f"📄 Configuration saved to: {args.save_config}")
        
        # Dry run mode
        if args.dry_run:
            print("🔍 DRY RUN MODE - No files will be processed")
            print(f"📁 Output directory: {args.output}")
            print(f"📋 Quality preset: {args.quality}")
            print(f"📄 Files to process: {len(existing_files)}")
            for f in existing_files:
                print(f"  - {f}")
            return
        
        # Check if output directory exists and handle force flag
        if args.output.exists() and not args.force:
            response = input(f"Output directory '{args.output}' exists. Overwrite? [y/N]: ")
            if response.lower() not in ['y', 'yes']:
                print("❌ Cancelled by user")
                sys.exit(1)
        
        # Initialize converter
        converter = DocMind(config=config, output_dir=str(args.output))
        
        # Process files
        success = converter.convert(existing_files)
        
        if success:
            print(f"🎉 All files converted successfully!")
            print(f"📁 Results in: {args.output}")
        else:
            print(f"⚠️  Some files failed to convert. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        if args.verbose if hasattr(args, 'verbose') else False:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()