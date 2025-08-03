"""
Parameter configuration panel for HBAT analysis.

This module provides the GUI components for configuring analysis parameters
such as distance cutoffs, angle thresholds, and analysis modes.
"""

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from ..constants import ParameterRanges
from ..constants.parameters import ParametersDefault
from ..core.analysis import AnalysisParameters


class ParameterPanel:
    """Panel for configuring analysis parameters.

    This class provides a GUI interface for setting all analysis parameters
    including distance cutoffs, angle thresholds, and analysis modes.
    Supports parameter presets and real-time validation.

    :param parent: Parent widget to contain this panel
    :type parent: tkinter widget
    """

    def __init__(self, parent) -> None:
        """Initialize the parameter panel.

        Creates the complete parameter configuration interface with
        organized sections for different interaction types.

        :param parent: Parent widget (typically a notebook or frame)
        :type parent: tkinter widget
        :returns: None
        :rtype: None
        """
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        self._set_defaults()

    def _create_widgets(self):
        """Create parameter configuration widgets."""
        # Main scrollable frame
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Replace single column with two-column layout
        self._create_two_column_layout(scrollable_frame)

    def _create_two_column_layout(self, parent):
        """Create two-column layout with analysis parameters on left and PDB fixing on right."""
        # Main container for two columns
        columns_frame = ttk.Frame(parent)
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configure grid for equal column sizing
        columns_frame.columnconfigure(0, weight=1)
        columns_frame.columnconfigure(1, weight=1)
        columns_frame.rowconfigure(0, weight=1)

        # Left column - Original analysis parameters
        left_frame = ttk.Frame(columns_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Right column - PDB fixing parameters
        right_frame = ttk.Frame(columns_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # Left column content - Original parameter groups
        self._create_general_parameters(left_frame)
        self._create_hydrogen_bond_parameters(left_frame)
        self._create_halogen_bond_parameters(left_frame)
        self._create_pi_interaction_parameters(left_frame)

        # Right column content - PDB fixing parameters
        self._create_pdb_fixing_parameters(right_frame)

        # Buttons at bottom spanning both columns
        button_frame = ttk.Frame(columns_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        ttk.Button(
            button_frame, text="Reset to Defaults", command=self._set_defaults
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Load Preset...", command=self._load_preset).pack(
            side=tk.LEFT, padx=(20, 5)
        )
        ttk.Button(button_frame, text="Save Preset...", command=self._save_preset).pack(
            side=tk.LEFT, padx=5
        )

    def _create_general_parameters(self, parent):
        """Create general analysis parameters."""
        group = ttk.LabelFrame(parent, text="General Parameters", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # Analysis mode
        ttk.Label(group, text="Analysis Mode:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.analysis_mode = tk.StringVar(value=ParametersDefault.ANALYSIS_MODE)
        mode_frame = ttk.Frame(group)
        mode_frame.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="Complete PDB Analysis",
            variable=self.analysis_mode,
            value="complete",
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            mode_frame,
            text="Local Interactions Only",
            variable=self.analysis_mode,
            value="local",
        ).pack(anchor=tk.W)

        # Covalent bond cutoff factor
        ttk.Label(group, text="Covalent Bond Factor:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.covalent_factor = tk.DoubleVar(
            value=ParametersDefault.COVALENT_CUTOFF_FACTOR
        )
        ttk.Scale(
            group,
            from_=ParameterRanges.MIN_COVALENT_FACTOR,
            to=ParameterRanges.MAX_COVALENT_FACTOR,
            variable=self.covalent_factor,
            orient=tk.HORIZONTAL,
            length=200,
        ).grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        # Value display
        factor_label = ttk.Label(group, text="")
        factor_label.grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)

        def update_factor_label(*args):
            factor_label.config(text=f"{self.covalent_factor.get():.2f}")

        self.covalent_factor.trace("w", update_factor_label)
        update_factor_label()

    def _create_pdb_fixing_parameters(self, parent):
        """Create PDB structure fixing parameters."""
        # Add title label at top
        title_label = ttk.Label(
            parent, text="PDB Structure Fixing", font=("TkDefaultFont", 10, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Main container frame
        group = ttk.Frame(parent, padding=10)
        group.pack(fill=tk.X, padx=5, pady=5)

        # Enable/disable PDB fixing
        self.fix_pdb_enabled = tk.BooleanVar(value=ParametersDefault.FIX_PDB_ENABLED)
        ttk.Checkbutton(
            group,
            text="Enable PDB structure fixing",
            variable=self.fix_pdb_enabled,
            command=self._on_fix_pdb_enabled_changed,
        ).pack(anchor=tk.W, pady=2)

        # Method selection
        method_section = ttk.Frame(group)
        method_section.pack(fill=tk.X, pady=5)

        ttk.Label(method_section, text="Fixing Method:").pack(anchor=tk.W, pady=2)
        self.fix_pdb_method = tk.StringVar(value=ParametersDefault.FIX_PDB_METHOD)

        method_frame = ttk.Frame(method_section)
        method_frame.pack(anchor=tk.W, padx=20)

        ttk.Radiobutton(
            method_frame,
            text="OpenBabel",
            variable=self.fix_pdb_method,
            value="openbabel",
            command=self._on_fix_method_changed,
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            method_frame,
            text="PDBFixer",
            variable=self.fix_pdb_method,
            value="pdbfixer",
            command=self._on_fix_method_changed,
        ).pack(anchor=tk.W)

        # Operations group
        operations_frame = ttk.LabelFrame(group, text="Fixing Operations", padding=5)
        operations_frame.pack(fill=tk.X, pady=10)

        # Add hydrogens (available for both methods)
        self.fix_pdb_add_hydrogens = tk.BooleanVar(
            value=ParametersDefault.FIX_PDB_ADD_HYDROGENS
        )
        self.fix_hydrogens_cb = ttk.Checkbutton(
            operations_frame,
            text="Add missing hydrogen atoms",
            variable=self.fix_pdb_add_hydrogens,
        )
        self.fix_hydrogens_cb.pack(anchor=tk.W, pady=1)

        # Add heavy atoms (PDBFixer only)
        self.fix_pdb_add_heavy_atoms = tk.BooleanVar(
            value=ParametersDefault.FIX_PDB_ADD_HEAVY_ATOMS
        )
        self.fix_heavy_atoms_cb = ttk.Checkbutton(
            operations_frame,
            text="Add missing heavy atoms (PDBFixer only)",
            variable=self.fix_pdb_add_heavy_atoms,
        )
        self.fix_heavy_atoms_cb.pack(anchor=tk.W, pady=1)

        # Replace nonstandard residues (PDBFixer only)
        self.fix_pdb_replace_nonstandard = tk.BooleanVar(
            value=ParametersDefault.FIX_PDB_REPLACE_NONSTANDARD
        )
        self.fix_nonstandard_cb = ttk.Checkbutton(
            operations_frame,
            text="Replace nonstandard residues (PDBFixer only)",
            variable=self.fix_pdb_replace_nonstandard,
        )
        self.fix_nonstandard_cb.pack(anchor=tk.W, pady=1)

        # Remove heterogens (PDBFixer only)
        self.fix_pdb_remove_heterogens = tk.BooleanVar(
            value=ParametersDefault.FIX_PDB_REMOVE_HETEROGENS
        )
        self.fix_heterogens_cb = ttk.Checkbutton(
            operations_frame,
            text="Remove heterogens (PDBFixer only)",
            variable=self.fix_pdb_remove_heterogens,
            command=self._on_remove_heterogens_changed,
        )
        self.fix_heterogens_cb.pack(anchor=tk.W, pady=1)

        # Keep water (sub-option for remove heterogens)
        self.fix_pdb_keep_water = tk.BooleanVar(
            value=ParametersDefault.FIX_PDB_KEEP_WATER
        )
        self.fix_keep_water_cb = ttk.Checkbutton(
            operations_frame,
            text="    ↳ Keep water molecules",
            variable=self.fix_pdb_keep_water,
        )
        self.fix_keep_water_cb.pack(anchor=tk.W, pady=1, padx=20)

        # Initialize widget states
        self._update_fix_pdb_widget_states()

    def _on_fix_pdb_enabled_changed(self):
        """Handle PDB fixing enable/disable changes."""
        self._update_fix_pdb_widget_states()

    def _on_fix_method_changed(self):
        """Handle PDB fixing method changes."""
        self._update_fix_pdb_widget_states()

    def _on_remove_heterogens_changed(self):
        """Handle remove heterogens option changes."""
        self._update_fix_pdb_widget_states()

    def _update_fix_pdb_widget_states(self):
        """Update the state of PDB fixing widgets based on current selections."""
        enabled = self.fix_pdb_enabled.get()
        method = self.fix_pdb_method.get()
        remove_heterogens = self.fix_pdb_remove_heterogens.get()

        # Enable/disable all operations based on main enable checkbox
        widgets_to_toggle = [
            self.fix_hydrogens_cb,
            self.fix_heavy_atoms_cb,
            self.fix_nonstandard_cb,
            self.fix_heterogens_cb,
            self.fix_keep_water_cb,
        ]

        for widget in widgets_to_toggle:
            widget.config(state=tk.NORMAL if enabled else tk.DISABLED)

        # PDBFixer-only options - disable for OpenBabel
        pdbfixer_only_widgets = [
            self.fix_heavy_atoms_cb,
            self.fix_nonstandard_cb,
            self.fix_heterogens_cb,
        ]

        if enabled and method == "openbabel":
            for widget in pdbfixer_only_widgets:
                widget.config(state=tk.DISABLED)

        # Keep water option - only available if remove heterogens is checked
        if enabled and method == "pdbfixer":
            self.fix_keep_water_cb.config(
                state=tk.NORMAL if remove_heterogens else tk.DISABLED
            )

    def _create_hydrogen_bond_parameters(self, parent):
        """Create hydrogen bond analysis parameters."""
        group = ttk.LabelFrame(parent, text="Hydrogen Bond Parameters", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # Distance cutoff (H...A)
        ttk.Label(group, text="H...A Distance Cutoff (Å):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.hb_distance = tk.DoubleVar(value=ParametersDefault.HB_DISTANCE_CUTOFF)
        distance_frame = ttk.Frame(group)
        distance_frame.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Scale(
            distance_frame,
            from_=ParameterRanges.MIN_DISTANCE,
            to=ParameterRanges.MAX_DISTANCE,
            variable=self.hb_distance,
            orient=tk.HORIZONTAL,
            length=150,
        ).pack(side=tk.LEFT)

        dist_label = ttk.Label(distance_frame, text="")
        dist_label.pack(side=tk.LEFT, padx=5)

        def update_dist_label(*args):
            dist_label.config(text=f"{self.hb_distance.get():.1f}")

        self.hb_distance.trace("w", update_dist_label)
        update_dist_label()

        # Angle cutoff (D-H...A)
        ttk.Label(group, text="D-H...A Angle Cutoff (°):").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.hb_angle = tk.DoubleVar(value=ParametersDefault.HB_ANGLE_CUTOFF)
        angle_frame = ttk.Frame(group)
        angle_frame.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Scale(
            angle_frame,
            from_=ParameterRanges.MIN_ANGLE,
            to=ParameterRanges.MAX_ANGLE,
            variable=self.hb_angle,
            orient=tk.HORIZONTAL,
            length=150,
        ).pack(side=tk.LEFT)

        angle_label = ttk.Label(angle_frame, text="")
        angle_label.pack(side=tk.LEFT, padx=5)

        def update_angle_label(*args):
            angle_label.config(text=f"{self.hb_angle.get():.0f}")

        self.hb_angle.trace("w", update_angle_label)
        update_angle_label()

        # Donor-Acceptor distance cutoff
        ttk.Label(group, text="D...A Distance Cutoff (Å):").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.da_distance = tk.DoubleVar(value=ParametersDefault.HB_DA_DISTANCE)
        da_frame = ttk.Frame(group)
        da_frame.grid(row=2, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Scale(
            da_frame,
            from_=ParameterRanges.MIN_DISTANCE,
            to=ParameterRanges.MAX_DISTANCE,
            variable=self.da_distance,
            orient=tk.HORIZONTAL,
            length=150,
        ).pack(side=tk.LEFT)

        da_label = ttk.Label(da_frame, text="")
        da_label.pack(side=tk.LEFT, padx=5)

        def update_da_label(*args):
            da_label.config(text=f"{self.da_distance.get():.1f}")

        self.da_distance.trace("w", update_da_label)
        update_da_label()

    def _create_halogen_bond_parameters(self, parent):
        """Create halogen bond analysis parameters."""
        group = ttk.LabelFrame(parent, text="Halogen Bond Parameters", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # Distance cutoff
        ttk.Label(group, text="X...A Distance Cutoff (Å):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.xb_distance = tk.DoubleVar(value=ParametersDefault.XB_DISTANCE_CUTOFF)
        xb_dist_frame = ttk.Frame(group)
        xb_dist_frame.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Scale(
            xb_dist_frame,
            from_=ParameterRanges.MIN_DISTANCE,
            to=ParameterRanges.MAX_DISTANCE,
            variable=self.xb_distance,
            orient=tk.HORIZONTAL,
            length=150,
        ).pack(side=tk.LEFT)

        xb_dist_label = ttk.Label(xb_dist_frame, text="")
        xb_dist_label.pack(side=tk.LEFT, padx=5)

        def update_xb_dist_label(*args):
            xb_dist_label.config(text=f"{self.xb_distance.get():.1f}")

        self.xb_distance.trace("w", update_xb_dist_label)
        update_xb_dist_label()

        # Angle cutoff (C-X...A)
        ttk.Label(group, text="C-X...A Angle Cutoff (°):").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.xb_angle = tk.DoubleVar(value=ParametersDefault.XB_ANGLE_CUTOFF)
        xb_angle_frame = ttk.Frame(group)
        xb_angle_frame.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Scale(
            xb_angle_frame,
            from_=ParameterRanges.MIN_ANGLE,
            to=ParameterRanges.MAX_ANGLE,
            variable=self.xb_angle,
            orient=tk.HORIZONTAL,
            length=150,
        ).pack(side=tk.LEFT)

        xb_angle_label = ttk.Label(xb_angle_frame, text="")
        xb_angle_label.pack(side=tk.LEFT, padx=5)

        def update_xb_angle_label(*args):
            xb_angle_label.config(text=f"{self.xb_angle.get():.0f}")

        self.xb_angle.trace("w", update_xb_angle_label)
        update_xb_angle_label()

    def _create_pi_interaction_parameters(self, parent):
        """Create π interaction analysis parameters."""
        group = ttk.LabelFrame(
            parent, text="X-H...π Interaction Parameters", padding=10
        )
        group.pack(fill=tk.X, padx=10, pady=5)

        # Distance cutoff
        ttk.Label(group, text="H...π Distance Cutoff (Å):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.pi_distance = tk.DoubleVar(value=ParametersDefault.PI_DISTANCE_CUTOFF)
        pi_dist_frame = ttk.Frame(group)
        pi_dist_frame.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Scale(
            pi_dist_frame,
            from_=ParameterRanges.MIN_DISTANCE,
            to=ParameterRanges.MAX_DISTANCE,
            variable=self.pi_distance,
            orient=tk.HORIZONTAL,
            length=150,
        ).pack(side=tk.LEFT)

        pi_dist_label = ttk.Label(pi_dist_frame, text="")
        pi_dist_label.pack(side=tk.LEFT, padx=5)

        def update_pi_dist_label(*args):
            pi_dist_label.config(text=f"{self.pi_distance.get():.1f}")

        self.pi_distance.trace("w", update_pi_dist_label)
        update_pi_dist_label()

        # Angle cutoff (D-H...π)
        ttk.Label(group, text="D-H...π Angle Cutoff (°):").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.pi_angle = tk.DoubleVar(value=ParametersDefault.PI_ANGLE_CUTOFF)
        pi_angle_frame = ttk.Frame(group)
        pi_angle_frame.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Scale(
            pi_angle_frame,
            from_=ParameterRanges.MIN_ANGLE,
            to=ParameterRanges.MAX_ANGLE,
            variable=self.pi_angle,
            orient=tk.HORIZONTAL,
            length=150,
        ).pack(side=tk.LEFT)

        pi_angle_label = ttk.Label(pi_angle_frame, text="")
        pi_angle_label.pack(side=tk.LEFT, padx=5)

        def update_pi_angle_label(*args):
            pi_angle_label.config(text=f"{self.pi_angle.get():.0f}")

        self.pi_angle.trace("w", update_pi_angle_label)
        update_pi_angle_label()

    def get_parameters(self) -> AnalysisParameters:
        """Get current parameter values as AnalysisParameters object.

        Retrieves all current parameter settings from the GUI controls
        and packages them into an AnalysisParameters object.

        :returns: Current analysis parameters
        :rtype: AnalysisParameters
        """
        return AnalysisParameters(
            hb_distance_cutoff=self.hb_distance.get(),
            hb_angle_cutoff=self.hb_angle.get(),
            hb_donor_acceptor_cutoff=self.da_distance.get(),
            xb_distance_cutoff=self.xb_distance.get(),
            xb_angle_cutoff=self.xb_angle.get(),
            pi_distance_cutoff=self.pi_distance.get(),
            pi_angle_cutoff=self.pi_angle.get(),
            covalent_cutoff_factor=self.covalent_factor.get(),
            analysis_mode=self.analysis_mode.get(),
            # PDB fixing parameters
            fix_pdb_enabled=self.fix_pdb_enabled.get(),
            fix_pdb_method=self.fix_pdb_method.get(),
            fix_pdb_add_hydrogens=self.fix_pdb_add_hydrogens.get(),
            fix_pdb_add_heavy_atoms=self.fix_pdb_add_heavy_atoms.get(),
            fix_pdb_replace_nonstandard=self.fix_pdb_replace_nonstandard.get(),
            fix_pdb_remove_heterogens=self.fix_pdb_remove_heterogens.get(),
            fix_pdb_keep_water=self.fix_pdb_keep_water.get(),
        )

    def set_parameters(self, params: AnalysisParameters) -> None:
        """Set parameter values from AnalysisParameters object.

        Updates all GUI controls to reflect the values in the provided
        AnalysisParameters object.

        :param params: Analysis parameters to set
        :type params: AnalysisParameters
        :returns: None
        :rtype: None
        """
        self.hb_distance.set(params.hb_distance_cutoff)
        self.hb_angle.set(params.hb_angle_cutoff)
        self.da_distance.set(params.hb_donor_acceptor_cutoff)
        self.xb_distance.set(params.xb_distance_cutoff)
        self.xb_angle.set(params.xb_angle_cutoff)
        self.pi_distance.set(params.pi_distance_cutoff)
        self.pi_angle.set(params.pi_angle_cutoff)
        self.covalent_factor.set(params.covalent_cutoff_factor)
        self.analysis_mode.set(params.analysis_mode)

        # PDB fixing parameters
        self.fix_pdb_enabled.set(params.fix_pdb_enabled)
        self.fix_pdb_method.set(params.fix_pdb_method)
        self.fix_pdb_add_hydrogens.set(params.fix_pdb_add_hydrogens)
        self.fix_pdb_add_heavy_atoms.set(params.fix_pdb_add_heavy_atoms)
        self.fix_pdb_replace_nonstandard.set(params.fix_pdb_replace_nonstandard)
        self.fix_pdb_remove_heterogens.set(params.fix_pdb_remove_heterogens)
        self.fix_pdb_keep_water.set(params.fix_pdb_keep_water)

        # Update widget states after setting parameters
        self._update_fix_pdb_widget_states()

    def _set_defaults(self):
        """Reset all parameters to default values."""
        default_params = AnalysisParameters()
        self.set_parameters(default_params)

    def reset_to_defaults(self) -> None:
        """Public method to reset parameters to defaults.

        Resets all parameter controls to their default values as
        defined in the application constants.

        :returns: None
        :rtype: None
        """
        self._set_defaults()

    def _load_preset(self):
        """Load parameter preset from file."""
        try:
            # Get the example presets directory first, fallback to user presets
            example_presets_dir = self._get_example_presets_directory()
            if not os.path.exists(example_presets_dir):
                default_dir = self._get_presets_directory()
            else:
                default_dir = example_presets_dir

            # Open file dialog
            filename = filedialog.askopenfilename(
                title="Load Parameter Preset",
                initialdir=default_dir,
                filetypes=[
                    ("HBAT Preset files", "*.hbat"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*"),
                ],
            )

            if not filename:
                return

            # Load and validate the preset file
            preset_data = self._load_preset_file(filename)
            if preset_data:
                # Apply the loaded parameters
                self._apply_preset_data(preset_data)
                messagebox.showinfo(
                    "Success",
                    f"Preset loaded successfully from:\n{os.path.basename(filename)}",
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset:\n{str(e)}")

    def _save_preset(self):
        """Save current parameters as preset."""
        try:
            # Get current parameters
            params = self.get_parameters()

            # Get the default presets directory
            default_dir = self._get_presets_directory()

            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"hbat_preset_{timestamp}.hbat"

            # Open save dialog
            filename = filedialog.asksaveasfilename(
                title="Save Parameter Preset",
                initialdir=default_dir,
                initialfile=default_filename,
                filetypes=[
                    ("HBAT Preset files", "*.hbat"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*"),
                ],
            )

            if not filename:
                return

            # Add extension if not provided
            if not filename.lower().endswith((".hbat", ".json")):
                filename += ".hbat"

            # Create preset data
            preset_data = self._create_preset_data(params)

            # Save the preset file
            self._save_preset_file(filename, preset_data)
            messagebox.showinfo(
                "Success",
                f"Preset saved successfully to:\n{os.path.basename(filename)}",
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preset:\n{str(e)}")

    def _get_presets_directory(self):
        """Get or create the user presets directory."""
        # Create presets directory in user's home folder
        home_dir = os.path.expanduser("~")
        presets_dir = os.path.join(home_dir, ".hbat", "presets")

        # Create directory if it doesn't exist
        os.makedirs(presets_dir, exist_ok=True)

        return presets_dir

    def _get_example_presets_directory(self):
        """Get the example presets directory relative to the package."""
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to the hbat package root, then to example_presets
        package_root = os.path.dirname(os.path.dirname(current_dir))
        example_presets_dir = os.path.join(package_root, "example_presets")

        return example_presets_dir

    def _create_preset_data(self, params: AnalysisParameters):
        """Create preset data dictionary from parameters."""
        return {
            "format_version": "1.0",
            "application": "HBAT",
            "created": datetime.now().isoformat(),
            "description": "HBAT Analysis Parameters Preset",
            "parameters": {
                "hydrogen_bonds": {
                    "h_a_distance_cutoff": params.hb_distance_cutoff,
                    "dha_angle_cutoff": params.hb_angle_cutoff,
                    "d_a_distance_cutoff": params.hb_donor_acceptor_cutoff,
                },
                "halogen_bonds": {
                    "x_a_distance_cutoff": params.xb_distance_cutoff,
                    "cxa_angle_cutoff": params.xb_angle_cutoff,
                },
                "pi_interactions": {
                    "h_pi_distance_cutoff": params.pi_distance_cutoff,
                    "dh_pi_angle_cutoff": params.pi_angle_cutoff,
                },
                "general": {
                    "covalent_cutoff_factor": params.covalent_cutoff_factor,
                    "analysis_mode": params.analysis_mode,
                },
                "pdb_fixing": {
                    "enabled": params.fix_pdb_enabled,
                    "method": params.fix_pdb_method,
                    "add_hydrogens": params.fix_pdb_add_hydrogens,
                    "add_heavy_atoms": params.fix_pdb_add_heavy_atoms,
                    "replace_nonstandard": params.fix_pdb_replace_nonstandard,
                    "remove_heterogens": params.fix_pdb_remove_heterogens,
                    "keep_water": params.fix_pdb_keep_water,
                },
            },
        }

    def _save_preset_file(self, filename, preset_data):
        """Save preset data to file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(preset_data, f, indent=2, ensure_ascii=False)

    def _load_preset_file(self, filename):
        """Load and validate preset file."""
        with open(filename, "r", encoding="utf-8") as f:
            preset_data = json.load(f)

        # Validate preset data structure
        if not self._validate_preset_data(preset_data):
            raise ValueError("Invalid preset file format")

        return preset_data

    def _validate_preset_data(self, preset_data):
        """Validate the structure of preset data."""
        try:
            # Check for required top-level keys
            required_keys = ["format_version", "parameters"]
            for key in required_keys:
                if key not in preset_data:
                    return False

            # Check parameters structure
            params = preset_data["parameters"]
            required_sections = [
                "hydrogen_bonds",
                "halogen_bonds",
                "pi_interactions",
                "general",
            ]

            for section in required_sections:
                if section not in params:
                    return False

            # Validate hydrogen bond parameters
            hb_params = params["hydrogen_bonds"]
            hb_required = [
                "h_a_distance_cutoff",
                "dha_angle_cutoff",
                "d_a_distance_cutoff",
            ]
            for param in hb_required:
                if param not in hb_params or not isinstance(
                    hb_params[param], (int, float)
                ):
                    return False

            # Validate halogen bond parameters
            xb_params = params["halogen_bonds"]
            xb_required = ["x_a_distance_cutoff", "cxa_angle_cutoff"]
            for param in xb_required:
                if param not in xb_params or not isinstance(
                    xb_params[param], (int, float)
                ):
                    return False

            # Validate π interaction parameters
            pi_params = params["pi_interactions"]
            pi_required = ["h_pi_distance_cutoff", "dh_pi_angle_cutoff"]
            for param in pi_required:
                if param not in pi_params or not isinstance(
                    pi_params[param], (int, float)
                ):
                    return False

            # Validate general parameters
            gen_params = params["general"]
            if "covalent_cutoff_factor" not in gen_params or not isinstance(
                gen_params["covalent_cutoff_factor"], (int, float)
            ):
                return False

            if "analysis_mode" not in gen_params or gen_params["analysis_mode"] not in [
                "complete",
                "local",
            ]:
                return False

            return True

        except (KeyError, TypeError, ValueError):
            return False

    def _apply_preset_data(self, preset_data):
        """Apply loaded preset data to the parameter controls."""
        params = preset_data["parameters"]

        # Apply hydrogen bond parameters
        hb = params["hydrogen_bonds"]
        self.hb_distance.set(hb["h_a_distance_cutoff"])
        self.hb_angle.set(hb["dha_angle_cutoff"])
        self.da_distance.set(hb["d_a_distance_cutoff"])

        # Apply halogen bond parameters
        xb = params["halogen_bonds"]
        self.xb_distance.set(xb["x_a_distance_cutoff"])
        self.xb_angle.set(xb["cxa_angle_cutoff"])

        # Apply π interaction parameters
        pi = params["pi_interactions"]
        self.pi_distance.set(pi["h_pi_distance_cutoff"])
        self.pi_angle.set(pi["dh_pi_angle_cutoff"])

        # Apply general parameters
        gen = params["general"]
        self.covalent_factor.set(gen["covalent_cutoff_factor"])
        self.analysis_mode.set(gen["analysis_mode"])

        # Apply PDB fixing parameters if present
        if "pdb_fixing" in params:
            pdb_fix = params["pdb_fixing"]
            self.fix_pdb_enabled.set(pdb_fix.get("enabled", False))
            self.fix_pdb_method.set(pdb_fix.get("method", "openbabel"))
            self.fix_pdb_add_hydrogens.set(pdb_fix.get("add_hydrogens", True))
            self.fix_pdb_add_heavy_atoms.set(pdb_fix.get("add_heavy_atoms", False))
            self.fix_pdb_replace_nonstandard.set(
                pdb_fix.get("replace_nonstandard", False)
            )
            self.fix_pdb_remove_heterogens.set(pdb_fix.get("remove_heterogens", False))
            self.fix_pdb_keep_water.set(pdb_fix.get("keep_water", True))

        # Update widget states after applying all parameters
        self._update_fix_pdb_widget_states()
