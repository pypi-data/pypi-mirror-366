"""
py-stats: A comprehensive Python statistics package

This package provides over 60 statistical functions for both univariate
and multivariate analysis, similar to those found on scientific calculators.
"""

from .univariate import (
    # Means
    arithmetic_mean,
    harmonic_mean,
    geometric_mean,
    quadratic_mean,
    
    # Central tendency
    median,
    mode,
    midrange,
    trimean,
    
    # Quantiles
    quartiles,
    hinges,
    quantile,
    
    # Dispersion
    variance,
    standard_deviation,
    average_deviation,
    median_absolute_deviation,
    
    # Shape
    skewness,
    kurtosis,
    
    # Specialized
    angular_mean,
    running_average,
    weighted_average,
    standard_error_mean,
    
    # Robust statistics
    winsorized_mean,
    trimmed_mean,
    interquartile_range,
    range_value,
    coefficient_of_variation,
    
    # Order statistics
    percentile_rank,
    deciles,
    percentile,
    
    # Shape and distribution
    coefficient_of_skewness,
    coefficient_of_kurtosis,
    simple_normality_test,
    
    # Central tendency alternatives
    winsorized_median,
    midhinge,
    
    # Probability and distribution
    z_score,
    t_score,
    percentile_from_z_score,
    confidence_interval_mean,
    confidence_interval_proportion,
    
    # Time series
    moving_average,
    exponential_smoothing,
    seasonal_decomposition_simple,
)

from .multivariate import (
    # Correlation
    pearson_correlation,
    q_correlation,
    spearman_correlation,
    kendall_tau,
    point_biserial_correlation,
    
    # Covariance
    covariance,
    
    # Regression
    linear_regression,
    multiple_linear_regression,
    polynomial_regression,
    residual_analysis,
    
    # Sums
    sum_xx,
    sum_yy,
    sum_xy,
    
    # Association measures
    chi_square_test,
    cramers_v,
    contingency_coefficient,
)

__version__ = "2.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    # Univariate functions
    "arithmetic_mean",
    "harmonic_mean", 
    "geometric_mean",
    "quadratic_mean",
    "median",
    "mode",
    "midrange",
    "trimean",
    "quartiles",
    "hinges",
    "quantile",
    "variance",
    "standard_deviation",
    "average_deviation",
    "median_absolute_deviation",
    "skewness",
    "kurtosis",
    "angular_mean",
    "running_average",
    "weighted_average",
    "standard_error_mean",
    
    # Robust statistics
    "winsorized_mean",
    "trimmed_mean",
    "interquartile_range",
    "range_value",
    "coefficient_of_variation",
    
    # Order statistics
    "percentile_rank",
    "deciles",
    "percentile",
    
    # Shape and distribution
    "coefficient_of_skewness",
    "coefficient_of_kurtosis",
    "simple_normality_test",
    
    # Central tendency alternatives
    "winsorized_median",
    "midhinge",
    
    # Probability and distribution
    "z_score",
    "t_score",
    "percentile_from_z_score",
    "confidence_interval_mean",
    "confidence_interval_proportion",
    
    # Time series
    "moving_average",
    "exponential_smoothing",
    "seasonal_decomposition_simple",
    
    # Multivariate functions
    "pearson_correlation",
    "q_correlation",
    "spearman_correlation",
    "kendall_tau",
    "point_biserial_correlation",
    "covariance",
    "linear_regression",
    "multiple_linear_regression",
    "polynomial_regression",
    "residual_analysis",
    "sum_xx",
    "sum_yy",
    "sum_xy",
    "chi_square_test",
    "cramers_v",
    "contingency_coefficient",
] 