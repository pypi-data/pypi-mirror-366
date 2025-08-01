"""
Data Mapper:
To convert the data from the internal formatting (pandas DataFrame) to the NGSI-LD format,
which is the standard adopted within SEDIMARK.

Author: Shahin ABDOUL SOUKOUR - Inria
Maintainer: Shahin ABDOUL SOUKOUR - Inria
"""
from datetime import datetime
import pandas as pd


def data_mapper(
    context_df: pd.DataFrame, time_series_df: pd.DataFrame, sep="__"
) -> dict:
    """
    Maps data from context and time series DataFrames into a structured dictionary format,
    while organizing instance-level quality annotations and grouping attributes from time
    series data. The function ensures proper nesting of "hasQuality" fields, utilizes a
    custom separator for splitting field names, and preserves timestamp data in ISO 8601 format.

    Args:
        context_df (pd.DataFrame): The context DataFrame, expected to contain a single row
            representing context-level metadata.
        time_series_df (pd.DataFrame): The time series DataFrame containing multiple rows,
            with each row representing attribute values observed over time along with
            a timestamp field named "observedAt".
        sep (str): Separator string used to delineate composite field names in the time
            series DataFrame. Default is "__".

    Returns:
        dict: A dictionary containing context-level attributes along with grouped and
        timestamped attribute data from the time series DataFrame.
    """
    # Extract context as dict
    context = context_df.iloc[0].to_dict()

    # Handle instance-level hasQuality annotation from context
    instance_type_key = f"hasQuality{sep}type"
    instance_object_key = f"hasQuality{sep}object"
    if instance_type_key in context and instance_object_key in context:
        if pd.notna(context[instance_type_key]) and pd.notna(
            context[instance_object_key]
        ):
            context["hasQuality"] = {
                "type": context.pop(instance_type_key),
                "object": context.pop(instance_object_key),
            }
        else:
            context.pop(instance_type_key, None)
            context.pop(instance_object_key, None)

    # Prepare time series attribute grouping
    attribute_groups = {}

    for _, row in time_series_df.iterrows():
        ts = row["observedAt"]
        ts_iso = datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%dT%H:%M:%SZ")

        attr_temp = {}

        for col, val in row.items():
            if col == "observedAt":
                continue

            if sep in col:
                attr, field = col.split(sep, 1)
                if attr not in attr_temp:
                    attr_temp[attr] = {}
                attr_temp[attr][field] = val

        for attr, data in attr_temp.items():
            data["observedAt"] = ts_iso

            # Detect and nest hasQuality fields if present
            hq_type_key = "hasQuality" + sep + "type"
            hq_obj_key = "hasQuality" + sep + "object"

            hq_type = data.pop(hq_type_key, None)
            hq_obj = data.pop(hq_obj_key, None)

            # if pd.notna(hq_type) and pd.notna(hq_obj):
            #    data["hasQuality"] = {"type": hq_type, "object": hq_obj}

            # Always add hasQuality key, with None if missing
            data["hasQuality"] = {
                "type": None if pd.isna(hq_type) else hq_type,
                "object": None if pd.isna(hq_obj) else hq_obj,
            }

            # Store observations per attribute
            if attr not in attribute_groups:
                attribute_groups[attr] = []
            attribute_groups[attr].append(data)

    # Merge and return
    return {**context, **attribute_groups}
