"""
Tests for multivariate statistics functions.
"""

import pytest
from py_stats.multivariate import (
    pearson_correlation, q_correlation, covariance, linear_regression,
    sum_xx, sum_yy, sum_xy,
    # Additional correlation measures
    spearman_correlation, kendall_tau, point_biserial_correlation,
    # Advanced regression
    multiple_linear_regression, polynomial_regression, residual_analysis,
    # Association measures
    chi_square_test, cramers_v, contingency_coefficient
)


class TestCorrelation:
    """Test correlation functions."""
    
    def test_pearson_correlation(self):
        """Test Pearson correlation calculation."""
        # Perfect positive correlation
        assert pearson_correlation([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == 1.0
        
        # Perfect negative correlation
        assert pearson_correlation([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) == -1.0
        
        # No correlation
        assert abs(pearson_correlation([1, 2, 3, 4, 5], [1, 1, 1, 1, 1])) < 1e-10
        
        # Example from docstring
        assert abs(pearson_correlation([1, 2, 3, 4, 5], [2, 4, 5, 4, 5]) - 0.8) < 1e-10
        
    def test_pearson_correlation_mismatched_lengths(self):
        """Test Pearson correlation with mismatched lengths."""
        with pytest.raises(ValueError):
            pearson_correlation([1, 2, 3], [1, 2])
            
    def test_pearson_correlation_insufficient_data(self):
        """Test Pearson correlation with insufficient data."""
        with pytest.raises(ValueError):
            pearson_correlation([1], [2])
            
    def test_pearson_correlation_zero_variance(self):
        """Test Pearson correlation with zero variance."""
        assert pearson_correlation([1, 1, 1], [1, 2, 3]) == 0.0
        assert pearson_correlation([1, 2, 3], [1, 1, 1]) == 0.0
        
    def test_q_correlation(self):
        """Test Q-correlation calculation."""
        # Perfect positive correlation
        assert abs(q_correlation([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) - 1.0) < 1e-10
        
        # Perfect negative correlation
        assert abs(q_correlation([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) - (-1.0)) < 1e-10
        
        # Example from docstring
        assert abs(q_correlation([1, 2, 3, 4, 5], [2, 4, 5, 4, 5]) - 0.8) < 1e-10
        
    def test_q_correlation_mismatched_lengths(self):
        """Test Q-correlation with mismatched lengths."""
        with pytest.raises(ValueError):
            q_correlation([1, 2, 3, 4], [1, 2, 3])
            
    def test_q_correlation_insufficient_data(self):
        """Test Q-correlation with insufficient data."""
        with pytest.raises(ValueError):
            q_correlation([1, 2, 3], [1, 2, 3])


class TestCovariance:
    """Test covariance functions."""
    
    def test_covariance_sample(self):
        """Test sample covariance calculation."""
        # Example from docstring
        assert covariance([1, 2, 3, 4, 5], [2, 4, 5, 4, 5]) == 1.5
        
        # Zero covariance for uncorrelated data
        assert abs(covariance([1, 2, 3, 4, 5], [1, 1, 1, 1, 1])) < 1e-10
        
        # Positive covariance
        assert covariance([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) > 0
        
        # Negative covariance
        assert covariance([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) < 0
        
    def test_covariance_population(self):
        """Test population covariance calculation."""
        # Population covariance should be smaller than sample covariance
        sample_cov = covariance([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        pop_cov = covariance([1, 2, 3, 4, 5], [2, 4, 5, 4, 5], population=True)
        assert pop_cov < sample_cov
        
    def test_covariance_mismatched_lengths(self):
        """Test covariance with mismatched lengths."""
        with pytest.raises(ValueError):
            covariance([1, 2, 3], [1, 2])
            
    def test_covariance_insufficient_data(self):
        """Test covariance with insufficient data."""
        with pytest.raises(ValueError):
            covariance([1], [2])


class TestLinearRegression:
    """Test linear regression functions."""
    
    def test_linear_regression(self):
        """Test linear regression calculation."""
        # Perfect linear relationship
        slope, intercept, r_squared = linear_regression([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
        assert abs(slope - 2.0) < 1e-10
        assert abs(intercept - 0.0) < 1e-10
        assert abs(r_squared - 1.0) < 1e-10
        
        # Example from docstring
        slope, intercept, r_squared = linear_regression([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        assert abs(slope - 0.6) < 1e-10
        assert abs(intercept - 2.2) < 1e-10
        assert abs(r_squared - 0.64) < 1e-10
        
    def test_linear_regression_zero_variance_x(self):
        """Test linear regression with zero variance in x."""
        with pytest.raises(ValueError):
            linear_regression([1, 1, 1], [1, 2, 3])
            
    def test_linear_regression_zero_variance_y(self):
        """Test linear regression with zero variance in y."""
        slope, intercept, r_squared = linear_regression([1, 2, 3], [1, 1, 1])
        assert abs(slope - 0.0) < 1e-10
        assert abs(intercept - 1.0) < 1e-10
        assert abs(r_squared - 1.0) < 1e-10
        
    def test_linear_regression_mismatched_lengths(self):
        """Test linear regression with mismatched lengths."""
        with pytest.raises(ValueError):
            linear_regression([1, 2, 3], [1, 2])
            
    def test_linear_regression_insufficient_data(self):
        """Test linear regression with insufficient data."""
        with pytest.raises(ValueError):
            linear_regression([1], [2])


class TestSums:
    """Test sum functions."""
    
    def test_sum_xx(self):
        """Test sum_xx calculation."""
        # Example from docstring
        assert sum_xx([1, 2, 3, 4, 5]) == 10.0
        
        # Zero variance
        assert sum_xx([1, 1, 1]) == 0.0
        
        # Larger variance
        assert sum_xx([1, 5, 9]) > sum_xx([1, 2, 3])
        
    def test_sum_yy(self):
        """Test sum_yy calculation."""
        # Example from docstring
        assert sum_yy([2, 4, 5, 4, 5]) == 6.0
        
        # Zero variance
        assert sum_yy([1, 1, 1]) == 0.0
        
    def test_sum_xy(self):
        """Test sum_xy calculation."""
        # Example from docstring
        assert sum_xy([1, 2, 3, 4, 5], [2, 4, 5, 4, 5]) == 6.0
        
        # Zero when one variable has zero variance
        assert sum_xy([1, 2, 3], [1, 1, 1]) == 0.0
        assert sum_xy([1, 1, 1], [1, 2, 3]) == 0.0
        
        # Positive when variables are positively correlated
        assert sum_xy([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) > 0
        
        # Negative when variables are negatively correlated
        assert sum_xy([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) < 0
        
    def test_sum_xy_mismatched_lengths(self):
        """Test sum_xy with mismatched lengths."""
        with pytest.raises(ValueError):
            sum_xy([1, 2, 3], [1, 2])
            
    def test_sum_xy_insufficient_data(self):
        """Test sum_xy with insufficient data."""
        with pytest.raises(ValueError):
            sum_xy([], [])
            
    def test_sum_xx_insufficient_data(self):
        """Test sum_xx with insufficient data."""
        with pytest.raises(ValueError):
            sum_xx([])
            
    def test_sum_yy_insufficient_data(self):
        """Test sum_yy with insufficient data."""
        with pytest.raises(ValueError):
            sum_yy([])


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_identical_data(self):
        """Test functions with identical data."""
        data = [1, 2, 3, 4, 5]
        
        # Perfect correlation
        assert pearson_correlation(data, data) == 1.0
        assert abs(q_correlation(data, data) - 1.0) < 1e-10
        
        # Perfect regression
        slope, intercept, r_squared = linear_regression(data, data)
        assert abs(slope - 1.0) < 1e-10
        assert abs(intercept - 0.0) < 1e-10
        assert abs(r_squared - 1.0) < 1e-10
        
    def test_opposite_data(self):
        """Test functions with opposite data."""
        x = [1, 2, 3, 4, 5]
        y = [5, 4, 3, 2, 1]
        
        # Perfect negative correlation
        assert pearson_correlation(x, y) == -1.0
        assert abs(q_correlation(x, y) - (-1.0)) < 1e-10
        
        # Perfect negative regression
        slope, intercept, r_squared = linear_regression(x, y)
        assert abs(slope - (-1.0)) < 1e-10
        assert abs(intercept - 6.0) < 1e-10
        assert abs(r_squared - 1.0) < 1e-10
        
    def test_constant_data(self):
        """Test functions with constant data."""
        x = [1, 2, 3, 4, 5]
        y = [1, 1, 1, 1, 1]
        
        # Zero correlation
        assert pearson_correlation(x, y) == 0.0
        assert abs(q_correlation(x, y)) < 1e-10
        
        # Zero slope regression
        slope, intercept, r_squared = linear_regression(x, y)
        assert abs(slope - 0.0) < 1e-10
        assert abs(intercept - 1.0) < 1e-10
        assert abs(r_squared - 1.0) < 1e-10 


class TestAdditionalCorrelation:
    """Test additional correlation functions."""
    
    def test_spearman_correlation(self):
        """Test Spearman correlation calculation."""
        # Perfect positive correlation
        assert spearman_correlation([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == 1.0
        
        # Perfect negative correlation
        assert spearman_correlation([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) == -1.0
        
        # No correlation
        assert abs(spearman_correlation([1, 2, 3, 4, 5], [1, 1, 1, 1, 1])) < 1e-10
        
        # Example with ties
        assert abs(spearman_correlation([1, 2, 2, 3, 4], [1, 2, 3, 3, 4]) - 0.8) < 0.1
        
    def test_spearman_correlation_mismatched_lengths(self):
        """Test Spearman correlation with mismatched lengths."""
        with pytest.raises(ValueError):
            spearman_correlation([1, 2, 3], [1, 2])
            
    def test_kendall_tau(self):
        """Test Kendall's tau calculation."""
        # Perfect positive correlation
        assert kendall_tau([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == 1.0
        
        # Perfect negative correlation
        assert kendall_tau([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) == -1.0
        
        # No correlation
        assert abs(kendall_tau([1, 2, 3, 4, 5], [1, 1, 1, 1, 1])) < 1e-10
        
        # Example with ties
        assert abs(kendall_tau([1, 2, 2, 3, 4], [1, 2, 3, 3, 4]) - 0.6) < 0.1
        
    def test_kendall_tau_mismatched_lengths(self):
        """Test Kendall's tau with mismatched lengths."""
        with pytest.raises(ValueError):
            kendall_tau([1, 2, 3], [1, 2])
            
    def test_point_biserial_correlation(self):
        """Test point-biserial correlation calculation."""
        # Perfect positive correlation
        continuous = [1, 2, 3, 4, 5]
        binary = [True, True, True, False, False]
        assert point_biserial_correlation(continuous, binary) > 0.8
        
        # Perfect negative correlation
        binary_neg = [False, False, True, True, True]
        assert point_biserial_correlation(continuous, binary_neg) < -0.8
        
        # No correlation
        binary_no_corr = [True, False, True, False, True]
        assert abs(point_biserial_correlation(continuous, binary_no_corr)) < 0.3
        
    def test_point_biserial_correlation_mismatched_lengths(self):
        """Test point-biserial correlation with mismatched lengths."""
        with pytest.raises(ValueError):
            point_biserial_correlation([1, 2, 3], [True, False])
            
    def test_point_biserial_correlation_invalid_binary(self):
        """Test point-biserial correlation with invalid binary data."""
        with pytest.raises(ValueError):
            point_biserial_correlation([1, 2, 3], [True, False, "maybe"])


class TestAdvancedRegression:
    """Test advanced regression functions."""
    
    def test_multiple_linear_regression(self):
        """Test multiple linear regression calculation."""
        # Simple case with two predictors
        x_vars = [[1, 2, 3, 4, 5], [1, 1, 2, 2, 3]]  # Two predictors
        y = [2, 4, 6, 8, 10]
        
        coefficients, intercept, r_squared = multiple_linear_regression(x_vars, y)
        
        assert len(coefficients) == 2
        assert abs(coefficients[0] - 2.0) < 0.1  # First predictor coefficient
        assert abs(coefficients[1] - 0.0) < 0.1  # Second predictor coefficient
        assert abs(intercept - 0.0) < 0.1
        assert abs(r_squared - 1.0) < 0.1
        
    def test_multiple_linear_regression_mismatched_lengths(self):
        """Test multiple linear regression with mismatched lengths."""
        x_vars = [[1, 2, 3], [1, 2, 3]]
        y = [1, 2]
        with pytest.raises(ValueError):
            multiple_linear_regression(x_vars, y)
            
    def test_multiple_linear_regression_insufficient_data(self):
        """Test multiple linear regression with insufficient data."""
        x_vars = [[1, 2], [1, 2]]
        y = [1, 2]
        with pytest.raises(ValueError):
            multiple_linear_regression(x_vars, y)
            
    def test_polynomial_regression(self):
        """Test polynomial regression calculation."""
        x = [1, 2, 3, 4, 5]
        y = [1, 4, 9, 16, 25]  # Perfect quadratic relationship
        
        coefficients, r_squared = polynomial_regression(x, y, degree=2)
        
        assert len(coefficients) == 3  # ax² + bx + c
        assert abs(coefficients[0] - 1.0) < 0.1  # a coefficient
        assert abs(coefficients[1] - 0.0) < 0.1  # b coefficient
        assert abs(coefficients[2] - 0.0) < 0.1  # c coefficient
        assert abs(r_squared - 1.0) < 0.1
        
    def test_polynomial_regression_degree_1(self):
        """Test polynomial regression with degree 1 (linear)."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]  # Perfect linear relationship
        
        coefficients, r_squared = polynomial_regression(x, y, degree=1)
        
        assert len(coefficients) == 2  # ax + b
        assert abs(coefficients[0] - 2.0) < 0.1  # slope
        assert abs(coefficients[1] - 0.0) < 0.1  # intercept
        assert abs(r_squared - 1.0) < 0.1
        
    def test_polynomial_regression_invalid_degree(self):
        """Test polynomial regression with invalid degree."""
        x = [1, 2, 3, 4, 5]
        y = [1, 2, 3, 4, 5]
        
        with pytest.raises(ValueError):
            polynomial_regression(x, y, degree=0)
        with pytest.raises(ValueError):
            polynomial_regression(x, y, degree=5)  # Too high for 5 data points
            
    def test_residual_analysis(self):
        """Test residual analysis calculation."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]  # Perfect linear relationship
        
        residuals, r_squared, adj_r_squared = residual_analysis(x, y)
        
        assert len(residuals) == len(x)
        assert all(abs(r) < 1e-10 for r in residuals)  # Perfect fit
        assert abs(r_squared - 1.0) < 1e-10
        assert abs(adj_r_squared - 1.0) < 1e-10
        
    def test_residual_analysis_imperfect_fit(self):
        """Test residual analysis with imperfect fit."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 5, 8, 9]  # Imperfect linear relationship
        
        residuals, r_squared, adj_r_squared = residual_analysis(x, y)
        
        assert len(residuals) == len(x)
        assert not all(abs(r) < 1e-10 for r in residuals)  # Imperfect fit
        assert 0.0 < r_squared < 1.0
        assert adj_r_squared <= r_squared
        
    def test_residual_analysis_mismatched_lengths(self):
        """Test residual analysis with mismatched lengths."""
        with pytest.raises(ValueError):
            residual_analysis([1, 2, 3], [1, 2])


class TestAssociationMeasures:
    """Test association measures functions."""
    
    def test_chi_square_test(self):
        """Test chi-square test calculation."""
        # Example 2x3 contingency table
        observed = [[10, 20, 30], [15, 25, 35]]
        
        chi_sq, p_value, df = chi_square_test(observed)
        
        assert chi_sq > 0  # Chi-square statistic should be positive
        assert 0.0 <= p_value <= 1.0  # p-value should be between 0 and 1
        assert df == 2  # (rows-1) * (cols-1) = (2-1) * (3-1) = 2
        
    def test_chi_square_test_independence(self):
        """Test chi-square test with independent data."""
        # Independent data (no association)
        observed = [[10, 10, 10], [10, 10, 10]]
        
        chi_sq, p_value, df = chi_square_test(observed)
        
        assert abs(chi_sq) < 1e-10  # Should be close to 0 for independence
        assert p_value > 0.05  # Should not reject null hypothesis
        
    def test_chi_square_test_dependence(self):
        """Test chi-square test with dependent data."""
        # Dependent data (strong association)
        observed = [[20, 10, 5], [5, 10, 20]]
        
        chi_sq, p_value, df = chi_square_test(observed)
        
        assert chi_sq > 10  # Should be large for strong association
        assert p_value < 0.05  # Should reject null hypothesis
        
    def test_chi_square_test_invalid_table(self):
        """Test chi-square test with invalid table."""
        # Empty table
        with pytest.raises(ValueError):
            chi_square_test([])
            
        # Single row
        with pytest.raises(ValueError):
            chi_square_test([[1, 2, 3]])
            
        # Single column
        with pytest.raises(ValueError):
            chi_square_test([[1], [2]])
            
        # Unequal row lengths
        with pytest.raises(ValueError):
            chi_square_test([[1, 2, 3], [1, 2]])
            
        # Zero frequencies
        with pytest.raises(ValueError):
            chi_square_test([[0, 0, 0], [0, 0, 0]])
            
    def test_cramers_v(self):
        """Test Cramer's V calculation."""
        # Strong association
        observed = [[20, 10, 5], [5, 10, 20]]
        cramer_v = cramers_v(observed)
        
        assert 0.0 <= cramer_v <= 1.0  # Cramer's V is between 0 and 1
        assert cramer_v > 0.5  # Should be high for strong association
        
        # No association
        observed = [[10, 10, 10], [10, 10, 10]]
        cramer_v = cramers_v(observed)
        
        assert abs(cramer_v) < 1e-10  # Should be close to 0 for independence
        
    def test_cramers_v_edge_cases(self):
        """Test Cramer's V edge cases."""
        # 2x2 table
        observed = [[10, 20], [15, 25]]
        cramer_v = cramers_v(observed)
        assert 0.0 <= cramer_v <= 1.0
        
        # Invalid table
        with pytest.raises(ValueError):
            cramers_v([])
            
    def test_contingency_coefficient(self):
        """Test contingency coefficient calculation."""
        # Strong association
        observed = [[20, 10, 5], [5, 10, 20]]
        coeff = contingency_coefficient(observed)
        
        assert 0.0 <= coeff <= 1.0  # Contingency coefficient is between 0 and 1
        assert coeff > 0.3  # Should be moderate to high for strong association
        
        # No association
        observed = [[10, 10, 10], [10, 10, 10]]
        coeff = contingency_coefficient(observed)
        
        assert abs(coeff) < 1e-10  # Should be close to 0 for independence
        
    def test_contingency_coefficient_edge_cases(self):
        """Test contingency coefficient edge cases."""
        # 2x2 table
        observed = [[10, 20], [15, 25]]
        coeff = contingency_coefficient(observed)
        assert 0.0 <= coeff <= 1.0
        
        # Invalid table
        with pytest.raises(ValueError):
            contingency_coefficient([]) 