# morphomeasure/features.py
"""
This module defines feature extraction parameters, tag labels, output order, and summary logic for morphometric analysis.
Attributes:
    features (dict): Maps feature names to their corresponding extraction command strings, with optional {TAG} placeholders for tag-specific features.
    TAG_LABELS (dict): Maps tag values to human-readable labels for different neuronal or glial structures.
    output_order (list): Specifies the order in which features should appear in output summaries or reports.
    summary_logic (dict): Maps feature names to a tuple specifying the aggregation method (e.g., 'sum', 'mean', 'max', 'first') and the corresponding feature key.
Usage:
    - Use `features` to retrieve the extraction command for a given feature.
    - Use `TAG_LABELS` to interpret tag values in feature extraction.
    - Use `output_order` to format output consistently.
    - Use `summary_logic` to determine how to aggregate feature values across samples.
"""

features = {
    "Soma_Surface": "-l1,2,8,1.0 -f0,0,0,10.0",
    "N_stems": "-l1,2,8,{TAG} -f1,0,0,10.0",
    "N_bifs": "-l1,2,8,{TAG} -f2,0,0,10.0",
    "N_branch": "-l1,2,8,{TAG} -f3,0,0,10.0",
    "N_tips": "-l1,2,8,{TAG} -f4,0,0,10.0",
    "Width": "-l1,2,8,{TAG} -f5,0,0,10.0",
    "Height": "-l1,2,8,{TAG} -f6,0,0,10.0",
    "Depth": "-l1,2,8,{TAG} -f7,0,0,10.0",
    "Diameter": "-l1,2,8,{TAG} -f9,0,0,10.0",
    "Length": "-l1,2,8,{TAG} -f11,0,0,10.0",
    "Surface": "-l1,2,8,{TAG} -f12,0,0,10.0",
    "Volume": "-l1,2,8,{TAG} -f14,0,0,10.0",
    "EucDistance": "-l1,2,8,{TAG} -f15,0,0,10.0",
    "PathDistance": "-l1,2,8,{TAG} -f16,0,0,10.0",
    "Branch_Order": "-l1,2,8,{TAG} -f18,0,0,10.0",
    "Branch_pathlength": "-l1,2,8,{TAG} -f23,0,0,10.0",
    "Contraction": "-l1,2,8,{TAG} -f24,0,0,10.0",
    "Fragmentation": "-l1,2,8,{TAG} -f25,0,0,10.0",
    "Partition_asymmetry": "-l1,2,8,{TAG} -f28,0,0,10.0",
    "Pk_classic": "-l1,2,8,{TAG} -f31,0,0,10.0",
    "Bif_ampl_local": "-l1,2,8,{TAG} -f33,0,0,10.0",
    "Bif_ampl_remote": "-l1,2,8,{TAG} -f34,0,0,10.0",
    "Bif_tilt_local": "-l1,2,8,{TAG} -f35,0,0,10.0",
    "Bif_tilt_remote": "-l1,2,8,{TAG} -f36,0,0,10.0",
    "Bif_torque_local": "-l1,2,8,{TAG} -f37,0,0,10.0",
    "Bif_torque_remote": "-l1,2,8,{TAG} -f38,0,0,10.0",
    "Helix": "-l1,2,8,{TAG} -f43,0,0,10.0",
    "Fractal_Dim": "-l1,2,8,{TAG} -f44,0,0,10.0",
    "Branch_pathlength_terminal": "-l1,2,8,{TAG} -l1,2,19,1.0 -f23,0,0,10.0",
    "Contraction_terminal": "-l1,2,8,{TAG} -l1,2,19,1.0 -f24,0,0,10.0",
    "Branch_pathlength_internal": "-l1,2,8,{TAG} -l1,3,19,1.0 -f23,0,0,10.0",
    "Contraction_internal": "-l1,2,8,{TAG} -l1,3,19,1.0 -f24,0,0,10.0"
}

TAG_LABELS = {
    '3.0': 'basal_dendrites',
    '4.0': 'apical_dendrites',
    '7.0': 'glia_processes'
}

output_order = [
    "Soma_Surface", "N_stems", "N_bifs", "N_branch", "N_tips", "Width", "Height", "Depth",
    "Diameter", "Length", "Surface", "Volume",
    "EucDistance", "Sum_EucDistance",
    "PathDistance", "Sum_PathDistance",
    "Branch_Order", "Branch_pathlength", "Contraction", "Fragmentation",
    "Partition_asymmetry", "Pk_classic", "Bif_ampl_local", "Bif_ampl_remote",
    "Bif_tilt_local", "Bif_tilt_remote", "Bif_torque_local", "Bif_torque_remote",
    "Helix", "Fractal_Dim", "ABEL", "ABEL_Terminal", "ABEL_internal",
    "BAPL", "BAPL_Terminal", "BAPL_Internal"
]

# Optional: Export your summary logic as a dictionary (for reuse)
summary_logic = {
    "Soma_Surface":        ("first",   "Soma_Surface"),
    "N_stems":             ("sum",     "N_stems"),
    "N_bifs":              ("sum",     "N_bifs"),
    "N_branch":            ("sum",     "N_branch"),
    "N_tips":              ("sum",     "N_tips"),
    "Width":               ("max",     "Width"),
    "Height":              ("max",     "Height"),
    "Depth":               ("max",     "Depth"),
    "Diameter":            ("mean",    "Diameter"),
    "Length":              ("sum",     "Length"),
    "Surface":             ("sum",     "Surface"),
    "Volume":              ("sum",     "Volume"),
    "EucDistance":         ("max",     "EucDistance"),
    "PathDistance":        ("max",     "PathDistance"),
    "Branch_Order":        ("max",     "Branch_Order"),
    "Branch_pathlength":   ("sum",     "Branch_pathlength"),
    "Contraction":         ("mean",    "Contraction"),
    "Fragmentation":       ("sum",     "Fragmentation"),
    "Partition_asymmetry": ("mean",    "Partition_asymmetry"),
    "Pk_classic":          ("mean",    "Pk_classic"),
    "Bif_ampl_local":      ("mean",    "Bif_ampl_local"),
    "Bif_ampl_remote":     ("mean",    "Bif_ampl_remote"),
    "Bif_tilt_local":      ("mean",    "Bif_tilt_local"),
    "Bif_tilt_remote":     ("mean",    "Bif_tilt_remote"),
    "Bif_torque_local":    ("mean",    "Bif_torque_local"),
    "Bif_torque_remote":   ("mean",    "Bif_torque_remote"),
    "Helix":               ("mean",    "Helix"),
    "Fractal_Dim":         ("mean",    "Fractal_Dim"),
}

