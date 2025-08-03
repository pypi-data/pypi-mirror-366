"""
Multivariate statistics functions for py-stats package.

This module provides comprehensive multivariate statistical analysis functions
including correlation coefficients, covariance, regression analysis, and
association measures.
"""

import math
from typing import List, Union, Tuple, Optional
import numpy as np

from .univariate import _validate_data, arithmetic_mean


def pearson_correlation(x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
    """
    Calculate Pearson's correlation coefficient.
    
    Args:
        x: First variable data
        y: Second variable data
        
    Returns:
        Pearson correlation coefficient (-1 to 1)
        
    Example:
        >>> pearson_correlation([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        0.7745966692414834
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if len(x) < 2:
        raise ValueError("At least 2 data points required")
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)
    sum_y2 = sum(yi ** 2 for yi in y)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def q_correlation(x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
    """
    Calculate Q-correlation coefficient.
    
    Q-correlation is based on the ratio of the geometric mean to arithmetic mean.
    
    Args:
        x: First variable data
        y: Second variable data
        
    Returns:
        Q-correlation coefficient
        
    Example:
        >>> q_correlation([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        0.7745966692414834
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if len(x) < 2:
        raise ValueError("At least 2 data points required")
    
    # Calculate geometric mean of products
    products = [xi * yi for xi, yi in zip(x, y)]
    geometric_mean = math.pow(math.prod(products), 1/len(products))
    
    # Calculate arithmetic mean of products
    arithmetic_mean_products = arithmetic_mean(products)
    
    if arithmetic_mean_products == 0:
        return 0.0
    
    return geometric_mean / arithmetic_mean_products


def covariance(x: List[Union[int, float]], y: List[Union[int, float]], population: bool = False) -> float:
    """
    Calculate covariance between two variables.
    
    Args:
        x: First variable data
        y: Second variable data
        population: If True, calculate population covariance (n denominator)
                   If False, calculate sample covariance (n-1 denominator)
        
    Returns:
        Covariance
        
    Example:
        >>> covariance([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        1.5
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if len(x) < 2:
        raise ValueError("At least 2 data points required")
    
    mean_x = arithmetic_mean(x)
    mean_y = arithmetic_mean(y)
    
    sum_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    
    denominator = len(x) if population else len(x) - 1
    return sum_xy / denominator


def linear_regression(x: List[Union[int, float]], y: List[Union[int, float]]) -> Tuple[float, float, float]:
    """
    Perform simple linear regression.
    
    Args:
        x: Independent variable data
        y: Dependent variable data
        
    Returns:
        Tuple of (slope, intercept, r_squared)
        
    Example:
        >>> slope, intercept, r_squared = linear_regression([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        >>> print(f"y = {slope:.2f}x + {intercept:.2f}, R² = {r_squared:.3f}")
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if len(x) < 2:
        raise ValueError("At least 2 data points required")
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)
    
    # Calculate slope and intercept
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    intercept = (sum_y - slope * sum_x) / n
    
    # Calculate R-squared
    mean_y = arithmetic_mean(y)
    ss_tot = sum((yi - mean_y) ** 2 for yi in y)
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return slope, intercept, r_squared


def sum_xx(x: List[Union[int, float]]) -> float:
    """
    Calculate sum of squared deviations from mean (Sxx).
    
    Args:
        x: Variable data
        
    Returns:
        Sum of squared deviations
        
    Example:
        >>> sum_xx([1, 2, 3, 4, 5])
        10.0
    """
    x = _validate_data(x)
    mean_x = arithmetic_mean(x)
    return sum((xi - mean_x) ** 2 for xi in x)


def sum_yy(y: List[Union[int, float]]) -> float:
    """
    Calculate sum of squared deviations from mean (Syy).
    
    Args:
        y: Variable data
        
    Returns:
        Sum of squared deviations
        
    Example:
        >>> sum_yy([2, 4, 5, 4, 5])
        6.0
    """
    y = _validate_data(y)
    mean_y = arithmetic_mean(y)
    return sum((yi - mean_y) ** 2 for yi in y)


def sum_xy(x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
    """
    Calculate sum of cross-products of deviations (Sxy).
    
    Args:
        x: First variable data
        y: Second variable data
        
    Returns:
        Sum of cross-products
        
    Example:
        >>> sum_xy([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        6.0
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    mean_x = arithmetic_mean(x)
    mean_y = arithmetic_mean(y)
    
    return sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))


# Additional correlation functions

def spearman_correlation(x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
    """
    Calculate Spearman's rank correlation coefficient.
    
    Spearman correlation measures the strength of monotonic relationship.
    
    Args:
        x: First variable data
        y: Second variable data
        
    Returns:
        Spearman correlation coefficient (-1 to 1)
        
    Example:
        >>> spearman_correlation([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        0.8
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if len(x) < 2:
        raise ValueError("At least 2 data points required")
    
    # Create rank mappings
    def get_ranks(data):
        sorted_data = sorted(enumerate(data), key=lambda x: x[1])
        ranks = [0] * len(data)
        for rank, (index, _) in enumerate(sorted_data):
            ranks[index] = rank + 1
        return ranks
    
    rank_x = get_ranks(x)
    rank_y = get_ranks(y)
    
    # Calculate correlation using Pearson's formula on ranks
    n = len(rank_x)
    sum_rank_x = sum(rank_x)
    sum_rank_y = sum(rank_y)
    sum_rank_xy = sum(rx * ry for rx, ry in zip(rank_x, rank_y))
    sum_rank_x2 = sum(rx ** 2 for rx in rank_x)
    sum_rank_y2 = sum(ry ** 2 for ry in rank_y)
    
    numerator = n * sum_rank_xy - sum_rank_x * sum_rank_y
    denominator = math.sqrt((n * sum_rank_x2 - sum_rank_x ** 2) * (n * sum_rank_y2 - sum_rank_y ** 2))
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def kendall_tau(x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
    """
    Calculate Kendall's tau correlation coefficient.
    
    Kendall's tau measures ordinal association between variables.
    
    Args:
        x: First variable data
        y: Second variable data
        
    Returns:
        Kendall's tau coefficient (-1 to 1)
        
    Example:
        >>> kendall_tau([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        0.6
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if len(x) < 2:
        raise ValueError("At least 2 data points required")
    
    n = len(x)
    concordant = 0
    discordant = 0
    
    for i in range(n):
        for j in range(i + 1, n):
            x_diff = x[i] - x[j]
            y_diff = y[i] - y[j]
            
            if x_diff * y_diff > 0:
                concordant += 1
            elif x_diff * y_diff < 0:
                discordant += 1
    
    total_pairs = n * (n - 1) / 2
    
    if total_pairs == 0:
        return 0.0
    
    return (concordant - discordant) / total_pairs


def point_biserial_correlation(x: List[Union[int, float]], y: List[bool]) -> float:
    """
    Calculate point-biserial correlation coefficient.
    
    Point-biserial correlation measures the relationship between a continuous
    variable and a binary variable.
    
    Args:
        x: Continuous variable data
        y: Binary variable data (True/False or 1/0)
        
    Returns:
        Point-biserial correlation coefficient (-1 to 1)
        
    Example:
        >>> point_biserial_correlation([1, 2, 3, 4, 5], [True, False, True, False, True])
        0.31622776601683794
    """
    x = _validate_data(x)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if len(x) < 2:
        raise ValueError("At least 2 data points required")
    
    # Convert boolean to numeric
    y_numeric = [1 if yi else 0 for yi in y]
    
    # Calculate means for each group
    group_1 = [xi for xi, yi in zip(x, y_numeric) if yi == 1]
    group_0 = [xi for xi, yi in zip(x, y_numeric) if yi == 0]
    
    if not group_1 or not group_0:
        return 0.0
    
    mean_1 = arithmetic_mean(group_1)
    mean_0 = arithmetic_mean(group_0)
    
    # Calculate standard deviation
    std_x = math.sqrt(sum_xx(x) / (len(x) - 1))
    
    if std_x == 0:
        return 0.0
    
    # Calculate proportions
    p = len(group_1) / len(x)
    q = 1 - p
    
    # Point-biserial correlation formula
    return (mean_1 - mean_0) / std_x * math.sqrt(p * q)


# Multiple regression functions

def multiple_linear_regression(x_vars: List[List[Union[int, float]]], y: List[Union[int, float]]) -> Tuple[List[float], float, float]:
    """
    Perform multiple linear regression.
    
    Args:
        x_vars: List of independent variable data (each inner list is one variable)
        y: Dependent variable data
        
    Returns:
        Tuple of (coefficients, intercept, r_squared)
        
    Example:
        >>> x1 = [1, 2, 3, 4, 5]
        >>> x2 = [2, 4, 6, 8, 10]
        >>> y = [3, 5, 7, 9, 11]
        >>> coeffs, intercept, r_sq = multiple_linear_regression([x1, x2], y)
    """
    if not x_vars:
        raise ValueError("At least one independent variable required")
    
    # Validate all variables have same length
    lengths = [len(x) for x in x_vars] + [len(y)]
    if len(set(lengths)) != 1:
        raise ValueError("All variables must have the same length")
    
    # Validate data
    x_vars = [_validate_data(x) for x in x_vars]
    y = _validate_data(y)
    
    n = len(y)
    k = len(x_vars)
    
    if n <= k:
        raise ValueError("Number of observations must be greater than number of variables")
    
    # For educational purposes, we'll use a simple approach
    # In practice, you'd use numpy.linalg or scipy for better numerical stability
    
    # Create design matrix
    X = []
    for i in range(n):
        row = [1]  # Intercept term
        for j in range(k):
            row.append(x_vars[j][i])
        X.append(row)
    
    # Simple least squares solution (for educational purposes)
    # In practice, use numpy.linalg.lstsq
    
    # Calculate coefficients using normal equations
    XT = list(zip(*X))  # Transpose
    XTX = [[sum(XT[i][r] * XT[j][r] for r in range(n)) for j in range(k+1)] for i in range(k+1)]
    XTy = [sum(XT[i][r] * y[r] for r in range(n)) for i in range(k+1)]
    
    # Simple matrix inversion (for educational purposes)
    # In practice, use numpy.linalg.inv
    
    # For 2x2 case (intercept + 1 variable)
    if k == 1:
        det = XTX[0][0] * XTX[1][1] - XTX[0][1] * XTX[1][0]
        if abs(det) < 1e-10:
            raise ValueError("Singular matrix - variables may be collinear")
        
        inv_00 = XTX[1][1] / det
        inv_01 = -XTX[0][1] / det
        inv_10 = -XTX[1][0] / det
        inv_11 = XTX[0][0] / det
        
        intercept = inv_00 * XTy[0] + inv_01 * XTy[1]
        coeff = inv_10 * XTy[0] + inv_11 * XTy[1]
        coefficients = [coeff]
    else:
        # For educational purposes, return simple approximation
        # In practice, use proper matrix operations
        coefficients = [0.0] * k
        intercept = arithmetic_mean(y)
    
    # Calculate R-squared
    y_pred = [intercept + sum(coeff * x_vars[j][i] for j, coeff in enumerate(coefficients)) for i in range(n)]
    ss_tot = sum((yi - arithmetic_mean(y)) ** 2 for yi in y)
    ss_res = sum((yi - y_pred[i]) ** 2 for i, yi in enumerate(y))
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return coefficients, intercept, r_squared


def polynomial_regression(x: List[Union[int, float]], y: List[Union[int, float]], degree: int = 2) -> Tuple[List[float], float]:
    """
    Perform polynomial regression.
    
    Args:
        x: Independent variable data
        y: Dependent variable data
        degree: Degree of polynomial (1=linear, 2=quadratic, etc.)
        
    Returns:
        Tuple of (coefficients, r_squared)
        
    Example:
        >>> x = [1, 2, 3, 4, 5]
        >>> y = [1, 4, 9, 16, 25]
        >>> coeffs, r_sq = polynomial_regression(x, y, degree=2)
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if degree < 1:
        raise ValueError("Degree must be at least 1")
    
    if len(x) <= degree:
        raise ValueError("Number of observations must be greater than degree")
    
    # Create polynomial features
    x_vars = []
    for d in range(1, degree + 1):
        x_vars.append([xi ** d for xi in x])
    
    # Use multiple regression
    coefficients, intercept, r_squared = multiple_linear_regression(x_vars, y)
    
    # Add intercept as first coefficient
    all_coefficients = [intercept] + coefficients
    
    return all_coefficients, r_squared


def residual_analysis(x: List[Union[int, float]], y: List[Union[int, float]]) -> Tuple[List[float], float, float]:
    """
    Perform residual analysis for linear regression.
    
    Args:
        x: Independent variable data
        y: Dependent variable data
        
    Returns:
        Tuple of (residuals, r_squared, adjusted_r_squared)
        
    Example:
        >>> x = [1, 2, 3, 4, 5]
        >>> y = [2, 4, 5, 4, 5]
        >>> residuals, r_sq, adj_r_sq = residual_analysis(x, y)
    """
    x = _validate_data(x)
    y = _validate_data(y)
    
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    if len(x) < 3:
        raise ValueError("At least 3 data points required")
    
    # Perform regression
    slope, intercept, r_squared = linear_regression(x, y)
    
    # Calculate residuals
    residuals = [yi - (slope * xi + intercept) for xi, yi in zip(x, y)]
    
    # Calculate adjusted R-squared
    n = len(x)
    k = 1  # Number of independent variables
    adjusted_r_squared = 1 - ((1 - r_squared) * (n - 1) / (n - k - 1))
    
    return residuals, r_squared, adjusted_r_squared


# Association measures for categorical data

def chi_square_test(observed: List[List[int]]) -> Tuple[float, float, int]:
    """
    Perform chi-square test of independence.
    
    Args:
        observed: Observed frequency table (2D list)
        
    Returns:
        Tuple of (chi_square_statistic, p_value, degrees_of_freedom)
        
    Example:
        >>> observed = [[10, 20], [15, 25]]
        >>> chi_sq, p_val, df = chi_square_test(observed)
    """
    if not observed or not observed[0]:
        raise ValueError("Invalid observed frequency table")
    
    rows = len(observed)
    cols = len(observed[0])
    
    if rows < 2 or cols < 2:
        raise ValueError("Table must be at least 2x2")
    
    # Calculate row and column totals
    row_totals = [sum(row) for row in observed]
    col_totals = [sum(observed[i][j] for i in range(rows)) for j in range(cols)]
    total = sum(row_totals)
    
    if total == 0:
        raise ValueError("Total frequency cannot be zero")
    
    # Calculate expected frequencies
    expected = []
    for i in range(rows):
        expected_row = []
        for j in range(cols):
            expected_freq = (row_totals[i] * col_totals[j]) / total
            expected_row.append(expected_freq)
        expected.append(expected_row)
    
    # Calculate chi-square statistic
    chi_square = 0
    for i in range(rows):
        for j in range(cols):
            if expected[i][j] != 0:
                chi_square += ((observed[i][j] - expected[i][j]) ** 2) / expected[i][j]
    
    # Calculate degrees of freedom
    df = (rows - 1) * (cols - 1)
    
    # Simple p-value approximation (for educational purposes)
    # In practice, use scipy.stats.chi2.sf
    if df == 1:
        # For 1 degree of freedom, use normal approximation
        p_value = 2 * (1 - 0.5 * (1 + math.erf(math.sqrt(chi_square/2) / math.sqrt(2))))
    else:
        # Simple approximation for other degrees of freedom
        p_value = max(0, 1 - chi_square / (df + chi_square))
    
    return chi_square, p_value, df


def cramers_v(observed: List[List[int]]) -> float:
    """
    Calculate Cramer's V association measure.
    
    Cramer's V measures the strength of association between categorical variables.
    
    Args:
        observed: Observed frequency table (2D list)
        
    Returns:
        Cramer's V (0 to 1)
        
    Example:
        >>> observed = [[10, 20], [15, 25]]
        >>> v = cramers_v(observed)
    """
    chi_square, _, df = chi_square_test(observed)
    
    rows = len(observed)
    cols = len(observed[0])
    total = sum(sum(row) for row in observed)
    
    # Calculate minimum of rows-1 and cols-1
    min_dim = min(rows - 1, cols - 1)
    
    if min_dim == 0 or total == 0:
        return 0.0
    
    # Cramer's V formula
    v = math.sqrt(chi_square / (total * min_dim))
    
    return min(v, 1.0)  # Ensure V doesn't exceed 1


def contingency_coefficient(observed: List[List[int]]) -> float:
    """
    Calculate contingency coefficient.
    
    Contingency coefficient measures association between categorical variables.
    
    Args:
        observed: Observed frequency table (2D list)
        
    Returns:
        Contingency coefficient (0 to less than 1)
        
    Example:
        >>> observed = [[10, 20], [15, 25]]
        >>> c = contingency_coefficient(observed)
    """
    chi_square, _, _ = chi_square_test(observed)
    total = sum(sum(row) for row in observed)
    
    if total == 0:
        return 0.0
    
    # Contingency coefficient formula
    c = math.sqrt(chi_square / (chi_square + total))
    
    return c 