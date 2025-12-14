from typing import List, Optional


def resolve_metrics(
    requested_metrics: List[str],
    df_columns: List[str],
    id_like_columns: List[str] | None = None,
) -> List[str]:
    """
    Resolve requested metric names to actual dataframe columns.
    Prefers exact matches, then safe fuzzy matches.
    """

    id_like_columns = id_like_columns or []
    resolved = []

    df_columns_lower = {col.lower(): col for col in df_columns}

    for metric in requested_metrics:
        metric_l = metric.lower()
        if metric_l in df_columns_lower:
            resolved.append(df_columns_lower[metric_l])
            continue
        candidates = [
            col for col in df_columns
            if (
                metric_l in col.lower()
                or col.lower() in metric_l
            )
            and col not in id_like_columns
        ]
        prefix_matches = [
            col for col in candidates
            if col.lower().startswith(metric_l)
        ]

        if len(prefix_matches) == 1:
            resolved.append(prefix_matches[0])
        elif len(candidates) == 1:
            resolved.append(candidates[0])
        else:
            raise ValueError(
                f"Cannot uniquely resolve metric '{metric}'. "
                f"Candidates: {candidates}. "
                f"Available columns: {df_columns}"
            )

    return resolved
