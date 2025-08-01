"""
Add quality annotations to a Dataframe

Author: Shahin ABDOUL SOUKOUR - Inria
Maintainer: Shahin ABDOUL SOUKOUR - Inria
"""

import pandas as pd


def add_quality_annotations_to_df(
    context_df, time_series_df, sep="__", assessed_attrs=None
):
    """
    Add NGSI-LD quality annotations to either the context (instance-level)
    or the time series (attribute-level).

    Args:
        context_df (pd.DataFrame): Single-row DataFrame with 'id' and 'type'.
        time_series_df (pd.DataFrame): Flattened time series DataFrame.
        sep (str): Separator used in flattened column names (default: "__").
        assessed_attrs (list of str, optional): List of attributes to annotate.
            If None, annotate the context (instance-level).

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (updated context_df, updated time_series_df)
    """
    # Copy inputs to avoid mutation
    context_df = context_df.copy()
    time_series_df = time_series_df.copy()

    entity_id = context_df.loc[0, "id"]
    entity_type = context_df.loc[0, "type"]

    if assessed_attrs is None:
        # Instance-level annotation → attach to context
        context_df[f"hasQuality{sep}type"] = "Relationship"
        context_df[f"hasQuality{sep}object"] = (
            f"urn:ngsi-ld:DataQualityAssessment:{entity_type}:{entity_id}"
        )
    else:
        # Attribute-level annotation → apply per-attribute, per-row
        for attr in assessed_attrs:
            attr_cols = [
                col for col in time_series_df.columns if col.startswith(f"{attr}{sep}")
            ]
            if not attr_cols:
                raise ValueError(f"Attribute '{attr}' not found in DataFrame.")

            rows_to_annotate = time_series_df[attr_cols].notna().any(axis=1)

            quality_type_col = f"{attr}{sep}hasQuality{sep}type"
            quality_obj_col = f"{attr}{sep}hasQuality{sep}object"

            # Initialize empty columns with None
            time_series_df[quality_type_col] = None
            time_series_df[quality_obj_col] = None

            # Apply values only to relevant rows
            time_series_df.loc[rows_to_annotate, quality_type_col] = "Relationship"
            time_series_df.loc[rows_to_annotate, quality_obj_col] = (
                f"urn:ngsi-ld:DataQualityAssessment:{entity_type}:{entity_id}:{attr}"
            )

    return context_df, time_series_df
