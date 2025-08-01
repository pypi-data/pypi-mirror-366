import logging
from contextlib import contextmanager
from pathlib import Path
from typing import List, Union, Dict

# Ghidra imports
# from ghidra.app.util.importer import MessageLog
# from ghidra.base.project import GhidraProject
#
# from ghidra.program.model.listing import Program
# from ghidra.util.exception import NotFoundException
# from java.io import IOException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
class PyGhidraContext:
    """
    Manages a Ghidra project, including its creation, program imports, and cleanup.
    """

    def __init__(self, project_name: str, project_path: Union[str, Path]):
        """
        Initializes a new Ghidra project context.

        Args:
            project_name: The name of the Ghidra project.
            project_path: The directory where the project will be created.
        """
        self.project_name = project_name
        self.project_path = Path(project_path)
        self.project: GhidraProject = self._get_or_create_project()
        self.programs: Dict[str, Program] = {}

    def _get_or_create_project(self) -> "ghidra.framework.model.GhidraProject":
        """
        Creates a new Ghidra project if it doesn't exist, otherwise opens the existing project.

        Returns:
            The Ghidra project object.
        """

        from ghidra.base.project import GhidraProject
        from java.lang import ClassLoader  # type:ignore @UnresolvedImport
        from ghidra.framework.model import ProjectLocator  # type:ignore @UnresolvedImport
        if project_location:
            project_location = Path(project_location)
        else:
            project_location = binary_path.parent
        if not project_name:
            project_name = f"{binary_path.name}_ghidra"
        project_location /= project_name

        from ghidra.framework.model import ProjectLocator

        project_location_str = str(self.project_path)
        project_dir = self.project_path / self.project_name
        project_dir.mkdir(exist_ok=True, parents=True)

        locator = ProjectLocator(str(self.project_path), self.project_name)

        if locator.exists():
            logger.info(f"Opening existing project: {self.project_name}")
            return GhidraProject.openProject(str(self.project_path), self.project_name, True)
        else:
            logger.info(f"Creating new project: {self.project_name}")
            return GhidraProject.createProject(str(self.project_path), self.project_name, False)

    def import_binaries(self, binary_paths: List[Union[str, Path]], analyze: bool = True):
        """
        Imports and optionally analyzes a list of binaries into the project.

        Args:
            binary_paths: A list of paths to the binary files.
            analyze: If True, run analysis on the imported programs.
        """
        for bin_path in binary_paths:
            self.import_binary(bin_path, analyze)

    def import_binary(self, binary_path: Union[str, Path], analyze: bool = True) -> "ghidra.program.model.listing.Program":
        """
        Imports and optionally analyzes a single binary into the project.

        Args:
            binary_path: Path to the binary file.
            analyze: If True, run analysis on the imported program.

        Returns:
            The imported Ghidra program object.
        """
        from ghidra.program.flatapi import FlatProgramAPI

        binary_path = Path(binary_path)
        program_name = binary_path.name

        root_folder = self.project.getRootFolder()
        program = None

        if root_folder.getFile(program_name):
            logger.info(f"Opening existing program: {program_name}")
            program = self.project.openProgram("/", program_name, False)
        else:
            logger.info(f"Importing new program: {program_name}")
            program = self.project.importProgram(binary_path)
            if program:
                self.project.saveAs(program, "/", program_name, True)
            else:
                raise ImportError(f"Failed to import binary: {binary_path}")

        if program:
            self.programs[program_name] = program

        return program

    def configure_symbols(self, symbols_path: Union[str, Path], symbol_urls: List[str] = None, allow_remote: bool = True):
        """
        Configures symbol servers and attempts to load PDBs for programs.
        """
        from ghidra.app.plugin.core.analysis import PdbAnalyzer, PdbUniversalAnalyzer
        from ghidra.app.util.pdb import PdbProgramAttributes

        logger.info("Configuring symbol search paths...")
        # This is a simplification. A real implementation would need to configure the symbol server
        # which is more involved. For now, we'll focus on enabling the analyzers.

        for program_name, program in self.programs.items():
            logger.info(f"Configuring symbols for {program_name}")
            try:
                if hasattr(PdbUniversalAnalyzer, 'setAllowUntrustedOption'):  # Ghidra 11.2+
                    PdbUniversalAnalyzer.setAllowUntrustedOption(
                        program, allow_remote)
                    PdbAnalyzer.setAllowUntrustedOption(program, allow_remote)
                else:  # Ghidra < 11.2
                    PdbUniversalAnalyzer.setAllowRemoteOption(
                        program, allow_remote)
                    PdbAnalyzer.setAllowRemoteOption(program, allow_remote)

                # The following is a placeholder for actual symbol loading logic
                pdb_attr = PdbProgramAttributes(program)
                if not pdb_attr.pdbLoaded:
                    logger.warning(
                        f"PDB not loaded for {program_name}. Manual loading might be required.")

            except Exception as e:
                logger.error(
                    f"Failed to configure symbols for {program_name}: {e}")

    def list_binaries(self) -> List[str]:
        """List all the binaries within the project."""
        return [f.getName() for f in self.project.getRootFolder().getFiles()]

    def close(self, save: bool = True):
        """
        Saves changes to all open programs and closes the project.
        """
        for program_name, program in self.programs.items():
            if program.isChanged() and save:
                logger.info(f"Saving program: {program_name}")
                program.save("Changes made by PyGhidraContext", None)
            self.project.close(program)

        self.project.close()
        logger.info(f"Project {self.project_name} closed.")
