#!/usr/bin/env python3
"""
KiCad to Python Synchronization Tool

This tool updates existing Python circuit definitions from modified KiCad schematics,
preserving manual Python code modifications while applying changes from the KiCad schematic.

Features:
- Parses KiCad schematics to extract components and nets
- Uses LLM-assisted code generation for intelligent merging
- Preserves existing Python code structure and comments
- Creates backups before making changes
- Supports preview mode for safe testing

Usage:
    kicad-to-python <kicad_project> <python_file> --preview
    kicad-to-python <kicad_project> <python_file> --apply --backup
"""

import argparse
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from circuit_synth.tools.kicad_parser import KiCadParser
from circuit_synth.tools.llm_code_updater import LLMCodeUpdater

# Import refactored modules
from circuit_synth.tools.models import Circuit, Component, Net

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KiCadToPythonSyncer:
    """Main synchronization class"""

    def __init__(
        self,
        kicad_project: str,
        python_file: str,
        preview_only: bool = True,
        create_backup: bool = True,
    ):
        self.kicad_project = Path(kicad_project)
        self.python_file = Path(python_file)
        self.preview_only = preview_only
        self.create_backup = create_backup

        # Initialize components
        self.parser = KiCadParser(str(self.kicad_project))
        self.updater = LLMCodeUpdater()

        logger.info(f"KiCadToPythonSyncer initialized")
        logger.info(f"KiCad project: {self.kicad_project}")
        logger.info(f"Python file: {self.python_file}")
        logger.info(f"Preview mode: {self.preview_only}")

    def sync(self) -> bool:
        """Perform the synchronization from KiCad to Python"""
        logger.info("=== Starting KiCad to Python Synchronization ===")

        try:
            # Step 1: Parse KiCad circuits (hierarchical)
            logger.info("Step 1: Parsing KiCad project")
            circuits = self.parser.parse_circuits()

            if not circuits:
                logger.error("No circuits found in KiCad project")
                return False

            logger.info(f"Found {len(circuits)} circuits:")
            for name, circuit in circuits.items():
                logger.info(
                    f"  - {name}: {len(circuit.components)} components, {len(circuit.nets)} nets"
                )

            # Step 2: Create backup if requested
            if self.create_backup and not self.preview_only:
                logger.info("Step 2: Creating backup")
                backup_path = self._create_backup()
                if backup_path:
                    logger.info(f"Backup created: {backup_path}")
                else:
                    logger.warning("Failed to create backup")

            # Step 3: Update Python file
            logger.info("Step 3: Updating Python file")
            updated_code = self.updater.update_python_file(
                self.python_file, circuits, self.preview_only
            )

            if updated_code:
                if self.preview_only:
                    logger.info("=== PREVIEW MODE - Updated Code ===")
                    print(updated_code)
                    logger.info("=== END PREVIEW ===")
                else:
                    logger.info("✅ Python file updated successfully")

                return True
            else:
                logger.error("❌ Failed to update Python file")
                return False

        except Exception as e:
            logger.error(f"Synchronization failed: {e}")
            return False

    def _create_backup(self) -> Optional[Path]:
        """Create a backup of the Python file"""
        try:
            if not self.python_file.exists():
                logger.warning(f"Python file does not exist: {self.python_file}")
                return None

            backup_path = self.python_file.with_suffix(
                f"{self.python_file.suffix}.backup"
            )

            # Read and write to create backup
            with open(self.python_file, "r") as source:
                content = source.read()

            with open(backup_path, "w") as backup:
                backup.write(content)

            return backup_path

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None


def _resolve_kicad_project_path(input_path: str) -> Optional[Path]:
    """Resolve KiCad project path from various input formats"""
    input_path = Path(input_path)

    # If it's a .kicad_pro file, use it directly
    if input_path.suffix == ".kicad_pro" and input_path.exists():
        return input_path

    # If it's a directory, look for .kicad_pro files
    if input_path.is_dir():
        pro_files = list(input_path.glob("*.kicad_pro"))
        if len(pro_files) == 1:
            return pro_files[0]
        elif len(pro_files) > 1:
            logger.error(f"Multiple .kicad_pro files found in {input_path}")
            for pro_file in pro_files:
                logger.error(f"  - {pro_file}")
            return None
        else:
            logger.error(f"No .kicad_pro files found in {input_path}")
            return None

    # If it's a file without extension, try adding .kicad_pro
    if input_path.suffix == "":
        pro_path = input_path.with_suffix(".kicad_pro")
        if pro_path.exists():
            return pro_path

    # If it's in a subdirectory, look in parent directories
    current_path = input_path
    while current_path.parent != current_path:
        pro_files = list(current_path.glob("*.kicad_pro"))
        if pro_files:
            if len(pro_files) == 1:
                return pro_files[0]
        current_path = current_path.parent

    logger.error(f"Could not resolve KiCad project path from: {input_path}")
    return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Synchronize KiCad schematics with Python circuit definitions"
    )
    parser.add_argument(
        "kicad_project", help="Path to KiCad project (.kicad_pro) or directory"
    )
    parser.add_argument("python_file", help="Path to Python file to update")
    parser.add_argument(
        "--preview", action="store_true", help="Preview changes without applying"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply changes to the Python file"
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup before applying changes"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate arguments
    if not args.preview and not args.apply:
        logger.error("Must specify either --preview or --apply")
        return 1

    if args.apply and args.preview:
        logger.error("Cannot specify both --preview and --apply")
        return 1

    # Resolve KiCad project path
    kicad_project = _resolve_kicad_project_path(args.kicad_project)
    if not kicad_project:
        return 1

    # Validate Python file
    python_file = Path(args.python_file)
    if not python_file.exists() and args.apply:
        logger.error(f"Python file does not exist: {python_file}")
        return 1

    # Create syncer and run
    syncer = KiCadToPythonSyncer(
        kicad_project=str(kicad_project),
        python_file=str(python_file),
        preview_only=args.preview,
        create_backup=args.backup,
    )

    success = syncer.sync()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
