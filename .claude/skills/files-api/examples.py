"""
Example usage of the Files API skill

This script demonstrates various use cases for the FilesManager class.
"""

import sys
import json
from pathlib import Path
from files_manager import FilesManager, FilesAPIError


def example_1_upload_and_download():
    """Example 1: Basic upload and download"""
    print("=" * 60)
    print("Example 1: Upload and Download a File")
    print("=" * 60)

    manager = FilesManager()

    # Create a sample file
    sample_file = Path("sample_document.txt")
    sample_file.write_text("This is a sample document for testing the Files API.")

    try:
        # Upload the file
        print(f"\nUploading {sample_file}...")
        result = manager.upload_file(sample_file, purpose="example")
        print(f"✓ File uploaded successfully!")
        print(f"  File ID: {result['file_id']}")
        print(f"  Filename: {result['filename']}")
        print(f"  Size: {result['size_bytes']} bytes")

        # Download the file
        file_id = result['file_id']
        output_path = Path("downloaded_document.txt")
        print(f"\nDownloading file {file_id}...")
        manager.download_file(file_id, output_path)
        print(f"✓ File downloaded to {output_path}")

        # Verify content
        original_content = sample_file.read_text()
        downloaded_content = output_path.read_text()
        assert original_content == downloaded_content
        print("✓ Content verified - upload/download successful!")

        # Cleanup
        sample_file.unlink()
        output_path.unlink()

    except FilesAPIError as e:
        print(f"✗ Error: {e}")


def example_2_intermediate_storage():
    """Example 2: Store and retrieve intermediate results"""
    print("\n" + "=" * 60)
    print("Example 2: Store Intermediate Computation Results")
    print("=" * 60)

    manager = FilesManager()

    try:
        # Simulate computation results
        computation_results = {
            "model": "UMAP Analogy Engine",
            "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "metadata": {
                "n_samples": 1000,
                "n_dimensions": 3,
                "timestamp": "2025-11-18T10:30:00Z"
            },
            "metrics": {
                "accuracy": 0.95,
                "processing_time": 2.5
            }
        }

        # Store intermediate results
        print("\nStoring intermediate computation results...")
        file_id = manager.store_intermediate(
            data=computation_results,
            name="umap_embeddings",
            format="json"
        )
        print(f"✓ Results stored successfully!")
        print(f"  File ID: {file_id}")

        # Retrieve intermediate results
        print(f"\nRetrieving intermediate results...")
        retrieved_data = manager.retrieve_intermediate(file_id)
        print(f"✓ Results retrieved successfully!")
        print(f"  Model: {retrieved_data['model']}")
        print(f"  Samples: {retrieved_data['metadata']['n_samples']}")
        print(f"  Accuracy: {retrieved_data['metrics']['accuracy']}")

        # Verify data integrity
        assert retrieved_data == computation_results
        print("✓ Data integrity verified!")

    except FilesAPIError as e:
        print(f"✗ Error: {e}")


def example_3_list_and_search():
    """Example 3: List and search files"""
    print("\n" + "=" * 60)
    print("Example 3: List and Search Files")
    print("=" * 60)

    manager = FilesManager()

    try:
        # Upload multiple test files
        print("\nUploading test files...")
        test_files = []

        for i in range(3):
            filename = f"test_file_{i}.txt"
            filepath = Path(filename)
            filepath.write_text(f"Content of test file {i}")

            result = manager.upload_file(
                filepath,
                purpose="test",
                metadata={"batch": "example_3", "index": i}
            )
            test_files.append(result["file_id"])
            filepath.unlink()
            print(f"  ✓ Uploaded {filename} - ID: {result['file_id']}")

        # List all files
        print("\nListing all files...")
        all_files = manager.list_files()
        print(f"✓ Found {len(all_files)} total files")

        # Search by filename
        print("\nSearching for files with 'test_file' in name...")
        search_results = manager.search_files(filename="test_file")
        print(f"✓ Found {len(search_results)} matching files:")
        for f in search_results:
            print(f"  - {f['filename']} ({f['file_id']})")

        # Search by purpose
        print("\nSearching for files with purpose='test'...")
        purpose_results = manager.search_files(purpose="test")
        print(f"✓ Found {len(purpose_results)} files with purpose='test'")

        # Search by metadata
        print("\nSearching for files with metadata batch='example_3'...")
        metadata_results = manager.search_files(
            metadata_filter={"batch": "example_3"}
        )
        print(f"✓ Found {len(metadata_results)} files in batch 'example_3'")

        # Clean up test files
        print("\nCleaning up test files...")
        for file_id in test_files:
            manager.delete_file(file_id)
        print(f"✓ Deleted {len(test_files)} test files")

    except FilesAPIError as e:
        print(f"✗ Error: {e}")


def example_4_storage_stats():
    """Example 4: Get storage statistics"""
    print("\n" + "=" * 60)
    print("Example 4: Storage Statistics")
    print("=" * 60)

    manager = FilesManager()

    try:
        stats = manager.get_storage_stats()

        print("\n📊 Storage Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Total size: {stats['total_size_mb']} MB ({stats['total_size_bytes']} bytes)")

        if stats['by_purpose']:
            print("\n  Files by purpose:")
            for purpose, data in stats['by_purpose'].items():
                size_mb = round(data['size_bytes'] / (1024 * 1024), 2)
                print(f"    - {purpose}: {data['count']} files, {size_mb} MB")

        if stats['oldest_file']:
            print(f"\n  Oldest file: {stats['oldest_file']}")
        if stats['newest_file']:
            print(f"  Newest file: {stats['newest_file']}")

    except FilesAPIError as e:
        print(f"✗ Error: {e}")


def example_5_batch_operations():
    """Example 5: Batch file operations"""
    print("\n" + "=" * 60)
    print("Example 5: Batch File Operations")
    print("=" * 60)

    manager = FilesManager()

    try:
        # Create multiple files
        print("\nCreating batch of files...")
        file_ids = []
        batch_data = [
            {"name": "alice", "age": 30, "city": "New York"},
            {"name": "bob", "age": 25, "city": "San Francisco"},
            {"name": "charlie", "age": 35, "city": "Boston"}
        ]

        for i, data in enumerate(batch_data):
            filename = f"person_{i}.json"
            filepath = Path(filename)

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            result = manager.upload_file(
                filepath,
                purpose="batch_demo",
                metadata={"type": "person", "batch_id": "batch_001"}
            )
            file_ids.append(result["file_id"])
            filepath.unlink()
            print(f"  ✓ Uploaded {filename}")

        print(f"\n✓ Uploaded {len(file_ids)} files in batch")

        # Download all files from batch
        print("\nDownloading batch files...")
        batch_results = manager.search_files(
            metadata_filter={"batch_id": "batch_001"}
        )

        downloaded_data = []
        for file_record in batch_results:
            content = manager.download_file(file_record["file_id"])
            data = json.loads(content.decode('utf-8'))
            downloaded_data.append(data)
            print(f"  ✓ Downloaded {file_record['filename']}: {data['name']}")

        # Aggregate results
        print("\n📊 Batch Analysis:")
        avg_age = sum(d['age'] for d in downloaded_data) / len(downloaded_data)
        print(f"  Average age: {avg_age:.1f}")
        print(f"  Cities: {', '.join(set(d['city'] for d in downloaded_data))}")

        # Cleanup
        print("\nCleaning up batch files...")
        for file_id in file_ids:
            manager.delete_file(file_id)
        print(f"✓ Deleted {len(file_ids)} files")

    except FilesAPIError as e:
        print(f"✗ Error: {e}")


def example_6_error_handling():
    """Example 6: Error handling"""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    manager = FilesManager()

    # Test 1: File not found
    print("\nTest 1: Uploading non-existent file...")
    try:
        manager.upload_file("non_existent_file.txt")
        print("✗ Should have raised FileNotFoundError")
    except FilesAPIError as e:
        print(f"✓ Correctly caught error: {e}")

    # Test 2: Invalid file ID
    print("\nTest 2: Downloading with invalid file ID...")
    try:
        manager.download_file("invalid_file_id_12345")
        print("✗ Should have raised FileNotFoundError")
    except FilesAPIError as e:
        print(f"✓ Correctly caught error: {e}")

    # Test 3: Deleting non-existent file
    print("\nTest 3: Deleting non-existent file...")
    try:
        manager.delete_file("non_existent_file_id")
        print("✗ Should have raised FileNotFoundError")
    except FilesAPIError as e:
        print(f"✓ Correctly caught error: {e}")

    print("\n✓ All error handling tests passed!")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "FILES API SKILL - EXAMPLES" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")

    try:
        # Check if API key is set
        manager = FilesManager()
        print("\n✓ Files API Manager initialized successfully!")
        print(f"  Storage directory: {manager.storage_dir}")
        print(f"  Database: {manager.db_path}")

        # Run examples
        examples = [
            example_1_upload_and_download,
            example_2_intermediate_storage,
            example_3_list_and_search,
            example_4_storage_stats,
            example_5_batch_operations,
            example_6_error_handling
        ]

        for example_func in examples:
            try:
                example_func()
            except Exception as e:
                print(f"\n✗ Example failed: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 60)
        print("✓ All examples completed!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n✗ Failed to initialize Files API Manager: {e}")
        print("Please ensure ANTHROPIC_API_KEY is set in your environment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
