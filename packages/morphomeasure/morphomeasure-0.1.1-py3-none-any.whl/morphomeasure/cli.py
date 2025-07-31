import argparse
import os
import pandas as pd
from morphomeasure.features import features, TAG_LABELS, output_order, summary_logic
from .lmwrapper import LMeasureWrapper

import os
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LM_EXE = os.path.join(PACKAGE_ROOT, "..", "Lm", "Lm.exe")

def abel(df, path_col, contract_col):
    """
    Calculates the mean of the element-wise product of two columns in a DataFrame.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing the data.
        path_col (str): The name of the column representing the 'path' values.
        contract_col (str): The name of the column representing the 'contract' values.

    Returns:
        float or None: The mean of the element-wise product of the specified columns,
                       or None if either column is not present in the DataFrame.
    """
    if path_col in df.columns and contract_col in df.columns:
        p = pd.to_numeric(df[path_col], errors="coerce")
        c = pd.to_numeric(df[contract_col], errors="coerce")
        return (p * c).mean()
    return None

def bapl(df, col):
    """
    Calculates the mean of a specified column in a DataFrame, coercing non-numeric values to NaN.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        col (str): The name of the column to calculate the mean for.

    Returns:
        float or None: The mean of the column as a float if the column exists, otherwise None.
    """
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").mean()
    return None

def main():
    """
    Entry point for the MorphoMeasure CLI.
    Parses command-line arguments to process SWC files and extract morphometric features using L-Measure.
    Supports multiple tags, feature output modes, and customizable directories for input, output, and temporary files.
    Workflow:
        1. Validates input SWC directory and creates output/tmp directories if needed.
        2. For each SWC file:
            - Extracts features for specified tags using L-Measure.
            - Saves branch-by-branch morphometrics and computes summary statistics.
            - Optionally combines features across tags.
        3. Writes summary CSV files for all morphometrics, basal, apical, and glia (as applicable).
        4. Cleans up temporary CSV files.
    Command-line Arguments:
        --tag: List of tags to process (e.g., 3.0 4.0 7.0). Required.
        --features: Output mode ('all', 'branch', 'combined'). Default: 'all'.
        --swc_dir: Directory containing input SWC files. Required.
        --output_dir: Directory to save output features. Required.
        --tmp_dir: Temporary directory for intermediate files. Default: './tmp'.
        --lm_exe_path: Path to L-Measure executable. Default: bundled with package.
    Raises:
        FileNotFoundError: If the input SWC directory does not exist.
    Outputs:
        - Branch morphometrics CSVs per tag and SWC file.
        - Summary CSVs for all morphometrics, basal, apical, and glia (as applicable).
        - Cleans up temporary files after processing.
    """
    parser = argparse.ArgumentParser(description="MorphoMeasure CLI")
    parser.add_argument('--tag', nargs='+', required=True, help='Tags to process (e.g., 3.0 4.0 7.0)')
    parser.add_argument('--features', choices=['all', 'branch', 'combined'], default='all',
                        help='Which outputs to produce: all, branch, or combined')
    parser.add_argument('--swc_dir', required=True, help='Directory with input SWC files')
    parser.add_argument('--output_dir', required=True, help='Directory to save output features')
    parser.add_argument('--tmp_dir', default='tmp', help='Temporary directory (default: ./tmp)')
    parser.add_argument(
    '--lm_exe_path',
    default=DEFAULT_LM_EXE,
    help="Path to L-Measure executable (default: bundled with package)")

    args = parser.parse_args()

    if not os.path.exists(args.swc_dir):
        raise FileNotFoundError(f"Input SWC folder not found: {args.swc_dir}")

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.tmp_dir, exist_ok=True)

    lm = LMeasureWrapper(args.lm_exe_path)
    tags = args.tag
    features_mode = args.features

    all_summaries_combined = {}
    all_summaries = {t: {} for t in tags}

    for swc_filename in os.listdir(args.swc_dir):
        if not swc_filename.endswith(".swc"):
            continue
        swc_path = os.path.join(args.swc_dir, swc_filename)
        swc_base = os.path.splitext(swc_filename)[0]
        per_tag_dfs = {}

        # Branch-by-branch
        if features_mode in ['branch', 'combined']:
            for tag in tags:
                tag_dir = os.path.join(args.output_dir, TAG_LABELS.get(tag, f"tag_{tag}"))
                os.makedirs(tag_dir, exist_ok=True)
                df_tag = lm.extract_features(
                    swc_file=swc_path,
                    features_dict=features,
                    tag=tag
                )
                morpho_outfile = os.path.join(tag_dir, f"Branch_Morphometrics_{swc_base}.csv")
                df_tag.to_csv(morpho_outfile, index=False)
                per_tag_dfs[tag] = df_tag

                # Summary logic
                summary = {}
                for col, (op, out_label) in summary_logic.items():
                    if col in df_tag.columns:
                        col_numeric = pd.to_numeric(df_tag[col], errors="coerce")
                        if op == "sum":
                            summary[out_label] = col_numeric.sum()
                        elif op == "mean":
                            summary[out_label] = col_numeric.mean()
                        elif op == "max":
                            summary[out_label] = col_numeric.max()
                        elif op == "first":
                            summary[out_label] = col_numeric.iloc[0] if not col_numeric.empty else None
                if "EucDistance" in df_tag.columns:
                    summary["Sum_EucDistance"] = pd.to_numeric(df_tag["EucDistance"], errors="coerce").sum()
                if "PathDistance" in df_tag.columns:
                    summary["Sum_PathDistance"] = pd.to_numeric(df_tag["PathDistance"], errors="coerce").sum()
                summary["ABEL"] = abel(df_tag, "Branch_pathlength", "Contraction")
                summary["ABEL_Terminal"] = abel(df_tag, "Branch_pathlength_terminal", "Contraction_terminal")
                summary["ABEL_internal"] = abel(df_tag, "Branch_pathlength_internal", "Contraction_internal")
                summary["BAPL"] = bapl(df_tag, "Branch_pathlength")
                summary["BAPL_Terminal"] = bapl(df_tag, "Branch_pathlength_terminal")
                summary["BAPL_Internal"] = bapl(df_tag, "Branch_pathlength_internal")
                all_summaries[tag][swc_filename] = summary

        # For All_Morphometrics summary
        if features_mode in ['all', 'combined']:
            if features_mode == 'all':
                for tag in tags:
                    df_tag = lm.extract_features(
                        swc_file=swc_path,
                        features_dict=features,
                        tag=tag
                    )
                    per_tag_dfs[tag] = df_tag

                    summary = {}
                    for col, (op, out_label) in summary_logic.items():
                        if col in df_tag.columns:
                            col_numeric = pd.to_numeric(df_tag[col], errors="coerce")
                            if op == "sum":
                                summary[out_label] = col_numeric.sum()
                            elif op == "mean":
                                summary[out_label] = col_numeric.mean()
                            elif op == "max":
                                summary[out_label] = col_numeric.max()
                            elif op == "first":
                                summary[out_label] = col_numeric.iloc[0] if not col_numeric.empty else None
                    if "EucDistance" in df_tag.columns:
                        summary["Sum_EucDistance"] = pd.to_numeric(df_tag["EucDistance"], errors="coerce").sum()
                    if "PathDistance" in df_tag.columns:
                        summary["Sum_PathDistance"] = pd.to_numeric(df_tag["PathDistance"], errors="coerce").sum()
                    summary["ABEL"] = abel(df_tag, "Branch_pathlength", "Contraction")
                    summary["ABEL_Terminal"] = abel(df_tag, "Branch_pathlength_terminal", "Contraction_terminal")
                    summary["ABEL_internal"] = abel(df_tag, "Branch_pathlength_internal", "Contraction_internal")
                    summary["BAPL"] = bapl(df_tag, "Branch_pathlength")
                    summary["BAPL_Terminal"] = bapl(df_tag, "Branch_pathlength_terminal")
                    summary["BAPL_Internal"] = bapl(df_tag, "Branch_pathlength_internal")
                    all_summaries[tag][swc_filename] = summary
            if per_tag_dfs:
                df_combined = pd.concat(list(per_tag_dfs.values()), axis=0, ignore_index=True)
                summary = {}
                for col, (op, out_label) in summary_logic.items():
                    if col in df_combined.columns:
                        col_numeric = pd.to_numeric(df_combined[col], errors="coerce")
                        if op == "sum":
                            summary[out_label] = col_numeric.sum()
                        elif op == "mean":
                            summary[out_label] = col_numeric.mean()
                        elif op == "max":
                            summary[out_label] = col_numeric.max()
                        elif op == "first":
                            summary[out_label] = col_numeric.iloc[0] if not col_numeric.empty else None
                if "EucDistance" in df_combined.columns:
                    summary["Sum_EucDistance"] = pd.to_numeric(df_combined["EucDistance"], errors="coerce").sum()
                if "PathDistance" in df_combined.columns:
                    summary["Sum_PathDistance"] = pd.to_numeric(df_combined["PathDistance"], errors="coerce").sum()
                summary["ABEL"] = abel(df_combined, "Branch_pathlength", "Contraction")
                summary["ABEL_Terminal"] = abel(df_combined, "Branch_pathlength_terminal", "Contraction_terminal")
                summary["ABEL_internal"] = abel(df_combined, "Branch_pathlength_internal", "Contraction_internal")
                summary["BAPL"] = bapl(df_combined, "Branch_pathlength")
                summary["BAPL_Terminal"] = bapl(df_combined, "Branch_pathlength_terminal")
                summary["BAPL_Internal"] = bapl(df_combined, "Branch_pathlength_internal")
                all_summaries_combined[swc_filename] = summary

    # Write All_Morphometrics summaries
    if features_mode in ['all', 'combined'] and all_summaries_combined:
        neuron_names = sorted(all_summaries_combined.keys())
        all_features = output_order

        def build_df_out(result_frames, column_name_func):
            df_out = pd.DataFrame({"Features": all_features})
            for df, neuron in result_frames:
                colname = column_name_func(df, neuron)
                df1 = df.set_index("Features")[df.columns[1]]
                df_out[colname] = df1.reindex(all_features).values
            return df_out

        only_glia = (len(tags) == 1 and tags[0] == "7.0")
        contains_glia = "7.0" in tags

        if set(tags) == {"3.0", "4.0"} and not contains_glia:
            result_frames_combined = []
            for neuron in neuron_names:
                comb = all_summaries_combined[neuron]
                df = pd.DataFrame({"combined": comb})
                df.insert(0, "Features", df.index)
                df.reset_index(drop=True, inplace=True)
                result_frames_combined.append((df, neuron))
            df_out_combined = build_df_out(result_frames_combined, lambda df, n: f"{n.replace('.swc','')}_combined")
            df_out_combined.to_csv(os.path.join(args.output_dir, "All_Morphometrics.csv"), index=False)

            result_frames_basal = []
            for neuron in neuron_names:
                tag_label = TAG_LABELS["3.0"]
                val = all_summaries["3.0"].get(neuron, {})
                df = pd.DataFrame({tag_label: val})
                df.insert(0, "Features", df.index)
                df.reset_index(drop=True, inplace=True)
                result_frames_basal.append((df, neuron))
            df_out_basal = build_df_out(result_frames_basal, lambda df, n: f"{n.replace('.swc','')}_basal_dendrites")
            df_out_basal.to_csv(os.path.join(args.output_dir, "All_Morphometrics_basal.csv"), index=False)

            result_frames_apical = []
            for neuron in neuron_names:
                tag_label = TAG_LABELS["4.0"]
                val = all_summaries["4.0"].get(neuron, {})
                df = pd.DataFrame({tag_label: val})
                df.insert(0, "Features", df.index)
                df.reset_index(drop=True, inplace=True)
                result_frames_apical.append((df, neuron))
            df_out_apical = build_df_out(result_frames_apical, lambda df, n: f"{n.replace('.swc','')}_apical_dendrites")
            df_out_apical.to_csv(os.path.join(args.output_dir, "All_Morphometrics_apical.csv"), index=False)

        else:
            for tag in tags:
                tag_label = TAG_LABELS.get(tag, f"tag_{tag}")
                result_frames = []
                for neuron in neuron_names:
                    val = all_summaries[tag].get(neuron, {})
                    df = pd.DataFrame({tag_label: val})
                    df.insert(0, "Features", df.index)
                    df.reset_index(drop=True, inplace=True)
                    result_frames.append((df, neuron))
                if tag == "3.0":
                    outname = "All_Morphometrics_basal.csv"
                elif tag == "4.0":
                    outname = "All_Morphometrics_apical.csv"
                elif tag == "7.0":
                    outname = "All_Morphometrics_glia.csv"
                else:
                    outname = f"All_Morphometrics_{tag_label}.csv"
                df_out = build_df_out(result_frames, lambda df, n: f"{n.replace('.swc','')}_{tag_label}")
                df_out.to_csv(os.path.join(args.output_dir, outname), index=False)

    # Clean up tmp folder
    for fname in os.listdir(args.tmp_dir):
        if fname.endswith(".csv"):
            try:
                os.remove(os.path.join(args.tmp_dir, fname))
            except Exception:
                pass

if __name__ == "__main__":
    main()
