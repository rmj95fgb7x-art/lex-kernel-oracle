# Contributing to Adaptive Spectral Oracle

Thank you for your interest in contributing to the Adaptive Spectral Kernel Oracle project! This document provides guidelines for contributions.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contribution Areas](#contribution-areas)
5. [Pull Request Process](#pull-request-process)
6. [Coding Standards](#coding-standards)
7. [Testing Requirements](#testing-requirements)
8. [Documentation](#documentation)
9. [Patent & Licensing](#patent--licensing)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race
- Ethnicity
- Age
- Religion
- Nationality

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Publishing others' private information
- Other conduct that could be considered inappropriate in a professional setting

---

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- GitHub account
- (Optional) Node.js 16+ for React components
- (Optional) Solidity development environment for smart contracts

### First-Time Contributors

1. **Fork the repository** to your GitHub account
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/adaptive-spectral-oracle.git
   cd adaptive-spectral-oracle
   	1.	Add upstream remote:
git remote add upstream https://github.com/ORIGINAL_OWNER/adaptive-spectral-oracle.git
	2.	Create a branch for your contribution:
  git checkout -b feature/your-feature-name
Development Setup
Python Environment
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -e ".[dev,benchmark,viz]"

# Verify installation
python -c "from adaptive_spectral_oracle import AdaptiveSpectralKernel; print('Success!')"
Running Tests
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=adaptive_spectral_oracle --cov-report=html

# Run specific test file
pytest tests/test_kernels.py -v

# Run benchmarks
python benchmarks/benchmark_suite.py
Code Quality Checks
# Format code
black src/ tests/ benchmarks/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
Contribution Areas
We welcome contributions in the following areas:
1. Mathematical Extensions
Priority Areas:
	∙	Frequency-adaptive per-band weighting
	∙	Causal temporal kernels (Granger causality)
	∙	Multi-modal fusion (radar + thermal + acoustic)
	∙	Wavelet-based variants
Requirements:
	∙	Mathematical proof of convergence/robustness
	∙	Benchmark against base kernel
	∙	Documentation in docs/
Example:
class FrequencyAdaptiveKernel(AdaptiveSpectralKernel):
    """
    Per-frequency adaptive weighting.
    
    w_i(ω) = exp(-|D̂_i(ω) - D̂̃(ω)|²/τ(ω)²)
    """
    def fit(self, signals):
        # Implementation here
        pass
2. Domain Applications
Needed Verticals:
	∙	Energy sector (grid monitoring, oil & gas)
	∙	Telecom (5G/6G spectrum management)
	∙	Agriculture (IoT sensor fusion)
	∙	Smart cities (traffic, environmental sensors)
Requirements:
	∙	Real-world use case description
	∙	Test data generation for domain
	∙	Performance benchmarks
	∙	Documentation in README
3. Performance Optimization
Areas:
	∙	GPU acceleration (CUDA/OpenCL)
	∙	Distributed computing (Dask/Ray)
	∙	Embedded systems (ARM Cortex-M optimization)
	∙	Just-In-Time compilation (Numba)
Requirements:
	∙	Benchmark showing speedup
	∙	Maintain numerical accuracy
	∙	Cross-platform compatibility
4. Testing & Validation
Needed:
	∙	Additional test scenarios
	∙	Edge case coverage
	∙	Integration tests
	∙	Property-based testing (Hypothesis)
Example:
@given(st.integers(min_value=3, max_value=20))
def test_arbitrary_sensor_count(n_sensors):
    """Test with arbitrary number of sensors."""
    signals, truth = generate_synthetic_signals(
        n_clean=n_sensors, n_poisoned=0, T=128
    )
    kernel = AdaptiveSpectralKernel()
    result, weights = kernel.fit(signals)
    assert np.allclose(weights.sum(), 1.0)
Documentation
Needed:
	∙	Tutorial notebooks (Jupyter)
	∙	API reference improvements
	∙	Use case examples
	∙	Translation (non-English docs)
Pull Request Process
Before Submitting
	1.	Ensure tests pass:
    pytest tests/ -v
Format code:
black src/ tests/
flake8 src/ tests/
Update documentation:
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation update
- [ ] Breaking change

## Testing
Describe tests added/modified

## Benchmarks (if applicable)
Include performance metrics

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Documentation updated
Review Process
	1.	Maintainer will review within 3-5 business days
	2.	Address feedback in new commits
	3.	Once approved, maintainer will merge
	4.	Your contribution will be credited in CHANGELOG
Coding Standards
Python Style
Follow PEP 8 with these specifics:
Line Length: 100 characters (not 80)
Imports:
# Standard library
import os
import sys

# Third-party
import numpy as np
from scipy.fft import fft

# Local
from adaptive_spectral_oracle import AdaptiveSpectralKernel
# Standard library
import os
import sys

# Third-party
import numpy as np
from scipy.fft import fft

# Local
from adaptive_spectral_oracle import AdaptiveSpectralKernel
# Standard library
import os
import sys

# Third-party
import numpy as np
from scipy.fft import fft
Type Hints
def compute_weights(
    distances: np.ndarray,
    tau: float
) -> np.ndarray:
    """
    Compute Gaussian kernel weights.
    
    Parameters
    ----------
    distances : ndarray
        L2 distances from robust center
    tau : float
        Adaptive scale parameter
        
    Returns
    -------
    weights : ndarray
        Normalized weights
    """
    weights = np.exp(-(distances ** 2) / (2 * tau ** 2))
    return weights / weights.sum()
Docstrings: Use NumPy style
Variable Names:
	∙	snake_case for functions/variables
	∙	PascalCase for classes
	∙	UPPER_CASE for constants
Solidity Style
Follow Solidity Style Guide:
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Example {
    // State variables
    uint256 public immutable CONSTANT_VALUE;
    
    // Events
    event SomethingHappened(address indexed user);
    
    // Errors
    error InvalidInput();
    
    // Functions (visibility order: external, public, internal, private)
    function externalFunction() external {}
    function publicFunction() public {}
    function _internalFunction() internal {}
    function _privateFunction() private {}
}
Testing Requirements
Unit Tests
Coverage Target: 80%+
Structure:
class TestFeatureName:
    """Test suite for feature."""
    
    def test_basic_functionality(self):
        """Test basic case."""
        # Arrange
        inputs = setup_test_data()
        
        # Act
        result = function_under_test(inputs)
        
        # Assert
        assert result == expected
    
    def test_edge_case(self):
        """Test edge case."""
        pass
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            function_under_test(invalid_input)
Benchmark Tests
For performance-critical changes, include benchmarks:
def test_performance_scaling():
    """Ensure O(n log n) scaling."""
    times = []
    sizes = [100, 500, 1000, 5000]
    
    for n in sizes:
        signals = generate_signals(n_clean=n, T=512)
        kernel = AdaptiveSpectralKernel()
        
        start = time.time()
        kernel.fit(signals)
        elapsed = time.time() - start
        
        times.append(elapsed)
    
    # Check scaling (should be roughly linear in n*log(n))
    assert times[-1] / times[0] < 100  # 50x size = <100x time
Documentation
Adding New Functions
Every public function needs:
	1.	Clear docstring (NumPy format)
	2.	Type hints
	3.	Example usage in docstring
	4.	Entry in API reference (if major feature)
Example:
def new_feature(
    param1: np.ndarray,
    param2: float = 1.5
) -> Tuple[np.ndarray, float]:
    """
    One-line summary.
    
    Detailed explanation of what this function does,
    when to use it, and any important notes.
    
    Parameters
    ----------
    param1 : ndarray
        Description of param1
    param2 : float, default=1.5
        Description of param2
        
    Returns
    -------
    result : ndarray
        Description of result
    metric : float
        Description of metric
        
    Examples
    --------
    >>> result, metric = new_feature(data)
    >>> print(metric)
    1.234
    
    Notes
    -----
    Any mathematical details or references.
    
    References
    ----------
    .. [1] Author et al. (2026). "Title". Journal.
    """
    # Implementation
    pass

