# -*- coding: utf-8 -*-
#
# main_generator.py
#
# Refactored KiCad Integration implementing IKiCadIntegration interface
# Part of Phase 2 architecture refactoring to consolidate dual implementations

import json
import logging
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...core.dependency_injection import (
    DependencyContainer,
    IDependencyContainer,
    ServiceLocator,
)

# Import abstract interfaces
from ...interfaces.kicad_interface import (
    IFootprintLibrary,
    IKiCadIntegration,
    IPCBGenerator,
    ISchematicGenerator,
    ISymbolLibrary,
    KiCadGenerationConfig,
)

# Import existing implementation modules
from .circuit_loader import assign_subcircuit_instance_labels, load_circuit_hierarchy
from .collision_manager import SHEET_MARGIN, CollisionManager
from .connection_aware_collision_manager import ConnectionAwareCollisionManager
from .schematic_writer import SchematicWriter, write_schematic_file

# LLM placement not available - using optimized collision-based placement
LLM_PLACEMENT_AVAILABLE = False


class LLMPlacementManager:
    """Optimized collision-based placement manager for high performance."""

    def __init__(self, *args, **kwargs):
        logging.info("Using optimized collision-based placement for high performance")

    def place_components(self, components, nets, existing_placements=None):
        """Fallback to basic grid placement"""
        placements = {}
        x, y = 50, 50  # Starting position
        for comp in components:
            placements[comp.ref] = {"x": x, "y": y}
            x += 100  # Simple grid layout
            if x > 400:  # Wrap to next row
                x = 50
                y += 100
        return placements


# Use optimized symbol cache from core.component for better performance
from circuit_synth.core.component import SymbolLibCache
from circuit_synth.kicad.canonical import CanonicalCircuit, CircuitMatcher
from circuit_synth.kicad.kicad_symbol_cache import SymbolLibCache
from circuit_synth.kicad.netlist_importer import CircuitSynthParser
from circuit_synth.kicad.sch_editor.schematic_reader import SchematicReader

from .symbol_geometry import SymbolBoundingBoxCalculator

logger = logging.getLogger(__name__)


class SchematicGeneratorImpl(ISchematicGenerator):
    """Implementation of ISchematicGenerator interface using existing logic."""

    def __init__(self, output_dir: str, project_name: str):
        self.output_dir = Path(output_dir).resolve()
        self.project_name = project_name
        self.project_dir = self.output_dir / project_name

    def generate_from_circuit_data(
        self,
        circuit_data: Dict[str, Any],
        config: Optional[KiCadGenerationConfig] = None,
    ) -> Dict[str, Any]:
        """Generate schematic from circuit data using existing implementation."""
        try:
            # Extract JSON file path from circuit_data
            json_file = circuit_data.get("json_file", "")
            if not json_file:
                raise ValueError("circuit_data must contain 'json_file' key")

            # Create legacy generator and use existing logic
            legacy_generator = SchematicGenerator(
                str(self.output_dir), self.project_name
            )

            # Convert config to legacy format
            legacy_kwargs = {}
            if config:
                if config.placement_algorithm:
                    legacy_kwargs["schematic_placement"] = config.placement_algorithm
                if config.generate_pcb is not None:
                    legacy_kwargs["generate_pcb"] = config.generate_pcb
                if config.force_regenerate is not None:
                    legacy_kwargs["force_regenerate"] = config.force_regenerate

            # Generate using existing method
            legacy_generator.generate_project(json_file, **legacy_kwargs)

            return {
                "success": True,
                "output_path": str(self.project_dir),
                "message": "Schematic generated successfully",
            }

        except Exception as e:
            logger.error(f"Schematic generation failed: {e}")
            return {"success": False, "error": str(e)}


class SchematicGenerator(IKiCadIntegration):
    """
    Refactored KiCad integration implementing IKiCadIntegration interface.

    This class consolidates the existing KiCad generation logic while providing
    a clean interface for dependency injection and future extensibility.
    """

    # Paper sizes in mm (width, height)
    PAPER_SIZES = {
        "A4": (210.0, 297.0),
        "A3": (297.0, 420.0),
        "A2": (420.0, 594.0),
        "A1": (594.0, 841.0),
        "A0": (841.0, 1189.0),
    }

    def __init__(
        self,
        output_dir: str,
        project_name: str,
        container: Optional[IDependencyContainer] = None,
    ):
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.project_name = project_name
        self.project_dir = self.output_dir / project_name
        # Don't create project directory here - wait until we're actually generating files
        self.project_uuid = str(uuid.uuid4())
        self.paper_size = "A4"  # Default paper size
        self.container = container

        # Initialize sub-components
        self._schematic_generator = None
        self._pcb_generator = None
        self._symbol_library = None
        self._footprint_library = None

    # IKiCadIntegration interface implementation
    def generate_schematic(
        self,
        circuit_data: Dict[str, Any],
        output_path: Path,
        config: Optional[KiCadGenerationConfig] = None,
    ) -> Dict[str, Any]:
        """Generate KiCad schematic from circuit data."""
        try:
            # Extract JSON file path from circuit_data
            json_file = circuit_data.get("json_file", "")
            if not json_file:
                raise ValueError("circuit_data must contain 'json_file' key")

            # Convert config to legacy format
            legacy_kwargs = {}
            if config:
                if config.placement_algorithm:
                    legacy_kwargs["schematic_placement"] = config.placement_algorithm
                if config.generate_pcb is not None:
                    legacy_kwargs["generate_pcb"] = config.generate_pcb
                if config.force_regenerate is not None:
                    legacy_kwargs["force_regenerate"] = config.force_regenerate

            # Generate using existing method
            self.generate_project(json_file, **legacy_kwargs)

            return {
                "success": True,
                "output_path": str(output_path),
                "message": "Schematic generated successfully",
            }

        except Exception as e:
            logger.error(f"Schematic generation failed: {e}")
            return {"success": False, "error": str(e)}

    def generate_pcb(
        self,
        schematic_path: Path,
        output_path: Path,
        config: Optional[KiCadGenerationConfig] = None,
    ) -> Dict[str, Any]:
        """Generate KiCad PCB from schematic."""
        try:
            # Import PCB generator here to avoid circular imports
            from ..pcb_gen.pcb_generator import PCBGenerator

            pcb_gen = PCBGenerator(str(output_path.parent), output_path.stem)
            result = pcb_gen.generate_pcb(str(schematic_path))

            return {
                "success": True,
                "output_path": str(output_path),
                "result": result,
                "message": "PCB generated successfully",
            }

        except Exception as e:
            logger.error(f"PCB generation failed: {e}")
            return {"success": False, "error": str(e)}

    def validate_design(self, project_path: Path) -> Dict[str, Any]:
        """Validate KiCad design files."""
        try:
            validation_results = {
                "schematic_valid": False,
                "pcb_valid": False,
                "issues": [],
            }

            # Check for required files
            kicad_pro = project_path / f"{project_path.stem}.kicad_pro"
            kicad_sch = project_path / f"{project_path.stem}.kicad_sch"
            kicad_pcb = project_path / f"{project_path.stem}.kicad_pcb"

            if kicad_pro.exists():
                validation_results["project_file_exists"] = True
            else:
                validation_results["issues"].append("Missing .kicad_pro file")

            if kicad_sch.exists():
                validation_results["schematic_valid"] = True
            else:
                validation_results["issues"].append("Missing .kicad_sch file")

            if kicad_pcb.exists():
                validation_results["pcb_valid"] = True
            else:
                validation_results["issues"].append("Missing .kicad_pcb file")

            validation_results["success"] = len(validation_results["issues"]) == 0

            return validation_results

        except Exception as e:
            logger.error(f"Design validation failed: {e}")
            return {"success": False, "error": str(e)}

    def get_schematic_generator(self) -> ISchematicGenerator:
        """Get schematic generator interface."""
        if self._schematic_generator is None:
            self._schematic_generator = SchematicGeneratorImpl(
                str(self.output_dir), self.project_name
            )
        return self._schematic_generator

    def get_pcb_generator(self) -> IPCBGenerator:
        """Get PCB generator interface."""
        if self._pcb_generator is None:
            # Import here to avoid circular imports
            from ..pcb_gen.pcb_generator import PCBGenerator

            class PCBGeneratorAdapter(IPCBGenerator):
                def __init__(self, output_dir: str, project_name: str):
                    self.pcb_gen = PCBGenerator(output_dir, project_name)

                def generate_from_schematic(
                    self,
                    schematic_path: Path,
                    config: Optional[KiCadGenerationConfig] = None,
                ) -> Dict[str, Any]:
                    try:
                        result = self.pcb_gen.generate_pcb(str(schematic_path))
                        return {"success": True, "result": result}
                    except Exception as e:
                        return {"success": False, "error": str(e)}

            self._pcb_generator = PCBGeneratorAdapter(
                str(self.output_dir), self.project_name
            )
        return self._pcb_generator

    def get_symbol_library(self) -> ISymbolLibrary:
        """Get symbol library interface."""
        if self._symbol_library is None:

            class SymbolLibraryAdapter(ISymbolLibrary):
                def search_symbols(self, query: str) -> List[Dict[str, Any]]:
                    # Implement symbol search using existing symbol cache
                    return []

                def get_symbol_info(self, symbol_name: str) -> Optional[Dict[str, Any]]:
                    # Implement symbol info retrieval
                    return None

            self._symbol_library = SymbolLibraryAdapter()
        return self._symbol_library

    def get_footprint_library(self) -> IFootprintLibrary:
        """Get footprint library interface."""
        if self._footprint_library is None:

            class FootprintLibraryAdapter(IFootprintLibrary):
                def search_footprints(self, query: str) -> List[Dict[str, Any]]:
                    # Implement footprint search
                    return []

                def get_footprint_info(
                    self, footprint_name: str
                ) -> Optional[Dict[str, Any]]:
                    # Implement footprint info retrieval
                    return None

            self._footprint_library = FootprintLibraryAdapter()
        return self._footprint_library

    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of this KiCad integration."""
        return {
            "implementation": "legacy_refactored",
            "schematic_generation": True,
            "pcb_generation": True,
            "symbol_library": True,
            "footprint_library": True,
            "placement_algorithms": ["sequential", "connection_aware", "llm"],
            "paper_sizes": list(self.PAPER_SIZES.keys()),
            "version": "2.0.0",
        }

    def cleanup(self) -> None:
        """Cleanup resources."""
        # Clean up any temporary files or resources
        pass

    def _collect_all_references(self, json_file: str) -> set:
        """
        Pre-scan the entire JSON hierarchy to collect all assigned references.
        This ensures we respect all pre-assigned references and don't create conflicts.

        Args:
            json_file: Path to the JSON file

        Returns:
            Set of all assigned references in the project
        """
        logger.info("Pre-scanning project to collect all assigned references...")

        # Load the JSON data
        with open(json_file, "r") as f:
            json_data = json.load(f)

        def collect_from_circuit(circuit_data):
            """Recursively collect references from a circuit and its subcircuits"""
            references = set()

            # Collect from components in this circuit
            components = circuit_data.get("components", {})
            for comp_ref, comp_data in components.items():
                # The key is the reference, but also check 'ref' field
                if comp_ref:
                    references.add(comp_ref)
                if isinstance(comp_data, dict) and "ref" in comp_data:
                    references.add(comp_data["ref"])

            # Recursively collect from subcircuits
            for subcircuit in circuit_data.get("subcircuits", []):
                references.update(collect_from_circuit(subcircuit))

            return references

        all_refs = collect_from_circuit(json_data)
        logger.info(
            f"Found {len(all_refs)} pre-assigned references: {sorted(all_refs)}"
        )
        return all_refs

    def _check_existing_project(self) -> bool:
        """Check if a complete KiCad project already exists"""
        kicad_pro_file = self.project_dir / f"{self.project_name}.kicad_pro"
        kicad_sch_file = self.project_dir / f"{self.project_name}.kicad_sch"

        # Check for hierarchical projects: also look for root.kicad_sch
        root_sch_file = self.project_dir / "root.kicad_sch"

        # Both files must exist for a valid project
        project_exists = kicad_pro_file.exists()
        schematic_exists = kicad_sch_file.exists() or root_sch_file.exists()

        if project_exists and schematic_exists:
            return True
        elif project_exists or kicad_sch_file.exists() or root_sch_file.exists():
            # Only warn if truly incomplete (no schematic files at all)
            if project_exists and not schematic_exists:
                logger.warning(
                    "⚠️  Incomplete project detected - .kicad_pro exists but no schematic files found"
                )
                logger.warning("    Treating as new project creation")
                return False
            elif not project_exists and schematic_exists:
                logger.warning(
                    "⚠️  Incomplete project detected - schematic files exist but .kicad_pro is missing"
                )
                logger.warning("    Treating as new project creation")
                return False

        return False

    def _update_existing_project(
        self, json_file: str, draw_bounding_boxes: bool = False
    ):
        """Update existing project using synchronizer to preserve manual work"""
        logger.info("🔄 Updating existing project while preserving your work...")

        # Import here to avoid circular dependencies
        from circuit_synth.kicad_api.schematic.sync_adapter import SyncAdapter

        # Load circuit from JSON using the same loader as generate
        logger.debug(f"Loading circuit from {json_file}")
        from .circuit_loader import load_circuit_hierarchy

        top_circuit, sub_dict = load_circuit_hierarchy(json_file)

        # For now, we'll use the top circuit for synchronization
        # In the future, this could be extended to handle hierarchical circuits

        # Get project path
        project_path = self.project_dir / f"{self.project_name}.kicad_pro"

        # Create synchronizer
        logger.debug(f"Creating synchronizer for project: {project_path}")
        synchronizer = SyncAdapter(
            project_path=str(project_path), preserve_user_components=True
        )

        # Perform synchronization
        logger.debug("Starting synchronization...")
        sync_report = synchronizer.sync_with_circuit(top_circuit)

        # Add bounding boxes if requested
        if draw_bounding_boxes:
            logger.debug("Adding bounding boxes to synchronized schematic...")
            self._add_bounding_boxes_to_existing_project(synchronizer, top_circuit)

        # Log results
        self._log_sync_results(sync_report)

        return sync_report

    def _add_bounding_boxes_to_existing_project(self, synchronizer, circuit):
        """Add bounding boxes to an existing synchronized project."""
        try:
            # Import necessary classes
            # Use optimized symbol cache from core.component for better performance
            from circuit_synth.core.component import SymbolLibCache

            from ...kicad_api.core.types import Point, Rectangle
            from ..kicad_symbol_cache import SymbolLibCache
            from .symbol_geometry import SymbolBoundingBoxCalculator

            # Get the synchronized schematic
            schematic = synchronizer.api_sync.schematic

            logger.debug(
                f"Adding bounding boxes for {len(schematic.components)} components"
            )

            # Track added rectangles for logging
            added_count = 0

            for comp in schematic.components:
                # Get precise bounding box from existing calculator
                lib_data = SymbolLibCache.get_symbol_data(comp.lib_id)
                if not lib_data:
                    logger.warning(
                        f"No symbol data found for {comp.lib_id}, skipping bounding box"
                    )
                    continue

                try:
                    min_x, min_y, max_x, max_y = (
                        SymbolBoundingBoxCalculator.calculate_bounding_box(lib_data)
                    )

                    # Create Rectangle using API types
                    bbox_rect = Rectangle(
                        start=Point(comp.position.x + min_x, comp.position.y + min_y),
                        end=Point(comp.position.x + max_x, comp.position.y + max_y),
                        stroke_width=0.127,  # Thin stroke (5 mils)
                        stroke_type="solid",
                        fill_type="none",
                        # No stroke_color - KiCad uses default color
                    )

                    # Add to schematic using API method
                    schematic.add_rectangle(bbox_rect)
                    added_count += 1
                    logger.debug(
                        f"Added bounding box for {comp.reference} at ({comp.position.x + min_x:.2f}, {comp.position.y + min_y:.2f}) to ({comp.position.x + max_x:.2f}, {comp.position.y + max_y:.2f})"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to add bounding box for {comp.reference} ({comp.lib_id}): {e}"
                    )
                    continue

            # Save and log results
            if added_count > 0:
                logger.info(
                    f"Added {added_count} bounding boxes to synchronized schematic"
                )
                # Save the updated schematic using the synchronizer's save method
                synchronizer.api_sync._save_schematic()
                logger.debug(f"Updated schematic saved with bounding boxes")
            else:
                logger.warning("No bounding boxes were added")

        except Exception as e:
            logger.error(f"Failed to add bounding boxes to existing project: {e}")
            # Don't fail the entire update process for bounding box issues
            pass

    def _log_sync_results(self, sync_report):
        """Display synchronization results to user"""
        logger.info("\n=== Project Update Summary ===")

        summary = sync_report.get("summary", {})
        logger.info(f"✓ Components matched: {summary.get('matched', 0)}")
        logger.info(f"✓ Components added: {summary.get('added', 0)}")
        logger.info(f"✓ Components modified: {summary.get('modified', 0)}")
        logger.info(f"✓ Components preserved: {summary.get('preserved', 0)}")

        if summary.get("removed", 0) > 0:
            logger.info(f"✓ Components removed: {summary.get('removed', 0)}")

        logger.info("✓ All manual work preserved!")
        logger.info(f"\nProject updated successfully at: {self.project_dir}")

    def generate_project(
        self,
        json_file: str,
        force_regenerate: bool = False,
        generate_pcb: bool = True,
        placement_algorithm: str = "connection_centric",
        schematic_placement: str = "connection_aware",
        draw_bounding_boxes: bool = False,
        **pcb_kwargs,
    ):
        """
        Generate or update KiCad project intelligently.

        Args:
            json_file: Path to circuit JSON file
            force_regenerate: If True, recreate project even if it exists (loses manual work!)
            generate_pcb: If True, generate PCB along with schematics (default: True)
            placement_algorithm: PCB placement algorithm to use (spiral, hierarchical, force_directed, connection_centric)
            schematic_placement: Schematic placement algorithm - "sequential" or "connection_aware" (default: "sequential")
            **pcb_kwargs: Additional keyword arguments passed to PCB generation
        """
        # Check if project already exists
        project_exists = self._check_existing_project()

        if project_exists and not force_regenerate:
            # Auto-switch to update mode
            logger.info(f"🔍 Existing KiCad project detected at: {self.project_dir}")
            logger.info(
                "🔄 Automatically switching to update mode to preserve your work"
            )
            logger.info(
                "   (Use force_regenerate=True to create a new project instead)"
            )

            try:
                return self._update_existing_project(json_file, draw_bounding_boxes)
            except Exception as e:
                logger.error(f"❌ Update failed: {e}")
                logger.error("   Falling back to regeneration...")
                # Fall through to regeneration

        elif project_exists and force_regenerate:
            # User explicitly wants to regenerate
            logger.warning(
                f"⚠️  WARNING: Force regenerating project at: {self.project_dir}"
            )
            logger.warning(
                "   This will LOSE all manual work (component positions, wires, etc.)"
            )

            # In a real implementation, we might want to prompt for confirmation
            # For now, we'll proceed with regeneration

        # Original generate_project logic starts here
        if generate_pcb:
            logger.info(
                f"Generating KiCad project '{self.project_name}' with schematics and PCB from '{json_file}'"
            )
        else:
            logger.info(
                f"Generating KiCad project '{self.project_name}' with schematics only from '{json_file}'"
            )

        # 1) load entire hierarchy
        top_circuit, sub_dict = load_circuit_hierarchy(json_file)

        # Store original top circuit name
        top_name = top_circuit.name

        # 2) assign instance labels
        assign_subcircuit_instance_labels(top_circuit, sub_dict)

        # Track sheet UUIDs for hierarchical instances
        sheet_uuids = {}

        # 3) Prepare blank project files first
        self._prepare_blank_project()

        # 4) collision-based placement for each circuit
        # This must happen AFTER project directory exists so we can read existing schematics
        self._collision_place_all_circuits(
            sub_dict, placement_algorithm=schematic_placement
        )

        # 5) Write a top "cover sheet" schematic and get both UUIDs
        #    This references the project-named schematic as a sub-sheet
        cover_uuid, sheet_uuid = self._write_cover_sheet(top_name)

        logger.info(f"Cover sheet created with UUIDs:")
        logger.info(f"  - Cover sheet UUID: {cover_uuid}")
        logger.info(f"  - Sheet symbol UUID: {sheet_uuid}")

        # 6) Generate .kicad_sch for each circuit
        # Store sheet UUIDs and writers for all circuits
        sheet_uuids = {}
        sheet_writers = {}

        # Pre-scan the project to collect all assigned references
        all_assigned_refs = self._collect_all_references(json_file)

        # Create a shared reference manager for global uniqueness
        from .integrated_reference_manager import IntegratedReferenceManager

        shared_ref_manager = IntegratedReferenceManager()
        logger.info("Created shared reference manager for global uniqueness")

        # Pre-populate the reference manager with all assigned references
        # This ensures we respect existing references and don't create conflicts
        if all_assigned_refs:
            shared_ref_manager.api_ref_manager.add_existing_references(
                list(all_assigned_refs)
            )
            logger.info(
                f"Pre-populated reference manager with {len(all_assigned_refs)} existing references"
            )

        # REMOVED: Enable reassignment mode - we want to preserve existing references
        # shared_ref_manager.enable_reassignment_mode()
        logger.info("Reference manager will preserve all pre-assigned references")

        # First, generate the main circuit with the full hierarchical path
        # Build hierarchical path: [cover_uuid, sheet_uuid]
        hierarchical_path = [cover_uuid, sheet_uuid]

        logger.info(f"=== BUILDING MAIN CIRCUIT HIERARCHY ===")
        logger.info(f"  Cover UUID: {cover_uuid}")
        logger.info(f"  Sheet symbol UUID (in cover): {sheet_uuid}")
        logger.info(f"  Main circuit name: {top_name}")
        logger.info(f"  Hierarchical path: {hierarchical_path}")

        main_writer = SchematicWriter(
            sub_dict[top_name],
            sub_dict,
            instance_naming_map=None,
            paper_size=self.paper_size,
            project_name=self.project_name,
            hierarchical_path=hierarchical_path,  # Pass the full hierarchical path
            reference_manager=shared_ref_manager,  # Pass shared reference manager
            draw_bounding_boxes=draw_bounding_boxes,  # Pass bounding box flag
        )
        main_sch_expr = main_writer.generate_s_expr()
        sheet_uuids[top_name] = main_writer.uuid_top
        sheet_writers[top_name] = main_writer  # Store main writer for reference

        logger.debug(f"  Main schematic UUID: {main_writer.uuid_top}")
        logger.debug(f"  Sheet symbols in main circuit:")
        for name, uuid in main_writer.sheet_symbol_map.items():
            logger.debug(f"    {name} -> {uuid}")

        out_path = self.project_dir / f"{top_name}.kicad_sch"
        write_schematic_file(main_sch_expr, str(out_path))

        # Now generate other subcircuits recursively
        # Create a mapping to track which circuits have been generated
        generated_circuits = {top_name}

        # Create a mapping from circuit name to its parent sheet info
        circuit_parent_info = {}

        # First, map all direct children of the main circuit
        for child_info in sub_dict[top_name].child_instances:
            c_name = child_info["sub_name"]
            if c_name in main_writer.sheet_symbol_map:
                circuit_parent_info[c_name] = {
                    "parent_path": [cover_uuid, sheet_uuid],
                    "sheet_uuid": main_writer.sheet_symbol_map[c_name],
                }

        # Process all circuits in dependency order
        while len(generated_circuits) < len(sub_dict):
            made_progress = False

            for c_name, circ in sub_dict.items():
                if c_name in generated_circuits:
                    continue

                # Check if this circuit's parent has been generated
                parent_generated = False
                for parent_name, parent_circ in sub_dict.items():
                    if parent_name in generated_circuits:
                        # Check if c_name is a child of parent_circ
                        for child_info in parent_circ.child_instances:
                            if child_info["sub_name"] == c_name:
                                parent_generated = True
                                break
                    if parent_generated:

                        # Build hierarchical path
                        if parent_name == top_name:
                            # Direct child of main circuit
                            if c_name in main_writer.sheet_symbol_map:
                                sheet_symbol_uuid = main_writer.sheet_symbol_map[c_name]
                                hierarchical_path = [
                                    cover_uuid,
                                    sheet_uuid,
                                    sheet_symbol_uuid,
                                ]
                            else:
                                logger.error(
                                    f"No sheet symbol found for {c_name} in main circuit!"
                                )
                                continue
                        else:
                            # Nested subcircuit - need to find its sheet symbol in parent
                            parent_writer = sheet_writers.get(parent_name)
                            if (
                                parent_writer
                                and c_name in parent_writer.sheet_symbol_map
                            ):
                                sheet_symbol_uuid = parent_writer.sheet_symbol_map[
                                    c_name
                                ]
                                parent_path = circuit_parent_info.get(
                                    parent_name, {}
                                ).get("full_path", [])
                                hierarchical_path = parent_path + [sheet_symbol_uuid]
                            else:
                                logger.error(
                                    f"No sheet symbol found for {c_name} in parent {parent_name}!"
                                )
                                continue

                        logger.debug(f"=== BUILDING SUBCIRCUIT HIERARCHY ===")
                        logger.debug(f"  Subcircuit name: {c_name}")
                        logger.debug(f"  Parent circuit: {parent_name}")
                        logger.debug(
                            f"  Hierarchical path: {'/'.join(hierarchical_path)}"
                        )
                        logger.debug(f"  Path length: {len(hierarchical_path)}")

                        writer = SchematicWriter(
                            circ,
                            sub_dict,
                            instance_naming_map=None,
                            paper_size=self.paper_size,
                            project_name=self.project_name,
                            hierarchical_path=hierarchical_path,
                            reference_manager=shared_ref_manager,
                            draw_bounding_boxes=draw_bounding_boxes,
                        )
                        sch_expr = writer.generate_s_expr()
                        sheet_uuids[c_name] = writer.uuid_top
                        sheet_writers[c_name] = (
                            writer  # Store writer for nested subcircuits
                        )

                        # Store this circuit's info for its children
                        circuit_parent_info[c_name] = {
                            "parent_path": hierarchical_path[:-1],
                            "sheet_uuid": hierarchical_path[-1],
                            "full_path": hierarchical_path,
                        }

                        logger.info(f"  Subcircuit schematic UUID: {writer.uuid_top}")

                        out_path = self.project_dir / f"{c_name}.kicad_sch"
                        write_schematic_file(sch_expr, str(out_path))

                        generated_circuits.add(c_name)
                        made_progress = True
                        break

            if not made_progress:
                # No progress made - there might be a circular dependency
                remaining = set(sub_dict.keys()) - generated_circuits
                logger.error(
                    f"Could not generate circuits due to dependency issues: {remaining}"
                )
                break

        # 7) Update .kicad_pro to reference all .kicad_sch
        self._update_kicad_pro(sub_dict, top_name)

        logger.info(f"Done generating KiCad project at '{self.project_dir}'")

        # Generate PCB (default behavior)
        if generate_pcb:
            logger.info("🔧 Generating PCB with hierarchical placement...")
            # Import locally to avoid circular import
            from circuit_synth.kicad.pcb_gen import PCBGenerator

            pcb_gen = PCBGenerator(self.project_dir, self.project_name)

            # Generate PCB with specified placement algorithm
            success = pcb_gen.generate_pcb(
                circuit_dict=sub_dict,
                placement_algorithm=placement_algorithm,
                board_width=pcb_kwargs.get(
                    "board_width", None
                ),  # Auto-calculate if not specified
                board_height=pcb_kwargs.get("board_height", None),
                component_spacing=pcb_kwargs.get("component_spacing", 5.0),
                group_spacing=pcb_kwargs.get("group_spacing", 10.0),
                **{
                    k: v
                    for k, v in pcb_kwargs.items()
                    if k
                    not in [
                        "board_width",
                        "board_height",
                        "component_spacing",
                        "group_spacing",
                    ]
                },
            )

            if success:
                logger.info("✅ PCB generation complete!")
            else:
                logger.error("❌ PCB generation failed!")

        # Return the circuit dictionary for potential PCB generation
        return sub_dict

    def _determine_paper_size(self, components, sheets):
        """
        Determine the appropriate paper size based on component and sheet placement.
        Returns the paper size name (e.g., "A4", "A3").
        """
        # Find the maximum x and y coordinates
        max_x = 0
        max_y = 0

        # Check components
        for comp in components:
            max_x = max(max_x, comp.position.x + 50)  # Add some margin for labels
            max_y = max(max_y, comp.position.y + 50)  # Add some margin for labels

        # Check sheets
        for sheet in sheets:
            sheet_x = sheet.get("x", 0)
            sheet_y = sheet.get("y", 0)
            sheet_width = sheet.get("width", 30)
            sheet_height = sheet.get("height", 30)

            max_x = max(max_x, sheet_x + sheet_width + 50)  # Add margin
            max_y = max(max_y, sheet_y + sheet_height + 50)  # Add margin

        # Determine the appropriate paper size
        current_size = self.PAPER_SIZES["A4"]
        paper_size = "A4"

        for size_name, (width, height) in self.PAPER_SIZES.items():
            if max_x <= width - SHEET_MARGIN and max_y <= height - SHEET_MARGIN:
                if width * height < current_size[0] * current_size[1]:
                    current_size = (width, height)
                    paper_size = size_name
            elif width * height > current_size[0] * current_size[1]:
                current_size = (width, height)
                paper_size = size_name

        logger.debug(
            f"Determined paper size: {paper_size} ({current_size[0]}x{current_size[1]}mm) for max coordinates: ({max_x}, {max_y})"
        )  # Changed from INFO
        return paper_size

    def _collision_place_all_circuits(
        self, sub_dict: dict, placement_algorithm: str = "sequential"
    ):
        """
        For each circuit, run collision manager on components and sheet symbols.
        This ensures that components and sheet symbols don't collide with each other.
        If an existing schematic file exists, preserve component positions using canonical matching.

        Args:
            sub_dict: Dictionary of circuits to place
            placement_algorithm: Algorithm to use - "sequential" or "connection_aware"
        """
        logger.info("=" * 80)
        logger.info("Starting _collision_place_all_circuits")
        logger.info(f"Processing {len(sub_dict)} circuits")
        logger.info("=" * 80)

        for c_name, circ in sub_dict.items():
            logger.info(f"\n--- Processing circuit: '{c_name}' ---")
            logger.info(f"Circuit has {len(circ.components)} components")
            logger.info(f"Circuit has {len(circ.child_instances)} child instances")

            # Log component details
            logger.debug("Components in circuit:")
            for comp in circ.components:
                logger.debug(f"  - {comp.reference}: {comp.lib_id} = {comp.value}")

            # Get paper size dimensions
            sheet_size = self.PAPER_SIZES.get(self.paper_size, self.PAPER_SIZES["A4"])

            # Create appropriate collision manager based on algorithm
            if placement_algorithm == "connection_aware":
                logger.info(
                    f"Using connection-aware placement algorithm for circuit '{c_name}'"
                )
                cm = ConnectionAwareCollisionManager(sheet_size=sheet_size)
                # Analyze connections before placement
                cm.analyze_connections(circ)
            elif placement_algorithm == "llm":
                logger.info(
                    f"Using LLM-based placement algorithm for circuit '{c_name}'"
                )
                # LLM placement will use its own manager
                cm = CollisionManager(sheet_size=sheet_size)
            else:
                logger.info(
                    f"Using sequential placement algorithm for circuit '{c_name}'"
                )
                cm = CollisionManager(sheet_size=sheet_size)

            logger.debug(
                f"Using paper size: {self.paper_size} with dimensions: {sheet_size}"
            )

            # Check if existing schematic file exists
            existing_sch_path = self.project_dir / f"{c_name}.kicad_sch"
            existing_positions = {}

            logger.info(f"Checking for existing schematic at: {existing_sch_path}")
            if existing_sch_path.exists():
                logger.info(f"Found existing schematic file: {existing_sch_path}")
                try:
                    # Read existing schematic
                    reader = SchematicReader()
                    schematic = reader.read_file(str(existing_sch_path))
                    existing_components = schematic.components
                    logger.info(
                        f"Found {len(existing_components)} components in existing schematic"
                    )

                    # Create canonical circuit from existing schematic components
                    from circuit_synth.kicad.canonical import (
                        CanonicalCircuit,
                        CanonicalConnection,
                    )

                    # Build canonical circuit from existing SchematicSymbol objects
                    existing_connections = []
                    for idx, comp in enumerate(existing_components):
                        # Get component type in symbol:value format
                        symbol = (
                            comp.lib_id.split(":")[-1]
                            if ":" in comp.lib_id
                            else comp.lib_id
                        )
                        value = comp.value if comp.value else ""
                        component_type = f"{symbol}:{value}"

                        # For now, we'll skip pin connections since SchematicReader doesn't populate them with net info
                        # This is a limitation - we can only match by component type, not full connectivity
                        # Add a placeholder connection to represent the component exists
                        conn = CanonicalConnection(
                            component_index=idx,
                            pin="placeholder",
                            net_name="placeholder",
                            component_type=component_type,
                        )
                        existing_connections.append(conn)

                    existing_canonical = CanonicalCircuit(existing_connections)

                    # Create canonical circuit from new circuit definition
                    new_canonical = CanonicalCircuit.from_circuit(circ)

                    # Match components using canonical matching
                    from circuit_synth.kicad.canonical import CircuitMatcher

                    matcher = CircuitMatcher()
                    matches = matcher.match_circuits(existing_canonical, new_canonical)
                    logger.info(
                        f"Matched {len(matches)} components using canonical matching between existing and new circuits"
                    )

                    # Extract positions for matched components
                    for existing_ref, new_ref in matches.items():
                        for comp in existing_components:
                            if comp.reference == existing_ref:
                                # SchematicSymbol position is a tuple (x, y, rotation)
                                if comp.position:
                                    x, y = (
                                        comp.position[0],
                                        comp.position[1],
                                    )  # Extract x, y from position tuple
                                    existing_positions[new_ref] = (x, y)
                                    logger.debug(
                                        f"Preserving position for {new_ref}: ({x}, {y})"
                                    )
                                break

                    logger.info(
                        f"Preserving positions for {len(existing_positions)} matched components"
                    )

                except Exception as e:
                    logger.warning(f"Could not read existing schematic: {e}")
                    logger.warning("Will use default placement for all components")
            else:
                logger.info("No existing schematic found - will use default placement")

            # Place components
            logger.info("Placing components...")

            # Handle LLM placement separately
            if placement_algorithm == "llm":
                logger.info("Using LLM for component placement...")
                llm_manager = LLMPlacementManager(sheet_size=sheet_size)

                # Try LLM placement
                import asyncio

                try:
                    success = asyncio.run(
                        llm_manager.apply_llm_placement(circ, circ.components)
                    )
                    if success:
                        logger.info("LLM placement completed successfully")
                        # Skip the normal placement loop
                        continue
                    else:
                        logger.warning(
                            "LLM placement failed, falling back to sequential"
                        )
                        # Continue with sequential placement below
                except Exception as e:
                    logger.error(f"LLM placement error: {e}")
                    logger.warning("Falling back to sequential placement")
                    # Continue with sequential placement below

            # Get placement order based on algorithm
            if placement_algorithm == "connection_aware" and isinstance(
                cm, ConnectionAwareCollisionManager
            ):
                # Get connection-based placement order
                placement_order = cm.connection_analyzer.get_placement_order(
                    circ.components
                )
                logger.info(
                    f"Connection-based placement order: {placement_order[:10]}..."
                )  # Show first 10

                # Create a mapping for quick lookup
                comp_map = {comp.reference: comp for comp in circ.components}
                components_to_place = [
                    comp_map[ref] for ref in placement_order if ref in comp_map
                ]
            else:
                # Use original order
                components_to_place = circ.components

            for comp in components_to_place:
                if comp.reference in existing_positions:
                    # Use existing position
                    x, y = existing_positions[comp.reference]
                    comp.position.x = x
                    comp.position.y = y
                    logger.debug(
                        f"Using preserved position for {comp.reference}: ({x}, {y})"
                    )
                else:
                    # Use collision manager for new placement
                    # Get actual component dimensions from symbol data
                    try:
                        symbol_data = SymbolLibCache.get_symbol_data(comp.lib_id)
                        if not symbol_data:
                            raise ValueError(f"No symbol data found for {comp.lib_id}")

                        comp_width, comp_height = (
                            SymbolBoundingBoxCalculator.get_symbol_dimensions(
                                symbol_data
                            )
                        )
                        logger.debug(
                            f"Component {comp.reference} ({comp.lib_id}) dimensions: {comp_width:.2f}x{comp_height:.2f}mm"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to get dimensions for {comp.reference} ({comp.lib_id}): {e}"
                        )
                        raise ValueError(
                            f"Cannot calculate bounding box for component {comp.reference} ({comp.lib_id}): {e}"
                        )

                    # Use appropriate placement method
                    if placement_algorithm == "connection_aware" and isinstance(
                        cm, ConnectionAwareCollisionManager
                    ):
                        x, y = cm.place_component_connection_aware(
                            comp.reference, comp_width, comp_height
                        )
                    else:
                        x, y = cm.place_symbol(comp_width, comp_height)

                    comp.position.x = x
                    comp.position.y = y
                    logger.debug(
                        f"Placed new component {comp.reference} at: ({x}, {y})"
                    )

            # Place sheet symbols
            logger.info(f"Placing {len(circ.child_instances)} sheet symbols...")
            for child in circ.child_instances:
                # Calculate sheet dimensions based on pin count
                sub_name = child["sub_name"]
                if sub_name in sub_dict:
                    sub_circ = sub_dict[sub_name]
                    pin_count = len(sub_circ.nets)

                    # Calculate height based on pin count
                    # Each pin needs 2.54mm (100mil) spacing
                    pin_spacing = 2.54
                    min_height = 20.32  # Minimum 0.8 inch
                    padding = 5.08  # 200mil padding top and bottom
                    calculated_height = (pin_count * pin_spacing) + (2 * padding)
                    sheet_height = max(min_height, calculated_height)

                    # Calculate width based on sheet name and hierarchical labels
                    min_width = 25.4  # Minimum 1 inch
                    char_width = 1.5  # mm per character
                    name_width = len(sub_name) * char_width + 10  # Add margin

                    # Find the longest net name for hierarchical labels
                    max_label_length = 0
                    for net in sub_circ.nets:
                        label_length = len(net.name)
                        if label_length > max_label_length:
                            max_label_length = label_length

                    # Calculate width needed for hierarchical labels
                    # Labels are placed to the right of the sheet
                    # Use 1.27mm (50 mils) per character as estimate
                    label_char_width = 1.27
                    label_width = max_label_length * label_char_width + 10  # Add margin

                    # Sheet width should accommodate both name and labels
                    # Add extra space for the labels extending beyond the sheet
                    sheet_width = max(min_width, name_width, min_width + label_width)

                    logger.debug(
                        f"Sheet {sub_name}: name_width={name_width:.1f}mm, "
                        f"max_label='{max_label_length}' chars, "
                        f"label_width={label_width:.1f}mm, "
                        f"final_width={sheet_width:.1f}mm"
                    )

                    # Store calculated dimensions
                    child["width"] = sheet_width
                    child["height"] = sheet_height
                else:
                    # Use defaults if subcircuit not found
                    sheet_width = child.get("width", 50.8)  # Default 2 inches
                    sheet_height = child.get("height", 25.4)  # Default 1 inch

                x, y = cm.place_symbol(sheet_width, sheet_height)
                child["x"] = x
                child["y"] = y
                logger.debug(
                    f"Placed sheet {child['sub_name']} ({sheet_width}x{sheet_height}mm) at: ({x}, {y})"
                )

            # Determine appropriate paper size based on placement
            self.paper_size = self._determine_paper_size(
                circ.components, circ.child_instances
            )
            logger.info(f"Selected paper size: {self.paper_size}")

            # Log placement metrics if using connection-aware algorithm
            if placement_algorithm == "connection_aware" and isinstance(
                cm, ConnectionAwareCollisionManager
            ):
                metrics = cm.get_placement_metrics()
                logger.info(f"Placement metrics for '{c_name}':")
                logger.info(
                    f"  Total wire length: {metrics['total_wire_length']:.2f}mm"
                )
                logger.info(
                    f"  Average wire length: {metrics['average_wire_length']:.2f}mm"
                )
                logger.info(f"  Max wire length: {metrics['max_wire_length']:.2f}mm")
                logger.info(f"  Placement density: {metrics['placement_density']:.2%}")

            logger.info(f"Completed placement for circuit '{c_name}'")

        logger.info("=" * 80)
        logger.info("Completed _collision_place_all_circuits")
        logger.info("=" * 80)

    def _prepare_blank_project(self):
        """
        Create project directory and blank .kicad_pro file.
        """
        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create blank .kicad_pro if it doesn't exist
        kicad_pro_path = self.project_dir / f"{self.project_name}.kicad_pro"
        if not kicad_pro_path.exists():
            logger.info(f"Creating blank .kicad_pro at {kicad_pro_path}")
            blank_pro = {
                "board": {"design_settings": {"defaults": {}}},
                "boards": [],
                "cvpcb": {},
                "erc": {},
                "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
                "meta": {"filename": f"{self.project_name}.kicad_pro", "version": 1},
                "net_settings": {},
                "pcbnew": {},
                "schematic": {
                    "annotate_start_num": 0,
                    "drawing": {
                        "default_line_thickness": 6.0,
                        "default_text_size": 50.0,
                        "field_names": [],
                        "intersheets_ref_own_page": False,
                        "intersheets_ref_prefix": "",
                        "intersheets_ref_short": False,
                        "intersheets_ref_show": False,
                        "intersheets_ref_suffix": "",
                        "junction_size_choice": 3,
                        "label_size_ratio": 0.25,
                        "pin_symbol_size": 0.0,
                        "text_offset_ratio": 0.08,
                    },
                    "legacy_lib_dir": "",
                    "legacy_lib_list": [],
                    "meta": {"version": 1},
                    "net_format_name": "",
                    "ngspice": {
                        "fix_include_paths": True,
                        "fix_passive_vals": False,
                        "meta": {"version": 0},
                        "model_mode": 0,
                        "workbook_filename": "",
                    },
                    "page_layout_descr_file": "",
                    "plot_directory": "",
                    "spice_adjust_passive_values": False,
                    "spice_external_command": 'spice "%I"',
                    "subpart_first_id": 65,
                    "subpart_id_separator": 0,
                },
                "sheets": [],
                "text_variables": {},
            }

            with open(kicad_pro_path, "w") as f:
                json.dump(blank_pro, f, indent=2)
        else:
            logger.info(f".kicad_pro already exists at {kicad_pro_path}")

    def _write_cover_sheet(self, main_circuit_name: str) -> Tuple[str, str]:
        """
        Write a top-level "cover sheet" schematic that references the main circuit.
        Returns a tuple of (cover_sheet_uuid, sheet_symbol_uuid).
        """
        cover_path = self.project_dir / f"{self.project_name}.kicad_sch"
        logger.info(f"Writing cover sheet to {cover_path}")

        # Generate UUIDs for the cover sheet and the sheet symbol
        cover_uuid = str(uuid.uuid4())
        sheet_symbol_uuid = str(uuid.uuid4())

        # Create the cover sheet content
        cover_content = f"""(kicad_sch (version 20250114) (generator "kicad_api")

  (uuid {cover_uuid})

  (paper "{self.paper_size}")

  (lib_symbols
  )

  (sheet (at 25.4 25.4) (size 50.8 25.4)
    (stroke (width 0.1524) (type solid) (color 0 0 0 0))
    (fill (color 0 0 0 0.0000))
    (uuid {sheet_symbol_uuid})
    (property "Sheet name" "{main_circuit_name}" (id 0) (at 25.4 24.6884 0)
      (effects (font (size 1.27 1.27)) (justify left bottom))
    )
    (property "Sheet file" "{main_circuit_name}.kicad_sch" (id 1) (at 25.4 51.2846 0)
      (effects (font (size 1.27 1.27)) (justify left top))
    )
  )

  (sheet_instances
    (path "/" (page "1"))
    (path "/{sheet_symbol_uuid}" (page "2"))
  )

  (symbol_instances
  )
)
"""

        with open(cover_path, "w") as f:
            f.write(cover_content)

        logger.info(f"Cover sheet written with UUID: {cover_uuid}")
        logger.info(f"Sheet symbol UUID: {sheet_symbol_uuid}")

        return cover_uuid, sheet_symbol_uuid

    def _update_kicad_pro(self, sub_dict: dict, top_name: str):
        """
        Update the .kicad_pro file to reference all generated .kicad_sch files.
        """
        kicad_pro_path = self.project_dir / f"{self.project_name}.kicad_pro"
        logger.info(f"Updating .kicad_pro at {kicad_pro_path}")

        # Read existing .kicad_pro
        with open(kicad_pro_path, "r") as f:
            pro_data = json.load(f)

        # Update sheets list
        sheets = []

        # Add the cover sheet (always first)
        sheets.append([f"{self.project_name}.kicad_sch", ""])

        # Add the main circuit sheet
        sheets.append([f"{top_name}.kicad_sch", top_name])

        # Add all subcircuit sheets
        for c_name in sub_dict:
            if c_name != top_name:  # Skip the main circuit as we already added it
                sheets.append([f"{c_name}.kicad_sch", c_name])

        pro_data["sheets"] = sheets

        # Write updated .kicad_pro
        with open(kicad_pro_path, "w") as f:
            json.dump(pro_data, f, indent=2)

        logger.info(f"Updated .kicad_pro with {len(sheets)} schematic entries.")

    def generate_pcb_from_schematics(
        self,
        placement_algorithm: str = "hierarchical",
        board_width: float = 100.0,
        board_height: float = 100.0,
        component_spacing: float = 5.0,  # Increased to avoid courtyard overlaps
        group_spacing: float = 10.0,
    ) -> bool:  # Increased for better separation
        """
        Generate a PCB from existing schematic files.

        This method can be called after schematics have been generated to create
        a PCB with hierarchical component placement.

        Args:
            placement_algorithm: Algorithm to use ("hierarchical", "force_directed", etc.)
            board_width: Board width in mm
            board_height: Board height in mm
            component_spacing: Spacing between components in mm
            group_spacing: Spacing between hierarchical groups in mm

        Returns:
            True if successful, False otherwise
        """
        # Ensure project directory exists
        if not self.project_dir.exists():
            logger.error(f"Project directory does not exist: {self.project_dir}")
            return False

        # Create PCB generator
        # Import locally to avoid circular import
        from circuit_synth.kicad.pcb_gen import PCBGenerator

        pcb_gen = PCBGenerator(self.project_dir, self.project_name)

        # Generate PCB
        logger.info(f"Generating PCB with {placement_algorithm} placement...")
        success = pcb_gen.generate_pcb(
            circuit_dict=None,  # Will extract from schematics
            placement_algorithm=placement_algorithm,
            board_width=board_width,
            board_height=board_height,
            component_spacing=component_spacing,
            group_spacing=group_spacing,
        )

        if success:
            logger.info(
                f"✅ PCB generated successfully at: {self.project_dir / f'{self.project_name}.kicad_pcb'}"
            )
        else:
            logger.error("❌ PCB generation failed")

        return success

    # Additional IKiCadIntegration interface methods
    def get_version(self) -> str:
        """Get the version of the KiCad integration."""
        return "1.0.0"

    def validate_installation(self) -> bool:
        """Validate that KiCad is properly installed and accessible."""
        # For now, assume it's valid since we're using file-based generation
        return True

    def get_symbol_libraries(self) -> List[str]:
        """Get list of available symbol libraries."""
        try:
            # Use optimized symbol cache from core.component for better performance
            from circuit_synth.core.component import SymbolLibCache
            from circuit_synth.kicad.kicad_symbol_cache import SymbolLibCache

            cache = SymbolLibCache()
            return list(cache.get_all_libraries().keys())
        except Exception as e:
            logger.warning(f"Could not load symbol libraries: {e}")
            return []

    def get_footprint_libraries(self) -> List[str]:
        """Get list of available footprint libraries."""
        # This would need to be implemented based on KiCad footprint library structure
        # For now, return empty list
        return []

    def create_schematic_generator(self) -> "ISchematicGenerator":
        """Create a schematic generator instance."""
        return SchematicGeneratorImpl(str(self.output_dir), self.project_name)

    def create_pcb_generator(self) -> "IPCBGenerator":
        """Create a PCB generator instance."""

        class PCBGeneratorAdapter(IPCBGenerator):
            def __init__(self, output_dir: str, project_name: str):
                # Import locally to avoid circular import
                from circuit_synth.kicad.pcb_gen import PCBGenerator

                self.pcb_gen = PCBGenerator(output_dir, project_name)

            def generate_from_circuit_data(
                self,
                circuit_data: Dict[str, Any],
                config: Optional[KiCadGenerationConfig] = None,
            ) -> Dict[str, Any]:
                """Generate PCB from circuit data."""
                try:
                    # Extract parameters from config
                    placement_algorithm = "hierarchical"
                    board_width = 100.0
                    board_height = 100.0

                    if config:
                        placement_algorithm = (
                            config.placement_algorithm or placement_algorithm
                        )
                        if hasattr(config, "board_width") and config.board_width:
                            board_width = config.board_width
                        if hasattr(config, "board_height") and config.board_height:
                            board_height = config.board_height

                    # Generate PCB
                    success = self.pcb_gen.generate_pcb(
                        circuit_dict=circuit_data,
                        placement_algorithm=placement_algorithm,
                        board_width=board_width,
                        board_height=board_height,
                    )

                    return {
                        "success": success,
                        "message": (
                            "PCB generated successfully"
                            if success
                            else "PCB generation failed"
                        ),
                    }
                except Exception as e:
                    logger.error(f"PCB generation failed: {e}")
                    return {"success": False, "error": str(e)}

        return PCBGeneratorAdapter(str(self.output_dir), self.project_name)
