"""
Univariate statistics functions for py-stats package.

This module provides comprehensive univariate statistical analysis functions
including means, central tendency measures, quantiles, dispersion measures,
shape measures, and specialized statistical functions.
"""

import math
import statistics
from typing import List, Union, Tuple, Optional
import numpy as np


def _validate_data(data: List[Union[int, float]]) -> List[float]:
    """Validate and convert data to list of floats."""
    if not data:
        raise ValueError("Data cannot be empty")
    
    try:
        return [float(x) for x in data]
    except (ValueError, TypeError):
        raise ValueError("All data points must be numeric")


def arithmetic_mean(data: List[Union[int, float]]) -> float:
    """
    Calculate the arithmetic mean (average) of a dataset.
    
    Args:
        data: List of numeric values
        
    Returns:
        Arithmetic mean of the data
        
    Example:
        >>> arithmetic_mean([1, 2, 3, 4, 5])
        3.0
    """
    data = _validate_data(data)
    return sum(data) / len(data)


def harmonic_mean(data: List[Union[int, float]]) -> float:
    """
    Calculate the harmonic mean of a dataset.
    
    The harmonic mean is the reciprocal of the arithmetic mean of reciprocals.
    Useful for rates, speeds, and ratios.
    
    Args:
        data: List of positive numeric values
        
    Returns:
        Harmonic mean of the data
        
    Example:
        >>> harmonic_mean([1, 2, 4])
        1.7142857142857142
    """
    data = _validate_data(data)
    if any(x <= 0 for x in data):
        raise ValueError("All values must be positive for harmonic mean")
    
    return len(data) / sum(1/x for x in data)


def geometric_mean(data: List[Union[int, float]]) -> float:
    """
    Calculate the geometric mean of a dataset.
    
    The geometric mean is the nth root of the product of n values.
    Useful for growth rates and ratios.
    
    Args:
        data: List of positive numeric values
        
    Returns:
        Geometric mean of the data
        
    Example:
        >>> geometric_mean([1, 2, 4])
        2.0
    """
    data = _validate_data(data)
    if any(x <= 0 for x in data):
        raise ValueError("All values must be positive for geometric mean")
    
    return math.pow(math.prod(data), 1/len(data))


def quadratic_mean(data: List[Union[int, float]]) -> float:
    """
    Calculate the quadratic mean (root mean square) of a dataset.
    
    The quadratic mean is the square root of the arithmetic mean of squares.
    Useful for physical quantities like voltage and current.
    
    Args:
        data: List of numeric values
        
    Returns:
        Quadratic mean of the data
        
    Example:
        >>> quadratic_mean([1, 2, 3, 4, 5])
        3.3166247903554
    """
    data = _validate_data(data)
    return math.sqrt(sum(x**2 for x in data) / len(data))


def median(data: List[Union[int, float]]) -> float:
    """
    Calculate the median of a dataset.
    
    The median is the middle value when data is sorted.
    For even-sized datasets, it's the average of the two middle values.
    
    Args:
        data: List of numeric values
        
    Returns:
        Median of the data
        
    Example:
        >>> median([1, 3, 5, 7, 9])
        5.0
        >>> median([1, 2, 3, 4])
        2.5
    """
    data = _validate_data(data)
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    if n % 2 == 1:
        return sorted_data[n // 2]
    else:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2


def mode(data: List[Union[int, float]]) -> List[float]:
    """
    Calculate the mode(s) of a dataset.
    
    The mode is the most frequently occurring value(s).
    Returns all modes if there are multiple.
    
    Args:
        data: List of numeric values
        
    Returns:
        List of mode(s)
        
    Example:
        >>> mode([1, 2, 2, 3, 4])
        [2.0]
        >>> mode([1, 1, 2, 2, 3])
        [1.0, 2.0]
    """
    data = _validate_data(data)
    frequency = {}
    
    for value in data:
        frequency[value] = frequency.get(value, 0) + 1
    
    max_freq = max(frequency.values())
    modes = [value for value, freq in frequency.items() if freq == max_freq]
    
    return sorted(modes)


def midrange(data: List[Union[int, float]]) -> float:
    """
    Calculate the midrange of a dataset.
    
    The midrange is the average of the minimum and maximum values.
    
    Args:
        data: List of numeric values
        
    Returns:
        Midrange of the data
        
    Example:
        >>> midrange([1, 2, 3, 4, 5])
        3.0
    """
    data = _validate_data(data)
    return (min(data) + max(data)) / 2


def trimean(data: List[Union[int, float]]) -> float:
    """
    Calculate the trimean of a dataset.
    
    The trimean is (Q1 + 2*Q2 + Q3) / 4, where Q1, Q2, Q3 are quartiles.
    It's a robust measure of central tendency.
    
    Args:
        data: List of numeric values
        
    Returns:
        Trimean of the data
        
    Example:
        >>> trimean([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        5.5
    """
    data = _validate_data(data)
    q1, q2, q3 = quartiles(data)
    return (q1 + 2 * q2 + q3) / 4


def quartiles(data: List[Union[int, float]]) -> Tuple[float, float, float]:
    """
    Calculate the first, second (median), and third quartiles.
    
    Args:
        data: List of numeric values
        
    Returns:
        Tuple of (Q1, Q2, Q3)
        
    Example:
        >>> quartiles([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        (3.25, 5.5, 7.75)
    """
    data = _validate_data(data)
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    q1 = quantile(sorted_data, 0.25)
    q2 = quantile(sorted_data, 0.50)
    q3 = quantile(sorted_data, 0.75)
    
    return q1, q2, q3


def hinges(data: List[Union[int, float]]) -> Tuple[float, float]:
    """
    Calculate the lower and upper hinges.
    
    Hinges are similar to quartiles but use a different calculation method.
    
    Args:
        data: List of numeric values
        
    Returns:
        Tuple of (lower_hinge, upper_hinge)
        
    Example:
        >>> hinges([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        (3.5, 7.5)
    """
    data = _validate_data(data)
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    if n % 2 == 0:
        lower_half = sorted_data[:n//2]
        upper_half = sorted_data[n//2:]
    else:
        lower_half = sorted_data[:n//2]
        upper_half = sorted_data[n//2 + 1:]
    
    lower_hinge = median(lower_half)
    upper_hinge = median(upper_half)
    
    return lower_hinge, upper_hinge


def quantile(data: List[Union[int, float]], q: float) -> float:
    """
    Calculate the quantile at probability q.
    
    Args:
        data: List of numeric values
        q: Probability (0 <= q <= 1)
        
    Returns:
        Quantile value
        
    Example:
        >>> quantile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.25)
        3.25
    """
    if not 0 <= q <= 1:
        raise ValueError("Quantile probability must be between 0 and 1")
    
    data = _validate_data(data)
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    if q == 0:
        return sorted_data[0]
    if q == 1:
        return sorted_data[-1]
    
    # Linear interpolation method
    index = q * (n - 1)
    lower_index = int(index)
    upper_index = min(lower_index + 1, n - 1)
    
    if lower_index == upper_index:
        return sorted_data[lower_index]
    
    weight = index - lower_index
    return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight


def variance(data: List[Union[int, float]], population: bool = False) -> float:
    """
    Calculate the variance of a dataset.
    
    Args:
        data: List of numeric values
        population: If True, calculate population variance (n denominator)
                   If False, calculate sample variance (n-1 denominator)
        
    Returns:
        Variance of the data
        
    Example:
        >>> variance([1, 2, 3, 4, 5])
        2.5
        >>> variance([1, 2, 3, 4, 5], population=True)
        2.0
    """
    data = _validate_data(data)
    if len(data) < 2:
        raise ValueError("At least 2 data points required for variance")
    
    mean_val = arithmetic_mean(data)
    squared_diff_sum = sum((x - mean_val) ** 2 for x in data)
    
    denominator = len(data) if population else len(data) - 1
    return squared_diff_sum / denominator


def standard_deviation(data: List[Union[int, float]], population: bool = False) -> float:
    """
    Calculate the standard deviation of a dataset.
    
    Args:
        data: List of numeric values
        population: If True, calculate population standard deviation
                   If False, calculate sample standard deviation
        
    Returns:
        Standard deviation of the data
        
    Example:
        >>> standard_deviation([1, 2, 3, 4, 5])
        1.5811388300841898
    """
    return math.sqrt(variance(data, population))


def average_deviation(data: List[Union[int, float]]) -> float:
    """
    Calculate the average absolute deviation from the mean.
    
    Args:
        data: List of numeric values
        
    Returns:
        Average absolute deviation
        
    Example:
        >>> average_deviation([1, 2, 3, 4, 5])
        1.2
    """
    data = _validate_data(data)
    mean_val = arithmetic_mean(data)
    return sum(abs(x - mean_val) for x in data) / len(data)


def median_absolute_deviation(data: List[Union[int, float]]) -> float:
    """
    Calculate the median absolute deviation (MAD).
    
    MAD is the median of absolute deviations from the median.
    It's a robust measure of dispersion.
    
    Args:
        data: List of numeric values
        
    Returns:
        Median absolute deviation
        
    Example:
        >>> median_absolute_deviation([1, 2, 3, 4, 5])
        1.0
    """
    data = _validate_data(data)
    median_val = median(data)
    absolute_deviations = [abs(x - median_val) for x in data]
    return median(absolute_deviations)


def skewness(data: List[Union[int, float]]) -> float:
    """
    Calculate the skewness of a dataset.
    
    Skewness measures the asymmetry of the distribution.
    Positive skewness indicates a longer right tail.
    
    Args:
        data: List of numeric values
        
    Returns:
        Skewness coefficient
        
    Example:
        >>> skewness([1, 2, 3, 4, 5])
        0.0
    """
    data = _validate_data(data)
    if len(data) < 3:
        raise ValueError("At least 3 data points required for skewness")
    
    mean_val = arithmetic_mean(data)
    std_val = standard_deviation(data)
    
    if std_val == 0:
        return 0.0
    
    n = len(data)
    skew_sum = sum(((x - mean_val) / std_val) ** 3 for x in data)
    return (n / ((n - 1) * (n - 2))) * skew_sum


def kurtosis(data: List[Union[int, float]]) -> float:
    """
    Calculate the kurtosis of a dataset.
    
    Kurtosis measures the "tailedness" of the distribution.
    Higher kurtosis indicates more extreme deviations.
    
    Args:
        data: List of numeric values
        
    Returns:
        Kurtosis coefficient
        
    Example:
        >>> kurtosis([1, 2, 3, 4, 5])
        -1.2
    """
    data = _validate_data(data)
    if len(data) < 4:
        raise ValueError("At least 4 data points required for kurtosis")
    
    mean_val = arithmetic_mean(data)
    std_val = standard_deviation(data)
    
    if std_val == 0:
        return 0.0
    
    n = len(data)
    kurt_sum = sum(((x - mean_val) / std_val) ** 4 for x in data)
    
    # Excess kurtosis (subtract 3 to make normal distribution = 0)
    return (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * kurt_sum - (3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))


def angular_mean(data: List[Union[int, float]], degrees: bool = True) -> float:
    """
    Calculate the mean of angular quantities.
    
    Args:
        data: List of angular values
        degrees: If True, input is in degrees; if False, in radians
        
    Returns:
        Mean angle in the same units as input
        
    Example:
        >>> angular_mean([0, 90, 180, 270])
        135.0
    """
    data = _validate_data(data)
    
    if degrees:
        # Convert to radians
        data_rad = [math.radians(x) for x in data]
    else:
        data_rad = data
    
    # Calculate mean of sines and cosines
    mean_sin = sum(math.sin(x) for x in data_rad) / len(data_rad)
    mean_cos = sum(math.cos(x) for x in data_rad) / len(data_rad)
    
    # Convert back to angle
    result = math.atan2(mean_sin, mean_cos)
    
    if degrees:
        result = math.degrees(result)
    
    # Ensure result is in [0, 360) for degrees or [0, 2π) for radians
    if degrees:
        return (result + 360) % 360
    else:
        return (result + 2 * math.pi) % (2 * math.pi)


def running_average(data: List[Union[int, float]], window: int = 3) -> List[float]:
    """
    Calculate running average with specified window size.
    
    Args:
        data: List of numeric values
        window: Size of the moving window
        
    Returns:
        List of running averages
        
    Example:
        >>> running_average([1, 2, 3, 4, 5], window=3)
        [2.0, 3.0, 4.0]
    """
    data = _validate_data(data)
    if window > len(data):
        raise ValueError("Window size cannot be larger than data size")
    if window < 1:
        raise ValueError("Window size must be at least 1")
    
    result = []
    for i in range(len(data) - window + 1):
        window_data = data[i:i + window]
        result.append(arithmetic_mean(window_data))
    
    return result


def weighted_average(data: List[Union[int, float]], weights: List[Union[int, float]]) -> float:
    """
    Calculate weighted average of a dataset.
    
    Args:
        data: List of numeric values
        weights: List of weights (must be same length as data)
        
    Returns:
        Weighted average
        
    Example:
        >>> weighted_average([1, 2, 3], [0.5, 1.0, 1.5])
        2.1666666666666665
    """
    data = _validate_data(data)
    weights = _validate_data(weights)
    
    if len(data) != len(weights):
        raise ValueError("Data and weights must have the same length")
    
    if any(w < 0 for w in weights):
        raise ValueError("Weights must be non-negative")
    
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Sum of weights cannot be zero")
    
    return sum(x * w for x, w in zip(data, weights)) / total_weight


def standard_error_mean(data: List[Union[int, float]]) -> float:
    """
    Calculate the standard error of the mean.
    
    Args:
        data: List of numeric values
        
    Returns:
        Standard error of the mean
        
    Example:
        >>> standard_error_mean([1, 2, 3, 4, 5])
        0.7071067811865476
    """
    data = _validate_data(data)
    if len(data) < 2:
        raise ValueError("At least 2 data points required for standard error")
    
    return standard_deviation(data) / math.sqrt(len(data))


# Additional robust statistics functions

def winsorized_mean(data: List[Union[int, float]], percent: float = 10.0) -> float:
    """
    Calculate the winsorized mean.
    
    Winsorization replaces extreme values with less extreme ones.
    
    Args:
        data: List of numeric values
        percent: Percentage of values to winsorize from each end
        
    Returns:
        Winsorized mean
        
    Example:
        >>> winsorized_mean([1, 2, 3, 4, 100], percent=20)
        3.0
    """
    data = _validate_data(data)
    if not 0 <= percent <= 50:
        raise ValueError("Percent must be between 0 and 50")
    
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = int(round(n * percent / 100))
    
    # Replace k smallest values with (k+1)th smallest
    # Replace k largest values with (n-k)th largest
    winsorized_data = sorted_data.copy()
    if k > 0:
        winsorized_data[:k] = [sorted_data[k]] * k
        winsorized_data[-k:] = [sorted_data[n-k-1]] * k
    
    return arithmetic_mean(winsorized_data)


def trimmed_mean(data: List[Union[int, float]], percent: float = 10.0) -> float:
    """
    Calculate the trimmed mean.
    
    Trimming removes extreme values from both ends.
    
    Args:
        data: List of numeric values
        percent: Percentage of values to trim from each end
        
    Returns:
        Trimmed mean
        
    Example:
        >>> trimmed_mean([1, 2, 3, 4, 100], percent=20)
        3.0
    """
    data = _validate_data(data)
    if not 0 <= percent <= 50:
        raise ValueError("Percent must be between 0 and 50")
    
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = int(round(n * percent / 100))
    
    # Remove k values from each end
    trimmed_data = sorted_data[k:n-k]
    
    if not trimmed_data:
        raise ValueError("No data remaining after trimming")
    
    return arithmetic_mean(trimmed_data)


def interquartile_range(data: List[Union[int, float]]) -> float:
    """
    Calculate the interquartile range (IQR).
    
    IQR is the difference between Q3 and Q1.
    
    Args:
        data: List of numeric values
        
    Returns:
        Interquartile range
        
    Example:
        >>> interquartile_range([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        4.5
    """
    data = _validate_data(data)
    q1, _, q3 = quartiles(data)
    return q3 - q1


def range_value(data: List[Union[int, float]]) -> float:
    """
    Calculate the range of a dataset.
    
    Range is the difference between maximum and minimum values.
    
    Args:
        data: List of numeric values
        
    Returns:
        Range of the data
        
    Example:
        >>> range_value([1, 2, 3, 4, 5])
        4.0
    """
    data = _validate_data(data)
    return max(data) - min(data)


def coefficient_of_variation(data: List[Union[int, float]]) -> float:
    """
    Calculate the coefficient of variation.
    
    CV is the ratio of standard deviation to mean, expressed as a decimal.
    
    Args:
        data: List of numeric values
        
    Returns:
        Coefficient of variation (as a decimal)
        
    Example:
        >>> coefficient_of_variation([1, 2, 3, 4, 5])
        0.5270462766947299
    """
    data = _validate_data(data)
    mean_val = arithmetic_mean(data)
    
    if mean_val == 0:
        raise ValueError("Cannot calculate CV when mean is zero")
    
    return standard_deviation(data) / abs(mean_val)


# Order statistics functions

def percentile_rank(data: List[Union[int, float]], value: Union[int, float]) -> float:
    """
    Calculate the percentile rank of a value in a dataset.
    
    Args:
        data: List of numeric values
        value: Value to find percentile rank for
        
    Returns:
        Percentile rank (0-100)
        
    Example:
        >>> percentile_rank([1, 2, 3, 4, 5], 3)
        50.0
    """
    data = _validate_data(data)
    sorted_data = sorted(data)
    
    # Count values less than the target value
    count_less = sum(1 for x in sorted_data if x < value)
    
    # Count values equal to the target value
    count_equal = sum(1 for x in sorted_data if x == value)
    
    # Calculate percentile rank
    rank = (count_less + 0.5 * count_equal) / len(sorted_data) * 100
    return rank


def deciles(data: List[Union[int, float]]) -> List[float]:
    """
    Calculate all deciles (10th, 20th, ..., 90th percentiles).
    
    Args:
        data: List of numeric values
        
    Returns:
        List of deciles [D1, D2, ..., D9]
        
    Example:
        >>> deciles([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        [1.9, 2.8, 3.7, 4.6, 5.5, 6.4, 7.3, 8.2, 9.1]
    """
    data = _validate_data(data)
    sorted_data = sorted(data)
    
    deciles_list = []
    for i in range(1, 10):
        q = i / 10
        deciles_list.append(quantile(sorted_data, q))
    
    return deciles_list


def percentile(data: List[Union[int, float]], p: float) -> float:
    """
    Calculate the pth percentile.
    
    Args:
        data: List of numeric values
        p: Percentile (0-100)
        
    Returns:
        pth percentile value
        
    Example:
        >>> percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 75)
        7.75
    """
    if not 0 <= p <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    
    return quantile(data, p / 100)


# Shape and distribution functions

def coefficient_of_skewness(data: List[Union[int, float]]) -> float:
    """
    Calculate the coefficient of skewness (standardized skewness).
    
    Args:
        data: List of numeric values
        
    Returns:
        Coefficient of skewness
        
    Example:
        >>> coefficient_of_skewness([1, 2, 3, 4, 5])
        0.0
    """
    data = _validate_data(data)
    if len(data) < 3:
        raise ValueError("At least 3 data points required")
    
    mean_val = arithmetic_mean(data)
    std_val = standard_deviation(data)
    
    if std_val == 0:
        return 0.0
    
    n = len(data)
    skew_sum = sum(((x - mean_val) / std_val) ** 3 for x in data)
    
    # Fisher-Pearson coefficient of skewness
    return (n / ((n - 1) * (n - 2))) * skew_sum


def coefficient_of_kurtosis(data: List[Union[int, float]]) -> float:
    """
    Calculate the coefficient of kurtosis (standardized kurtosis).
    
    Args:
        data: List of numeric values
        
    Returns:
        Coefficient of kurtosis
        
    Example:
        >>> coefficient_of_kurtosis([1, 2, 3, 4, 5])
        -1.2
    """
    data = _validate_data(data)
    if len(data) < 4:
        raise ValueError("At least 4 data points required")
    
    mean_val = arithmetic_mean(data)
    std_val = standard_deviation(data)
    
    if std_val == 0:
        return 0.0
    
    n = len(data)
    kurt_sum = sum(((x - mean_val) / std_val) ** 4 for x in data)
    
    # Excess kurtosis
    return (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * kurt_sum - (3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))


def simple_normality_test(data: List[Union[int, float]]) -> bool:
    """
    Simple normality test based on skewness and kurtosis.
    
    This is a basic test that checks if skewness and kurtosis are close to normal.
    
    Args:
        data: List of numeric values
        
    Returns:
        True if data appears approximately normal, False otherwise
        
    Example:
        >>> simple_normality_test([1, 2, 3, 4, 5])
        True
    """
    data = _validate_data(data)
    if len(data) < 10:
        return False  # Need sufficient data for meaningful test
    
    skew = coefficient_of_skewness(data)
    kurt = coefficient_of_kurtosis(data)
    
    # Check if skewness and kurtosis are within normal ranges
    # Normal distribution has skewness ≈ 0 and kurtosis ≈ 0
    return abs(skew) < 1.0 and abs(kurt) < 2.0


# Central tendency alternatives

def winsorized_median(data: List[Union[int, float]], percent: float = 10.0) -> float:
    """
    Calculate the winsorized median.
    
    Args:
        data: List of numeric values
        percent: Percentage of values to winsorize from each end
        
    Returns:
        Winsorized median
        
    Example:
        >>> winsorized_median([1, 2, 3, 4, 100], percent=20)
        3.0
    """
    data = _validate_data(data)
    if not 0 <= percent <= 50:
        raise ValueError("Percent must be between 0 and 50")
    
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = int(round(n * percent / 100))
    
    # Replace k smallest values with (k+1)th smallest
    # Replace k largest values with (n-k)th largest
    winsorized_data = sorted_data.copy()
    if k > 0:
        winsorized_data[:k] = [sorted_data[k]] * k
        winsorized_data[-k:] = [sorted_data[n-k-1]] * k
    
    return median(winsorized_data)


def midhinge(data: List[Union[int, float]]) -> float:
    """
    Calculate the midhinge.
    
    Midhinge is the average of the lower and upper hinges.
    
    Args:
        data: List of numeric values
        
    Returns:
        Midhinge value
        
    Example:
        >>> midhinge([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        5.5
    """
    data = _validate_data(data)
    lower_hinge, upper_hinge = hinges(data)
    return (lower_hinge + upper_hinge) / 2


# Probability and distribution functions

def z_score(data: List[Union[int, float]], value: Union[int, float]) -> float:
    """
    Calculate the z-score of a value relative to a dataset.
    
    Args:
        data: List of numeric values
        value: Value to calculate z-score for
        
    Returns:
        Z-score
        
    Example:
        >>> z_score([1, 2, 3, 4, 5], 3)
        0.0
    """
    data = _validate_data(data)
    mean_val = arithmetic_mean(data)
    std_val = standard_deviation(data)
    
    if std_val == 0:
        raise ValueError("Cannot calculate z-score when standard deviation is zero")
    
    return (value - mean_val) / std_val


def t_score(data: List[Union[int, float]], value: Union[int, float]) -> float:
    """
    Calculate the t-score of a value relative to a dataset.
    
    T-score is similar to z-score but uses sample standard deviation.
    
    Args:
        data: List of numeric values
        value: Value to calculate t-score for
        
    Returns:
        T-score
        
    Example:
        >>> t_score([1, 2, 3, 4, 5], 3)
        0.0
    """
    data = _validate_data(data)
    mean_val = arithmetic_mean(data)
    std_val = standard_deviation(data)  # Sample standard deviation
    
    if std_val == 0:
        raise ValueError("Cannot calculate t-score when standard deviation is zero")
    
    return (value - mean_val) / std_val


def percentile_from_z_score(z: float) -> float:
    """
    Calculate the percentile from a z-score.
    
    This uses the standard normal distribution.
    
    Args:
        z: Z-score
        
    Returns:
        Percentile (0-100)
        
    Example:
        >>> percentile_from_z_score(0)
        50.0
        >>> percentile_from_z_score(1.96)
        97.5
    """
    # Use normal distribution approximation
    # For educational purposes, we'll use a simple approximation
    # In practice, you'd use scipy.stats.norm.cdf
    
    # Simple approximation using error function
    import math
    percentile = 0.5 * (1 + math.erf(z / math.sqrt(2))) * 100
    return percentile


def confidence_interval_mean(data: List[Union[int, float]], confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for the mean.
    
    Args:
        data: List of numeric values
        confidence: Confidence level (0-1)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
        
    Example:
        >>> confidence_interval_mean([1, 2, 3, 4, 5], 0.95)
        (1.0367563145369689, 4.963243685463031)
    """
    data = _validate_data(data)
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1")
    
    if len(data) < 2:
        raise ValueError("At least 2 data points required")
    
    mean_val = arithmetic_mean(data)
    std_err = standard_error_mean(data)
    
    # For educational purposes, using z-distribution approximation
    # In practice, you'd use t-distribution for small samples
    if confidence == 0.95:
        z_critical = 1.96
    elif confidence == 0.99:
        z_critical = 2.576
    elif confidence == 0.90:
        z_critical = 1.645
    else:
        # Simple approximation for other confidence levels
        z_critical = 2.0  # Conservative estimate
    
    margin_of_error = z_critical * std_err
    
    return mean_val - margin_of_error, mean_val + margin_of_error


def confidence_interval_proportion(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for a proportion.
    
    Args:
        successes: Number of successes
        total: Total number of trials
        confidence: Confidence level (0-1)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
        
    Example:
        >>> confidence_interval_proportion(8, 10, 0.95)
        (0.4439045090940593, 0.9560954909059407)
    """
    if total <= 0:
        raise ValueError("Total must be positive")
    if not 0 <= successes <= total:
        raise ValueError("Successes must be between 0 and total")
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1")
    
    p_hat = successes / total
    
    # For educational purposes, using normal approximation
    # In practice, you'd use Wilson score interval for small samples
    if confidence == 0.95:
        z_critical = 1.96
    elif confidence == 0.99:
        z_critical = 2.576
    elif confidence == 0.90:
        z_critical = 1.645
    else:
        z_critical = 2.0  # Conservative estimate
    
    standard_error = math.sqrt(p_hat * (1 - p_hat) / total)
    margin_of_error = z_critical * standard_error
    
    lower_bound = max(0, p_hat - margin_of_error)
    upper_bound = min(1, p_hat + margin_of_error)
    
    return lower_bound, upper_bound


# Time series functions

def moving_average(data: List[Union[int, float]], window: int = 3) -> List[float]:
    """
    Calculate simple moving average.
    
    Args:
        data: List of numeric values
        window: Size of the moving window
        
    Returns:
        List of moving averages
        
    Example:
        >>> moving_average([1, 2, 3, 4, 5], window=3)
        [2.0, 3.0, 4.0]
    """
    return running_average(data, window)


def exponential_smoothing(data: List[Union[int, float]], alpha: float = 0.3) -> List[float]:
    """
    Calculate exponential smoothing.
    
    Args:
        data: List of numeric values
        alpha: Smoothing factor (0-1)
        
    Returns:
        List of smoothed values
        
    Example:
        >>> exponential_smoothing([1, 2, 3, 4, 5], alpha=0.3)
        [1.0, 1.3, 1.81, 2.467, 3.2269]
    """
    data = _validate_data(data)
    if not 0 <= alpha <= 1:
        raise ValueError("Alpha must be between 0 and 1")
    
    if not data:
        return []
    
    smoothed = [data[0]]  # First value is the same
    
    for i in range(1, len(data)):
        next_value = alpha * data[i] + (1 - alpha) * smoothed[i-1]
        smoothed.append(next_value)
    
    return smoothed


def seasonal_decomposition_simple(data: List[Union[int, float]], period: int = 4) -> Tuple[List[float], List[float], List[float]]:
    """
    Simple seasonal decomposition into trend, seasonal, and residual components.
    
    This is a basic implementation for educational purposes.
    
    Args:
        data: List of numeric values
        period: Seasonal period length
        
    Returns:
        Tuple of (trend, seasonal, residual) components
        
    Example:
        >>> trend, seasonal, residual = seasonal_decomposition_simple([1, 2, 3, 4, 5, 6, 7, 8], period=4)
    """
    data = _validate_data(data)
    if period <= 1 or period >= len(data):
        raise ValueError("Period must be between 2 and data length - 1")
    
    n = len(data)
    
    # Simple trend using moving average
    trend = []
    for i in range(n):
        start = max(0, i - period // 2)
        end = min(n, i + period // 2 + 1)
        trend.append(arithmetic_mean(data[start:end]))
    
    # Detrend the data
    detrended = [data[i] - trend[i] for i in range(n)]
    
    # Simple seasonal component
    seasonal = []
    for i in range(n):
        season_idx = i % period
        season_values = [detrended[j] for j in range(season_idx, n, period)]
        seasonal.append(arithmetic_mean(season_values))
    
    # Residual component
    residual = [data[i] - trend[i] - seasonal[i] for i in range(n)]
    
    return trend, seasonal, residual 