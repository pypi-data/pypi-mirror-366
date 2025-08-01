from typing import List, Dict, Optional, Any
from pydantic import BaseModel, ValidationError, Field, field_validator, model_validator
import json
import os
from os.path import exists, dirname
from os import makedirs
from functools import lru_cache
import sys

DEFAULT_CONFIG_LOCATION = "./ara/.araconfig/ara_config.json"

class LLMConfigItem(BaseModel):
    provider: str
    model: str
    temperature: float = Field(ge=0.0, le=1.0)
    max_tokens: Optional[int] = None
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float, info) -> float:
        if not 0.0 <= v <= 1.0:
            print(f"Warning: Temperature is outside the 0.0 to 1.0 range")
            # Return a valid default
            return 0.8
        return v

class ExtCodeDirItem(BaseModel):
    source_dir: str

class ARAconfig(BaseModel):
    ext_code_dirs: List[ExtCodeDirItem] = Field(default_factory=lambda: [
        ExtCodeDirItem(source_dir="./src"),
        ExtCodeDirItem(source_dir="./tests")
    ])
    glossary_dir: str = "./glossary"
    doc_dir: str = "./docs"
    local_prompt_templates_dir: str = "./ara/.araconfig"
    custom_prompt_templates_subdir: Optional[str] = "custom-prompt-modules"
    local_ara_templates_dir: str = "./ara/.araconfig/templates/"
    ara_prompt_given_list_includes: List[str] = Field(default_factory=lambda: [
        "*.businessgoal",
        "*.vision",
        "*.capability",
        "*.keyfeature",
        "*.epic",
        "*.userstory",
        "*.example",
        "*.feature",
        "*.task",
        "*.py",
        "*.md",
        "*.png",
        "*.jpg",
        "*.jpeg",
    ])
    llm_config: Dict[str, LLMConfigItem] = Field(default_factory=lambda: {
        "gpt-4o": LLMConfigItem(
            provider="openai",
            model="openai/gpt-4o",
            temperature=0.8,
            max_tokens=16384
        ),
        "gpt-4.1": LLMConfigItem(
            provider="openai",
            model="openai/gpt-4.1",
            temperature=0.8,
            max_tokens=1024
        ),
        "o3-mini": LLMConfigItem(
            provider="openai",
            model="openai/o3-mini",
            temperature=1.0,
            max_tokens=1024
        ),
        "opus-4": LLMConfigItem(
            provider="anthropic",
            model="anthropic/claude-opus-4-20250514",
            temperature=0.8,
            max_tokens=32000
        ),
        "sonnet-4": LLMConfigItem(
            provider="anthropic",
            model="anthropic/claude-sonnet-4-20250514",
            temperature=0.8,
            max_tokens=1024
        ),
        "together-ai-llama-2": LLMConfigItem(
            provider="together_ai",
            model="together_ai/togethercomputer/llama-2-70b",
            temperature=0.8,
            max_tokens=1024
        ),
        "groq-llama-3": LLMConfigItem(
            provider="groq",
            model="groq/llama3-70b-8192",
            temperature=0.8,
            max_tokens=1024
        )
    })
    default_llm: Optional[str] = "gpt-4o"
    
    model_config = {
        "extra": "forbid"  # This will help identify unrecognized keys
    }

    @model_validator(mode='after')
    def check_critical_fields(self) -> 'ARAconfig':
        """Check for empty critical fields and use defaults if needed"""
        critical_fields = {
            'ext_code_dirs': [ExtCodeDirItem(source_dir="./src"), ExtCodeDirItem(source_dir="./tests")],
            'local_ara_templates_dir': "./ara/.araconfig/templates/",
            'local_prompt_templates_dir': "./ara/.araconfig",
            'glossary_dir': "./glossary"
        }
        
        for field, default_value in critical_fields.items():
            current_value = getattr(self, field)
            if (not current_value or 
                (isinstance(current_value, list) and len(current_value) == 0) or
                (isinstance(current_value, str) and current_value.strip() == "")):
                print(f"Warning: Value for '{field}' is missing or empty.")
                setattr(self, field, default_value)
        
        return self

# Function to ensure the necessary directories exist
@lru_cache(maxsize=None)
def ensure_directory_exists(directory: str):
    if not exists(directory):
        os.makedirs(directory)
        print(f"New directory created at {directory}")
    return directory

def handle_unrecognized_keys(data: dict, known_fields: set) -> dict:
    """Remove unrecognized keys and warn the user"""
    cleaned_data = {}
    for key, value in data.items():
        if key not in known_fields:
            print(f"Warning: {key} is not recognized as a valid configuration option.")
        else:
            cleaned_data[key] = value
    return cleaned_data

def fix_llm_temperatures(data: dict) -> dict:
    """Fix invalid temperatures in LLM configurations"""
    if 'llm_config' in data:
        for model_key, model_config in data['llm_config'].items():
            if isinstance(model_config, dict) and 'temperature' in model_config:
                temp = model_config['temperature']
                if not 0.0 <= temp <= 1.0:
                    print(f"Warning: Temperature for model '{model_key}' is outside the 0.0 to 1.0 range")
                    model_config['temperature'] = 0.8
    return data

def validate_and_fix_config_data(filepath: str) -> dict:
    """Load, validate, and fix configuration data"""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Get known fields from the ARAconfig model
        known_fields = set(ARAconfig.model_fields.keys())
        
        # Handle unrecognized keys
        data = handle_unrecognized_keys(data, known_fields)
        
        # Fix LLM temperatures before validation
        data = fix_llm_temperatures(data)
        
        return data
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        print("Creating new configuration with defaults...")
        return {}
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return {}

# Function to read the JSON file and return an ARAconfig model
@lru_cache(maxsize=1)
def read_data(filepath: str) -> ARAconfig:
    # Ensure the directory for the config file exists
    config_dir = dirname(filepath)
    ensure_directory_exists(config_dir)

    if not exists(filepath):
        # If the file does not exist, create it with default values
        default_config = ARAconfig()
        save_data(filepath, default_config)
        print(
            f"ara-cli configuration file '{filepath}' created with default configuration."
            f" Please modify it as needed and re-run your command"
        )
        sys.exit(0)  # Exit the application

    # Validate and load the existing configuration
    data = validate_and_fix_config_data(filepath)
    
    try:
        # Try to create the config with the loaded data
        config = ARAconfig(**data)
        
        # Save the potentially fixed configuration back
        save_data(filepath, config)
        
        return config
    except ValidationError as e:
        print(f"ValidationError: {e}")
        print("Correcting configuration with default values...")
        
        # Create a default config
        default_config = ARAconfig()
        
        # Try to preserve valid fields from the original data
        for field_name, field_value in data.items():
            if field_name in ARAconfig.model_fields:
                try:
                    # Attempt to set the field value
                    setattr(default_config, field_name, field_value)
                except:
                    # If it fails, keep the default
                    pass
        
        # Save the corrected configuration
        save_data(filepath, default_config)
        print("Fixed configuration saved to file.")
        
        return default_config

# Function to save the modified configuration back to the JSON file
def save_data(filepath: str, config: ARAconfig):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(config.model_dump(), file, indent=4)

# Singleton for configuration management
class ConfigManager:
    _config_instance = None

    @classmethod
    def get_config(cls, filepath=DEFAULT_CONFIG_LOCATION):
        if cls._config_instance is None:
            config_dir = dirname(filepath)

            if not exists(config_dir):
                makedirs(config_dir)

            cls._config_instance = read_data(filepath)
        return cls._config_instance
    
    @classmethod
    def reset(cls):
        """Reset the configuration instance (useful for testing)"""
        cls._config_instance = None
        read_data.cache_clear()