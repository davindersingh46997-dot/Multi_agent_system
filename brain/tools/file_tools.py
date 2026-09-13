from pathlib import Path

from brain.tools.Base_tool import BaseTool

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
        """
        prevent access outside the project directory
        """  
        requested_path = (
            self._project_root / file_path
        ).resolve()

        if not requested_path.is_relative_to(self._project_root):
            raise PermissionError(
                "Access outside project directory is not allowed. "
            )

        return requested_path

    def execute(self,file_path : str) -> str:
        path = self._safe_path(file_path)

        if not path.exist():
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

        requested_path = (
            self._project_root / file_path
        ).resolve()  

        if not request_path.is_relative_to(self._project_root):
            raise PermissionError(
                "Access outside project directory is not allowed. "
            )

            