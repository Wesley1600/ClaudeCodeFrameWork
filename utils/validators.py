"""Configuration validation utilities.

This module provides validation functions for agent and skill configurations,
ensuring they conform to the defined schemas and contain all required fields.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import yaml


class ValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.errors = errors or []

    def __str__(self):
        if self.errors:
            error_list = '\n  - '.join(self.errors)
            return f"{super().__str__()}\n  - {error_list}"
        return super().__str__()


class ConfigValidator:
    """Validates agent and skill configurations against schemas.

    Attributes:
        schema_dir: Directory containing schema YAML files
        agent_schema: Loaded agent schema
        skill_schema: Loaded skill schema

    Example:
        >>> validator = ConfigValidator()
        >>> config = {"id": "agent_001", "name": "TestAgent", ...}
        >>> is_valid, errors = validator.validate_agent(config)
    """

    def __init__(self, schema_dir: Optional[str] = None):
        """Initialize the validator with schema files.

        Args:
            schema_dir: Path to directory containing schema YAML files.
                       Defaults to 'config' directory in project root.
        """
        if schema_dir is None:
            # Default to config directory
            base_path = Path(__file__).parent.parent
            schema_dir = str(base_path / "config")

        self.schema_dir = Path(schema_dir)
        self.agent_schema = self._load_schema("agent_schema.yaml")
        self.skill_schema = self._load_schema("skill_schema.yaml")

    def _load_schema(self, schema_file: str) -> Dict[str, Any]:
        """Load a schema YAML file.

        Args:
            schema_file: Name of schema file

        Returns:
            Loaded schema dictionary

        Raises:
            FileNotFoundError: If schema file doesn't exist
        """
        schema_path = self.schema_dir / schema_file

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_agent(
        self,
        config: Dict[str, Any],
        strict: bool = True
    ) -> Tuple[bool, List[str]]:
        """Validate an agent configuration.

        Args:
            config: Agent configuration dictionary
            strict: If True, enforce all validation rules strictly

        Returns:
            Tuple of (is_valid, error_messages)

        Example:
            >>> validator = ConfigValidator()
            >>> config = {"id": "agent_001", "name": "TestAgent"}
            >>> is_valid, errors = validator.validate_agent(config)
            >>> if not is_valid:
            ...     print(f"Validation failed: {errors}")
        """
        errors = []

        # Check required fields
        required = self.agent_schema.get('required_fields', [])
        for field in required:
            if field not in config:
                errors.append(f"Missing required field: '{field}'")
            elif not config[field]:
                errors.append(f"Required field '{field}' is empty")

        # Validate field types and constraints
        fields_schema = self.agent_schema.get('fields', {})

        # Validate ID pattern
        if 'id' in config:
            pattern = fields_schema.get('id', {}).get('pattern')
            if pattern and not re.match(pattern, config['id']):
                errors.append(
                    f"Agent ID '{config['id']}' doesn't match pattern '{pattern}'"
                )

        # Validate version format
        if 'version' in config:
            pattern = fields_schema.get('version', {}).get('pattern')
            if pattern and not re.match(pattern, config['version']):
                errors.append(
                    f"Version '{config['version']}' doesn't match pattern '{pattern}'"
                )

        # Validate skills array
        if 'skills' in config:
            if not isinstance(config['skills'], list):
                errors.append("'skills' must be an array")
            elif len(config['skills']) == 0:
                errors.append("'skills' array cannot be empty")
            else:
                # Validate skill_id patterns
                skill_pattern = r'^skill_[a-z0-9_]+$'
                for skill_id in config['skills']:
                    if not re.match(skill_pattern, skill_id):
                        errors.append(
                            f"Invalid skill_id '{skill_id}' (must match pattern '{skill_pattern}')"
                        )

        # Validate string lengths
        string_fields = ['name', 'description']
        for field in string_fields:
            if field in config:
                field_schema = fields_schema.get(field, {})
                min_len = field_schema.get('min_length')
                max_len = field_schema.get('max_length')

                value = config[field]
                if min_len and len(value) < min_len:
                    errors.append(
                        f"Field '{field}' must be at least {min_len} characters"
                    )
                if max_len and len(value) > max_len:
                    errors.append(
                        f"Field '{field}' must be at most {max_len} characters"
                    )

        # Validate parameters if present
        if 'parameters' in config:
            param_errors = self._validate_parameters(config['parameters'])
            errors.extend(param_errors)

        # Validate metadata if present
        if 'metadata' in config and strict:
            meta_errors = self._validate_metadata(config['metadata'], 'agent')
            errors.extend(meta_errors)

        return (len(errors) == 0, errors)

    def validate_skill(
        self,
        config: Dict[str, Any],
        strict: bool = True
    ) -> Tuple[bool, List[str]]:
        """Validate a skill configuration.

        Args:
            config: Skill configuration dictionary
            strict: If True, enforce all validation rules strictly

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        required = self.skill_schema.get('required_fields', [])
        for field in required:
            if field not in config:
                errors.append(f"Missing required field: '{field}'")
            elif not config[field]:
                errors.append(f"Required field '{field}' is empty")

        # Validate field types and constraints
        fields_schema = self.skill_schema.get('fields', {})

        # Validate skill_id pattern
        if 'skill_id' in config:
            pattern = fields_schema.get('skill_id', {}).get('pattern')
            if pattern and not re.match(pattern, config['skill_id']):
                errors.append(
                    f"Skill ID '{config['skill_id']}' doesn't match pattern '{pattern}'"
                )

        # Validate category
        if 'category' in config:
            valid_categories = fields_schema.get('category', {}).get('enum', [])
            if valid_categories and config['category'] not in valid_categories:
                errors.append(
                    f"Invalid category '{config['category']}'. "
                    f"Must be one of: {', '.join(valid_categories)}"
                )

        # Validate string lengths
        string_fields = ['name', 'description']
        for field in string_fields:
            if field in config:
                field_schema = fields_schema.get(field, {})
                min_len = field_schema.get('min_length')
                max_len = field_schema.get('max_length')

                value = config[field]
                if min_len and len(value) < min_len:
                    errors.append(
                        f"Field '{field}' must be at least {min_len} characters"
                    )
                if max_len and len(value) > max_len:
                    errors.append(
                        f"Field '{field}' must be at most {max_len} characters"
                    )

        # Validate inputs/outputs if present
        if 'inputs' in config:
            input_errors = self._validate_io_specs(config['inputs'], 'inputs')
            errors.extend(input_errors)

        if 'outputs' in config:
            output_errors = self._validate_io_specs(config['outputs'], 'outputs')
            errors.extend(output_errors)

        # Validate metadata if present
        if 'metadata' in config and strict:
            meta_errors = self._validate_metadata(config['metadata'], 'skill')
            errors.extend(meta_errors)

        return (len(errors) == 0, errors)

    def _validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """Validate agent parameters.

        Args:
            params: Parameters dictionary

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate temperature
        if 'temperature' in params:
            temp = params['temperature']
            if not isinstance(temp, (int, float)):
                errors.append("'temperature' must be a number")
            elif temp < 0.0 or temp > 2.0:
                errors.append("'temperature' must be between 0.0 and 2.0")

        # Validate max_tokens
        if 'max_tokens' in params:
            max_tok = params['max_tokens']
            if not isinstance(max_tok, int):
                errors.append("'max_tokens' must be an integer")
            elif max_tok < 1:
                errors.append("'max_tokens' must be at least 1")

        # Validate top_p
        if 'top_p' in params:
            top_p = params['top_p']
            if not isinstance(top_p, (int, float)):
                errors.append("'top_p' must be a number")
            elif top_p < 0.0 or top_p > 1.0:
                errors.append("'top_p' must be between 0.0 and 1.0")

        return errors

    def _validate_io_specs(
        self,
        io_list: List[Dict[str, Any]],
        field_name: str
    ) -> List[str]:
        """Validate input/output specifications.

        Args:
            io_list: List of input/output specifications
            field_name: Name of field being validated ('inputs' or 'outputs')

        Returns:
            List of validation error messages
        """
        errors = []

        if not isinstance(io_list, list):
            errors.append(f"'{field_name}' must be an array")
            return errors

        valid_types = ['string', 'integer', 'float', 'boolean', 'array', 'object']

        for idx, io_spec in enumerate(io_list):
            if not isinstance(io_spec, dict):
                errors.append(f"{field_name}[{idx}] must be an object")
                continue

            # Check required fields
            if 'name' not in io_spec:
                errors.append(f"{field_name}[{idx}] missing required field 'name'")
            if 'type' not in io_spec:
                errors.append(f"{field_name}[{idx}] missing required field 'type'")
            elif io_spec['type'] not in valid_types:
                errors.append(
                    f"{field_name}[{idx}] has invalid type '{io_spec['type']}'. "
                    f"Must be one of: {', '.join(valid_types)}"
                )

        return errors

    def _validate_metadata(
        self,
        metadata: Dict[str, Any],
        config_type: str
    ) -> List[str]:
        """Validate metadata fields.

        Args:
            metadata: Metadata dictionary
            config_type: Type of config ('agent' or 'skill')

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate complexity if present
        if 'complexity' in metadata:
            valid_levels = ['low', 'medium', 'high']
            if metadata['complexity'] not in valid_levels:
                errors.append(
                    f"Invalid complexity '{metadata['complexity']}'. "
                    f"Must be one of: {', '.join(valid_levels)}"
                )

        # Validate tags if present
        if 'tags' in metadata:
            if not isinstance(metadata['tags'], list):
                errors.append("'tags' must be an array")

        # Validate version if present
        if 'version' in metadata:
            version_pattern = r'^\d+\.\d+\.\d+$'
            if not re.match(version_pattern, metadata['version']):
                errors.append(
                    f"Version '{metadata['version']}' doesn't match pattern '{version_pattern}'"
                )

        return errors


def validate_agent_config(
    config: Dict[str, Any],
    strict: bool = True,
    schema_dir: Optional[str] = None
) -> None:
    """Validate an agent configuration, raising exception if invalid.

    Args:
        config: Agent configuration dictionary
        strict: If True, enforce all validation rules strictly
        schema_dir: Optional custom schema directory

    Raises:
        ValidationError: If configuration is invalid

    Example:
        >>> config = {"id": "agent_001", "name": "TestAgent"}
        >>> try:
        ...     validate_agent_config(config)
        ... except ValidationError as e:
        ...     print(f"Invalid config: {e}")
    """
    validator = ConfigValidator(schema_dir)
    is_valid, errors = validator.validate_agent(config, strict)

    if not is_valid:
        raise ValidationError("Agent configuration validation failed", errors)


def validate_skill_config(
    config: Dict[str, Any],
    strict: bool = True,
    schema_dir: Optional[str] = None
) -> None:
    """Validate a skill configuration, raising exception if invalid.

    Args:
        config: Skill configuration dictionary
        strict: If True, enforce all validation rules strictly
        schema_dir: Optional custom schema directory

    Raises:
        ValidationError: If configuration is invalid

    Example:
        >>> config = {"skill_id": "skill_001", "name": "TestSkill"}
        >>> try:
        ...     validate_skill_config(config)
        ... except ValidationError as e:
        ...     print(f"Invalid config: {e}")
    """
    validator = ConfigValidator(schema_dir)
    is_valid, errors = validator.validate_skill(config, strict)

    if not is_valid:
        raise ValidationError("Skill configuration validation failed", errors)
