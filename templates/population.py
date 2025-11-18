"""Helper functions for populating agent and skill templates.

This module provides high-level convenience functions for generating
agent and skill configurations with automatic ID generation and metadata
handling.
"""

import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List


def generate_skill_id(
    name: str,
    category: Optional[str] = None,
    use_uuid: bool = False
) -> str:
    """Generate a unique skill_id based on name and category.

    Args:
        name: Skill name
        category: Optional category for namespacing
        use_uuid: If True, append UUID for guaranteed uniqueness

    Returns:
        Generated skill_id

    Examples:
        >>> generate_skill_id("TextAnalyzer", "nlp")
        'skill_nlp_textanalyzer_001'

        >>> generate_skill_id("DataProcessor", use_uuid=True)
        'skill_dataprocessor_f47ac10b'
    """
    # Normalize name
    normalized_name = name.lower().replace(' ', '_').replace('-', '_')

    # Build ID components
    parts = ['skill']

    if category:
        normalized_category = category.lower().replace(' ', '_')
        parts.append(normalized_category)

    parts.append(normalized_name)

    if use_uuid:
        # Use first 8 chars of UUID
        unique_id = str(uuid.uuid4())[:8]
        parts.append(unique_id)
    else:
        # Use counter-style suffix
        parts.append('001')

    return '_'.join(parts)


def generate_agent_id(
    name: str,
    version: str = "1.0.0",
    use_uuid: bool = False
) -> str:
    """Generate a unique agent ID.

    Args:
        name: Agent name
        version: Agent version
        use_uuid: If True, append UUID for guaranteed uniqueness

    Returns:
        Generated agent ID

    Examples:
        >>> generate_agent_id("ResearchAgent")
        'agent_researchagent_v1'

        >>> generate_agent_id("DataAgent", "2.1.0", use_uuid=True)
        'agent_dataagent_v2_f47ac10b'
    """
    normalized_name = name.lower().replace(' ', '_').replace('-', '_')

    # Extract major version
    major_version = version.split('.')[0] if version else '1'

    parts = ['agent', normalized_name, f'v{major_version}']

    if use_uuid:
        unique_id = str(uuid.uuid4())[:8]
        parts.append(unique_id)

    return '_'.join(parts)


def populate_agent_config(
    name: str,
    description: str,
    skills: List[str],
    agent_id: Optional[str] = None,
    version: str = "1.0.0",
    metadata: Optional[Dict[str, Any]] = None,
    prompt_template: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a complete agent configuration dictionary.

    This is a convenience function that builds a properly structured
    agent configuration ready for template population.

    Args:
        name: Human-readable agent name
        description: Agent description
        skills: List of skill_ids this agent uses
        agent_id: Optional custom agent ID (auto-generated if not provided)
        version: Agent version (default: "1.0.0")
        metadata: Optional metadata dictionary
        prompt_template: Optional prompt template reference
        parameters: Optional agent parameters (temperature, max_tokens, etc.)

    Returns:
        Complete agent configuration dictionary

    Example:
        >>> config = populate_agent_config(
        ...     name="ResearchAgent",
        ...     description="Conducts comprehensive research",
        ...     skills=["skill_search_001", "skill_analyze_001"],
        ...     metadata={"author": "AI Team", "tags": ["research", "analysis"]}
        ... )
    """
    if agent_id is None:
        agent_id = generate_agent_id(name, version)

    agent_config = {
        'id': agent_id,
        'name': name,
        'version': version,
        'description': description,
        'skills': skills,
        'created_at': datetime.utcnow(),
        'metadata': metadata or {},
    }

    # Add optional fields if provided
    if prompt_template:
        agent_config['prompt_template'] = prompt_template

    if parameters:
        agent_config['parameters'] = parameters
    else:
        # Default parameters
        agent_config['parameters'] = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.9,
        }

    # Ensure metadata has required fields
    if 'author' not in agent_config['metadata']:
        agent_config['metadata']['author'] = 'Unknown'

    if 'tags' not in agent_config['metadata']:
        agent_config['metadata']['tags'] = []

    return agent_config


def populate_skill_config(
    name: str,
    description: str,
    category: str = "general",
    skill_id: Optional[str] = None,
    inputs: Optional[List[Dict[str, Any]]] = None,
    outputs: Optional[List[Dict[str, Any]]] = None,
    prompt_template: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    dependencies: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create a complete skill configuration dictionary.

    This is a convenience function that builds a properly structured
    skill configuration ready for template population.

    Args:
        name: Human-readable skill name
        description: Skill description
        category: Skill category (e.g., 'nlp', 'data', 'communication')
        skill_id: Optional custom skill ID (auto-generated if not provided)
        inputs: Optional list of input specifications
        outputs: Optional list of output specifications
        prompt_template: Optional prompt template reference
        metadata: Optional metadata dictionary
        dependencies: Optional list of skill dependencies

    Returns:
        Complete skill configuration dictionary

    Example:
        >>> config = populate_skill_config(
        ...     name="TextAnalyzer",
        ...     description="Analyzes text patterns and sentiment",
        ...     category="nlp",
        ...     inputs=[{"name": "text", "type": "string", "required": True}],
        ...     outputs=[{"name": "sentiment", "type": "string"}]
        ... )
    """
    if skill_id is None:
        skill_id = generate_skill_id(name, category)

    skill_config = {
        'skill_id': skill_id,
        'name': name,
        'description': description,
        'category': category,
        'created_at': datetime.utcnow(),
        'inputs': inputs or [],
        'outputs': outputs or [],
        'metadata': metadata or {},
    }

    # Add optional fields if provided
    if prompt_template:
        skill_config['prompt_template'] = prompt_template

    if dependencies:
        skill_config['metadata']['dependencies'] = dependencies

    # Ensure metadata has required fields
    if 'complexity' not in skill_config['metadata']:
        skill_config['metadata']['complexity'] = 'medium'

    if 'tags' not in skill_config['metadata']:
        skill_config['metadata']['tags'] = []

    return skill_config


def validate_skill_references(
    agent_config: Dict[str, Any],
    available_skills: List[str]
) -> List[str]:
    """Validate that all skill_ids in agent config exist.

    Args:
        agent_config: Agent configuration dictionary
        available_skills: List of available skill_ids

    Returns:
        List of invalid skill_ids (empty if all valid)

    Example:
        >>> agent = {"skills": ["skill_001", "skill_999"]}
        >>> available = ["skill_001", "skill_002"]
        >>> validate_skill_references(agent, available)
        ['skill_999']
    """
    agent_skills = agent_config.get('skills', [])
    invalid_skills = [
        skill_id for skill_id in agent_skills
        if skill_id not in available_skills
    ]

    return invalid_skills


def merge_metadata(
    base_metadata: Dict[str, Any],
    override_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge two metadata dictionaries, with override taking precedence.

    Args:
        base_metadata: Base metadata dictionary
        override_metadata: Override metadata dictionary

    Returns:
        Merged metadata dictionary

    Example:
        >>> base = {"author": "Team A", "tags": ["ml"]}
        >>> override = {"tags": ["ml", "nlp"], "version": "2.0"}
        >>> merge_metadata(base, override)
        {'author': 'Team A', 'tags': ['ml', 'nlp'], 'version': '2.0'}
    """
    merged = base_metadata.copy()

    for key, value in override_metadata.items():
        if key in merged and isinstance(merged[key], list) and isinstance(value, list):
            # Merge lists, removing duplicates while preserving order
            merged[key] = list(dict.fromkeys(merged[key] + value))
        else:
            # Override value
            merged[key] = value

    return merged


def generate_template_hash(config: Dict[str, Any]) -> str:
    """Generate a hash of a configuration for versioning.

    Args:
        config: Configuration dictionary

    Returns:
        SHA-256 hash (first 16 chars)

    Example:
        >>> config = {"name": "Agent", "version": "1.0"}
        >>> hash_val = generate_template_hash(config)
        >>> len(hash_val)
        16
    """
    import json

    # Sort keys for consistent hashing
    config_str = json.dumps(config, sort_keys=True)
    hash_obj = hashlib.sha256(config_str.encode('utf-8'))

    return hash_obj.hexdigest()[:16]
