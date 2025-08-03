"""
Tests for univariate statistics functions.
"""

import pytest
import math
from py_stats.univariate import (
    arithmetic_mean, harmonic_mean, geometric_mean, quadratic_mean,
    median, mode, midrange, trimean, quartiles, hinges, quantile,
    variance, standard_deviation, average_deviation, median_absolute_deviation,
    skewness, kurtosis, angular_mean, running_average, weighted_average,
    standard_error_mean,
    # Robust statistics
    winsorized_mean, trimmed_mean, interquartile_range, range_value, coefficient_of_variation,
    # Order statistics
    percentile_rank, deciles, percentile,
    # Shape and distribution
    coefficient_of_skewness, coefficient_of_kurtosis, simple_normality_test,
    # Central tendency alternatives
    winsorized_median, midhinge,
    # Probability and distribution
    z_score, t_score, percentile_from_z_score, confidence_interval_mean, confidence_interval_proportion,
    # Time series
    moving_average, exponential_smoothing, seasonal_decomposition_simple
)


class TestMeans:
    """Test mean functions."""
    
    def test_arithmetic_mean(self):
        """Test arithmetic mean calculation."""
        assert arithmetic_mean([1, 2, 3, 4, 5]) == 3.0
        assert arithmetic_mean([10, 20, 30]) == 20.0
        assert arithmetic_mean([1.5, 2.5, 3.5]) == 2.5
        
    def test_harmonic_mean(self):
        """Test harmonic mean calculation."""
        assert harmonic_mean([1, 2, 4]) == 2.0
        assert harmonic_mean([2, 3, 6]) == 3.0
        assert harmonic_mean([1, 1, 1]) == 1.0
        
    def test_harmonic_mean_negative_error(self):
        """Test harmonic mean with negative values."""
        with pytest.raises(ValueError):
            harmonic_mean([1, -2, 3])
            
    def test_geometric_mean(self):
        """Test geometric mean calculation."""
        assert geometric_mean([1, 2, 4]) == 2.0
        assert geometric_mean([2, 8, 32]) == 8.0
        assert geometric_mean([1, 1, 1]) == 1.0
        
    def test_geometric_mean_negative_error(self):
        """Test geometric mean with negative values."""
        with pytest.raises(ValueError):
            geometric_mean([1, -2, 3])
            
    def test_quadratic_mean(self):
        """Test quadratic mean calculation."""
        assert abs(quadratic_mean([1, 2, 3, 4, 5]) - 3.3166247903554) < 1e-10
        assert abs(quadratic_mean([1, 2, 3]) - 2.160246899469287) < 1e-10


class TestCentralTendency:
    """Test central tendency measures."""
    
    def test_median(self):
        """Test median calculation."""
        assert median([1, 3, 5, 7, 9]) == 5.0
        assert median([1, 2, 3, 4]) == 2.5
        assert median([1]) == 1.0
        
    def test_mode(self):
        """Test mode calculation."""
        assert mode([1, 2, 2, 3, 4]) == [2.0]
        assert mode([1, 1, 2, 2, 3]) == [1.0, 2.0]
        assert mode([1, 2, 3]) == [1.0, 2.0, 3.0]
        
    def test_midrange(self):
        """Test midrange calculation."""
        assert midrange([1, 2, 3, 4, 5]) == 3.0
        assert midrange([10, 20, 30]) == 20.0
        assert midrange([1]) == 1.0
        
    def test_trimean(self):
        """Test trimean calculation."""
        assert trimean([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 5.5
        assert trimean([1, 2, 3, 4, 5]) == 3.0


class TestQuantiles:
    """Test quantile functions."""
    
    def test_quartiles(self):
        """Test quartile calculation."""
        q1, q2, q3 = quartiles([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert q1 == 3.0
        assert q2 == 5.5
        assert q3 == 8.0
        
    def test_hinges(self):
        """Test hinge calculation."""
        lower, upper = hinges([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert lower == 3.0
        assert upper == 8.0
        
    def test_quantile(self):
        """Test quantile calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert quantile(data, 0.25) == 3.0
        assert quantile(data, 0.5) == 5.5
        assert quantile(data, 0.75) == 8.0
        assert quantile(data, 0.0) == 1.0
        assert quantile(data, 1.0) == 10.0
        
    def test_quantile_invalid_probability(self):
        """Test quantile with invalid probability."""
        with pytest.raises(ValueError):
            quantile([1, 2, 3], 1.5)
        with pytest.raises(ValueError):
            quantile([1, 2, 3], -0.1)


class TestDispersion:
    """Test dispersion measures."""
    
    def test_variance_sample(self):
        """Test sample variance calculation."""
        assert variance([1, 2, 3, 4, 5]) == 2.5
        assert variance([1, 2, 3]) == 1.0
        
    def test_variance_population(self):
        """Test population variance calculation."""
        assert variance([1, 2, 3, 4, 5], population=True) == 2.0
        assert variance([1, 2, 3], population=True) == 0.6666666666666666
        
    def test_standard_deviation_sample(self):
        """Test sample standard deviation calculation."""
        assert abs(standard_deviation([1, 2, 3, 4, 5]) - 1.5811388300841898) < 1e-10
        
    def test_standard_deviation_population(self):
        """Test population standard deviation calculation."""
        assert abs(standard_deviation([1, 2, 3, 4, 5], population=True) - 1.4142135623730951) < 1e-10
        
    def test_average_deviation(self):
        """Test average deviation calculation."""
        assert average_deviation([1, 2, 3, 4, 5]) == 1.2
        assert average_deviation([1, 1, 1]) == 0.0
        
    def test_median_absolute_deviation(self):
        """Test median absolute deviation calculation."""
        assert median_absolute_deviation([1, 2, 3, 4, 5]) == 1.0
        assert median_absolute_deviation([1, 1, 1]) == 0.0


class TestShape:
    """Test shape measures."""
    
    def test_skewness(self):
        """Test skewness calculation."""
        # Symmetric data should have skewness close to 0
        assert abs(skewness([1, 2, 3, 4, 5])) < 1e-10
        # Right-skewed data
        assert skewness([1, 2, 3, 4, 10]) > 0
        # Left-skewed data
        assert skewness([1, 7, 8, 9, 10]) < 0
        
    def test_kurtosis(self):
        """Test kurtosis calculation."""
        # Normal-like data should have kurtosis close to 0
        assert abs(kurtosis([1, 2, 3, 4, 5])) < 1.5
        # Data with outliers should have higher kurtosis
        assert kurtosis([1, 2, 3, 4, 20]) > 0
        
    def test_skewness_insufficient_data(self):
        """Test skewness with insufficient data."""
        with pytest.raises(ValueError):
            skewness([1, 2])
            
    def test_kurtosis_insufficient_data(self):
        """Test kurtosis with insufficient data."""
        with pytest.raises(ValueError):
            kurtosis([1, 2, 3])


class TestSpecialized:
    """Test specialized functions."""
    
    def test_angular_mean_degrees(self):
        """Test angular mean in degrees."""
        assert abs(angular_mean([0, 90, 180, 270]) - 180.0) < 1e-10
        assert abs(angular_mean([0, 120, 240]) - 120.0) < 1e-10
        
    def test_angular_mean_radians(self):
        """Test angular mean in radians."""
        angles_rad = [0, math.pi/2, math.pi, 3*math.pi/2]
        assert abs(angular_mean(angles_rad, degrees=False) - math.pi) < 1e-10
        
    def test_running_average(self):
        """Test running average calculation."""
        result = running_average([1, 2, 3, 4, 5], 3)
        assert result == [2.0, 3.0, 4.0]
        
        result = running_average([1, 2, 3, 4, 5], 2)
        assert result == [1.5, 2.5, 3.5, 4.5]
        
    def test_running_average_invalid_window(self):
        """Test running average with invalid window."""
        with pytest.raises(ValueError):
            running_average([1, 2, 3], 0)
        with pytest.raises(ValueError):
            running_average([1, 2, 3], 4)
            
    def test_weighted_average(self):
        """Test weighted average calculation."""
        assert weighted_average([1, 2, 3], [1, 2, 1]) == 2.0
        assert weighted_average([10, 20, 30], [1, 1, 1]) == 20.0
        assert weighted_average([1, 2], [3, 1]) == 1.25
        
    def test_weighted_average_mismatched_lengths(self):
        """Test weighted average with mismatched lengths."""
        with pytest.raises(ValueError):
            weighted_average([1, 2, 3], [1, 2])
            
    def test_weighted_average_negative_weights(self):
        """Test weighted average with negative weights."""
        with pytest.raises(ValueError):
            weighted_average([1, 2, 3], [1, -2, 1])
            
    def test_standard_error_mean(self):
        """Test standard error of the mean calculation."""
        assert abs(standard_error_mean([1, 2, 3, 4, 5]) - 0.7071067811865476) < 1e-10
        assert abs(standard_error_mean([1, 2, 3]) - 0.5773502691896258) < 1e-10
        
    def test_standard_error_mean_insufficient_data(self):
        """Test standard error with insufficient data."""
        with pytest.raises(ValueError):
            standard_error_mean([1])


class TestRobustStatistics:
    """Test robust statistics functions."""
    
    def test_winsorized_mean(self):
        """Test winsorized mean calculation."""
        data = [1, 2, 3, 4, 5, 100, 200]
        assert abs(winsorized_mean(data, 10) - 3.0) < 1e-10  # 10% winsorization
        assert abs(winsorized_mean(data, 20) - 3.0) < 1e-10  # 20% winsorization
        
    def test_winsorized_mean_edge_cases(self):
        """Test winsorized mean edge cases."""
        data = [1, 2, 3, 4, 5]
        assert winsorized_mean(data, 0) == arithmetic_mean(data)
        assert winsorized_mean(data, 50) == median(data)
        
    def test_trimmed_mean(self):
        """Test trimmed mean calculation."""
        data = [1, 2, 3, 4, 5, 100, 200]
        assert abs(trimmed_mean(data, 10) - 3.0) < 1e-10  # 10% trimming
        assert abs(trimmed_mean(data, 20) - 3.0) < 1e-10  # 20% trimming
        
    def test_trimmed_mean_edge_cases(self):
        """Test trimmed mean edge cases."""
        data = [1, 2, 3, 4, 5]
        assert trimmed_mean(data, 0) == arithmetic_mean(data)
        
    def test_interquartile_range(self):
        """Test interquartile range calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert interquartile_range(data) == 5.0  # Q3 - Q1 = 8 - 3 = 5
        
    def test_range_value(self):
        """Test range calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert range_value(data) == 9.0  # max - min = 10 - 1 = 9
        
    def test_coefficient_of_variation(self):
        """Test coefficient of variation calculation."""
        data = [1, 2, 3, 4, 5]
        cv = coefficient_of_variation(data)
        expected_cv = standard_deviation(data) / arithmetic_mean(data)
        assert abs(cv - expected_cv) < 1e-10
        
    def test_coefficient_of_variation_zero_mean(self):
        """Test coefficient of variation with zero mean."""
        with pytest.raises(ValueError):
            coefficient_of_variation([0, 0, 0])


class TestOrderStatistics:
    """Test order statistics functions."""
    
    def test_percentile_rank(self):
        """Test percentile rank calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert percentile_rank(data, 5) == 40.0  # 5 is at 40th percentile
        assert percentile_rank(data, 8) == 70.0  # 8 is at 70th percentile
        assert percentile_rank(data, 1) == 0.0   # 1 is at 0th percentile
        assert percentile_rank(data, 10) == 100.0  # 10 is at 100th percentile
        
    def test_percentile_rank_value_not_in_data(self):
        """Test percentile rank with value not in data."""
        data = [1, 2, 3, 4, 5]
        assert percentile_rank(data, 2.5) == 25.0  # 2.5 is between 2 and 3
        
    def test_deciles(self):
        """Test deciles calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        deciles_result = deciles(data)
        assert len(deciles_result) == 9  # 10th through 90th percentiles
        assert deciles_result[0] == 1.5   # 10th percentile
        assert deciles_result[4] == 5.5   # 50th percentile (median)
        assert deciles_result[8] == 9.5   # 90th percentile
        
    def test_percentile(self):
        """Test percentile calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert percentile(data, 25) == 3.0   # 25th percentile
        assert percentile(data, 50) == 5.5   # 50th percentile (median)
        assert percentile(data, 75) == 8.0   # 75th percentile
        assert percentile(data, 0) == 1.0    # 0th percentile (min)
        assert percentile(data, 100) == 10.0  # 100th percentile (max)
        
    def test_percentile_invalid_p(self):
        """Test percentile with invalid p value."""
        with pytest.raises(ValueError):
            percentile([1, 2, 3], -1)
        with pytest.raises(ValueError):
            percentile([1, 2, 3], 101)


class TestShapeAndDistribution:
    """Test shape and distribution functions."""
    
    def test_coefficient_of_skewness(self):
        """Test coefficient of skewness calculation."""
        data = [1, 2, 3, 4, 5]
        coef_skew = coefficient_of_skewness(data)
        # For symmetric data, coefficient should be close to 0
        assert abs(coef_skew) < 0.1
        
    def test_coefficient_of_kurtosis(self):
        """Test coefficient of kurtosis calculation."""
        data = [1, 2, 3, 4, 5]
        coef_kurt = coefficient_of_kurtosis(data)
        # For normal-like data, coefficient should be close to 0
        assert abs(coef_kurt) < 2.0
        
    def test_simple_normality_test(self):
        """Test simple normality test."""
        # Normal-like data
        normal_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert simple_normality_test(normal_data) == True
        
        # Skewed data
        skewed_data = [1, 1, 1, 2, 2, 3, 4, 5, 10, 20]
        assert simple_normality_test(skewed_data) == False
        
    def test_simple_normality_test_insufficient_data(self):
        """Test normality test with insufficient data."""
        with pytest.raises(ValueError):
            simple_normality_test([1, 2, 3])


class TestCentralTendencyAlternatives:
    """Test central tendency alternative functions."""
    
    def test_winsorized_median(self):
        """Test winsorized median calculation."""
        data = [1, 2, 3, 4, 5, 100, 200]
        assert winsorized_median(data, 10) == 3.0  # 10% winsorization
        assert winsorized_median(data, 20) == 3.0  # 20% winsorization
        
    def test_midhinge(self):
        """Test midhinge calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        midhinge_val = midhinge(data)
        lower_hinge, upper_hinge = hinges(data)
        expected = (lower_hinge + upper_hinge) / 2
        assert abs(midhinge_val - expected) < 1e-10


class TestProbabilityAndDistribution:
    """Test probability and distribution functions."""
    
    def test_z_score(self):
        """Test z-score calculation."""
        data = [1, 2, 3, 4, 5]
        z = z_score(data, 3)
        assert abs(z - 0.0) < 1e-10  # 3 is the mean, so z-score should be 0
        
        z = z_score(data, 5)
        assert z > 0  # 5 is above the mean
        
        z = z_score(data, 1)
        assert z < 0  # 1 is below the mean
        
    def test_t_score(self):
        """Test t-score calculation."""
        data = [1, 2, 3, 4, 5]
        t = t_score(data, 3)
        assert abs(t - 50.0) < 1e-10  # 3 is the mean, so t-score should be 50
        
    def test_percentile_from_z_score(self):
        """Test percentile from z-score calculation."""
        # Z-score of 0 corresponds to 50th percentile
        assert abs(percentile_from_z_score(0) - 50.0) < 1e-10
        
        # Z-score of 1 corresponds to ~84th percentile
        assert abs(percentile_from_z_score(1) - 84.13) < 1.0
        
        # Z-score of -1 corresponds to ~16th percentile
        assert abs(percentile_from_z_score(-1) - 15.87) < 1.0
        
    def test_confidence_interval_mean(self):
        """Test confidence interval for mean calculation."""
        data = [1, 2, 3, 4, 5]
        ci_lower, ci_upper = confidence_interval_mean(data, 0.95)
        mean_val = arithmetic_mean(data)
        assert ci_lower < mean_val < ci_upper
        
        # Test with different confidence levels
        ci_lower_90, ci_upper_90 = confidence_interval_mean(data, 0.90)
        ci_lower_99, ci_upper_99 = confidence_interval_mean(data, 0.99)
        
        # Higher confidence should give wider intervals
        assert (ci_upper_99 - ci_lower_99) > (ci_upper - ci_lower) > (ci_upper_90 - ci_lower_90)
        
    def test_confidence_interval_proportion(self):
        """Test confidence interval for proportion calculation."""
        ci_lower, ci_upper = confidence_interval_proportion(8, 10, 0.95)
        assert 0.0 < ci_lower < ci_upper < 1.0
        
        # Test edge cases
        ci_lower, ci_upper = confidence_interval_proportion(0, 10, 0.95)
        assert ci_lower == 0.0
        
        ci_lower, ci_upper = confidence_interval_proportion(10, 10, 0.95)
        assert ci_upper == 1.0
        
    def test_confidence_interval_proportion_invalid_inputs(self):
        """Test confidence interval for proportion with invalid inputs."""
        with pytest.raises(ValueError):
            confidence_interval_proportion(-1, 10, 0.95)
        with pytest.raises(ValueError):
            confidence_interval_proportion(11, 10, 0.95)
        with pytest.raises(ValueError):
            confidence_interval_proportion(5, 0, 0.95)


class TestTimeSeries:
    """Test time series functions."""
    
    def test_moving_average(self):
        """Test moving average calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        ma = moving_average(data, window=3)
        assert len(ma) == 8  # 10 - 3 + 1 = 8
        assert ma[0] == 2.0  # (1+2+3)/3
        assert ma[1] == 3.0  # (2+3+4)/3
        assert ma[-1] == 9.0  # (8+9+10)/3
        
    def test_moving_average_edge_cases(self):
        """Test moving average edge cases."""
        data = [1, 2, 3]
        ma = moving_average(data, window=3)
        assert ma == [2.0]
        
        with pytest.raises(ValueError):
            moving_average(data, window=4)
        with pytest.raises(ValueError):
            moving_average(data, window=0)
            
    def test_exponential_smoothing(self):
        """Test exponential smoothing calculation."""
        data = [1, 2, 3, 4, 5]
        smoothed = exponential_smoothing(data, alpha=0.3)
        assert len(smoothed) == len(data)
        assert smoothed[0] == data[0]  # First value should be unchanged
        assert all(isinstance(x, (int, float)) for x in smoothed)
        
    def test_exponential_smoothing_alpha_limits(self):
        """Test exponential smoothing with alpha limits."""
        data = [1, 2, 3, 4, 5]
        
        # Alpha = 0 should give constant values
        smoothed_0 = exponential_smoothing(data, alpha=0)
        assert all(abs(x - smoothed_0[0]) < 1e-10 for x in smoothed_0)
        
        # Alpha = 1 should give original data
        smoothed_1 = exponential_smoothing(data, alpha=1)
        assert all(abs(smoothed_1[i] - data[i]) < 1e-10 for i in range(len(data)))
        
    def test_exponential_smoothing_invalid_alpha(self):
        """Test exponential smoothing with invalid alpha."""
        with pytest.raises(ValueError):
            exponential_smoothing([1, 2, 3], alpha=-0.1)
        with pytest.raises(ValueError):
            exponential_smoothing([1, 2, 3], alpha=1.1)
            
    def test_seasonal_decomposition_simple(self):
        """Test simple seasonal decomposition."""
        # Create seasonal data with period 4
        data = [10, 15, 20, 25, 12, 17, 22, 27, 14, 19, 24, 29]
        trend, seasonal, residual = seasonal_decomposition_simple(data, period=4)
        
        assert len(trend) == len(data)
        assert len(seasonal) == len(data)
        assert len(residual) == len(data)
        
        # Check that decomposition components sum to original data
        for i in range(len(data)):
            assert abs(trend[i] + seasonal[i] + residual[i] - data[i]) < 1e-10
            
    def test_seasonal_decomposition_invalid_period(self):
        """Test seasonal decomposition with invalid period."""
        data = [1, 2, 3, 4, 5]
        with pytest.raises(ValueError):
            seasonal_decomposition_simple(data, period=0)
        with pytest.raises(ValueError):
            seasonal_decomposition_simple(data, period=6)


class TestValidation:
    """Test input validation."""
    
    def test_empty_data(self):
        """Test functions with empty data."""
        with pytest.raises(ValueError):
            arithmetic_mean([])
        with pytest.raises(ValueError):
            median([])
        with pytest.raises(ValueError):
            variance([])
            
    def test_non_numeric_data(self):
        """Test functions with non-numeric data."""
        with pytest.raises(ValueError):
            arithmetic_mean([1, "2", 3])
        with pytest.raises(ValueError):
            median([1, None, 3])
        with pytest.raises(ValueError):
            variance([1, [2], 3]) 