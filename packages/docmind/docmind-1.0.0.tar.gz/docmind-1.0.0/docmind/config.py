"""Configuration management for DocMind."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from .exceptions import ConfigurationError

@dataclass
class ImageConfig:
    """Image processing configuration."""
    min_width: int = 800
    min_height: int = 600
    quality: int = 95
    optimize_for_llm: bool = True
    enhance_contrast: float = 1.1
    enhance_sharpness: float = 1.2
    format: str = "PNG"

@dataclass
class ConversionConfig:
    """Document conversion configuration."""
    extract_tables: bool = True
    preserve_formatting: bool = True
    include_metadata: bool = True
    ocr_enabled: bool = False
    ocr_language: str = "eng"
    pandoc_extra_args: list = None

@dataclass  
class OutputConfig:
    """Output configuration."""
    format: str = "markdown"  # markdown, html, json
    flavor: str = "github"  # github, gitlab, standard
    include_toc: bool = False
    separate_tables: bool = True
    separate_images: bool = True

@dataclass
class PerformanceConfig:
    """Performance configuration."""
    max_file_size_mb: int = 500
    chunk_size_pages: int = 10
    max_workers: int = 4
    enable_resume: bool = True
    cache_enabled: bool = True

@dataclass
class DocMindConfig:
    """Main DocMind configuration."""
    image: ImageConfig = None
    conversion: ConversionConfig = None
    output: OutputConfig = None
    performance: PerformanceConfig = None
    
    def __post_init__(self):
        if self.image is None:
            self.image = ImageConfig()
        if self.conversion is None:
            self.conversion = ConversionConfig()
        if self.output is None:
            self.output = OutputConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
            
        # Set default pandoc args if None
        if self.conversion.pandoc_extra_args is None:
            self.conversion.pandoc_extra_args = []

def load_config(config_path: Optional[Path] = None) -> DocMindConfig:
    """Load configuration from file or return defaults."""
    if config_path is None:
        # Look for config in common locations
        for path in [
            Path.cwd() / "docmind.yaml",
            Path.cwd() / "docmind.yml", 
            Path.cwd() / "docmind.json",
            Path.home() / ".docmind.yaml",
            Path.home() / ".docmind.yml",
            Path.home() / ".docmind.json"
        ]:
            if path.exists():
                config_path = path
                break
    
    if config_path is None or not config_path.exists():
        return DocMindConfig()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ConfigurationError(f"Unsupported config format: {config_path.suffix}")
        
        return _dict_to_config(data)
        
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise ConfigurationError(f"Invalid config file format: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error loading config: {e}")

def save_config(config: DocMindConfig, config_path: Path) -> None:
    """Save configuration to file."""
    try:
        data = asdict(config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(data, f, indent=2, default_flow_style=False)
            elif config_path.suffix.lower() == '.json':
                json.dump(data, f, indent=2)
            else:
                raise ConfigurationError(f"Unsupported config format: {config_path.suffix}")
                
    except Exception as e:
        raise ConfigurationError(f"Error saving config: {e}")

def _dict_to_config(data: Dict[str, Any]) -> DocMindConfig:
    """Convert dictionary to DocMindConfig."""
    try:
        image_data = data.get('image', {})
        conversion_data = data.get('conversion', {})
        output_data = data.get('output', {})
        performance_data = data.get('performance', {})
        
        return DocMindConfig(
            image=ImageConfig(**image_data),
            conversion=ConversionConfig(**conversion_data),
            output=OutputConfig(**output_data),
            performance=PerformanceConfig(**performance_data)
        )
    except TypeError as e:
        raise ConfigurationError(f"Invalid configuration data: {e}")

# Quality presets
QUALITY_PRESETS = {
    "fast": DocMindConfig(
        image=ImageConfig(min_width=400, min_height=300, quality=80, optimize_for_llm=False),
        conversion=ConversionConfig(extract_tables=False, ocr_enabled=False),
        performance=PerformanceConfig(chunk_size_pages=20, max_workers=8)
    ),
    "balanced": DocMindConfig(),  # Default config
    "high": DocMindConfig(
        image=ImageConfig(min_width=1200, min_height=900, quality=98, optimize_for_llm=True),
        conversion=ConversionConfig(extract_tables=True, ocr_enabled=True),
        performance=PerformanceConfig(chunk_size_pages=5, max_workers=2)
    ),
    "ai_optimized": DocMindConfig(
        image=ImageConfig(
            min_width=1600, min_height=1200, quality=98, 
            optimize_for_llm=True, enhance_contrast=1.3, enhance_sharpness=1.5
        ),
        conversion=ConversionConfig(extract_tables=True, ocr_enabled=True, preserve_formatting=True),
        output=OutputConfig(include_toc=True, separate_tables=True),
        performance=PerformanceConfig(chunk_size_pages=3, max_workers=1)
    )
}

def get_preset_config(preset: str) -> DocMindConfig:
    """Get a quality preset configuration."""
    if preset not in QUALITY_PRESETS:
        raise ConfigurationError(f"Unknown preset: {preset}. Available: {list(QUALITY_PRESETS.keys())}")
    return QUALITY_PRESETS[preset]