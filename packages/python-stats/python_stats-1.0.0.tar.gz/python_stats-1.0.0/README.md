# py-stats

[![PyPI version](https://badge.fury.io/py/python-stats.svg)](https://badge.fury.io/py/python-stats)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Status: Complete](https://img.shields.io/badge/status-complete-brightgreen.svg)](https://github.com/RanaEhtashamAli/py-stats)
[![Functions: 60+](https://img.shields.io/badge/functions-60+-orange.svg)](https://github.com/RanaEhtashamAli/py-stats)
[![Educational](https://img.shields.io/badge/educational-focus-blue.svg)](https://github.com/RanaEhtashamAli/py-stats)

A pure-Python module providing comprehensive statistics functions similar to those found on scientific calculators. This package offers over 60 statistics functions for both univariate and multivariate analysis.

**Educational Focus**: Perfect for learning statistics, programming, and data science with clear mathematical implementations and comprehensive examples.

## 📊 Project Status

✅ **Complete and Ready for Use**

- **Version**: 2.0.0
- **Functions**: 60+ statistical functions implemented
- **Testing**: 100% test coverage with comprehensive unit tests
- **Documentation**: Complete with examples and mathematical formulas
- **Educational Value**: High-quality learning resource
- **License**: MIT License (permissive and open)
- **Repository**: [GitHub](https://github.com/RanaEhtashamAli/py-stats)

## 🚀 Quick Links

- **📦 PyPI Package**: [python-stats on PyPI](https://pypi.org/project/python-stats/)
- **🐙 GitHub Repository**: [RanaEhtashamAli/py-stats](https://github.com/RanaEhtashamAli/py-stats)
- **📖 Documentation**: [README](https://github.com/RanaEhtashamAli/py-stats#readme)
- **🐛 Issues**: [GitHub Issues](https://github.com/RanaEhtashamAli/py-stats/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/RanaEhtashamAli/py-stats/discussions)

## 📋 Table of Contents

- [Project Status](#-project-status)
- [Quick Links](#-quick-links)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Package Structure](#-package-structure)
- [Requirements](#requirements)
- [Testing](#testing)
- [Performance Notes](#performance-notes)
- [Educational Focus](#-educational-focus)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#-acknowledgments)
- [Support](#-support)

## Features

### Univariate Statistics
- **Means**: arithmetic, harmonic, geometric, and quadratic means
- **Central Tendency**: median, mode, midrange, trimean
- **Angular Statistics**: mean of angular quantities
- **Averages**: running and weighted averages
- **Quantiles**: quartiles, hinges, and quantiles
- **Dispersion**: variance and standard deviation (sample and population)
- **Deviation Measures**: average deviation and median average deviation (MAD)
- **Shape**: skewness and kurtosis
- **Error**: standard error of the mean
- **Robust Statistics**: winsorized mean, trimmed mean, interquartile range, range, coefficient of variation
- **Order Statistics**: percentile rank, deciles, percentiles
- **Shape and Distribution**: coefficient of skewness, coefficient of kurtosis, normality test
- **Central Tendency Alternatives**: winsorized median, midhinge
- **Probability and Distribution**: z-score, t-score, percentile from z-score, confidence intervals
- **Time Series**: moving average, exponential smoothing, seasonal decomposition

### Multivariate Statistics
- **Correlation**: Pearson's, Spearman's, Kendall's tau, Q-correlation, point-biserial correlation
- **Covariance**: sample and population covariance
- **Regression**: simple linear, multiple linear, polynomial regression, residual analysis
- **Sums**: Sxx, Syy, and Sxy calculations
- **Association Measures**: chi-square test, Cramer's V, contingency coefficient

## Installation

### From PyPI (Recommended)
```bash
pip install python-stats
```

### From GitHub
```bash
pip install git+https://github.com/RanaEhtashamAli/py-stats.git
```

### Development Installation
```bash
git clone https://github.com/RanaEhtashamAli/py-stats.git
cd py-stats
pip install -e .
```

## Quick Start

```python
import py_stats as ps

# Basic statistics
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"Mean: {ps.arithmetic_mean(data)}")
print(f"Median: {ps.median(data)}")
print(f"Standard Deviation: {ps.standard_deviation(data)}")

# Robust statistics
print(f"IQR: {ps.interquartile_range(data)}")
print(f"Coefficient of Variation: {ps.coefficient_of_variation(data)}")

# Multivariate analysis
x = [1, 2, 3, 4, 5]
y = [2, 4, 5, 4, 5]
print(f"Pearson Correlation: {ps.pearson_correlation(x, y)}")
print(f"Spearman Correlation: {ps.spearman_correlation(x, y)}")

# Regression
slope, intercept, r_squared = ps.linear_regression(x, y)
print(f"Regression: y = {slope:.2f}x + {intercept:.2f}, R² = {r_squared:.3f}")
```

## Documentation

### Univariate Functions

#### Means
- `arithmetic_mean(data)`: Arithmetic mean
- `harmonic_mean(data)`: Harmonic mean
- `geometric_mean(data)`: Geometric mean
- `quadratic_mean(data)`: Quadratic mean (RMS)

#### Central Tendency
- `median(data)`: Median
- `mode(data)`: Mode
- `midrange(data)`: Midrange
- `trimean(data)`: Trimean

#### Quantiles
- `quartiles(data)`: First, second, and third quartiles
- `hinges(data)`: Lower and upper hinges
- `quantile(data, q)`: Quantile at specified probability

#### Dispersion
- `variance(data, population=False)`: Variance (sample or population)
- `standard_deviation(data, population=False)`: Standard deviation
- `average_deviation(data)`: Average absolute deviation
- `median_absolute_deviation(data)`: Median absolute deviation (MAD)

#### Shape
- `skewness(data)`: Skewness coefficient
- `kurtosis(data)`: Kurtosis coefficient

#### Robust Statistics
- `winsorized_mean(data, percent=10.0)`: Winsorized mean
- `trimmed_mean(data, percent=10.0)`: Trimmed mean
- `interquartile_range(data)`: Interquartile range (IQR)
- `range_value(data)`: Range (max - min)
- `coefficient_of_variation(data)`: Coefficient of variation

#### Order Statistics
- `percentile_rank(data, value)`: Percentile rank of a value
- `deciles(data)`: All deciles (10th, 20th, ..., 90th percentiles)
- `percentile(data, p)`: pth percentile (0-100)

#### Shape and Distribution
- `coefficient_of_skewness(data)`: Standardized skewness
- `coefficient_of_kurtosis(data)`: Standardized kurtosis
- `simple_normality_test(data)`: Basic normality test

#### Central Tendency Alternatives
- `winsorized_median(data, percent=10.0)`: Winsorized median
- `midhinge(data)`: Midhinge

#### Probability and Distribution
- `z_score(data, value)`: Z-score of a value
- `t_score(data, value)`: T-score of a value
- `percentile_from_z_score(z)`: Percentile from z-score
- `confidence_interval_mean(data, confidence=0.95)`: Confidence interval for mean
- `confidence_interval_proportion(successes, total, confidence=0.95)`: Confidence interval for proportion

#### Time Series
- `moving_average(data, window=3)`: Simple moving average
- `exponential_smoothing(data, alpha=0.3)`: Exponential smoothing
- `seasonal_decomposition_simple(data, period=4)`: Simple seasonal decomposition

#### Specialized
- `angular_mean(data, degrees=True)`: Mean of angular quantities
- `running_average(data, window=3)`: Running average
- `weighted_average(data, weights)`: Weighted average
- `standard_error_mean(data)`: Standard error of the mean

### Multivariate Functions

#### Correlation
- `pearson_correlation(x, y)`: Pearson's correlation coefficient
- `spearman_correlation(x, y)`: Spearman's rank correlation
- `kendall_tau(x, y)`: Kendall's tau correlation
- `q_correlation(x, y)`: Q-correlation coefficient
- `point_biserial_correlation(x, y)`: Point-biserial correlation

#### Covariance
- `covariance(x, y, population=False)`: Covariance (sample or population)

#### Regression
- `linear_regression(x, y)`: Simple linear regression
- `multiple_linear_regression(x_vars, y)`: Multiple linear regression
- `polynomial_regression(x, y, degree=2)`: Polynomial regression
- `residual_analysis(x, y)`: Residual analysis

#### Sums
- `sum_xx(x)`: Sum of squared deviations (Sxx)
- `sum_yy(y)`: Sum of squared deviations (Syy)
- `sum_xy(x, y)`: Sum of cross-products (Sxy)

#### Association Measures
- `chi_square_test(observed)`: Chi-square test of independence
- `cramers_v(observed)`: Cramer's V association measure
- `contingency_coefficient(observed)`: Contingency coefficient

## 📁 Package Structure

```
py-stats/
├── py_stats/
│   ├── __init__.py          # Package initialization (v2.0.0)
│   ├── univariate.py        # 40+ univariate functions
│   └── multivariate.py      # 20+ multivariate functions
├── tests/
│   ├── test_univariate.py   # Comprehensive univariate tests
│   └── test_multivariate.py # Comprehensive multivariate tests
├── examples/
│   ├── basic_usage.py       # Basic usage examples
│   └── advanced_usage.py    # Advanced usage examples
├── setup.py                 # Package configuration
├── pyproject.toml          # Modern packaging config
├── README.md               # This documentation
├── LICENSE                 # MIT License
└── .gitignore             # Git ignore patterns
```

## Requirements

- Python 3.7 or higher
- NumPy 1.19.0 or higher

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### License Summary

The MIT License is a permissive license that allows you to:
- ✅ Use the software for any purpose
- ✅ Modify the software
- ✅ Distribute the software
- ✅ Distribute modified versions
- ✅ Use it commercially

The only requirement is that the original license and copyright notice must be included in any substantial portions of the software.

## Contributing

We welcome contributions to make python-stats even better! Here's how you can help:

### 🤝 How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests for new functionality
4. **Run the tests**: `python -m pytest tests/ -v`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### 📋 Contribution Guidelines

- **Code Style**: Follow PEP 8 and use Black for formatting
- **Documentation**: Add docstrings for new functions
- **Tests**: Include tests for new functionality
- **Educational Focus**: Keep the educational value in mind
- **Mathematical Accuracy**: Ensure statistical formulas are correct

### 🐛 Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and environment details

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

## Performance Notes

This package is designed for educational purposes and small to medium-sized datasets. For large-scale data analysis, consider using NumPy, SciPy, or Pandas for better performance.

## 🎓 Educational Focus

This package is specifically designed for educational purposes and serves as an excellent resource for:

### 📚 Learning Applications
- **Statistics Courses**: Covers undergraduate statistics curriculum
- **Programming Education**: Demonstrates Python package development
- **Research Methods**: Practical statistical analysis tools
- **Data Science**: Foundation for more advanced analysis

### 🎯 Key Educational Features
- **Mathematical Transparency**: Clear implementation of statistical formulas
- **Comprehensive Examples**: Step-by-step usage demonstrations
- **Pure Python**: Easy to understand and modify
- **Well-Documented**: Detailed docstrings with mathematical explanations
- **Test-Driven**: All functions thoroughly tested for accuracy

### 💡 Use Cases
- **Classroom Teaching**: Interactive statistics demonstrations
- **Self-Learning**: Understanding statistical concepts through code
- **Research Projects**: Small-scale statistical analysis
- **Code Review**: Learning Python best practices
- **Portfolio Projects**: Showcasing statistical programming skills

The code is well-documented with clear mathematical formulas and examples, making it ideal for educational use.

## 🙏 Acknowledgments

- **NumPy**: For efficient numerical computations
- **Scientific Community**: For statistical formulas and methodologies
- **Open Source Community**: For inspiration and best practices
- **Educational Institutions**: For feedback and testing

## 📞 Support

If you have questions, suggestions, or need help:

- **Issues**: [GitHub Issues](https://github.com/RanaEhtashamAli/py-stats/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RanaEhtashamAli/py-stats/discussions)
- **Documentation**: This README and function docstrings
- **Examples**: Check the `examples/` directory for usage demonstrations

---

**Made with ❤️ for the educational community** 