LIST_FILES_DESCRIPTION = """Lists all files from the local filesystem. You can use this tool to see a comprehensive list of all files in the filesystem.
Assume that this tool is able to see all files on the machine.

Usage:
- You should call this tool before trying to read, update, or create new files. This tool will give you context as to what the current filesystem looks like, which is crucial for reading, updating, and writing."""

READ_FILE_DESCRIPTION = """Reads a file from the local filesystem. You can access any file directly by using this tool.
Assume this tool is able to read all files on the machine. If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.

Usage:
- The file_path parameter must be an absolute path, not a relative path
- By default, it reads up to 2000 lines starting from the beginning of the file
- You can optionally specify a line offset and limit (especially handy for long files), but it's recommended to read the whole file by not providing these parameters
- Any lines longer than 2000 characters will be truncated
- Results are returned using cat -n format, with line numbers starting at 1
- You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful. 
- If you read a file that exists but has empty contents you will receive a system reminder warning in place of file contents."""

CREATE_FILE_DESCRIPTION = """Creates a new file in the local filesystem. You can use this tool to create a net new file.

Usage:
- Always call the list files tool before creating a new file. This will give you context as to what the current filesystem looks like, which is crucial for writing new files.
- Reason carefully about where it makes the most sense to create a new file.
- The file_path parameter must be an absolute path, not a relative path
- The path should NOT start with a /, but you can use / to denote directories within the path
    - For example, you can create a file called 'learnings/past_mistakes.txt'.
    - This would make sense if you are trying to store all of your 'learnings' in a single folder.
- The content parameter must be a string of the content to write to the file
- Use \n to separate lines in the content of the file."""

UPDATE_FILE_DESCRIPTION = """Performs exact string replacements in files. You can use this tool to update the contents of an existing file.

Usage:
- You must use your `Read` tool at least once in the conversation before editing. This tool will error if you attempt an edit without reading the file. 
- When editing text from Read tool output, ensure you preserve the exact indentation (tabs/spaces) as it appears AFTER the line number prefix. The line number prefix format is: spaces + line number + tab. Everything after that tab is the actual file content to match. Never include any part of the line number prefix in the old_string or new_string.
- ALWAYS prefer editing existing files. NEVER write new files unless explicitly required.
- Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.
- The edit will FAIL if `old_string` is not unique in the file. Either provide a larger string with more surrounding context to make it unique or use `replace_all` to change every instance of `old_string`. 
- Use `replace_all` for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance."""