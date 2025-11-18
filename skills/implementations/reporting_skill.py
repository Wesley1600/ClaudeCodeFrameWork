"""
Reporting Skill

Formats results from previous skills into structured reports.
Supports multiple output formats: text, markdown, JSON, HTML.
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import json
import logging

from ..base_skill import BaseSkill, SkillContext, SkillMetadata


logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Output format for reports"""
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


class ReportingSkill(BaseSkill):
    """
    Generate formatted reports from skill chain results.

    Aggregates outputs from previous skills (RAG, summarization, etc.)
    and formats them into readable reports.

    Configuration:
        format: Output format (text/markdown/json/html, default: markdown)
        include_metadata: Include execution metadata (default: True)
        include_sources: Include source documents (default: True)
        title: Report title (default: auto-generated)
    """

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="reporting",
            description="Generate formatted reports from skill results",
            version="1.0.0",
            author="Skill Framework",
            input_schema={
                "context": "SkillContext - Results from previous skills"
            },
            output_schema={
                "report": "str - Formatted report",
                "format": "str - Report format",
                "metadata": "Dict - Report metadata"
            },
            dependencies=["summarization"],  # Often used after summarization
            tags=["reporting", "formatting", "output"]
        )

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # Configuration
        format_str = self.config.get("format", "markdown")
        self.format = ReportFormat(format_str)

        self.include_metadata = self.config.get("include_metadata", True)
        self.include_sources = self.config.get("include_sources", True)
        self.title = self.config.get("title")

    def execute(self, context: SkillContext, **kwargs) -> Dict[str, Any]:
        """
        Generate report from context.

        Args:
            context: SkillContext with results from previous skills
            **kwargs: Additional parameters

        Returns:
            Dict with report text and metadata
        """
        # Generate report based on format
        if self.format == ReportFormat.MARKDOWN:
            report = self._generate_markdown_report(context)

        elif self.format == ReportFormat.TEXT:
            report = self._generate_text_report(context)

        elif self.format == ReportFormat.JSON:
            report = self._generate_json_report(context)

        elif self.format == ReportFormat.HTML:
            report = self._generate_html_report(context)

        else:
            raise ValueError(f"Unknown format: {self.format}")

        result = {
            "report": report,
            "format": self.format.value,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "chain_id": context.chain_id,
                "skills_executed": list(context.results.keys()),
                "total_errors": len(context.errors),
                "execution_time": context.get_elapsed_time()
            }
        }

        logger.info(f"Generated {self.format.value} report ({len(report)} chars)")

        return result

    def _generate_markdown_report(self, context: SkillContext) -> str:
        """Generate Markdown-formatted report"""
        lines = []

        # Title
        title = self.title or "Skill Chain Execution Report"
        lines.append(f"# {title}\n")

        # Metadata
        if self.include_metadata:
            lines.append("## Execution Summary\n")
            lines.append(f"- **Chain ID**: `{context.chain_id}`")
            lines.append(f"- **Execution Time**: {context.get_elapsed_time():.2f}s")
            lines.append(f"- **Skills Executed**: {len(context.results)}")
            lines.append(f"- **Errors**: {len(context.errors)}\n")

        # RAG Results
        rag_result = context.get_result("rag_pipeline")
        if rag_result:
            lines.append("## Retrieved Context\n")

            metadata = rag_result.get("metadata", {})
            lines.append(f"**Query**: {metadata.get('query', 'N/A')}\n")
            lines.append(f"**Documents Retrieved**: {metadata.get('total_retrieved', 0)}\n")

            if self.include_sources:
                lines.append("### Source Documents\n")
                for i, doc in enumerate(rag_result.get("documents", [])):
                    score = rag_result.get("scores", [])[i] if i < len(rag_result.get("scores", [])) else 0
                    lines.append(f"#### Document {i+1} (Relevance: {score:.3f})\n")
                    lines.append(f"```\n{doc['content'][:200]}...\n```\n")

        # Summarization Results
        summary_result = context.get_result("summarization")
        if summary_result:
            lines.append("## Summary\n")
            lines.append(f"{summary_result['summary']}\n")

            lines.append("### Key Points\n")
            for point in summary_result.get("key_points", []):
                lines.append(f"- {point}")
            lines.append("")

            if self.include_metadata:
                meta = summary_result.get("metadata", {})
                lines.append("### Summary Statistics\n")
                lines.append(f"- **Strategy**: {meta.get('strategy', 'N/A')}")
                lines.append(f"- **Compression Ratio**: {meta.get('compression_ratio', 0):.1%}")
                lines.append(f"- **Original Length**: {meta.get('original_length', 0)} words")
                lines.append(f"- **Summary Length**: {meta.get('summary_length', 0)} words\n")

        # Errors
        if context.errors:
            lines.append("## Errors\n")
            for error in context.errors:
                lines.append(f"- **{error['skill']}**: {error['error']} ({error['error_type']})\n")

        return "\n".join(lines)

    def _generate_text_report(self, context: SkillContext) -> str:
        """Generate plain text report"""
        lines = []

        # Title
        title = self.title or "Skill Chain Execution Report"
        lines.append(title)
        lines.append("=" * len(title))
        lines.append("")

        # Metadata
        if self.include_metadata:
            lines.append("EXECUTION SUMMARY")
            lines.append("-" * 40)
            lines.append(f"Chain ID: {context.chain_id}")
            lines.append(f"Execution Time: {context.get_elapsed_time():.2f}s")
            lines.append(f"Skills Executed: {len(context.results)}")
            lines.append(f"Errors: {len(context.errors)}")
            lines.append("")

        # Summary
        summary_result = context.get_result("summarization")
        if summary_result:
            lines.append("SUMMARY")
            lines.append("-" * 40)
            lines.append(summary_result["summary"])
            lines.append("")

            lines.append("KEY POINTS:")
            for i, point in enumerate(summary_result.get("key_points", []), 1):
                lines.append(f"  {i}. {point}")
            lines.append("")

        # RAG info
        rag_result = context.get_result("rag_pipeline")
        if rag_result and self.include_metadata:
            metadata = rag_result.get("metadata", {})
            lines.append("RETRIEVAL INFO")
            lines.append("-" * 40)
            lines.append(f"Query: {metadata.get('query', 'N/A')}")
            lines.append(f"Documents Retrieved: {metadata.get('total_retrieved', 0)}")
            lines.append("")

        return "\n".join(lines)

    def _generate_json_report(self, context: SkillContext) -> str:
        """Generate JSON report"""
        report_data = {
            "title": self.title or "Skill Chain Execution Report",
            "metadata": {
                "chain_id": context.chain_id,
                "execution_time": context.get_elapsed_time(),
                "skills_executed": list(context.results.keys()),
                "errors": context.errors
            },
            "results": {}
        }

        # Add results from each skill
        for skill_name, result in context.results.items():
            report_data["results"][skill_name] = result

        return json.dumps(report_data, indent=2)

    def _generate_html_report(self, context: SkillContext) -> str:
        """Generate HTML report"""
        title = self.title or "Skill Chain Execution Report"

        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{title}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }",
            "h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }",
            "h2 { color: #555; margin-top: 30px; }",
            ".metadata { background: #f5f5f5; padding: 15px; border-radius: 5px; }",
            ".summary { background: #e8f5e9; padding: 20px; border-left: 4px solid #4CAF50; margin: 20px 0; }",
            ".key-points { list-style-type: none; padding-left: 0; }",
            ".key-points li { padding: 8px; margin: 5px 0; background: #fff; border-left: 3px solid #2196F3; }",
            ".document { background: #fafafa; padding: 10px; margin: 10px 0; border-radius: 3px; }",
            ".error { background: #ffebee; padding: 10px; border-left: 4px solid #f44336; margin: 10px 0; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>"
        ]

        # Metadata
        if self.include_metadata:
            html_parts.append("<div class='metadata'>")
            html_parts.append("<h2>Execution Summary</h2>")
            html_parts.append(f"<p><strong>Chain ID:</strong> {context.chain_id}</p>")
            html_parts.append(f"<p><strong>Execution Time:</strong> {context.get_elapsed_time():.2f}s</p>")
            html_parts.append(f"<p><strong>Skills Executed:</strong> {len(context.results)}</p>")
            html_parts.append(f"<p><strong>Errors:</strong> {len(context.errors)}</p>")
            html_parts.append("</div>")

        # Summary
        summary_result = context.get_result("summarization")
        if summary_result:
            html_parts.append("<div class='summary'>")
            html_parts.append("<h2>Summary</h2>")
            html_parts.append(f"<p>{summary_result['summary']}</p>")

            html_parts.append("<h3>Key Points</h3>")
            html_parts.append("<ul class='key-points'>")
            for point in summary_result.get("key_points", []):
                html_parts.append(f"<li>{point}</li>")
            html_parts.append("</ul>")
            html_parts.append("</div>")

        # Errors
        if context.errors:
            html_parts.append("<h2>Errors</h2>")
            for error in context.errors:
                html_parts.append(f"<div class='error'>")
                html_parts.append(f"<strong>{error['skill']}</strong>: {error['error']}")
                html_parts.append("</div>")

        html_parts.append("</body>")
        html_parts.append("</html>")

        return "\n".join(html_parts)

    def validate_inputs(self, context: SkillContext, **kwargs) -> bool:
        """Always valid - can generate report from any context"""
        return True
