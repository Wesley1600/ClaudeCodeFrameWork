"""
Task Classification and Routing System

This module provides intelligent task classification and routing capabilities
to automatically detect task types and select appropriate skills or agents.

Components:
- TaskClassifier: Classifies input tasks/documents into categories
- SkillRegistry: Manages available skills and their metadata
- TaskRouter: Routes classified tasks to appropriate skills

Example Usage:
    >>> router = TaskRouter()
    >>> result = router.route("Process this PDF file: report.pdf")
    >>> print(result.skill_id)  # 'pdf_processor'
    >>> print(result.confidence)  # 0.95
"""

from typing import List, Dict, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path


class TaskCategory(Enum):
    """Enumeration of supported task categories."""
    PDF = "pdf"
    SPREADSHEET = "spreadsheet"
    CODE_EXECUTION = "code_execution"
    TEXT_PROCESSING = "text_processing"
    IMAGE_PROCESSING = "image_processing"
    DATA_ANALYSIS = "data_analysis"
    WEB_SCRAPING = "web_scraping"
    FILE_MANAGEMENT = "file_management"
    API_INTERACTION = "api_interaction"
    DATABASE_QUERY = "database_query"
    MACHINE_LEARNING = "machine_learning"
    ANALOGY_FINDING = "analogy_finding"
    UNKNOWN = "unknown"


@dataclass
class SkillMetadata:
    """Metadata for a registered skill."""
    skill_id: str
    name: str
    category: TaskCategory
    description: str
    file_patterns: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    priority: int = 1  # Higher priority skills are preferred
    enabled: bool = True


@dataclass
class ClassificationResult:
    """Result of task classification."""
    category: TaskCategory
    confidence: float  # 0.0 to 1.0
    matched_patterns: List[str] = field(default_factory=list)
    matched_keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingResult:
    """Result of task routing."""
    skill_id: str
    skill_name: str
    category: TaskCategory
    confidence: float
    reasoning: str
    alternative_skills: List[str] = field(default_factory=list)


class TaskClassifier:
    """
    Classifies input tasks or documents into predefined categories.

    Uses multiple classification strategies:
    1. File extension pattern matching
    2. Keyword detection in task description
    3. Regex pattern matching
    4. Contextual analysis
    """

    def __init__(self):
        """Initialize the task classifier with pattern definitions."""
        # File extension patterns for each category
        self.file_patterns = {
            TaskCategory.PDF: [r'\.pdf$', r'pdf\s+file', r'pdf\s+document'],
            TaskCategory.SPREADSHEET: [
                r'\.(xlsx?|csv|ods)$',
                r'(excel|spreadsheet|csv|sheet)\s+(file|document)',
            ],
            TaskCategory.CODE_EXECUTION: [
                r'\.(py|js|ts|java|cpp|c|go|rb|rs|sh)$',
                r'(run|execute|eval|compile)\s+(code|script|program)',
            ],
            TaskCategory.IMAGE_PROCESSING: [
                r'\.(png|jpg|jpeg|gif|bmp|svg|webp)$',
                r'(image|photo|picture|screenshot)',
            ],
            TaskCategory.DATABASE_QUERY: [
                r'\.(sql|db|sqlite)$',
                r'(database|query|sql|select|insert|update)',
            ],
            TaskCategory.WEB_SCRAPING: [
                r'(scrape|crawl|extract)\s+(web|website|page|html)',
                r'https?://\S+',
            ],
        }

        # Keyword patterns for each category
        self.keyword_patterns = {
            TaskCategory.PDF: [
                'pdf', 'extract text from pdf', 'parse pdf', 'read pdf',
                'convert pdf', 'pdf to text', 'pdf reader', 'pdf document'
            ],
            TaskCategory.SPREADSHEET: [
                'excel', 'spreadsheet', 'csv', 'data table', 'pivot table',
                'dataframe', 'columns', 'rows', 'cells', 'formula', 'workbook'
            ],
            TaskCategory.CODE_EXECUTION: [
                'execute', 'run code', 'eval', 'compile', 'interpret',
                'debug', 'trace', 'python script', 'javascript code',
                'run script', 'run python', 'run this', 'execute code',
                'run the script', 'execute script'
            ],
            TaskCategory.TEXT_PROCESSING: [
                'text analysis', 'nlp', 'natural language', 'tokenize',
                'parse text', 'text mining', 'sentiment', 'summarize'
            ],
            TaskCategory.IMAGE_PROCESSING: [
                'image', 'photo', 'picture', 'resize', 'crop', 'filter',
                'ocr', 'computer vision', 'detect objects', 'face detection',
                'compress', 'optimize'
            ],
            TaskCategory.DATA_ANALYSIS: [
                'analyze data', 'statistics', 'visualization', 'plot',
                'chart', 'graph', 'correlation', 'regression', 'cluster',
                'visualize'
            ],
            TaskCategory.WEB_SCRAPING: [
                'scrape', 'crawl', 'web scraping', 'html', 'beautifulsoup',
                'selenium', 'extract from website', 'parse html', 'website',
                'web data', 'scraping'
            ],
            TaskCategory.FILE_MANAGEMENT: [
                'copy file', 'move file', 'delete file', 'rename file',
                'organize files', 'file system', 'directory', 'folder'
            ],
            TaskCategory.API_INTERACTION: [
                'api call', 'rest api', 'http request', 'endpoint',
                'api integration', 'fetch data', 'post request', 'get request'
            ],
            TaskCategory.DATABASE_QUERY: [
                'database', 'sql query', 'select from', 'insert into',
                'update table', 'join tables', 'mysql', 'postgresql', 'sqlite',
                'query'
            ],
            TaskCategory.MACHINE_LEARNING: [
                'machine learning', 'train model', 'neural network', 'deep learning',
                'classification', 'prediction', 'tensorflow', 'pytorch', 'sklearn',
                'train', 'model training', 'ml model'
            ],
            TaskCategory.ANALOGY_FINDING: [
                'analogy', 'semantic similarity', 'word vector', 'embedding',
                'relation', 'king queen', 'man woman', 'find similar',
                'analogies', 'semantic', 'word analogy', 'relation axis',
                'find analogy', 'semantic relationship'
            ],
        }

    def classify(self, task_input: str) -> ClassificationResult:
        """
        Classify a task input into a category.

        Args:
            task_input: The task description or file reference

        Returns:
            ClassificationResult with category and confidence score
        """
        task_lower = task_input.lower().strip()

        # Track scores for each category
        category_scores: Dict[TaskCategory, float] = {cat: 0.0 for cat in TaskCategory}
        matched_patterns: List[str] = []
        matched_keywords: List[str] = []

        # 1. File pattern matching (highest confidence)
        for category, patterns in self.file_patterns.items():
            for pattern in patterns:
                if re.search(pattern, task_lower, re.IGNORECASE):
                    category_scores[category] += 0.4
                    matched_patterns.append(pattern)

        # 2. Keyword matching (medium confidence)
        for category, keywords in self.keyword_patterns.items():
            for keyword in keywords:
                if keyword.lower() in task_lower:
                    category_scores[category] += 0.3 / len(keywords)
                    matched_keywords.append(keyword)

        # 3. Multi-keyword boost (contextual)
        for category, keywords in self.keyword_patterns.items():
            keyword_count = sum(1 for kw in keywords if kw.lower() in task_lower)
            if keyword_count >= 2:
                category_scores[category] += 0.2 * (keyword_count - 1)

        # Find the best matching category
        best_category = max(category_scores.items(), key=lambda x: x[1])
        category, score = best_category

        # Normalize confidence to 0-1 range
        confidence = min(1.0, score)

        # If confidence is too low, mark as unknown
        if confidence < 0.1:
            category = TaskCategory.UNKNOWN
            confidence = 0.0

        return ClassificationResult(
            category=category,
            confidence=confidence,
            matched_patterns=matched_patterns,
            matched_keywords=matched_keywords,
            metadata={
                'task_length': len(task_input),
                'all_scores': {k.value: v for k, v in category_scores.items()}
            }
        )

    def classify_file(self, file_path: Union[str, Path]) -> ClassificationResult:
        """
        Classify based on file path and extension.

        Args:
            file_path: Path to the file

        Returns:
            ClassificationResult for the file
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        filename = path.name

        # Create a task string that includes file info
        task_input = f"Process file: {filename} with extension {extension}"

        return self.classify(task_input)

    def classify_batch(self, tasks: List[str]) -> List[ClassificationResult]:
        """
        Classify multiple tasks in batch.

        Args:
            tasks: List of task descriptions

        Returns:
            List of classification results
        """
        return [self.classify(task) for task in tasks]


class SkillRegistry:
    """
    Registry for managing available skills and their metadata.

    Provides skill registration, lookup, and filtering capabilities.
    """

    def __init__(self):
        """Initialize the skill registry with default skills."""
        self.skills: Dict[str, SkillMetadata] = {}
        self._initialize_default_skills()

    def _initialize_default_skills(self):
        """Register default skills for common task categories."""
        default_skills = [
            SkillMetadata(
                skill_id="pdf_processor",
                name="PDF Processor",
                category=TaskCategory.PDF,
                description="Extract text, parse, and process PDF documents",
                file_patterns=["*.pdf"],
                keywords=["pdf", "extract", "parse"],
                capabilities=["text_extraction", "ocr", "metadata_extraction"],
                priority=10
            ),
            SkillMetadata(
                skill_id="excel_handler",
                name="Excel & Spreadsheet Handler",
                category=TaskCategory.SPREADSHEET,
                description="Read, write, and manipulate Excel and CSV files",
                file_patterns=["*.xlsx", "*.xls", "*.csv", "*.ods"],
                keywords=["excel", "spreadsheet", "csv", "dataframe"],
                capabilities=["read_excel", "write_excel", "pivot_table", "formulas"],
                priority=10
            ),
            SkillMetadata(
                skill_id="code_executor",
                name="Code Executor",
                category=TaskCategory.CODE_EXECUTION,
                description="Execute code snippets in various languages",
                file_patterns=["*.py", "*.js", "*.java", "*.cpp"],
                keywords=["execute", "run", "eval", "compile"],
                capabilities=["python", "javascript", "shell", "sandboxed_execution"],
                priority=9
            ),
            SkillMetadata(
                skill_id="text_analyzer",
                name="Text Analyzer",
                category=TaskCategory.TEXT_PROCESSING,
                description="Natural language processing and text analysis",
                keywords=["nlp", "text analysis", "sentiment", "tokenize"],
                capabilities=["sentiment_analysis", "entity_extraction", "summarization"],
                priority=7
            ),
            SkillMetadata(
                skill_id="image_processor",
                name="Image Processor",
                category=TaskCategory.IMAGE_PROCESSING,
                description="Process and analyze images",
                file_patterns=["*.png", "*.jpg", "*.jpeg", "*.gif"],
                keywords=["image", "photo", "ocr", "resize"],
                capabilities=["resize", "crop", "filter", "ocr", "object_detection"],
                priority=8
            ),
            SkillMetadata(
                skill_id="data_analyst",
                name="Data Analyst",
                category=TaskCategory.DATA_ANALYSIS,
                description="Statistical analysis and data visualization",
                keywords=["analyze", "statistics", "plot", "visualization"],
                capabilities=["statistics", "plotting", "correlation", "regression"],
                priority=8
            ),
            SkillMetadata(
                skill_id="web_scraper",
                name="Web Scraper",
                category=TaskCategory.WEB_SCRAPING,
                description="Extract data from websites",
                keywords=["scrape", "crawl", "html", "website"],
                capabilities=["html_parsing", "javascript_rendering", "data_extraction"],
                priority=7
            ),
            SkillMetadata(
                skill_id="file_manager",
                name="File Manager",
                category=TaskCategory.FILE_MANAGEMENT,
                description="File system operations",
                keywords=["copy", "move", "delete", "rename", "file"],
                capabilities=["copy", "move", "delete", "rename", "organize"],
                priority=5
            ),
            SkillMetadata(
                skill_id="api_client",
                name="API Client",
                category=TaskCategory.API_INTERACTION,
                description="Interact with REST APIs",
                keywords=["api", "rest", "http", "endpoint"],
                capabilities=["get", "post", "put", "delete", "authentication"],
                priority=7
            ),
            SkillMetadata(
                skill_id="db_client",
                name="Database Client",
                category=TaskCategory.DATABASE_QUERY,
                description="Execute database queries",
                file_patterns=["*.sql", "*.db", "*.sqlite"],
                keywords=["database", "sql", "query", "select"],
                capabilities=["mysql", "postgresql", "sqlite", "query_builder"],
                priority=8
            ),
            SkillMetadata(
                skill_id="ml_engine",
                name="Machine Learning Engine",
                category=TaskCategory.MACHINE_LEARNING,
                description="Train and deploy ML models",
                keywords=["machine learning", "train", "model", "neural"],
                capabilities=["training", "inference", "preprocessing", "evaluation"],
                priority=9
            ),
            SkillMetadata(
                skill_id="analogy_finder",
                name="Analogy Finder (UMAP)",
                category=TaskCategory.ANALOGY_FINDING,
                description="Find semantic analogies using UMAP-based engine",
                keywords=["analogy", "semantic", "relation", "embedding"],
                capabilities=["word_analogies", "relation_extraction", "similarity_search"],
                priority=10
            ),
        ]

        for skill in default_skills:
            self.register_skill(skill)

    def register_skill(self, skill: SkillMetadata) -> None:
        """
        Register a new skill.

        Args:
            skill: SkillMetadata object to register
        """
        self.skills[skill.skill_id] = skill

    def unregister_skill(self, skill_id: str) -> bool:
        """
        Unregister a skill.

        Args:
            skill_id: ID of the skill to unregister

        Returns:
            True if skill was unregistered, False if not found
        """
        if skill_id in self.skills:
            del self.skills[skill_id]
            return True
        return False

    def get_skill(self, skill_id: str) -> Optional[SkillMetadata]:
        """
        Get skill by ID.

        Args:
            skill_id: The skill ID

        Returns:
            SkillMetadata if found, None otherwise
        """
        return self.skills.get(skill_id)

    def get_skills_by_category(self, category: TaskCategory) -> List[SkillMetadata]:
        """
        Get all skills for a specific category.

        Args:
            category: The task category

        Returns:
            List of matching skills, sorted by priority
        """
        matching_skills = [
            skill for skill in self.skills.values()
            if skill.category == category and skill.enabled
        ]
        return sorted(matching_skills, key=lambda s: s.priority, reverse=True)

    def list_all_skills(self) -> List[SkillMetadata]:
        """
        List all registered skills.

        Returns:
            List of all skills, sorted by priority
        """
        return sorted(self.skills.values(), key=lambda s: s.priority, reverse=True)

    def search_skills(self, query: str) -> List[SkillMetadata]:
        """
        Search skills by keyword.

        Args:
            query: Search query

        Returns:
            List of matching skills
        """
        query_lower = query.lower()
        matching_skills = []

        for skill in self.skills.values():
            if not skill.enabled:
                continue

            # Search in name, description, keywords
            if (query_lower in skill.name.lower() or
                query_lower in skill.description.lower() or
                any(query_lower in kw.lower() for kw in skill.keywords)):
                matching_skills.append(skill)

        return sorted(matching_skills, key=lambda s: s.priority, reverse=True)


class TaskRouter:
    """
    Routes classified tasks to appropriate skills.

    Combines TaskClassifier and SkillRegistry to provide
    end-to-end task routing capabilities.
    """

    def __init__(self, classifier: Optional[TaskClassifier] = None,
                 registry: Optional[SkillRegistry] = None):
        """
        Initialize the task router.

        Args:
            classifier: TaskClassifier instance (creates new if None)
            registry: SkillRegistry instance (creates new if None)
        """
        self.classifier = classifier or TaskClassifier()
        self.registry = registry or SkillRegistry()

    def route(self, task_input: str, min_confidence: float = 0.1) -> RoutingResult:
        """
        Route a task to the most appropriate skill.

        Args:
            task_input: The task description or file reference
            min_confidence: Minimum confidence threshold for routing

        Returns:
            RoutingResult with selected skill and metadata
        """
        # Step 1: Classify the task
        classification = self.classifier.classify(task_input)

        # Step 2: Get candidate skills
        candidate_skills = self.registry.get_skills_by_category(classification.category)

        # Handle unknown category or no candidates
        if classification.category == TaskCategory.UNKNOWN or not candidate_skills:
            # Try keyword-based fallback
            candidate_skills = self.registry.search_skills(task_input)

            if not candidate_skills:
                return RoutingResult(
                    skill_id="unknown",
                    skill_name="Unknown",
                    category=TaskCategory.UNKNOWN,
                    confidence=0.0,
                    reasoning="No matching skill found for this task",
                    alternative_skills=[]
                )

        # Step 3: Select the best skill (highest priority)
        best_skill = candidate_skills[0]
        alternative_skills = [s.skill_id for s in candidate_skills[1:4]]  # Top 3 alternatives

        # Calculate routing confidence (combines classification confidence and skill match)
        routing_confidence = classification.confidence

        # Build reasoning
        reasoning_parts = []
        if classification.matched_patterns:
            reasoning_parts.append(f"Matched patterns: {', '.join(classification.matched_patterns[:3])}")
        if classification.matched_keywords:
            reasoning_parts.append(f"Matched keywords: {', '.join(classification.matched_keywords[:3])}")
        reasoning_parts.append(f"Category: {classification.category.value}")
        reasoning_parts.append(f"Selected skill priority: {best_skill.priority}")

        reasoning = " | ".join(reasoning_parts)

        return RoutingResult(
            skill_id=best_skill.skill_id,
            skill_name=best_skill.name,
            category=best_skill.category,
            confidence=routing_confidence,
            reasoning=reasoning,
            alternative_skills=alternative_skills
        )

    def route_file(self, file_path: Union[str, Path],
                   min_confidence: float = 0.1) -> RoutingResult:
        """
        Route based on file path.

        Args:
            file_path: Path to the file
            min_confidence: Minimum confidence threshold

        Returns:
            RoutingResult for the file
        """
        classification = self.classifier.classify_file(file_path)
        return self.route(str(file_path), min_confidence)

    def route_batch(self, tasks: List[str],
                    min_confidence: float = 0.1) -> List[RoutingResult]:
        """
        Route multiple tasks in batch.

        Args:
            tasks: List of task descriptions
            min_confidence: Minimum confidence threshold

        Returns:
            List of routing results
        """
        return [self.route(task, min_confidence) for task in tasks]

    def get_routing_statistics(self, tasks: List[str]) -> Dict[str, Any]:
        """
        Get statistics about routing for a batch of tasks.

        Args:
            tasks: List of task descriptions

        Returns:
            Dictionary with routing statistics
        """
        results = self.route_batch(tasks)

        category_counts = {}
        skill_counts = {}
        total_confidence = 0.0

        for result in results:
            # Count categories
            cat_name = result.category.value
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

            # Count skills
            skill_counts[result.skill_id] = skill_counts.get(result.skill_id, 0) + 1

            # Sum confidence
            total_confidence += result.confidence

        return {
            'total_tasks': len(tasks),
            'category_distribution': category_counts,
            'skill_distribution': skill_counts,
            'average_confidence': total_confidence / len(tasks) if tasks else 0.0,
            'unique_categories': len(category_counts),
            'unique_skills': len(skill_counts)
        }


# Convenience functions for quick usage
def classify_task(task: str) -> ClassificationResult:
    """Quick function to classify a task."""
    classifier = TaskClassifier()
    return classifier.classify(task)


def route_task(task: str) -> RoutingResult:
    """Quick function to route a task."""
    router = TaskRouter()
    return router.route(task)


def get_skill_for_category(category: TaskCategory) -> Optional[str]:
    """Quick function to get the best skill ID for a category."""
    registry = SkillRegistry()
    skills = registry.get_skills_by_category(category)
    return skills[0].skill_id if skills else None
