"""
Skill Orchestration Framework and Management System

A flexible, extensible system for chaining AI/ML skills together,
with skill loading and management capabilities.
"""

# Orchestration framework
from .base_skill import (
    BaseSkill,
    SkillContext,
    SkillMetadata,
    SkillStatus,
    PassthroughSkill,
    TransformSkill
)

from .registry import SkillRegistry, SkillCatalog, get_global_registry
from .orchestrator import SkillOrchestrator, ChainConfig

# Skill management system
from .skill_loader import SkillLoader, load_skill, load_all_skills

__all__ = [
    # Orchestration framework
    "BaseSkill",
    "SkillContext",
    "SkillMetadata",
    "SkillStatus",
    "PassthroughSkill",
    "TransformSkill",
    "SkillRegistry",
    "SkillCatalog",
    "get_global_registry",
    "SkillOrchestrator",
    "ChainConfig",
    # Skill management
    "SkillLoader",
    "load_skill",
    "load_all_skills",
]

__version__ = "1.0.0"