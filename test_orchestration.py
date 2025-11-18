"""
Quick test script for skill orchestration framework

Run with: python test_orchestration.py
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        from skills import (
            BaseSkill,
            SkillContext,
            SkillMetadata,
            SkillStatus,
            SkillRegistry,
            SkillOrchestrator,
            ChainConfig,
            get_global_registry
        )
        print("✓ Core modules imported successfully")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

    try:
        from skills.implementations import (
            RAGPipelineSkill,
            SummarizationSkill,
            ReportingSkill
        )
        print("✓ Implementation modules imported successfully")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

    return True


def test_skill_registration():
    """Test skill registration and discovery"""
    print("\nTesting skill registration...")

    from skills import get_global_registry

    registry = get_global_registry()

    # Discover skills
    num_discovered = registry.discover_skills("skills.implementations")

    if num_discovered > 0:
        print(f"✓ Discovered {num_discovered} skills")
        print(f"  Available: {', '.join(registry.list_skills())}")
        return True
    else:
        print("✗ No skills discovered")
        return False


def test_simple_chain():
    """Test creating and executing a simple chain"""
    print("\nTesting simple chain execution...")

    from skills import SkillOrchestrator, get_global_registry

    registry = get_global_registry()
    registry.discover_skills("skills.implementations")

    orchestrator = SkillOrchestrator(registry)

    # Create a simple summarization chain
    chain = orchestrator.create_chain(
        name="test_chain",
        description="Simple test chain"
    )

    chain.add_step("summarization", config={
        "summarization": {
            "strategy": "extractive",
            "num_sentences": 2
        }
    })

    chain.add_step("reporting", config={
        "reporting": {
            "format": "text",
            "include_metadata": False,
            "title": "Test Report"
        }
    })

    chain.initial_data = {
        "text": "The skill orchestration framework is a powerful tool. "
                "It allows chaining multiple AI skills together. "
                "Data flows seamlessly between skills. "
                "This enables complex workflows with simple configuration."
    }

    try:
        context = orchestrator.execute_chain(chain)

        # Verify results
        if context.get_result("summarization") and context.get_result("reporting"):
            print("✓ Chain executed successfully")
            print("\nGenerated report:")
            print("-" * 60)
            report = context.get_result("reporting")["report"]
            print(report)
            print("-" * 60)
            return True
        else:
            print("✗ Chain execution incomplete")
            return False

    except Exception as e:
        print(f"✗ Chain execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yaml_config():
    """Test loading chain from YAML"""
    print("\nTesting YAML configuration loading...")

    from skills import ChainConfig
    from pathlib import Path

    yaml_path = Path("chains/quick_summary.yaml")

    if not yaml_path.exists():
        print(f"⚠ YAML file not found: {yaml_path}")
        print("  Skipping this test")
        return True

    try:
        chain = ChainConfig.from_yaml(yaml_path)

        print(f"✓ Loaded chain from YAML: '{chain.name}'")
        print(f"  Description: {chain.description.strip()}")
        print(f"  Steps: {len(chain.steps)}")

        return True

    except Exception as e:
        print(f"✗ YAML loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_pipeline():
    """Test RAG pipeline skill"""
    print("\nTesting RAG pipeline...")

    from skills import get_global_registry, SkillContext

    registry = get_global_registry()
    registry.discover_skills("skills.implementations")

    try:
        # Create RAG skill
        rag_skill = registry.create_skill("rag_pipeline", config={
            "documents": [
                "Python is a high-level programming language. "
                "It emphasizes code readability and simplicity.",

                "Machine learning is a subset of artificial intelligence. "
                "It enables computers to learn from data.",

                "Neural networks are inspired by biological brains. "
                "They consist of interconnected layers of nodes."
            ],
            "top_k": 2,
            "similarity_threshold": 0.0
        })

        # Execute
        context = SkillContext()
        context.shared_state["query"] = "What is Python?"

        result = rag_skill.run(context, query="What is Python?")

        if result and "documents" in result:
            print(f"✓ RAG pipeline executed successfully")
            print(f"  Retrieved {len(result['documents'])} documents")
            return True
        else:
            print("✗ RAG pipeline returned invalid result")
            return False

    except Exception as e:
        print(f"✗ RAG pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_shared_state():
    """Test RAG pipeline with documents in shared_state (YAML chain scenario)"""
    print("\nTesting RAG pipeline with shared_state documents...")

    from skills import get_global_registry, SkillContext

    registry = get_global_registry()
    registry.discover_skills("skills.implementations")

    try:
        # Create RAG skill WITHOUT documents in config
        rag_skill = registry.create_skill("rag_pipeline", config={
            "top_k": 2,
            "similarity_threshold": 0.0
        })

        # Put documents in shared_state (simulating initial_data from YAML)
        context = SkillContext()
        context.shared_state["query"] = "What is machine learning?"
        context.shared_state["documents"] = [
            "Machine learning is a subset of artificial intelligence. "
            "It enables computers to learn from data without explicit programming.",

            "Deep learning uses neural networks with multiple layers. "
            "It has achieved remarkable success in image and speech recognition.",

            "Supervised learning trains models on labeled data. "
            "Unsupervised learning finds patterns in unlabeled data."
        ]

        # Execute - should load documents from shared_state
        result = rag_skill.run(context)

        if result and "documents" in result and len(result["documents"]) > 0:
            print(f"✓ RAG pipeline loaded documents from shared_state")
            print(f"  Retrieved {len(result['documents'])} documents")
            print(f"  Total indexed: {result['metadata']['total_indexed']}")
            return True
        else:
            print("✗ RAG pipeline failed to load documents from shared_state")
            return False

    except Exception as e:
        print(f"✗ RAG shared_state test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_yaml_chain():
    """Test full RAG→Summarization→Reporting chain from YAML"""
    print("\nTesting full RAG chain from YAML (rag_summarize_report.yaml)...")

    from skills import SkillOrchestrator, ChainConfig, get_global_registry
    from pathlib import Path

    registry = get_global_registry()
    registry.discover_skills("skills.implementations")
    orchestrator = SkillOrchestrator(registry)

    yaml_path = Path("chains/rag_summarize_report.yaml")

    if not yaml_path.exists():
        print(f"⚠ YAML file not found: {yaml_path}, skipping test")
        return True

    try:
        # Load and execute the chain
        chain = ChainConfig.from_yaml(yaml_path)
        context = orchestrator.execute_chain(chain)

        # Verify RAG step
        rag_result = context.get_result("rag_pipeline")
        if not rag_result:
            print("✗ RAG pipeline did not execute")
            return False

        total_retrieved = rag_result["metadata"]["total_retrieved"]
        total_indexed = rag_result["metadata"]["total_indexed"]

        print(f"  RAG: Indexed {total_indexed} docs, retrieved {total_retrieved}")

        if total_indexed == 0:
            print("✗ RAG did not load any documents from initial_data")
            return False

        if total_retrieved == 0:
            print("✗ RAG did not retrieve any documents")
            return False

        # Verify summarization step
        summary_result = context.get_result("summarization")
        if not summary_result:
            print("✗ Summarization did not execute")
            return False

        summary = summary_result.get("summary", "")
        if not summary:
            print("✗ Summarization produced empty summary")
            return False

        print(f"  Summarization: {len(summary)} chars, {len(summary_result.get('key_points', []))} key points")

        # Verify reporting step
        report_result = context.get_result("reporting")
        if not report_result:
            print("✗ Reporting did not execute")
            return False

        report = report_result.get("report", "")
        if not report:
            print("✗ Reporting produced empty report")
            return False

        print(f"  Reporting: {report_result.get('format')} format, {len(report)} chars")

        # Verify shared_state contains retrieved documents
        if "retrieved_documents" not in context.shared_state:
            print("⚠ Warning: retrieved_documents not in shared_state")

        print("✓ Full RAG→Summarization→Reporting chain executed successfully")
        return True

    except Exception as e:
        print(f"✗ YAML chain execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("SKILL ORCHESTRATION FRAMEWORK - TEST SUITE")
    print("=" * 70)

    tests = [
        ("Imports", test_imports),
        ("Skill Registration", test_skill_registration),
        ("Simple Chain", test_simple_chain),
        ("YAML Config", test_yaml_config),
        ("RAG Pipeline", test_rag_pipeline),
        ("RAG Shared State", test_rag_shared_state),
        ("RAG YAML Chain", test_rag_yaml_chain),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
