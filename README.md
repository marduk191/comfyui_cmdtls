# ComfyUI Command-Line Tools (cmdtls)

A comprehensive set of ComfyUI custom nodes for file system operations, file browsing, upload/download, and shell command execution.

## Features

- **File Browser**: Browse directories and files on your local machine
- **File Reader**: Read file contents (supports multiple encodings)
- **File Writer**: Write content to files (upload functionality)
- **File Copy**: Copy files between locations (download/upload helper)
- **Shell Executor**: Execute shell commands with timeout and output capture
- **Directory Creator**: Create directories with parent directory support
- **File Delete**: Delete files with confirmation

## Installation

1. Clone or download this repository into your ComfyUI custom_nodes directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/marduk191/comfyui_cmdtls.git
```

2. Install dependencies (if any):

```bash
cd comfyui_cmdtls
pip install -r requirements.txt
```

3. Restart ComfyUI

## Nodes

### 1. File Browser

Browse directories and files on the local machine.

**Inputs:**
- `directory_path` (STRING): Path to directory to browse (default: home directory)
- `show_hidden` (BOOLEAN): Whether to show hidden files (default: False)
- `filter_pattern` (STRING): Pattern to filter files, e.g., `*.txt`, `*.py` (default: `*`)

**Outputs:**
- `files_json` (STRING): JSON array of files with metadata
- `directories_json` (STRING): JSON array of directories with metadata
- `current_path` (STRING): The current resolved path

**Example Output:**
```json
[
  {
    "name": "example.txt",
    "path": "/home/user/example.txt",
    "size": 1024,
    "modified": 1699999999.0,
    "is_dir": false,
    "is_file": true,
    "is_symlink": false
  }
]
```

### 2. File Reader

Read file contents with support for multiple encodings.

**Inputs:**
- `file_path` (STRING): Path to file to read
- `encoding` (CHOICE): Encoding to use - utf-8, ascii, latin-1, or binary
- `max_size_mb` (INT): Maximum file size to read in MB (1-100, default: 10)

**Outputs:**
- `content` (STRING): File content (or base64 for binary files)
- `file_info` (STRING): JSON metadata about the file

**Note:** Binary files are returned as base64-encoded strings.

### 3. File Writer (Upload)

Write content to a file on the local machine.

**Inputs:**
- `file_path` (STRING): Path where to write the file
- `content` (STRING): Content to write
- `encoding` (CHOICE): Encoding to use - utf-8, ascii, or latin-1
- `overwrite` (BOOLEAN): Whether to overwrite if file exists (default: False)

**Outputs:**
- `status` (STRING): Success or error message
- `file_info` (STRING): JSON metadata about the written file

**Note:** Parent directories are automatically created if they don't exist.

### 4. File Copy (Download/Upload)

Copy files from source to destination.

**Inputs:**
- `source_path` (STRING): Source file path
- `destination_path` (STRING): Destination file path
- `overwrite` (BOOLEAN): Whether to overwrite if destination exists (default: False)

**Outputs:**
- `status` (STRING): Success or error message
- `file_info` (STRING): JSON metadata about the copied file

**Use Cases:**
- Download: Copy from remote/temp location to local storage
- Upload: Copy from local storage to remote/temp location
- Backup: Create file backups

### 5. Shell Executor

Execute shell commands on the local machine.

**Inputs:**
- `command` (STRING): Command to execute (supports multiline)
- `working_directory` (STRING): Working directory for execution (default: home directory)
- `timeout_seconds` (INT): Timeout in seconds (1-300, default: 30)
- `capture_output` (BOOLEAN): Whether to capture stdout/stderr (default: True)

**Outputs:**
- `stdout` (STRING): Standard output from command
- `stderr` (STRING): Standard error from command
- `return_code` (INT): Return code from command (0 = success)

**Warning:** This node can execute arbitrary commands. Use with caution and only in trusted environments!

**Examples:**
```bash
# List files
ls -la

# Check Python version
python --version

# Run a script
python /path/to/script.py

# Chain commands
echo "Hello" && echo "World"
```

### 6. Directory Creator

Create directories on the local machine.

**Inputs:**
- `directory_path` (STRING): Path to directory to create
- `create_parents` (BOOLEAN): Whether to create parent directories (default: True)

**Outputs:**
- `status` (STRING): Success or error message
- `directory_info` (STRING): JSON metadata about the directory

### 7. File Delete

Delete files from the local machine.

**Inputs:**
- `file_path` (STRING): Path to file to delete
- `confirm_delete` (BOOLEAN): Must be True to actually delete (safety feature)

**Outputs:**
- `status` (STRING): Success or error message

**Warning:** This permanently deletes files! There is no undo.

## Usage Examples

### Example 1: Browse and Read a File

1. Add a **File Browser** node
   - Set `directory_path` to the directory you want to browse
   - Connect the outputs to see available files

2. Add a **File Reader** node
   - Set `file_path` to the file you want to read
   - Connect the `content` output to see the file contents

### Example 2: Upload/Write a File

1. Add a **File Writer** node
   - Set `file_path` to where you want to save the file
   - Set `content` to the text you want to write
   - Set `overwrite` to True if you want to replace existing files
   - Execute to write the file

### Example 3: Execute Shell Commands

1. Add a **Shell Executor** node
   - Set `command` to the command you want to run
   - Set `working_directory` to the appropriate directory
   - Connect the `stdout`, `stderr`, and `return_code` outputs to see results

### Example 4: Copy Files (Download)

1. Add a **File Copy** node
   - Set `source_path` to the file you want to copy
   - Set `destination_path` to where you want to copy it
   - Set `overwrite` as needed
   - Execute to copy the file

## Security Considerations

**WARNING:** These nodes provide powerful file system and shell access. Use them responsibly:

1. **Shell Executor**: Can execute arbitrary commands on your system
2. **File Delete**: Permanently deletes files with no recovery
3. **File Writer**: Can overwrite existing files
4. **Path Traversal**: All nodes use path resolution to prevent basic path traversal, but be cautious with user inputs

**Recommendations:**
- Only use these nodes in trusted environments
- Be careful when allowing user-provided paths or commands
- Consider file size limits when reading/writing files
- Always verify paths before deleting files
- Use timeouts for shell commands to prevent hanging
- Review command outputs for sensitive information

## Category

All nodes are organized under: **utilities/file_browser**

## Technical Details

- **Language**: Python 3
- **Dependencies**: Standard library + optional (pathlib, aiofiles, psutil)
- **ComfyUI Compatibility**: Tested with ComfyUI 1.0+
- **Path Handling**: Uses `pathlib.Path` for cross-platform compatibility
- **Error Handling**: Comprehensive error handling with JSON error messages

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

[Specify your license here]

## Author

marduk191

## Version

1.0.0

## Changelog

### v1.0.0 (Initial Release)
- File Browser with filtering and hidden file support
- File Reader with multiple encoding support
- File Writer for uploading content
- File Copy for download/upload operations
- Shell Executor with timeout and output capture
- Directory Creator with parent directory support
- File Delete with confirmation safety feature