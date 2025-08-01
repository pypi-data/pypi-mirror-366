import httpx
import os
from typing import List, Optional
from langchain_core.tools import tool
from .exceptions import (
    FilesystemError,
    FileNotFoundInFilesystemError,
    FileAlreadyExistsError,
    AuthenticationError,
)
from .models import FileData
from dotenv import load_dotenv
from .prompts import LIST_FILES_DESCRIPTION, READ_FILE_DESCRIPTION, CREATE_FILE_DESCRIPTION, UPDATE_FILE_DESCRIPTION

load_dotenv()
    
class FilesystemClient:    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        filesystem: str = "default",
        api_url: Optional[str] = None
    ):
        self.api_url = (api_url or os.getenv("AGENT_FS_URL", "https://agent-file-system-production.up.railway.app")).rstrip('/')
        self.api_key = api_key or os.getenv("AGENT_FS_API_KEY")
        self.filesystem = filesystem
        
        if not self.api_key:
            raise ValueError("API key must be provided either as parameter or AGENT_FS_API_KEY environment variable")
            
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def _list_files(self) -> List[FileData]:
        params = {"filesystem": self.filesystem}
        response = httpx.get(
            f"{self.api_url}/v1/files",
            headers=self.headers,
            params=params
        )
        self._handle_response(response)
        return [FileData(**f) for f in response.json()["files"]]
    
    def _read_file(self, path: str, offset: Optional[int] = 0, limit: Optional[int] = 2000) -> FileData:
        response = httpx.get(
            f"{self.api_url}/v1/files/{path}",
            headers=self.headers,
            params={"filesystem": self.filesystem, "offset": offset, "limit": limit}
        )
        self._handle_response(response)
        return FileData(**response.json())
    
    def _create_file(self, path: str, content: str) -> FileData:
        response = httpx.post(
            f"{self.api_url}/v1/files/{path}",
            headers=self.headers,
            json={"content": content},
            params={"filesystem": self.filesystem}
        )
        self._handle_response(response)
        return FileData(**response.json())
    
    def _update_file(self, path: str, old_string: str, new_string: str, replace_all: bool = False) -> FileData:
        response = httpx.put(
            f"{self.api_url}/v1/files/{path}",
            headers=self.headers,
            json={"old_string": old_string, "new_string": new_string, "replace_all": replace_all},
            params={"filesystem": self.filesystem}
        )
        self._handle_response(response)
        return FileData(**response.json())
        
    def list_files(self) -> str:
        try:
            files = self._list_files()
            if not files:
                return "No files found in the filesystem."
            file_list = []
            for file in files:
                file_list.append(
                    f"- {file.path} (v{file.version}, "
                    f"{file.updated_at.strftime('%Y-%m-%d %H:%M')})"
                )
            return "Files:\n" + "\n".join(file_list)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def read_file(self, path: str, offset: Optional[int] = 0, limit: Optional[int] = 2000) -> str:
        try:
            file_data = self._read_file(path, offset, limit)
            content = file_data.content or "[File is empty]"
            return f"[File version: {file_data.version}]\n{content}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def create_file(self, path: str, content: str) -> str:
        try:
            file_data = self._create_file(path, content)
            return f"Successfully created file: {file_data.path} (version {file_data.version})"
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def edit_file(self, path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
        try:
            updated = self._update_file(path, old_string, new_string, replace_all)
            return f"Successfully updated {updated.path} to version {updated.version}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    def create_tools(self):
        return [
            tool(self.list_files, description=LIST_FILES_DESCRIPTION),
            tool(self.read_file, description=READ_FILE_DESCRIPTION),
            tool(self.create_file, description=CREATE_FILE_DESCRIPTION),
            tool(self.edit_file, description=UPDATE_FILE_DESCRIPTION),
        ]

    def _handle_response(self, response: httpx.Response):
        if response.status_code == 200 or response.status_code == 201:
            return
        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired token")
        elif response.status_code == 404:
            raise FileNotFoundInFilesystemError("File not found")
        elif response.status_code == 409:
            error_detail = response.json().get("detail", "")
            if "already exists" in error_detail:
                raise FileAlreadyExistsError(error_detail)
            else:
                raise VersionConflictError(error_detail)
        else:
            try:
                error_data = response.json() if response.text else {}
            except Exception:
                error_data = {}
            raise FilesystemError(
                error_data.get("detail", f"API error: {response.status_code}")
            )