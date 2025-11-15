"""
ComfyUI Command-Line Tools (cmdtls)
Custom nodes for file browsing, upload, download, and shell execution
"""

from .nodes.file_browser import (
    FileBrowser,
    FileReader,
    FileWriter,
    FileCopy,
    ShellExecutor,
    DirectoryCreator,
    FileDelete,
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
)

# Version info
__version__ = "1.0.0"
__author__ = "marduk191"
__description__ = "ComfyUI custom nodes for file system operations and shell commands"

# Export for ComfyUI
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]

# This is what ComfyUI looks for
WEB_DIRECTORY = "./web"
