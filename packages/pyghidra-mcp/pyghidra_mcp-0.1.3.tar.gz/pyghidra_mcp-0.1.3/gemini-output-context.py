   1 import logging
       2 from contextlib import contextmanager
        3 from pathlib import Path
        4 from typing import List
        5
        6 from ghidra.app.util.importer import MessageLog
        7 from ghidra.framework.model import Project, Tool, ToolListener
        8 from ghidra.framework.project import ProjectManager
        9 from ghidra.program.model.listing import Program
    10 from ghidra.util import SystemUtilities
    11
    12  # Configure logging
    13 logging.basicConfig(level=logging.INFO)
    14 logger = logging.getLogger(__name__)
    15
    16 class PyGhidraContext:
    17     """
   18     Manages a Ghidra project, including its creation, program imports, and cleanup.
   19     """
    20
    21 def __init__(self, project_name: str, project_path: Path):
    22         """
   23         Initializes a new Ghidra project context.
   24 
   25         Args:
   26             project_name: The name of the Ghidra project.
   27             project_path: The directory where the project will be created.
   28         """
    29         self.project_name = project_name
    30         self.project_path = project_path
    31         self.project: Project = self._get_or_create_project()
    32         self.open_programs: List[Program] = []
    33
    34 def _get_or_create_project(self) -> Project:
    35         """
   36         Creates a new Ghidra project if it doesn't exist, otherwise opens the existing project.
   37 
   38         Returns:
   39             The Ghidra project object.
   40         """
    41         project_dir = self.project_path.joinpath(self.project_name)
    42         project_dir.mkdir(parents=True, exist_ok=True)
    43
    44         pm = ProjectManager.getInstance()
    45         # Attempt to restore the project first
    46         restored_project = pm.recoverProject(project_dir.as_posix())
    47 if restored_project:
    48             logger.info(f"Successfully restored project: {self.project_name}")
    49 return restored_project
    50
    51         # Create a new project if restoration fails
    52         project = pm.createProject(project_dir.as_posix(), self.project_name, True)
    53         logger.info(f"Successfully created project: {self.project_name}")
    54 return project
    55
    56 def close(self):
    57         """
   58         Saves changes to all open programs and closes the project.
   59         """
    60 for program in self.open_programs:
    61 if program.isChanged():
    62                 program.save("Changes made by PyGhidra", None)
    63         self.project.close()
    64
    65 @ contextmanager
    66 def open_context(project_name: str, project_path: Path):
    67     """
   68     Context manager for creating and managing a Ghidra project.
   69     """
    70     context = PyGhidraContext(project_name, project_path)
    71 try:
    72 yield context
    73 finally:
    74         context.close()
