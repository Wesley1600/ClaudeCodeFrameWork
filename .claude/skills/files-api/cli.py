#!/usr/bin/env python3
"""
Files API CLI Tool

A command-line interface for the Files API skill.

Usage:
    python cli.py upload <file_path> [--purpose PURPOSE]
    python cli.py download <file_id> [--output OUTPUT]
    python cli.py list
    python cli.py delete <file_id>
    python cli.py stats
    python cli.py search [--filename FILENAME] [--purpose PURPOSE]
    python cli.py cleanup [--days DAYS]
"""

import argparse
import sys
import json
from pathlib import Path
from files_manager import FilesManager, FilesAPIError


def cmd_upload(args, manager):
    """Upload a file"""
    try:
        result = manager.upload_file(
            args.file_path,
            purpose=args.purpose or "user"
        )
        print(f"✓ File uploaded successfully!")
        print(f"  File ID: {result['file_id']}")
        print(f"  Filename: {result['filename']}")
        print(f"  Size: {result['size_bytes']} bytes")
        print(f"\nTo download: python cli.py download {result['file_id']}")
    except FilesAPIError as e:
        print(f"✗ Upload failed: {e}")
        sys.exit(1)


def cmd_download(args, manager):
    """Download a file"""
    try:
        output_path = args.output or f"downloaded_{args.file_id}"
        manager.download_file(args.file_id, output_path)
        print(f"✓ File downloaded successfully to {output_path}")
    except FilesAPIError as e:
        print(f"✗ Download failed: {e}")
        sys.exit(1)


def cmd_list(args, manager):
    """List all files"""
    try:
        files = manager.list_files()

        if not files:
            print("No files found.")
            return

        print(f"\n📁 Files ({len(files)} total):\n")
        print(f"{'Filename':<30} {'File ID':<35} {'Size':<12} {'Purpose':<15}")
        print("-" * 95)

        for f in files:
            filename = f.get('filename', 'N/A')[:29]
            file_id = f.get('file_id', f.get('id', 'N/A'))[:34]
            size_bytes = f.get('size_bytes', 0)
            size_mb = f"{size_bytes / (1024*1024):.2f} MB" if size_bytes else "N/A"
            purpose = f.get('purpose', 'N/A')[:14]

            print(f"{filename:<30} {file_id:<35} {size_mb:<12} {purpose:<15}")

        print()

    except FilesAPIError as e:
        print(f"✗ List failed: {e}")
        sys.exit(1)


def cmd_delete(args, manager):
    """Delete a file"""
    try:
        manager.delete_file(args.file_id)
        print(f"✓ File {args.file_id} deleted successfully")
    except FilesAPIError as e:
        print(f"✗ Delete failed: {e}")
        sys.exit(1)


def cmd_stats(args, manager):
    """Show storage statistics"""
    try:
        stats = manager.get_storage_stats()

        print("\n📊 Storage Statistics:\n")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Total size:  {stats['total_size_mb']} MB ({stats['total_size_bytes']} bytes)")

        if stats['by_purpose']:
            print("\n  Files by purpose:")
            for purpose, data in stats['by_purpose'].items():
                size_mb = round(data['size_bytes'] / (1024 * 1024), 2)
                print(f"    • {purpose:15s}: {data['count']:3d} files, {size_mb:8.2f} MB")

        if stats['oldest_file']:
            print(f"\n  Oldest file: {stats['oldest_file']}")
        if stats['newest_file']:
            print(f"  Newest file: {stats['newest_file']}")

        print()

    except FilesAPIError as e:
        print(f"✗ Stats failed: {e}")
        sys.exit(1)


def cmd_search(args, manager):
    """Search for files"""
    try:
        results = manager.search_files(
            filename=args.filename,
            purpose=args.purpose
        )

        if not results:
            print("No files found matching criteria.")
            return

        print(f"\n🔍 Search Results ({len(results)} files):\n")
        print(f"{'Filename':<30} {'File ID':<35} {'Purpose':<15}")
        print("-" * 83)

        for f in results:
            filename = f.get('filename', 'N/A')[:29]
            file_id = f.get('file_id', 'N/A')[:34]
            purpose = f.get('purpose', 'N/A')[:14]
            print(f"{filename:<30} {file_id:<35} {purpose:<15}")

        print()

    except FilesAPIError as e:
        print(f"✗ Search failed: {e}")
        sys.exit(1)


def cmd_cleanup(args, manager):
    """Cleanup old files"""
    try:
        days = args.days or 30
        print(f"Cleaning up files older than {days} days...")

        deleted_count = manager.cleanup_old_files(days)
        print(f"✓ Deleted {deleted_count} files")

    except FilesAPIError as e:
        print(f"✗ Cleanup failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Files API CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Upload a file:
    python cli.py upload document.pdf --purpose analysis

  Download a file:
    python cli.py download file_011CNha8iCJcU1wXNR6q4V8w --output doc.pdf

  List all files:
    python cli.py list

  Search for files:
    python cli.py search --filename report --purpose analysis

  Get storage stats:
    python cli.py stats

  Delete a file:
    python cli.py delete file_011CNha8iCJcU1wXNR6q4V8w

  Cleanup old files:
    python cli.py cleanup --days 30
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a file')
    upload_parser.add_argument('file_path', help='Path to file to upload')
    upload_parser.add_argument('--purpose', help='Purpose of the file (default: user)')

    # Download command
    download_parser = subparsers.add_parser('download', help='Download a file')
    download_parser.add_argument('file_id', help='File ID to download')
    download_parser.add_argument('--output', help='Output path (default: downloaded_<file_id>)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all files')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a file')
    delete_parser.add_argument('file_id', help='File ID to delete')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show storage statistics')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for files')
    search_parser.add_argument('--filename', help='Filter by filename')
    search_parser.add_argument('--purpose', help='Filter by purpose')

    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup old files')
    cleanup_parser.add_argument('--days', type=int, help='Delete files older than N days (default: 30)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize manager
    try:
        manager = FilesManager()
    except Exception as e:
        print(f"✗ Failed to initialize Files Manager: {e}")
        print("\nPlease ensure ANTHROPIC_API_KEY is set:")
        print("  export ANTHROPIC_API_KEY='your_api_key_here'")
        sys.exit(1)

    # Execute command
    commands = {
        'upload': cmd_upload,
        'download': cmd_download,
        'list': cmd_list,
        'delete': cmd_delete,
        'stats': cmd_stats,
        'search': cmd_search,
        'cleanup': cmd_cleanup
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args, manager)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
