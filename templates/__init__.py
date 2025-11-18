"""Template system for agent and skill configuration generation."""

from .template_engine import TemplatePopulator, TemplateType
from .population import (
    populate_agent_config,
    populate_skill_config,
    generate_skill_id,
)

__all__ = [
    'TemplatePopulator',
    'TemplateType',
    'populate_agent_config',
    'populate_skill_config',
    'generate_skill_id',
]
