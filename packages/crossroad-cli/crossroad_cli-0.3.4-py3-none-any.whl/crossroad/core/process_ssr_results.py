#!/usr/bin/env python3
import argparse
import os
import pandas as pd
import logging

def group_records(df, logger, dynamic_column):
    """Group records by motif and gene, combining other fields with ':'."""
    # Base columns that are always expected
    columns = ['motif', 'gene', 'genomeID', 'repeat', 'length_of_motif',
               'loci', 'length_of_ssr', 'category', 'year',
               'ssr_position']
    
    # Add the dynamic column if it exists in the dataframe
    if dynamic_column in df.columns:
        columns.append(dynamic_column)
    
    # Filter df to only include columns that actually exist to prevent KeyErrors
    existing_columns = [col for col in columns if col in df.columns]
    
    grouped = df[existing_columns].groupby(['motif', 'gene'], as_index=False)
    merged = grouped.agg(lambda x: ': '.join(map(str, x.unique())))
    merged['repeat_count'] = merged['repeat'].str.count(':') + 1
    merged['genomeID_count'] = merged['genomeID'].str.count(':') + 1
    return merged

def find_variations(motif):
    """Find all circular shifts of a motif."""
    if not isinstance(motif, str):
        motif = str(motif)
    variations = [motif[i:] + motif[:i] for i in range(len(motif))]
    return ', '.join(sorted(variations))

def find_different_repeats(df, reference_id):
    """Find entries with different repeats compared to reference."""
    ref_data = {f"{row['gene']}_{row['loci']}": row['repeat']
                for _, row in df[df['genomeID'] == reference_id].iterrows()}
    different = [row.to_dict() for _, row in df[df['genomeID'] != reference_id].iterrows()
                 if f"{row['gene']}_{row['loci']}" not in ref_data or ref_data[f"{row['gene']}_{row['loci']}"] != row['repeat']]
    return pd.DataFrame(different).sort_values(['gene', 'loci']) if different else pd.DataFrame()

def process_hssr(hotspot_df, ssrcombo_df, logger):
    """Process HSSR data using hotspot records."""
    hotspot_keys = {f"{row['motif']}{row['gene']}:{gid.strip()}"
                    for _, row in hotspot_df.iterrows()
                    for gid in str(row['genomeID']).split(':')}
    hssr_df = ssrcombo_df[ssrcombo_df.apply(
        lambda row: f"{row['motif']}{row['gene']}:{row['genomeID']}" in hotspot_keys, 
        axis=1)]
    logger.info(f"Found {len(hssr_df)} HSSR records")
    return hssr_df

def main(args=None):
    # Setup logging and parse args
    logger = getattr(args, 'logger', logging.getLogger(__name__))
    if args is None:
        parser = argparse.ArgumentParser(description="Process SSR combo file")
        parser.add_argument("--ssrcombo", required=True, help="SSR combo file path")
        parser.add_argument("--jobOut", default="output", help="Output directory")
        parser.add_argument("--reference", help="Reference genome ID")
        parser.add_argument("--tmp", required=True, help="Directory for intermediate files") # Keep arg name as tmp
        parser.add_argument("--min_repeat_count", type=int, default=1, help="Minimum repeat count")
        parser.add_argument("--min_genome_count", type=int, default=4, help="Minimum genome count")
        parser.add_argument("--dynamic_column", required=True, help="Name of the dynamic metadata column.")
        args = parser.parse_args()
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

    # Setup paths
    out_dir = args.jobOut
    intrim_dir = args.tmp # Assign the value from args.tmp to intrim_dir
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(intrim_dir, exist_ok=True) # Use renamed variable
    files = {
        'hssr': os.path.join(out_dir, "hssr_data.csv"),
        'all_vars': os.path.join(intrim_dir, "all_variations.csv"), # Use renamed variable
        'hotspot': os.path.join(intrim_dir, "mutational_hotspot.csv"), # Use renamed variable
        'ref_ssr': None
    }

    # Read input data
    ssrcombo_df = pd.read_csv(args.ssrcombo, sep='\t')
    
    total_unique_genomes = ssrcombo_df['genomeID'].nunique()
    logger.info(f"Total unique genomes found: {total_unique_genomes}")

    if args.reference:
        logger.info(f"\nComparing against reference genome {args.reference}")
        # First, extract reference genome rows
        reference_rows = ssrcombo_df[ssrcombo_df['genomeID'] == args.reference]
        
        # Then get the rows with different repeats
        different_df = find_different_repeats(ssrcombo_df, args.reference)
        
        if not different_df.empty or not reference_rows.empty:
            # Combine reference rows with different rows
            combined_df = pd.concat([reference_rows, different_df]).drop_duplicates()
            
            # Sort by gene and loci for better organization
            combined_df = combined_df.sort_values(['gene', 'loci'])
            
            # Save the combined data
            files['ref_ssr'] = os.path.join(out_dir, "ref_ssr_genecombo.csv")
            combined_df.to_csv(files['ref_ssr'], index=False)
            
            logger.info(f"Found {len(reference_rows)} rows from reference genome")
            logger.info(f"Found {len(different_df)} rows with different repeats")
            logger.info(f"Total rows in combined file: {len(combined_df)}")
            
            # Continue with the rest of the process using just the different rows
            all_records_df = group_records(combined_df, logger, args.dynamic_column)
        else:
            logger.info("No records found")
            return files
    else:
        all_records_df = group_records(ssrcombo_df, logger, args.dynamic_column)

    # Save all variations
    all_records_df.to_csv(files['all_vars'], index=False)

    # Add count columns
    all_records_df['repeat_count'] = all_records_df['repeat'].str.count(':') + 1
    all_records_df['genomeID_count'] = all_records_df['genomeID'].str.count(':') + 1

    # Generate hotspots
    logger.info("\nFiltering mutational hotspot records ...")
    all_records_df['motif_variations'] = all_records_df['motif'].apply(find_variations)
    all_records_df['concat_column'] = all_records_df['gene'].astype(str) + '_' + all_records_df['motif_variations'].astype(str)
    
    # Find group sizes
    group_sizes = all_records_df.groupby('concat_column').size()
    
    # Groups with multiple records
    multiple_record_groups = group_sizes[group_sizes > 1].index

    hotspot_df = all_records_df[all_records_df['concat_column'].isin(multiple_record_groups)]
    


    # Include single-record groups with stricter criteria

    filtered_single_df = all_records_df[
        (all_records_df['genomeID_count'] > args.min_genome_count) & 
        (all_records_df['repeat_count'] > args.min_repeat_count)
    ]
######### Current Logic

    filtered_multi_groups_df = hotspot_df.groupby('concat_column').filter(
        lambda g: g['genomeID_count'].sum() <= total_unique_genomes
    )

    filtered_hotspot_df = filtered_multi_groups_df.copy()    

#########

########## 2nd Logic
    # Find the concat_column values that exist in both DataFrames
    single_concat_values = set(filtered_single_df['concat_column'])
    
    # Extract rows from hotspot_df where concat_column is in single_concat_values
    matching_hotspot_rows = hotspot_df[hotspot_df['concat_column'].isin(single_concat_values)]
    
    # Log the number of matching rows found
    logger.info(f"Found {len(matching_hotspot_rows)} rows in hotspot_df with concat_column matching filtered_single_df")
    
    # Save these matching rows to a CSV file
    matching_csv_path = os.path.join(intrim_dir, "hotspot_single_matches.csv") # Use renamed variable
    matching_hotspot_rows.to_csv(matching_csv_path, index=False)
    logger.info(f"Saved matching rows to: {matching_csv_path}")
#########

    # Save these matching rows to a CSV file
    repeatvariation_path = os.path.join(intrim_dir, "repeatvariation.csv") # Use renamed variable
    filtered_single_df.to_csv(repeatvariation_path, index=False)
    logger.info(f"Saved matching rows to: {repeatvariation_path}")
     # Save these matching rows to a CSV file
    cyclical_path = os.path.join(intrim_dir, "cyclical_variation.csv") # Use renamed variable
    filtered_hotspot_df.to_csv(cyclical_path, index=False)
    logger.info(f"Saved matching rows to: {cyclical_path}")
    
    
    # Combine both
    filtered_hotspot_df = pd.concat([matching_hotspot_rows, filtered_single_df])

    
    # After dropping temporary columns and duplicates:
    filtered_hotspot_df = filtered_hotspot_df.drop(columns=['motif_variations', 'concat_column'])
    filtered_hotspot_df = filtered_hotspot_df.drop_duplicates()

    logger.info(f"Records after filtering: {len(filtered_hotspot_df)}")
    
    # Create a copy for the cleaned version (to keep the original intact for HSSR processing)
    mutational_hotspot_df = filtered_hotspot_df.copy()
    mutational_hotspot_df_path = os.path.join(intrim_dir, "mh_tmp.csv") # Use renamed variable
    mutational_hotspot_df.to_csv(mutational_hotspot_df_path, index=False)
    # Drop the specified columns from the cleaned version
    columns_to_drop = ['genomeID', 'repeat', 'category', 'year', 'ssr_position']
    # Also drop the dynamic column, which is passed as an argument
    if args.dynamic_column in mutational_hotspot_df.columns:
        columns_to_drop.append(args.dynamic_column)

    for col in columns_to_drop:
        if col in mutational_hotspot_df.columns:
            mutational_hotspot_df = mutational_hotspot_df.drop(columns=[col])
    
    # Save the cleaned version to the main output directory
    mutational_hotspot_file = os.path.join(out_dir, "mutational_hotspot.csv")
    mutational_hotspot_df.to_csv(mutational_hotspot_file, index=False)
    logger.info(f"Saved mutational hotspot data (with columns removed) to: {os.path.basename(mutational_hotspot_file)}")
    

    # Process and save HSSR data
    hssr_df = process_hssr(filtered_hotspot_df, ssrcombo_df, logger)

    # --- FIX: Merge dynamic column back into HSSR data ---
    # The dynamic column can be lost during the gc2.py step. We need to re-merge it
    # to ensure it's available for downstream plotting.
    merged_out_path = os.path.join(os.path.dirname(args.ssrcombo), 'mergedOut.tsv')
    if os.path.exists(merged_out_path) and args.dynamic_column not in hssr_df.columns:
        logger.info(f"Re-merging dynamic column '{args.dynamic_column}' from {os.path.basename(merged_out_path)} into HSSR data...")
        try:
            # Read the source of truth for metadata, keeping only unique genome IDs
            metadata_df = pd.read_csv(
                merged_out_path, 
                sep='\t', 
                usecols=['genomeID', args.dynamic_column]
            ).drop_duplicates(subset=['genomeID'])
            
            # Merge it into the hssr_df
            hssr_df = pd.merge(hssr_df, metadata_df, on='genomeID', how='left')
            logger.info(f"Successfully merged dynamic column. HSSR data now has columns: {hssr_df.columns.tolist()}")
        except Exception as e:
            logger.error(f"Failed to re-merge dynamic column into HSSR data: {e}")
    elif not os.path.exists(merged_out_path):
        logger.warning(f"Could not find {merged_out_path} to re-merge dynamic column.")
    else:
        logger.info("Dynamic column already present in HSSR data. No merge needed.")

    hssr_df.to_csv(files['hssr'], index=False)
    
    

    # Log output files
    logger.info("\nOutput files:")
    logger.info(f"Main directory: {out_dir}")
    logger.info(f"1. HSSR Data: {os.path.basename(files['hssr'])}")
    if files['ref_ssr']:
        logger.info(f"2. Reference SSR: {os.path.basename(files['ref_ssr'])}")
    logger.info(f"\nIntermediate files directory: {intrim_dir}") # Use renamed variable
    logger.info(f"1. All variations: {os.path.basename(files['all_vars'])}")
    logger.info(f"2. Mutational hotspots: {os.path.basename(files['hotspot'])}")

    return files

if __name__ == '__main__':
    main()
