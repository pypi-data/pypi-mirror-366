#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from io import StringIO
import csv
import logging

import pandas as pd

# --- Utility functions ---


def run_cmd(cmd, cwd=None, logger=None):
    """Run a command and raise error if it fails."""
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Stdout: {result.stdout}")
        logger.error(f"Stderr: {result.stderr}")
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result.stdout


def clean_fasta(in_fasta, out_fasta, logger):
    """Run seqtk to generate single-line FASTA then replace illegal chars and
    uppercase.
    """
    # Ensure we have absolute paths
    in_fasta = os.path.abspath(in_fasta)
    out_fasta = os.path.abspath(out_fasta)
    
    logger.info("Running seqtk to generate single-line FASTA...")
    
    # Use a temporary file to hold single-line fasta output
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp1:
        tmp1_name = tmp1.name
    
    # Run seqtk in the directory containing the input file
    work_dir = os.path.dirname(in_fasta)
    try:
        run_cmd(["seqtk", "seq", in_fasta], cwd=work_dir, logger=logger)
        with open(tmp1_name, "w") as outf:
            result = subprocess.run(
                ["seqtk", "seq", in_fasta],
                stdout=outf,
                check=True,
                cwd=work_dir
            )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running seqtk: {e}")
        logger.error(f"Input file exists: {os.path.exists(in_fasta)}")
        logger.error(f"Input file path: {in_fasta}")
        raise
        
    logger.info("Cleaning and formatting FASTA content...")
    with open(tmp1_name) as fin, open(out_fasta, "w") as fout:
        for line in fin:
            if line.startswith(">"):
                fout.write(line)
            else:
                line = line.strip().upper()
                cleaned = re.sub(r"[^AGTCN]", "N", line)
                fout.write(cleaned + "\n")
    os.remove(tmp1_name)
    logger.info("FASTA cleaning completed")


def parse_fasta_stats(fasta_file):
    data = []
    with open(fasta_file) as f:
        genome_id = None
        seq = ""
        for line in f:
            line = line.rstrip()
            if line.startswith(">"):
                if genome_id is not None:
                    data.append(
                        (genome_id, len(seq), seq.count("N"), gc_percentage(seq))
                    )
                genome_id = line[1:]
                seq = ""
            else:
                seq += line
        if genome_id is not None:
            data.append(
                (genome_id, len(seq), seq.count("N"), gc_percentage(seq))
            )
    df = pd.DataFrame(
        data, columns=["genomeID", "length_genome", "N_count", "genome_GC_per"]
    )
    return df


def gc_percentage(seq):
    seq = seq.upper()
    nonN = len(seq) - seq.count("N")
    if nonN > 0:
        return round((seq.count("G") + seq.count("C")) / nonN * 100, 2)
    return 0


def filter_genomes(stats_df, min_len, max_len, max_ns):
    return stats_df.loc[
        (stats_df["length_genome"] >= min_len)
        & (stats_df["length_genome"] <= max_len)
        & (stats_df["N_count"] <= max_ns),
        "genomeID",
    ].tolist()


def extract_filtered_fasta(in_fasta, genome_ids, out_fasta):
    ids_set = set(genome_ids)
    with open(in_fasta) as fin, open(out_fasta, "w") as fout:
        write_seq = False
        for line in fin:
            if line.startswith(">"):
                curr_id = line[1:].strip()
                write_seq = curr_id in ids_set
            if write_seq:
                fout.write(line)


def write_perf_params(mono, di, tri, tetra, penta, hexa, out_params):
    with open(out_params, "w") as f:
        for motif, count in [
            (1, mono),
            (2, di),
            (3, tri),
            (4, tetra),
            (5, penta),
            (6, hexa),
        ]:
            f.write(f"{motif}\t{count}\n")


def reformat_perf(perf_out, reformatted):
    df = pd.read_csv(perf_out, sep="\t", header=None, dtype=str)
    if df.shape[1] < 8:
        raise ValueError("PERF output has fewer than 8 columns")
    df.columns = [f"col{i}" for i in range(1, df.shape[1] + 1)]

    def calc_row(row):
        motif = row["col8"]
        repeat = row["col7"]
        motif_len = len(motif)
        gc_count = motif.upper().count("G") + motif.upper().count("C")
        gc_per = round(gc_count / motif_len * 100, 1)
        at_per = round(100 - gc_per, 1)
        loci = f"({motif}){repeat}"
        try:
            rep = int(repeat)
        except:
            rep = 0
        length_ssr = rep * motif_len
        return pd.Series(
            {
                "genomeID": row["col1"],
                "start": row["col2"],
                "stop": row["col3"],
                "repeat": row["col7"],
                "motif": motif,
                "GC_per": gc_per,
                "AT_per": at_per,
                "length_of_motif": motif_len,
                "loci": loci,
                "length_of_ssr": length_ssr,
            }
        )

    reform_df = df.apply(calc_row, axis=1)
    reform_df.to_csv(reformatted, sep="\t", index=False)


def merge_categories(ssr_file, cat_file, stats_file, out_file):
    """Merge SSR data with category and stats data, handling missing values appropriately."""
    ssr_df = pd.read_csv(ssr_file, sep="\t")
    
    # Read categories file, treating all data as strings to avoid type issues.
    cat_df = pd.read_csv(cat_file, sep="\t", dtype=str)
    
    # If the categories file has fewer than 3 columns, add a default one.
    if len(cat_df.columns) < 3:
        cat_df['optional_category'] = 'undefined'

    stats_df = pd.read_csv(stats_file, sep="\t")
    
    # Merge the dataframes. Pandas will use the column names as they are.
    merged = (ssr_df.merge(cat_df, on="genomeID", how="left")
             .merge(stats_df, on="genomeID", how="left"))
    
    # Handle 'year' column if it exists, otherwise do nothing.
    if 'year' in merged.columns:
        def process_year(year):
            if pd.isna(year) or year == '' or year == 'NA':
                return 'undefined'
            try:
                return str(int(float(year)))
            except (ValueError, TypeError):
                return 'undefined'
        merged['year'] = merged['year'].apply(process_year)

    # Fill NaN values that may have been introduced by the left merge.
    # Get the dynamic column name (it's the 3rd column from cat_df)
    dynamic_col_name = None
    if len(cat_df.columns) >= 3:
        dynamic_col_name = cat_df.columns[2]
        if dynamic_col_name in merged.columns:
            merged[dynamic_col_name].fillna('undefined', inplace=True)

    if 'category' in merged.columns:
        merged['category'].fillna('undefined', inplace=True)
    if 'year' in merged.columns:
        merged['year'].fillna('undefined', inplace=True)
    
    # Write to file with controlled formatting
    merged.to_csv(out_file, sep="\t", index=False, na_rep='undefined')


def generate_locicons(merged_tsv, intrim_dir, logger): # Renamed to intrim_dir
    """Generate locicons.txt file containing conserved motifs."""
    logger.info("Generating locicons list...")
    
    # Read the merged TSV file
    df = pd.read_csv(merged_tsv, sep='\t', header=0)
    
    # Repeat loci based on the "repeat" column
    df['repeated_motif'] = df.apply(lambda row: row['motif'] * int(row['repeat']), axis=1)
    
    # Group by motif and count unique genomeIDs
    motif_counts = df.groupby('repeated_motif')['genomeID'].nunique()
    
    # Find conserved motifs (present in all genomes)
    total_genomes = len(df['genomeID'].unique())
    conserved = motif_counts[motif_counts == total_genomes].index
    
    # Write conserved motifs to file
    locicons_file = os.path.join(intrim_dir, "locicons.txt") # Use renamed variable
    with open(locicons_file, "w") as file:
        for motif in conserved:
            file.write(motif + "\n")
    
    logger.info(f"Generated locicons list at: {locicons_file}")
    return locicons_file


def find_longest_common_substring(strings):
    if not strings:
        return ""
    
    def lcs_between_two(s1, s2):
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        max_length = 0
        ending_index = 0
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                    if dp[i][j] > max_length:
                        max_length = dp[i][j]
                        ending_index = i
        
        return s1[ending_index - max_length:ending_index]
    
    result = strings[0]
    for i in range(1, len(strings)):
        result = lcs_between_two(result, strings[i])
    
    return result


def process_flanking_regions(genome_file, locicons_file, main_out_dir, intrim_dir, thread_count, logger):
    """Process flanking regions and generate pattern summary, saving to main output."""
    logger.info("Processing flanking regions...")

    # Define the output directory for flank files within the main output
    flanks_out_dir = os.path.join(main_out_dir, "flanks")
    os.makedirs(flanks_out_dir, exist_ok=True) # Ensure the directory exists

    # Generate sequences with flanks (still uses intrim for temp file)
    nfile = os.path.join(intrim_dir, "flank_sequences.fa")
    with open(locicons_file, 'r') as fh, open(nfile, 'w') as fh2:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            new_n = 'N' * 10
            fh2.write(f">{line_num}\n{new_n}{line}{new_n}\n")

    # Run seqkit locate, outputting to the new flanks directory
    flanked_tsv = os.path.join(flanks_out_dir, "flanked.tsv") # Save to main/flanks/
    with open(flanked_tsv, 'w') as output_file:
        subprocess.run(
            ['seqkit', 'locate', '-i', '-j', str(thread_count), '-d', '-P', '-f',
             nfile, genome_file],
            stdout=output_file, 
            check=True
        )

    # Process patterns and create summary
    patterns_by_name = {}
    with open(flanked_tsv, 'r') as f:
        next(f)  # Skip header
        for line in f:
            seqID, patternName, pattern, strand, start, end, matched = line.strip().split('\t')
            if patternName not in patterns_by_name:
                patterns_by_name[patternName] = {}
            if seqID not in patterns_by_name[patternName]:
                patterns_by_name[patternName][seqID] = []
            patterns_by_name[patternName][seqID].append(matched)

    # Generate CSV data
    csv_data = []
    excluded_patterns = set(open(locicons_file).read().splitlines())
    
    for pattern_name, genome_patterns in patterns_by_name.items():
        if pattern_name in excluded_patterns:
            continue
        
        total_seqids = len(genome_patterns)
        all_patterns = [p for sublist in genome_patterns.values() for p in sublist]
        common_substring = find_longest_common_substring(all_patterns)
        pattern_size = len(common_substring) if common_substring else 0
        
        if pattern_size >= 14:
            csv_data.append({
                'PatternName': pattern_name,
                'TotalSeqIDs': total_seqids,
                'PatternSize': pattern_size,
                'Pattern': common_substring
            })

    # Write results to CSV in the flanks output directory
    pattern_summary_path = os.path.join(flanks_out_dir, "pattern_summary.csv") # Save to main/flanks/
    with open(pattern_summary_path, 'w', newline='') as f:
        fieldnames = ['PatternName', 'TotalSeqIDs', 'PatternSize', 'Pattern']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)

    # Print pattern count
    total_patterns = len(csv_data)
    logger.info("=" * 50)
    logger.info(f"Total Conserved Patterns found: {total_patterns}")
    logger.info("=" * 50)

    logger.info(f"Generated pattern summary at: {pattern_summary_path}")
    logger.info(f"Generated flanked data at: {flanked_tsv}") # Log flanked file path too
    # Return both paths
    return pattern_summary_path, flanked_tsv


# --- Main pipeline ---


def main(args=None):
    # Get logger from args, or create a default one
    logger = getattr(args, 'logger', logging.getLogger(__name__))
    
    # If args is not provided, parse from command line
    if args is None:
        parser = argparse.ArgumentParser(description="Generate mergedOut.tsv")
        parser.add_argument("--fasta", required=True, help="Path to all_genome.fa")
        parser.add_argument("--cat", required=True, help="Path to genome_categories.tsv")
        parser.add_argument("--mono", type=int, default=10)
        parser.add_argument("--di", type=int, default=6)
        parser.add_argument("--tri", type=int, default=4)
        parser.add_argument("--tetra", type=int, default=3)
        parser.add_argument("--penta", type=int, default=2)
        parser.add_argument("--hexa", type=int, default=2)
        parser.add_argument("--minLen", type=int, default=1000)
        parser.add_argument("--maxLen", type=int, default=10000000)
        parser.add_argument("--unfair", type=int, default=0)
        parser.add_argument("--thread", type=int, default=50)
        parser.add_argument("--out", default="output", help="Output directory")
        parser.add_argument("--tmp", default="intrim", help="Directory for intermediate files") # Keep arg name as tmp for compatibility, default to intrim
        parser.add_argument("--flanks", action="store_true", help="Process flanking regions")
        args = parser.parse_args()
        # Create default logger if running standalone
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

    # Ensure all required attributes exist with defaults if not provided
    if not hasattr(args, 'mono'): args.mono = 10
    if not hasattr(args, 'di'): args.di = 6
    if not hasattr(args, 'tri'): args.tri = 4
    if not hasattr(args, 'tetra'): args.tetra = 3
    if not hasattr(args, 'penta'): args.penta = 2
    if not hasattr(args, 'hexa'): args.hexa = 2
    if not hasattr(args, 'minLen'): args.minLen = 1000
    if not hasattr(args, 'maxLen'): args.maxLen = 10000000
    if not hasattr(args, 'unfair'): args.unfair = 0
    if not hasattr(args, 'thread'): args.thread = 50

    # Use the provided intermediate directory (passed as 'tmp' from CLI/API)
    intrim_dir = args.tmp # Assign the value from args.tmp to intrim_dir
    main_out_dir = args.out # Assign main output directory path

    # Final output will go directly to main output directory
    merged_out_path = os.path.join(main_out_dir, "mergedOut.tsv")
    reformatted_path = os.path.join(intrim_dir, "reformatted.tsv") # Define path for reformatted file

    # Ensure main output and intrim directories exist (API might create them, CLI needs this)
    os.makedirs(main_out_dir, exist_ok=True)
    os.makedirs(intrim_dir, exist_ok=True)

    # 1. Process and clean FASTA.
    cleanFasta = os.path.join(intrim_dir, "clean_genome.fa") # Use renamed variable
    logger.info("Cleaning FASTA...")
    clean_fasta(args.fasta, cleanFasta, logger)

    # 2. Calculate genome statistics.
    logger.info("Calculating genome stats...")
    stats_df = parse_fasta_stats(cleanFasta)
    stats_file = os.path.join(intrim_dir, "genome_stats.tsv") # Use renamed variable
    stats_df.to_csv(stats_file, sep="\t", index=False)

    # Checkpoint 1: Total number of genomes detected
    total_genomes = len(stats_df)
    logger.info(f"Total number of genomes detected: {total_genomes}")

    # 3. Filter genomes.
    logger.info("Filtering genomes...")
    good_ids = filter_genomes(stats_df, args.minLen, args.maxLen, args.unfair)
    filteredFasta = os.path.join(intrim_dir, "filtered_genomes.fa") # Use renamed variable
    extract_filtered_fasta(cleanFasta, good_ids, filteredFasta)

    # Checkpoint 2: No of genomes removed
    genomes_removed = total_genomes - len(good_ids)
    logger.info(f"No of genomes removed: {genomes_removed}")

    # Checkpoint 3: No of clean genomes used for comparison
    logger.info(f"No of clean genomes used for comparison: {len(good_ids)}")

    # 4. Write PERF parameters.
    params_file = os.path.join(intrim_dir, "perf_params.txt") # Use renamed variable
    write_perf_params(
        args.mono, args.di, args.tri, args.tetra, args.penta, args.hexa, params_file
    )

    # 5. Run PERF in the intermediate files directory.
    perf_out = os.path.join(intrim_dir, "perf_out.tsv") # Use renamed variable
    logger.info("Running PERF...")
    run_cmd(
        [
            "PERF",
            "-i",
            os.path.abspath(filteredFasta),
            "-o",
            os.path.abspath(perf_out),
            "-u",
            os.path.abspath(params_file),
            "-t",
            str(args.thread),
        ],
        cwd=intrim_dir, # Use renamed variable
        logger=logger
    )

    # 6. Reformat PERF output.
    # reformatted path defined earlier
    reformat_perf(perf_out, reformatted_path)

    # Checkpoint 4: No of SSRs Detected in total Genomes
    try:
        ssr_df = pd.read_csv(reformatted_path, sep="\t")
        total_ssrs = len(ssr_df)
        logger.info(f"No of SSRs Detected in total Genomes: {total_ssrs}")
    except FileNotFoundError:
        logger.error("PERF output not found. No SSRs detected.")
    except pd.errors.EmptyDataError:
        logger.error("PERF output is empty. No SSRs detected.")

    # --- Conditional Steps based on Category File ---
    locicons_file = None
    pattern_summary_path = None # Initialize path variables
    flanked_tsv_path = None
    final_output_file = reformatted_path # Default to reformatted if no categories

    if args.cat and os.path.exists(args.cat):
        logger.info("Category file provided. Proceeding with merging and further analysis.")
        # 7. Merge with metadata.
        merge_categories(reformatted_path, args.cat, stats_file, merged_out_path)
        logger.info(f"Merged output generated at: {merged_out_path}")
        final_output_file = merged_out_path # Update final output

        # 8. Generate locicons list (only if merged data exists)
        locicons_file = generate_locicons(merged_out_path, intrim_dir, logger)

        # 9. Process flanking regions if requested (only if locicons were generated)
        if hasattr(args, 'flanks') and args.flanks and locicons_file:
            # Pass main_out_dir to the function now
            pattern_summary_path, flanked_tsv_path = process_flanking_regions(
                cleanFasta,  # Use the cleaned FASTA file
                locicons_file,
                main_out_dir, # Pass main output dir
                intrim_dir,
                args.thread,
                logger
            )
        elif hasattr(args, 'flanks') and args.flanks:
             logger.warning("Flanking region processing skipped as locicons file was not generated (likely due to missing category data).")

    else:
        logger.info("Category file not provided or not found. Skipping merge, locicons, and flanking region analysis.")
        # The main output is reformatted.tsv in this case.
        # locicons_file and pattern_summary remain None.

    # Return all relevant file paths
    # Return the path to the main output file (either merged or reformatted)
    # and the paths to locicons and pattern summary if they were generated.
    # Flanked TSV path is generated but not explicitly returned by main() currently.
    return final_output_file, locicons_file, pattern_summary_path


if __name__ == "__main__":
    main()
