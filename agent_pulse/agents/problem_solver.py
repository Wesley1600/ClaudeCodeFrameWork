"""
Problem Solver Agent

Proactively suggests solutions to problems:
- Analyzes recurring issues
- Suggests known solutions
- Provides debugging strategies
- Recommends tools and resources
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from ..storage.memory_store import MemoryStore


class ProblemSolver:
    """
    Analyzes problems and suggests solutions.
    """

    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

        # Knowledge base of common problems and solutions
        self.solution_patterns = {
            "import error": {
                "solutions": [
                    "Check if the package is installed: pip list | grep <package>",
                    "Verify virtual environment is activated",
                    "Install the package: pip install <package>",
                    "Check for typos in the import statement",
                ],
                "category": "dependency",
            },
            "permission denied": {
                "solutions": [
                    "Check file permissions: ls -la <file>",
                    "Add execute permissions: chmod +x <file>",
                    "Run with sudo (if appropriate): sudo <command>",
                    "Check ownership: chown user:group <file>",
                ],
                "category": "permissions",
            },
            "api error": {
                "solutions": [
                    "Check API endpoint URL",
                    "Verify authentication credentials",
                    "Review API rate limits",
                    "Check request payload format",
                    "Examine response error messages",
                ],
                "category": "api",
            },
            "database connection": {
                "solutions": [
                    "Verify database is running",
                    "Check connection string credentials",
                    "Test network connectivity",
                    "Review firewall rules",
                    "Check database logs",
                ],
                "category": "database",
            },
            "performance": {
                "solutions": [
                    "Profile the code to identify bottlenecks",
                    "Add caching for repeated operations",
                    "Optimize database queries",
                    "Use async/await for I/O operations",
                    "Consider load balancing",
                ],
                "category": "optimization",
            },
        }

    def analyze_problems(
        self,
        days: int = 7,
        max_problems: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Analyze recent problems and suggest solutions.

        Args:
            days: Days to look back
            max_problems: Maximum number of problems to analyze

        Returns:
            List of problems with suggested solutions
        """
        problems = self.memory_store.get_all_problems(days=days)
        analyzed_problems = []

        for problem_entry in problems[:max_problems]:
            problem_text = problem_entry["problem"]
            analysis = self._analyze_single_problem(problem_text)

            analyzed_problems.append({
                **problem_entry,
                **analysis,
            })

        # Group recurring problems
        recurring = self._identify_recurring_problems(analyzed_problems)

        return {
            "all_problems": analyzed_problems,
            "recurring_problems": recurring,
            "summary": self._generate_summary(analyzed_problems),
            "timestamp": datetime.now().isoformat(),
        }

    def _analyze_single_problem(self, problem_text: str) -> Dict[str, Any]:
        """
        Analyze a single problem and suggest solutions.
        """
        problem_lower = problem_text.lower()

        # Match against known patterns
        matched_solutions = []
        category = "general"

        for pattern, pattern_data in self.solution_patterns.items():
            if pattern in problem_lower:
                matched_solutions.extend(pattern_data["solutions"])
                category = pattern_data["category"]
                break

        # If no specific match, provide general debugging approach
        if not matched_solutions:
            matched_solutions = self._general_debugging_steps(problem_text)

        return {
            "category": category,
            "suggested_solutions": matched_solutions,
            "resources": self._find_resources(problem_text, category),
            "priority": self._assess_priority(problem_text),
        }

    def _general_debugging_steps(self, problem_text: str) -> List[str]:
        """
        Provide general debugging steps.
        """
        return [
            "Review error messages and stack traces carefully",
            "Check recent code changes that might have introduced the issue",
            "Verify input data and assumptions",
            "Add logging to trace execution flow",
            "Search for similar issues online (Stack Overflow, GitHub issues)",
            "Try to reproduce the issue in a minimal example",
            "Review relevant documentation",
        ]

    def _find_resources(self, problem_text: str, category: str) -> List[Dict[str, str]]:
        """
        Find relevant resources for the problem.
        """
        resources = [
            {
                "type": "search",
                "description": f"Search Stack Overflow for '{problem_text[:50]}'",
                "url": f"https://stackoverflow.com/search?q={problem_text[:50].replace(' ', '+')}",
            },
            {
                "type": "documentation",
                "description": f"Review documentation for {category}",
                "url": "#",
            },
        ]

        return resources

    def _assess_priority(self, problem_text: str) -> str:
        """
        Assess the priority of a problem.
        """
        high_priority_keywords = ["critical", "crash", "production", "urgent", "blocker"]
        medium_priority_keywords = ["error", "fail", "broken", "issue"]

        problem_lower = problem_text.lower()

        if any(kw in problem_lower for kw in high_priority_keywords):
            return "high"
        elif any(kw in problem_lower for kw in medium_priority_keywords):
            return "medium"
        else:
            return "low"

    def _identify_recurring_problems(
        self,
        problems: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify recurring problems.
        """
        # Group similar problems by category
        category_groups = {}

        for problem in problems:
            category = problem.get("category", "general")
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(problem)

        # Find categories with multiple occurrences
        recurring = []
        for category, group in category_groups.items():
            if len(group) >= 2:
                recurring.append({
                    "category": category,
                    "count": len(group),
                    "problems": group,
                    "recommendation": f"Consider creating a reusable solution for {category} issues",
                })

        return sorted(recurring, key=lambda x: x["count"], reverse=True)

    def _generate_summary(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of problems.
        """
        total = len(problems)
        by_priority = {"high": 0, "medium": 0, "low": 0}
        by_category = {}

        for problem in problems:
            priority = problem.get("priority", "low")
            by_priority[priority] = by_priority.get(priority, 0) + 1

            category = problem.get("category", "general")
            by_category[category] = by_category.get(category, 0) + 1

        return {
            "total_problems": total,
            "by_priority": by_priority,
            "by_category": by_category,
            "most_common_category": max(by_category.items(), key=lambda x: x[1])[0] if by_category else None,
        }

    def suggest_preventive_measures(
        self,
        recurring_problems: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest preventive measures for recurring problems.
        """
        measures = []

        for problem_group in recurring_problems:
            category = problem_group["category"]

            if category == "dependency":
                measures.append({
                    "category": category,
                    "measure": "Create a requirements.txt or environment.yml file",
                    "benefit": "Ensures consistent dependencies across environments",
                    "effort": "low",
                })
            elif category == "permissions":
                measures.append({
                    "category": category,
                    "measure": "Document required permissions in README",
                    "benefit": "Helps team members set up correctly",
                    "effort": "low",
                })
            elif category == "api":
                measures.append({
                    "category": category,
                    "measure": "Implement robust error handling and retry logic",
                    "benefit": "Gracefully handles API failures",
                    "effort": "medium",
                })
            elif category == "database":
                measures.append({
                    "category": category,
                    "measure": "Add database health checks and monitoring",
                    "benefit": "Early detection of connection issues",
                    "effort": "medium",
                })
            else:
                measures.append({
                    "category": category,
                    "measure": "Add comprehensive logging for this category",
                    "benefit": "Easier debugging in the future",
                    "effort": "low",
                })

        return measures

    def get_solution_quick_wins(
        self,
        problems: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify problems that can be solved quickly (quick wins).
        """
        quick_wins = []

        for problem in problems:
            priority = problem.get("priority", "low")
            category = problem.get("category", "general")

            # Quick wins: low effort categories with clear solutions
            if category in ["dependency", "permissions"] or priority == "low":
                quick_wins.append({
                    "problem": problem.get("problem", ""),
                    "solution": problem.get("suggested_solutions", [])[0] if problem.get("suggested_solutions") else "",
                    "estimated_time": "5-15 minutes",
                    "impact": "immediate",
                })

        return quick_wins[:5]
