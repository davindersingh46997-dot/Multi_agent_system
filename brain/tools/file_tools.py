from pathlib import Path

from brain.tools.Base_tool import BaseTool


def _safe_project_path(project_root: Path, file_path: str) -> Path:
    candidate = Path(file_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise PermissionError("Absolute paths and traversal are not permitted.")
    requested_path = project_root
    for part in candidate.parts:
        if part != ".":
            requested_path = requested_path / part
        if requested_path.is_symlink():
            raise PermissionError("Symbolic links are not permitted.")
    requested_path = requested_path.resolve()
    if not requested_path.is_relative_to(project_root):
        raise PermissionError("Access outside project directory is not allowed.")
    name = requested_path.name.lower()
    if name.startswith(".env") or requested_path.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".db"}:
        raise PermissionError("Sensitive files are not available to project tools.")
    return requested_path


class FileReaderTool(BaseTool):
    """
    Tools to read inside the allowed project directory
    """

    def __init__(self,project_root: str):
        super().__init__(
            name = "read_file",
            description="Read the contents of the project file"
        )

        self._project_root = Path(project_root).resolve()

    def _safe_path(self,file_path : str) -> Path:
        return _safe_project_path(self._project_root, file_path)

    def execute(self,file_path : str) -> str:
        path = self._safe_path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File does not exist : {file_path}"
            )        

        if not path.is_file():
            raise IsADirectoryError(
                f"path is not file directory : {file_path}"
            ) 

        return path.read_text(
            encoding = "utf-8",
            errors = "replace"
        ) 

class FileWriterTool(BaseTool):
    """
    Tool for writing files inside the project directory
    """
    def __init__(self,project_file : str):
        super().__init__(
            name = "write_file",
            description = "write or replace the contents of a project file "
        ) 
        
        self._project_root = Path(project_file).resolve()

    def _safe_path(self,file_path : str) -> Path:
        return _safe_project_path(self._project_root, file_path)
    
    def execute(self,file_path : str,content : str) -> None:
        self._safe_path(file_path)
        raise PermissionError(
            "Direct writes are disabled. Stage changes through the approval workflow."
        )
    

class FileCreaterTool(BaseTool):
    """
    Tool to create the file inside the project directory 
    """  

    def __init__(self, project_root: str):
        super().__init__(
            name="create_file",
            description="Create a new file in the project directory"
        )
        self._project_root = Path(project_root).resolve()

    def _safe_path(self, file_path: str) -> Path:
        return _safe_project_path(self._project_root, file_path)

    def execute(self, file_path: str) -> None:
        self._safe_path(file_path)
        raise PermissionError(
            "Direct file creation is disabled. Stage changes through the approval workflow."
        )


class DirectoryListerTool(BaseTool):
    """
    Tool for listing project directories.
    """

    def __init__(self, project_root: str):
        super().__init__(
            name="list_directory",
            description=(
                "List files and directories "
                "inside the project directory."
            )
        )

        self._project_root = Path(
            project_root
        ).resolve()

    def _safe_path(self, file_path: str) -> Path:
        """
        Resolve and validate a directory path
        inside the project directory.
        """

        return _safe_project_path(self._project_root, file_path)

    def execute(
        self,
        directory_path: str = "."
    ) -> list[str]:
        """
        List files and directories inside
        the requested directory.
        """

        requested_path = self._safe_path(
            directory_path
        )

        if not requested_path.exists():
            raise FileNotFoundError(
                f"Directory does not exist: "
                f"{directory_path}"
            )

        if not requested_path.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: "
                f"{directory_path}"
            )

        entries = sorted(
            requested_path.iterdir(),
            key=lambda path: (
                not path.is_dir(),
                path.name.lower()
            )
        )

        result = []

        for entry in entries:

            if entry.is_symlink() or entry.name.lower().startswith(".env"):
                continue

            if entry.is_dir():
                result.append(
                    f"[DIR]  {entry.name}"
                )

            else:
                result.append(
                    f"[FILE] {entry.name}"
                )

        return result