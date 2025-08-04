# crossroad/core/plots/category_country_sankey.py

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import plotly.colors
import plotly.express as px
import colorsys # Import the colorsys module
import os
import logging
import traceback

logger = logging.getLogger(__name__)

# Helper function removed as Plotly palettes provide hex strings directly.
# Alpha will be added during link color generation.
# --- Plotting Function ---

def create_category_country_sankey(df, output_dir, dynamic_column):
    """
    Creates a publication-quality Sankey diagram visualizing the flow
    of genomes from categories to a dynamic metadata column (e.g., country), 
    with summary statistics and export options.
    Saves outputs to the specified directory.

    Args:
        df (pd.DataFrame): DataFrame containing 'category', the dynamic column, and 'genomeID'.
        output_dir (str): Base directory where plot-specific subdirectories will be created.
        dynamic_column (str): The name of the column to use for the right side of the Sankey.
    """
    plot_name = f"category_{dynamic_column}_sankey"
    logger.info(f"Processing data for {plot_name}...")

    # --- Basic Validation and Type Conversion ---
    required_cols = ['category', dynamic_column, 'genomeID']
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        logger.error(f"{plot_name}: Missing required columns: {missing}")
        raise ValueError(f"Missing required columns: {missing}") # Raise error to stop processing

    df_proc = df[required_cols].dropna().copy()

    # Ensure correct types
    df_proc['category'] = df_proc['category'].astype(str)
    df_proc[dynamic_column] = df_proc[dynamic_column].astype(str)
    df_proc['genomeID'] = df_proc['genomeID'].astype(str)

    if df_proc.empty:
        logger.warning(f"{plot_name}: DataFrame is empty after cleaning/filtering. Cannot generate plot.")
        return # Exit gracefully

    # --- Data Aggregation ---
    logger.info(f"{plot_name}: Aggregating genome counts...")
    link_data = df_proc.groupby(['category', dynamic_column])['genomeID'].nunique().reset_index()
    link_data = link_data[link_data['genomeID'] > 0]

    if link_data.empty:
        logger.warning(f"{plot_name}: No valid links found after aggregation. Cannot generate plot.")
        return # Exit gracefully

    # --- Prepare Nodes and Links for Sankey ---
    logger.info(f"{plot_name}: Preparing nodes and links...")
    unique_categories = sorted(link_data['category'].unique())
    unique_dynamic_values = sorted(link_data[dynamic_column].unique())

    nodes = unique_categories + unique_dynamic_values
    node_map = {name: i for i, name in enumerate(nodes)}

    # --- Assign colors using Plotly palettes ---
    num_categories = len(unique_categories)
    num_dynamic_values = len(unique_dynamic_values)

    # --- Generate Category Colors using HSL ---
    # Generate evenly spaced hues for categories
    category_palette_px = []
    # Fixed saturation and lightness for good visibility
    saturation = 0.7
    lightness = 0.6
    for i in range(num_categories):
        hue = i / num_categories # Distribute hue evenly from 0.0 to 1.0
        # Convert HSL to RGB (values are 0-1)
        rgb_0_1 = colorsys.hls_to_rgb(hue, lightness, saturation)
        # Convert RGB from 0-1 to 0-255
        rgb_0_255 = tuple(int(c * 255) for c in rgb_0_1)
        # Format as 'rgb(r, g, b)' string
        category_palette_px.append(f"rgb({rgb_0_255[0]}, {rgb_0_255[1]}, {rgb_0_255[2]})")
    logger.info(f"Generated {num_categories} HSL-based colors for categories.")

    # --- Generate Dynamic Column Colors using a standard palette ---
    dynamic_palette_px = px.colors.qualitative.Pastel[:num_dynamic_values]
    if len(dynamic_palette_px) < num_dynamic_values: # Handle palette running out
        dynamic_palette_px.extend(px.colors.qualitative.Plotly[:num_dynamic_values - len(dynamic_palette_px)])
        if len(dynamic_palette_px) < num_dynamic_values:
             dynamic_palette_px.extend(['#AAAAAA'] * (num_dynamic_values - len(dynamic_palette_px)))

    # Node colors can be directly assigned from the palettes
    node_colors = category_palette_px + dynamic_palette_px

    # Create source, target, value lists using the node map
    sources = [node_map[cat] for cat in link_data['category']]
    targets = [node_map[val] for val in link_data[dynamic_column]]
    values = link_data['genomeID'].tolist()

    # --- Link colors - color by source (category) node (alpha=0.6) ---
    # Convert hex colors from the palette to rgba strings with alpha
    link_colors_rgba = []
    alpha = 0.6
    for cat in link_data['category']:
        cat_index = unique_categories.index(cat)
        hex_color = category_palette_px[cat_index % len(category_palette_px)]
        # Convert color to RGB tuple, handling both hex and rgb() strings
        # Category palette now reliably contains 'rgb(r, g, b)' strings
        try:
            # Parse the rgb string
            parts = hex_color.strip('rgb()').split(',')
            if len(parts) == 3:
                r, g, b = [int(p.strip()) for p in parts]
                # Format rgba string directly
                link_colors_rgba.append(f"rgba({r}, {g}, {b}, {alpha})")
            else:
                 raise ValueError(f"Could not parse generated RGB string: {hex_color}")
        except Exception as color_err:
             logger.warning(f"Could not process generated color '{hex_color}' for link: {color_err}. Using default grey.")
             # Fallback to grey RGBA
             link_colors_rgba.append(f"rgba(204, 204, 204, {alpha})")

    # --- Calculate Summary Statistics ---
    total_unique_genomes = df_proc['genomeID'].nunique()
    total_links = len(link_data)
    total_flow = sum(values)

    stats = {
        'total_categories': num_categories,
        f'total_{dynamic_column}s': num_dynamic_values,
        'total_unique_genomes': total_unique_genomes,
        'total_links_shown': total_links,
        'total_genome_flow': total_flow,
    }
    logger.info(f"{plot_name}: Summary statistics calculated.")

    # --- Create Sankey Figure ---
    logger.info(f"{plot_name}: Creating plot figure...")
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
            color=node_colors,
            hovertemplate='%{label}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors_rgba,
            hovertemplate='%{source.label} → %{target.label}: %{value} genomes<extra></extra>'
        )
    )])

    # --- Customize Layout ---
    title_text = f"Genome Metadata Visualization (Category → {dynamic_column.replace('_', ' ').title()})"
    base_font_family = "Arial, sans-serif"
    title_font_size = 18
    axis_label_font_size = 12
    tick_font_size = 10
    annotation_font_size = 10
    signature_font_size = 9

    title_font = dict(family=base_font_family, size=title_font_size, color='#333333')
    label_font = dict(family=base_font_family, size=axis_label_font_size, color='#555555')
    tick_font = dict(family=base_font_family, size=tick_font_size, color='#555555')
    annotation_font = dict(family=base_font_family, size=annotation_font_size, color='#333333')
    signature_font = dict(family=base_font_family, size=signature_font_size, color='#888888')

    fixed_left_margin = 80
    fixed_right_margin = 150
    fixed_top_margin = 80
    fixed_bottom_margin = 80

    fig.update_layout(
        title=dict(
            text=f"{title_text}",  # Just the main title text
            x=0.5,
            xanchor='center'
        ),
        font=label_font,
        height=max(700, num_categories * 25, num_dynamic_values * 25),
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=fixed_left_margin, r=fixed_right_margin, t=fixed_top_margin, b=fixed_bottom_margin),
    )

    # --- Add Annotations ---
    stats_lines = ["<b>Summary Stats:</b>",
                   f"Categories: {stats['total_categories']:,}",
                   f"{dynamic_column.replace('_', ' ').title()}: {stats[f'total_{dynamic_column}s']:,}",
                   f"Unique Genomes: {stats['total_unique_genomes']:,}",
                   f"Links Shown: {stats['total_links_shown']:,}",
                   f"Total Flow: {stats['total_genome_flow']:,}"]
    stats_text = "<br>".join(stats_lines)

    fig.add_annotation(
        xref="paper", yref="paper",
        x=1.01, y=0.95,
        text=stats_text,
        showarrow=False,
        font=annotation_font,
        align='left',
        bordercolor="#cccccc",
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(255, 255, 255, 0.8)",
        xanchor='left',
        yanchor='top'
    )

    # Adjust signature position to be lower
    # Signature removed, integrated into title

    # --- Prepare Data for CSV Export ---
    logger.info(f"{plot_name}: Preparing data for CSV export...")
    export_df = link_data.rename(columns={
        'category': 'Source_Category',
        dynamic_column: f'Target_{dynamic_column.title()}',
        'genomeID': 'Genome_Count'
    })

    # --- Create Subdirectory and Save Outputs ---
    plot_specific_dir = os.path.join(output_dir, plot_name)
    try:
        os.makedirs(plot_specific_dir, exist_ok=True)
        logger.info(f"Ensured output directory exists: {plot_specific_dir}")
    except OSError as e:
        logger.error(f"Could not create plot directory {plot_specific_dir}: {e}")
        return # Cannot save if directory creation fails

    logger.info(f"{plot_name}: Saving plot outputs to {plot_specific_dir}...")
    try:
        # HTML (Interactive)
        html_path = os.path.join(plot_specific_dir, f"{plot_name}.html")
        fig.write_html(html_path, include_plotlyjs='cdn')
        logger.info(f"Saved HTML plot to {html_path}")
    except Exception as html_err:
        logger.error(f"Failed to save HTML plot {plot_name}: {html_err}\n{traceback.format_exc()}")

    try:
        # PNG (High Resolution)
        png_path = os.path.join(plot_specific_dir, f"{plot_name}.png")
        fig.write_image(png_path, scale=3)
        logger.info(f"Saved PNG plot to {png_path}")
    except ValueError as img_err:
         logger.error(f"Error saving PNG {plot_name}: {img_err}. Ensure 'kaleido' is installed: pip install -U kaleido")
    except Exception as img_save_err:
         logger.error(f"An unexpected error occurred during PNG saving for {plot_name}: {img_save_err}\n{traceback.format_exc()}")

    # --- Save the export data to CSV ---
    if not export_df.empty:
        try:
            output_csv_path = os.path.join(plot_specific_dir, f'{plot_name}_links.csv')
            export_df.to_csv(output_csv_path, index=False, float_format='%.0f')
            logger.info(f"Link data for {plot_name} saved to: {output_csv_path}")
        except Exception as csv_err:
            logger.error(f"Failed to save CSV data for {plot_name}: {csv_err}\n{traceback.format_exc()}")
    else:
        logger.warning(f"{plot_name}: No export data generated.")

    # --- Save summary stats ---
    if stats:
         try:
             stats_path = os.path.join(plot_specific_dir, f'{plot_name}_summary_statistics.txt')
             with open(stats_path, 'w') as f:
                 f.write(f"Summary Statistics for {plot_name}:\n")
                 f.write("------------------------------------\n")
                 for key, value in stats.items():
                     key_title = key.replace('_', ' ').title()
                     if isinstance(value, (int, np.integer)):
                         f.write(f"{key_title}: {value:,}\n")
                     else:
                          f.write(f"{key_title}: {value}\n")
             logger.info(f"Summary statistics for {plot_name} saved to: {stats_path}")
         except Exception as stats_err:
             logger.error(f"Failed to save summary statistics for {plot_name}: {stats_err}\n{traceback.format_exc()}")

    logger.info(f"{plot_name}: Plot generation and saving complete.")
