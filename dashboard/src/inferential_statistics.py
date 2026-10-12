# -*- coding: utf-8 -*-
"""
Inferential Statistics & Hypothesis Testing Engine
File: inferential_statistics.py
Provides rigorous statistical hypothesis testing methods matching 'how to/is.txt':
1. Two-Sample Welch's t-test (compares means of two groups)
2. One-Way ANOVA (compares means across 3+ groups with effect size eta-squared)
3. Chi-Square Test of Independence (relationships between categorical variables)
4. Empirical 95% Confidence Intervals for population parameters
5. Pearson & Spearman Correlation Matrices
"""

import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def run_two_sample_t_test(
    df: pd.DataFrame,
    group_col: str,
    target_col: str = "price",
    val1: Optional[Any] = None,
    val2: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Executes Welch's two-sample t-test (unequal variances assumed)
    comparing the mean of target_col between two groups in group_col.
    """
    clean_df = df.dropna(subset=[group_col, target_col]).copy()
    unique_vals = list(clean_df[group_col].unique())
    if len(unique_vals) < 2:
        raise ValueError(f"Column '{group_col}' must contain at least 2 distinct values.")

    group1_name = val1 if val1 is not None else unique_vals[0]
    group2_name = val2 if val2 is not None else unique_vals[1]

    data1 = clean_df[clean_df[group_col] == group1_name][target_col].values.astype(float)
    data2 = clean_df[clean_df[group_col] == group2_name][target_col].values.astype(float)

    n1, n2 = len(data1), len(data2)
    if n1 < 5 or n2 < 5:
        raise ValueError("Insufficient sample size for reliable two-sample t-test.")

    mean1, mean2 = float(np.mean(data1)), float(np.mean(data2))
    std1, std2 = float(np.std(data1, ddof=1)), float(np.std(data2, ddof=1))
    mean_diff = mean1 - mean2

    # Welch's t-test
    res = stats.ttest_ind(data1, data2, equal_var=False)
    t_stat = float(res.statistic)
    p_val = float(res.pvalue)

    # Welch-Satterthwaite degrees of freedom
    se1 = (std1 ** 2) / n1
    se2 = (std2 ** 2) / n2
    se_diff = math.sqrt(se1 + se2)
    dof = ((se1 + se2) ** 2) / ((se1 ** 2) / (n1 - 1) + (se2 ** 2) / (n2 - 1)) if (se1 + se2) > 0 else 1.0

    # 95% Confidence Interval for the difference in means
    crit_t = stats.t.ppf(0.975, df=dof)
    ci_lower = mean_diff - crit_t * se_diff
    ci_upper = mean_diff + crit_t * se_diff

    # Cohen's d effect size
    pooled_sd = math.sqrt(((n1 - 1) * (std1 ** 2) + (n2 - 1) * (std2 ** 2)) / (n1 + n2 - 2))
    cohen_d = (mean_diff / pooled_sd) if pooled_sd > 0 else 0.0

    is_significant = p_val < 0.05
    conclusion = (
        f"Mean for '{group1_name}' (EGP {mean1:,.0f}) is "
        f"{'significantly higher' if mean_diff > 0 else 'significantly lower'} "
        f"than '{group2_name}' (EGP {mean2:,.0f}) "
        f"[t({dof:.0f}) = {t_stat:.2f}, p < 0.001, Cohen's d = {cohen_d:.2f}]."
        if p_val < 0.001 else
        f"Mean difference of EGP {mean_diff:,.0f} is "
        f"{'statistically significant' if is_significant else 'not statistically significant'} "
        f"at α = 0.05 [t({dof:.0f}) = {t_stat:.2f}, p = {p_val:.4f}]."
    )

    return {
        "test_type": "Welch's Two-Sample t-test",
        "target_col": target_col,
        "group_col": group_col,
        "group1_name": str(group1_name),
        "group2_name": str(group2_name),
        "sample_size_1": n1,
        "sample_size_2": n2,
        "mean_1": mean1,
        "mean_2": mean2,
        "std_1": std1,
        "std_2": std2,
        "mean_difference": mean_diff,
        "t_statistic": t_stat,
        "degrees_of_freedom": float(dof),
        "p_value": p_val,
        "ci_95_diff_lower": float(ci_lower),
        "ci_95_diff_upper": float(ci_upper),
        "cohens_d": float(cohen_d),
        "is_significant_at_05": is_significant,
        "conclusion": conclusion
    }


def run_one_way_anova(
    df: pd.DataFrame,
    group_col: str,
    target_col: str = "price"
) -> Dict[str, Any]:
    """
    Executes One-Way ANOVA (Analysis of Variance) comparing target_col
    means across 3 or more groups defined by group_col.
    """
    clean_df = df.dropna(subset=[group_col, target_col]).copy()
    groups = clean_df.groupby(group_col)
    
    group_arrays = []
    group_summaries = []
    grand_values = clean_df[target_col].values.astype(float)
    grand_mean = float(np.mean(grand_values))
    total_n = len(grand_values)

    ss_between = 0.0
    for name, grp in groups:
        vals = grp[target_col].values.astype(float)
        if len(vals) < 3:
            continue
        group_arrays.append(vals)
        grp_mean = float(np.mean(vals))
        grp_std = float(np.std(vals, ddof=1))
        ss_between += len(vals) * ((grp_mean - grand_mean) ** 2)
        group_summaries.append({
            "group": str(name),
            "sample_count": len(vals),
            "mean": grp_mean,
            "std": grp_std,
            "median": float(np.median(vals))
        })

    if len(group_arrays) < 2:
        raise ValueError(f"Column '{group_col}' must have at least 2 valid groups with sufficient sample size.")

    res = stats.f_oneway(*group_arrays)
    f_stat = float(res.statistic)
    p_val = float(res.pvalue)

    ss_total = float(np.sum((grand_values - grand_mean) ** 2))
    eta_squared = (ss_between / ss_total) if ss_total > 0 else 0.0
    k = len(group_arrays)
    df_between = k - 1
    df_within = total_n - k

    is_significant = p_val < 0.05
    conclusion = (
        f"Significant price variation observed across {k} {group_col} segments "
        f"[F({df_between}, {df_within}) = {f_stat:.1f}, p < 0.001, Eta2 = {eta_squared:.2f}]. "
        f"{group_col} explains approximately {eta_squared*100:.1f}% of total price variance."
        if p_val < 0.001 else
        f"ANOVA indicates {'significant' if is_significant else 'no significant'} "
        f"differences among {group_col} groups [F = {f_stat:.2f}, p = {p_val:.4f}]."
    )

    return {
        "test_type": "One-Way ANOVA (F-Test)",
        "target_col": target_col,
        "group_col": group_col,
        "num_groups": k,
        "total_sample_size": total_n,
        "f_statistic": f_stat,
        "p_value": p_val,
        "df_between": df_between,
        "df_within": df_within,
        "eta_squared": float(eta_squared),
        "is_significant_at_05": is_significant,
        "group_summaries": group_summaries,
        "conclusion": conclusion
    }


def run_chi_square_test(
    df: pd.DataFrame,
    col1: str,
    col2: str
) -> Dict[str, Any]:
    """
    Executes Pearson's Chi-Square Test of Independence between two categorical features.
    """
    clean_df = df.dropna(subset=[col1, col2]).copy()
    contingency = pd.crosstab(clean_df[col1], clean_df[col2])

    res = stats.chi2_contingency(contingency)
    chi2_stat = float(res.statistic)
    p_val = float(res.pvalue)
    dof = int(res.dof)

    # Cramér's V effect size
    n = contingency.sum().sum()
    min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
    cramers_v = math.sqrt(chi2_stat / (n * min_dim)) if (n * min_dim) > 0 else 0.0

    is_significant = p_val < 0.05
    conclusion = (
        f"Significant statistical association between '{col1}' and '{col2}' "
        f"[Chi2({dof}) = {chi2_stat:.1f}, p < 0.001, Cramers V = {cramers_v:.2f}]."
        if p_val < 0.001 else
        f"Association between '{col1}' and '{col2}' is "
        f"{'statistically significant' if is_significant else 'not statistically significant'} "
        f"[Chi2({dof}) = {chi2_stat:.2f}, p = {p_val:.4f}]."
    )

    return {
        "test_type": "Pearson's Chi-Square Test of Independence",
        "variable_1": col1,
        "variable_2": col2,
        "sample_size": int(n),
        "chi2_statistic": chi2_stat,
        "degrees_of_freedom": dof,
        "p_value": p_val,
        "cramers_v": float(cramers_v),
        "is_significant_at_05": is_significant,
        "contingency_table": contingency.to_dict(),
        "conclusion": conclusion
    }


def compute_confidence_intervals(
    df: pd.DataFrame,
    group_col: str,
    target_col: str = "price",
    confidence: float = 0.95
) -> pd.DataFrame:
    """
    Calculates empirical population mean confidence intervals (e.g. 95% CI)
    grouped by group_col.
    """
    clean_df = df.dropna(subset=[group_col, target_col]).copy()
    records = []

    for name, grp in clean_df.groupby(group_col):
        vals = grp[target_col].values.astype(float)
        n = len(vals)
        if n < 3:
            continue
        m = float(np.mean(vals))
        s = float(np.std(vals, ddof=1))
        se = s / math.sqrt(n)
        crit = stats.t.ppf((1 + confidence) / 2, df=n - 1)
        moe = crit * se

        records.append({
            group_col: str(name),
            "Sample Count (N)": int(n),
            f"Mean {target_col}": float(m),
            "Std Dev": float(s),
            "Std Error (SE)": float(se),
            f"Lower {int(confidence*100)}% CI": float(m - moe),
            f"Upper {int(confidence*100)}% CI": float(m + moe)
        })

    return pd.DataFrame(records)


def compute_correlation_matrix(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates Pearson (linear) and Spearman (rank-order) correlation matrices.
    """
    if columns is None:
        columns = ["size_sqm", "bedrooms", "bathrooms", "floor", "air_quality", "green_space", "price"]

    avail_cols = [c for c in columns if c in df.columns]
    num_df = df[avail_cols].apply(pd.to_numeric, errors="coerce").dropna()

    pearson_corr = num_df.corr(method="pearson").round(3)
    spearman_corr = num_df.corr(method="spearman").round(3)

    return pearson_corr, spearman_corr
