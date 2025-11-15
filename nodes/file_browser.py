"""
ComfyUI File Browser Node
Provides file browsing, upload, download, and shell execution capabilities
"""

import os
import json
import shutil
import subprocess
import base64
from pathlib import Path
from typing import Dict, List, Tuple, Any


class FileBrowser:
    """
    File Browser Node - Browse directories and files on the local machine
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> Dict:
        return {
            "required": {
                "directory_path": ("STRING", {
                    "default": os.path.expanduser("~"),
                    "multiline": False
                }),
                "show_hidden": ("BOOLEAN", {"default": False}),
                "filter_pattern": ("STRING", {
                    "default": "*",
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("files_json", "directories_json", "current_path")
    FUNCTION = "browse_files"
    CATEGORY = "utilities/file_browser"
    OUTPUT_NODE = True

    def browse_files(self, directory_path: str, show_hidden: bool = False,
                    filter_pattern: str = "*") -> Tuple[str, str, str]:
        """
        Browse files in a directory

        Args:
            directory_path: Path to directory to browse
            show_hidden: Whether to show hidden files
            filter_pattern: Pattern to filter files (e.g., *.txt, *.py)

        Returns:
            Tuple of (files_json, directories_json, current_path)
        """
        try:
            # Expand user path and resolve
            path = Path(directory_path).expanduser().resolve()

            if not path.exists():
                return (
                    json.dumps({"error": "Path does not exist"}),
                    json.dumps({"error": "Path does not exist"}),
                    str(directory_path)
                )

            if not path.is_dir():
                return (
                    json.dumps({"error": "Path is not a directory"}),
                    json.dumps({"error": "Path is not a directory"}),
                    str(directory_path)
                )

            # Get list of files and directories
            files = []
            directories = []

            try:
                for item in path.iterdir():
                    # Skip hidden files if requested
                    if not show_hidden and item.name.startswith('.'):
                        continue

                    item_info = {
                        "name": item.name,
                        "path": str(item),
                        "size": item.stat().st_size if item.is_file() else 0,
                        "modified": item.stat().st_mtime,
                        "is_dir": item.is_dir(),
                        "is_file": item.is_file(),
                        "is_symlink": item.is_symlink(),
                    }

                    if item.is_dir():
                        directories.append(item_info)
                    elif item.is_file():
                        # Apply filter pattern
                        if filter_pattern == "*" or item.match(filter_pattern):
                            files.append(item_info)

                # Sort files and directories by name
                files.sort(key=lambda x: x["name"].lower())
                directories.sort(key=lambda x: x["name"].lower())

                return (
                    json.dumps(files, indent=2),
                    json.dumps(directories, indent=2),
                    str(path)
                )

            except PermissionError:
                return (
                    json.dumps({"error": "Permission denied"}),
                    json.dumps({"error": "Permission denied"}),
                    str(path)
                )

        except Exception as e:
            return (
                json.dumps({"error": str(e)}),
                json.dumps({"error": str(e)}),
                str(directory_path)
            )


class FileReader:
    """
    File Reader Node - Read file contents
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> Dict:
        return {
            "required": {
                "file_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "encoding": (["utf-8", "ascii", "latin-1", "binary"], {
                    "default": "utf-8"
                }),
                "max_size_mb": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 100
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("content", "file_info")
    FUNCTION = "read_file"
    CATEGORY = "utilities/file_browser"
    OUTPUT_NODE = True

    def read_file(self, file_path: str, encoding: str = "utf-8",
                 max_size_mb: int = 10) -> Tuple[str, str]:
        """
        Read file contents

        Args:
            file_path: Path to file to read
            encoding: Encoding to use (utf-8, ascii, latin-1, binary)
            max_size_mb: Maximum file size to read in MB

        Returns:
            Tuple of (content, file_info)
        """
        try:
            path = Path(file_path).expanduser().resolve()

            if not path.exists():
                return (
                    "Error: File does not exist",
                    json.dumps({"error": "File does not exist"})
                )

            if not path.is_file():
                return (
                    "Error: Path is not a file",
                    json.dumps({"error": "Path is not a file"})
                )

            # Check file size
            file_size = path.stat().st_size
            max_size = max_size_mb * 1024 * 1024

            if file_size > max_size:
                return (
                    f"Error: File too large ({file_size / 1024 / 1024:.2f} MB > {max_size_mb} MB)",
                    json.dumps({"error": "File too large", "size": file_size})
                )

            # Read file
            if encoding == "binary":
                with open(path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('ascii')
                    content = f"[Binary file - Base64 encoded]\n{content}"
            else:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()

            # Get file info
            file_info = {
                "name": path.name,
                "path": str(path),
                "size": file_size,
                "modified": path.stat().st_mtime,
                "encoding": encoding,
            }

            return (content, json.dumps(file_info, indent=2))

        except Exception as e:
            return (
                f"Error: {str(e)}",
                json.dumps({"error": str(e)})
            )


class FileWriter:
    """
    File Writer Node - Write content to a file (Upload)
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> Dict:
        return {
            "required": {
                "file_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "content": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "encoding": (["utf-8", "ascii", "latin-1"], {
                    "default": "utf-8"
                }),
                "overwrite": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status", "file_info")
    FUNCTION = "write_file"
    CATEGORY = "utilities/file_browser"
    OUTPUT_NODE = True

    def write_file(self, file_path: str, content: str,
                   encoding: str = "utf-8", overwrite: bool = False) -> Tuple[str, str]:
        """
        Write content to a file

        Args:
            file_path: Path to file to write
            content: Content to write
            encoding: Encoding to use
            overwrite: Whether to overwrite if file exists

        Returns:
            Tuple of (status, file_info)
        """
        try:
            path = Path(file_path).expanduser().resolve()

            # Check if file exists
            if path.exists() and not overwrite:
                return (
                    "Error: File exists and overwrite is False",
                    json.dumps({"error": "File exists", "path": str(path)})
                )

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            # Get file info
            file_info = {
                "name": path.name,
                "path": str(path),
                "size": path.stat().st_size,
                "modified": path.stat().st_mtime,
                "encoding": encoding,
            }

            return (
                f"Successfully wrote {len(content)} characters to {path.name}",
                json.dumps(file_info, indent=2)
            )

        except Exception as e:
            return (
                f"Error: {str(e)}",
                json.dumps({"error": str(e)})
            )


class FileCopy:
    """
    File Copy Node - Copy files (Download/Upload helper)
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> Dict:
        return {
            "required": {
                "source_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "destination_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "overwrite": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status", "file_info")
    FUNCTION = "copy_file"
    CATEGORY = "utilities/file_browser"
    OUTPUT_NODE = True

    def copy_file(self, source_path: str, destination_path: str,
                 overwrite: bool = False) -> Tuple[str, str]:
        """
        Copy a file from source to destination

        Args:
            source_path: Source file path
            destination_path: Destination file path
            overwrite: Whether to overwrite if destination exists

        Returns:
            Tuple of (status, file_info)
        """
        try:
            src = Path(source_path).expanduser().resolve()
            dst = Path(destination_path).expanduser().resolve()

            if not src.exists():
                return (
                    "Error: Source file does not exist",
                    json.dumps({"error": "Source does not exist"})
                )

            if not src.is_file():
                return (
                    "Error: Source is not a file",
                    json.dumps({"error": "Source is not a file"})
                )

            if dst.exists() and not overwrite:
                return (
                    "Error: Destination exists and overwrite is False",
                    json.dumps({"error": "Destination exists"})
                )

            # Create parent directories if needed
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(src, dst)

            # Get file info
            file_info = {
                "source": str(src),
                "destination": str(dst),
                "size": dst.stat().st_size,
                "modified": dst.stat().st_mtime,
            }

            return (
                f"Successfully copied {src.name} to {dst}",
                json.dumps(file_info, indent=2)
            )

        except Exception as e:
            return (
                f"Error: {str(e)}",
                json.dumps({"error": str(e)})
            )


class ShellExecutor:
    """
    Shell Executor Node - Execute shell commands
    WARNING: This node can execute arbitrary commands. Use with caution!
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> Dict:
        return {
            "required": {
                "command": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "working_directory": ("STRING", {
                    "default": os.path.expanduser("~"),
                    "multiline": False
                }),
                "timeout_seconds": ("INT", {
                    "default": 30,
                    "min": 1,
                    "max": 300
                }),
                "capture_output": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("stdout", "stderr", "return_code")
    FUNCTION = "execute_command"
    CATEGORY = "utilities/file_browser"
    OUTPUT_NODE = True

    def execute_command(self, command: str, working_directory: str = None,
                       timeout_seconds: int = 30,
                       capture_output: bool = True) -> Tuple[str, str, int]:
        """
        Execute a shell command

        Args:
            command: Command to execute
            working_directory: Working directory for command execution
            timeout_seconds: Timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        try:
            # Expand working directory
            if working_directory:
                cwd = Path(working_directory).expanduser().resolve()
                if not cwd.exists() or not cwd.is_dir():
                    return (
                        "",
                        f"Error: Working directory does not exist: {cwd}",
                        -1
                    )
            else:
                cwd = None

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd) if cwd else None,
                capture_output=capture_output,
                text=True,
                timeout=timeout_seconds
            )

            return (
                result.stdout if result.stdout else "",
                result.stderr if result.stderr else "",
                result.returncode
            )

        except subprocess.TimeoutExpired:
            return (
                "",
                f"Error: Command timed out after {timeout_seconds} seconds",
                -1
            )
        except Exception as e:
            return (
                "",
                f"Error: {str(e)}",
                -1
            )


class DirectoryCreator:
    """
    Directory Creator Node - Create directories
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> Dict:
        return {
            "required": {
                "directory_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "create_parents": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status", "directory_info")
    FUNCTION = "create_directory"
    CATEGORY = "utilities/file_browser"
    OUTPUT_NODE = True

    def create_directory(self, directory_path: str,
                        create_parents: bool = True) -> Tuple[str, str]:
        """
        Create a directory

        Args:
            directory_path: Path to directory to create
            create_parents: Whether to create parent directories

        Returns:
            Tuple of (status, directory_info)
        """
        try:
            path = Path(directory_path).expanduser().resolve()

            if path.exists():
                if path.is_dir():
                    return (
                        f"Directory already exists: {path}",
                        json.dumps({"path": str(path), "exists": True})
                    )
                else:
                    return (
                        "Error: Path exists but is not a directory",
                        json.dumps({"error": "Path is not a directory"})
                    )

            # Create directory
            path.mkdir(parents=create_parents, exist_ok=True)

            # Get directory info
            dir_info = {
                "path": str(path),
                "created": True,
                "modified": path.stat().st_mtime,
            }

            return (
                f"Successfully created directory: {path}",
                json.dumps(dir_info, indent=2)
            )

        except Exception as e:
            return (
                f"Error: {str(e)}",
                json.dumps({"error": str(e)})
            )


class FileDelete:
    """
    File Delete Node - Delete files
    WARNING: This permanently deletes files!
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> Dict:
        return {
            "required": {
                "file_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "confirm_delete": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "delete_file"
    CATEGORY = "utilities/file_browser"
    OUTPUT_NODE = True

    def delete_file(self, file_path: str, confirm_delete: bool = False) -> Tuple[str]:
        """
        Delete a file

        Args:
            file_path: Path to file to delete
            confirm_delete: Must be True to actually delete

        Returns:
            Tuple of (status,)
        """
        try:
            if not confirm_delete:
                return ("Error: confirm_delete must be True to delete files",)

            path = Path(file_path).expanduser().resolve()

            if not path.exists():
                return (f"Error: File does not exist: {path}",)

            if not path.is_file():
                return (f"Error: Path is not a file: {path}",)

            # Delete file
            path.unlink()

            return (f"Successfully deleted: {path}",)

        except Exception as e:
            return (f"Error: {str(e)}",)


# Export node classes
NODE_CLASS_MAPPINGS = {
    "FileBrowser": FileBrowser,
    "FileReader": FileReader,
    "FileWriter": FileWriter,
    "FileCopy": FileCopy,
    "ShellExecutor": ShellExecutor,
    "DirectoryCreator": DirectoryCreator,
    "FileDelete": FileDelete,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FileBrowser": "File Browser",
    "FileReader": "File Reader",
    "FileWriter": "File Writer (Upload)",
    "FileCopy": "File Copy (Download/Upload)",
    "ShellExecutor": "Shell Executor",
    "DirectoryCreator": "Directory Creator",
    "FileDelete": "File Delete",
}
