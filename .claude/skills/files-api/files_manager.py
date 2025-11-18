"""
Files API Manager for Claude

A comprehensive interface for uploading, downloading, and managing files
using the Anthropic Files API.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import mimetypes
import time


class FilesAPIError(Exception):
    """Base exception for Files API errors"""
    pass


class AuthenticationError(FilesAPIError):
    """Raised when API authentication fails"""
    pass


class FileNotFoundError(FilesAPIError):
    """Raised when a file is not found"""
    pass


class FileSizeLimitError(FilesAPIError):
    """Raised when file exceeds size limit"""
    pass


class FilesManager:
    """
    Manages file operations with the Anthropic Files API.

    Provides methods for uploading, downloading, listing, and deleting files,
    as well as tracking file metadata and managing intermediate outputs.
    """

    # API Configuration
    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"
    BETA_VERSION = "files-api-2025-04-14"
    MAX_FILE_SIZE = 350 * 1024 * 1024  # 350 MB in bytes
    MAX_RETRIES = 4

    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the Files Manager.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            config_path: Path to config file (defaults to skill directory)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Set up paths
        self.skill_dir = Path(__file__).parent
        self.config_path = Path(config_path) if config_path else self.skill_dir / "config.json"
        self.storage_dir = self.skill_dir / "storage"
        self.db_path = self.skill_dir / "files_db.json"

        # Initialize
        self._ensure_directories()
        self._load_or_create_config()
        self._load_or_create_db()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.skill_dir.mkdir(parents=True, exist_ok=True)

    def _load_or_create_config(self):
        """Load or create configuration file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "api_version": self.API_VERSION,
                "beta_version": self.BETA_VERSION,
                "storage_dir": str(self.storage_dir),
                "tracking_db": str(self.db_path)
            }
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

    def _load_or_create_db(self):
        """Load or create file tracking database"""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                self.db = json.load(f)
        else:
            self.db = {"files": []}
            self._save_db()

    def _save_db(self):
        """Save file tracking database"""
        with open(self.db_path, 'w') as f:
            json.dump(self.db, f, indent=2)

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "x-api-key": self.api_key,
            "anthropic-version": self.config["api_version"],
            "anthropic-beta": self.config["beta_version"]
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an API request with retry logic.

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests

        Returns:
            Response object
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()

        # Merge with any additional headers
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=30,
                    **kwargs
                )

                # Handle authentication errors
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")

                # Handle not found errors
                if response.status_code == 404:
                    raise FileNotFoundError("File not found")

                # Raise for other HTTP errors
                response.raise_for_status()

                return response

            except requests.exceptions.RequestException as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise FilesAPIError(f"Request failed after {self.MAX_RETRIES} attempts: {e}")

        raise FilesAPIError("Unexpected error in request handling")

    def upload_file(
        self,
        file_path: Union[str, Path],
        purpose: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to the Files API.

        Args:
            file_path: Path to the file to upload
            purpose: Purpose of the file (default: 'user')
            metadata: Additional metadata to store locally

        Returns:
            Dictionary with file_id, filename, size_bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            FileSizeLimitError: If file exceeds size limit
        """
        file_path = Path(file_path)

        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise FileSizeLimitError(
                f"File size ({file_size} bytes) exceeds limit "
                f"({self.MAX_FILE_SIZE} bytes)"
            )

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"

        # Prepare multipart form data
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, mime_type)
            }
            data = {
                'purpose': purpose
            }

            # Upload
            response = self._make_request(
                'POST',
                '/files',
                files=files,
                data=data
            )

        result = response.json()

        # Store in local database
        file_record = {
            "file_id": result.get("id"),
            "filename": file_path.name,
            "original_path": str(file_path.absolute()),
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "size_bytes": file_size,
            "purpose": purpose,
            "mime_type": mime_type,
            "metadata": metadata or {}
        }

        self.db["files"].append(file_record)
        self._save_db()

        return {
            "file_id": result.get("id"),
            "filename": file_path.name,
            "size_bytes": file_size,
            "uploaded_at": file_record["uploaded_at"]
        }

    def download_file(
        self,
        file_id: str,
        output_path: Optional[Union[str, Path]] = None
    ) -> Union[bytes, Path]:
        """
        Download a file from the Files API.

        Args:
            file_id: The file ID to download
            output_path: Where to save the file (optional)

        Returns:
            File content as bytes if output_path is None, else Path to saved file
        """
        response = self._make_request(
            'GET',
            f'/files/{file_id}/content'
        )

        content = response.content

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(content)

            return output_path

        return content

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all uploaded files.

        Returns:
            List of file metadata dictionaries
        """
        try:
            response = self._make_request('GET', '/files')
            api_files = response.json().get("data", [])

            # Merge with local database
            local_files = {f["file_id"]: f for f in self.db["files"]}

            result = []
            for api_file in api_files:
                file_id = api_file.get("id")
                if file_id in local_files:
                    # Merge API data with local metadata
                    merged = {**local_files[file_id], **api_file}
                    result.append(merged)
                else:
                    result.append(api_file)

            return result

        except Exception as e:
            # Fall back to local database if API fails
            return self.db["files"]

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file.

        Args:
            file_id: The file ID

        Returns:
            File metadata dictionary
        """
        response = self._make_request('GET', f'/files/{file_id}')
        return response.json()

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from the Files API.

        Args:
            file_id: The file ID to delete

        Returns:
            True if successful
        """
        self._make_request('DELETE', f'/files/{file_id}')

        # Remove from local database
        self.db["files"] = [
            f for f in self.db["files"] if f["file_id"] != file_id
        ]
        self._save_db()

        return True

    def store_intermediate(
        self,
        data: Any,
        name: str,
        format: str = 'json'
    ) -> str:
        """
        Store intermediate computation results.

        Args:
            data: The data to store (dict, list, str)
            name: Name for the intermediate file
            format: Format to store in ('json', 'txt', 'csv')

        Returns:
            File ID of stored data
        """
        # Create temporary file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.{format}"
        temp_path = self.storage_dir / filename

        # Write data based on format
        if format == 'json':
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == 'txt':
            with open(temp_path, 'w') as f:
                f.write(str(data))
        elif format == 'csv':
            import csv
            with open(temp_path, 'w', newline='') as f:
                if isinstance(data, list) and len(data) > 0:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    f.write(str(data))
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Upload to Files API
        result = self.upload_file(
            temp_path,
            purpose="intermediate",
            metadata={"type": "intermediate", "name": name}
        )

        return result["file_id"]

    def retrieve_intermediate(self, file_id: str) -> Any:
        """
        Retrieve intermediate computation results.

        Args:
            file_id: The file ID to retrieve

        Returns:
            Parsed data (dict, list, or str depending on format)
        """
        content = self.download_file(file_id)

        # Try to parse as JSON first
        try:
            return json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            # Return as text
            return content.decode('utf-8')

    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Delete files older than specified days.

        Args:
            days: Delete files older than this many days

        Returns:
            Number of files deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0

        for file_record in self.db["files"][:]:  # Copy list to avoid modification during iteration
            uploaded_at = datetime.fromisoformat(
                file_record["uploaded_at"].replace("Z", "+00:00")
            )

            if uploaded_at < cutoff_date:
                try:
                    self.delete_file(file_record["file_id"])
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {file_record['file_id']}: {e}")

        return deleted_count

    def search_files(
        self,
        filename: Optional[str] = None,
        purpose: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for files by criteria.

        Args:
            filename: Filter by filename (partial match)
            purpose: Filter by purpose
            metadata_filter: Filter by metadata key-value pairs

        Returns:
            List of matching file metadata
        """
        results = self.db["files"]

        if filename:
            results = [
                f for f in results
                if filename.lower() in f["filename"].lower()
            ]

        if purpose:
            results = [
                f for f in results
                if f["purpose"] == purpose
            ]

        if metadata_filter:
            results = [
                f for f in results
                if all(
                    f.get("metadata", {}).get(k) == v
                    for k, v in metadata_filter.items()
                )
            ]

        return results

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored files.

        Returns:
            Dictionary with storage statistics
        """
        total_files = len(self.db["files"])
        total_size = sum(f.get("size_bytes", 0) for f in self.db["files"])

        # Group by purpose
        by_purpose = {}
        for f in self.db["files"]:
            purpose = f.get("purpose", "unknown")
            if purpose not in by_purpose:
                by_purpose[purpose] = {"count": 0, "size_bytes": 0}
            by_purpose[purpose]["count"] += 1
            by_purpose[purpose]["size_bytes"] += f.get("size_bytes", 0)

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_purpose": by_purpose,
            "oldest_file": min(
                (f["uploaded_at"] for f in self.db["files"]),
                default=None
            ),
            "newest_file": max(
                (f["uploaded_at"] for f in self.db["files"]),
                default=None
            )
        }


def main():
    """Example usage"""
    try:
        manager = FilesManager()

        print("Files API Manager initialized successfully!")
        print(f"Storage directory: {manager.storage_dir}")
        print(f"Database path: {manager.db_path}")

        # Show storage stats
        stats = manager.get_storage_stats()
        print(f"\nStorage Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Total size: {stats['total_size_mb']} MB")

    except AuthenticationError as e:
        print(f"Authentication Error: {e}")
        print("Please set ANTHROPIC_API_KEY environment variable")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
