# CLAUDE.md - Project Memory

## Project Overview
This is a matplotlib styles package (`mplstyles-seaborn`) that provides seaborn-style matplotlib stylesheets. The package contains 120 pre-generated .mplstyle files covering all combinations of seaborn v0.8 styles, palettes, and contexts.

## Package Structure
```
mplstyles-seaborn/
├── src/mplstyles_seaborn/
│   ├── __init__.py              # Main package with convenience functions
│   ├── py.typed                 # Type hints marker
│   └── styles/                  # 120 .mplstyle files (5×6×4 combinations)
├── tests/                       # Comprehensive test suite
│   ├── __init__.py              # Test package marker
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── test_api.py              # Unit tests for core API functions
│   ├── test_integration.py      # Matplotlib integration tests
│   ├── test_styles.py           # Style file validation tests
│   ├── test_errors.py           # Error handling and edge case tests
│   └── test_performance.py      # Performance and scalability tests
├── examples/                    # Comprehensive usage examples
│   ├── README.md                # Examples documentation
│   ├── basic_usage.py           # Basic usage patterns
│   ├── style_comparison.py      # Style comparison demonstrations
│   └── comprehensive_demo.py    # Advanced usage examples
├── scripts/                     # Development utilities
│   ├── build_styles.py          # Combined script to generate and fix all style files
│   └── research_seaborn_styles.py # Research script for seaborn configurations
├── .github/workflows/           # CI/CD automation
│   └── test.yml                 # GitHub Actions test workflow
├── pyproject.toml               # Package configuration with test dependencies
└── README.md                    # Project documentation
```

## Available Style Combinations
- **Styles** (5): darkgrid, whitegrid, dark, white, ticks
- **Palettes** (6): dark, colorblind, muted, bright, pastel, deep
- **Contexts** (4): paper, notebook, talk, poster
- **Total**: 120 unique style files

## Usage Methods
1. **Convenience function**: `mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')`
2. **Direct matplotlib**: `plt.style.use('seaborn-v0_8-whitegrid-colorblind-talk')`
3. **Auto-registration**: All styles are automatically registered with matplotlib on import

## Work Completed

### Style File Generation and Fixes (2025-07-24)
- **Problem**: Generated .mplstyle files had formatting issues:
  1. `axes.prop_cycle` used cycler syntax instead of matplotlib's expected comma-separated format
  2. `axes.facecolor` had inconsistent quote formatting
  3. Missing `font.family` setting causing font fallback issues

- **Solution**: Updated `fix_styles.py` to properly format parameters:
  - `axes.prop_cycle`: Changed from cycler syntax to comma-separated colors
  - `axes.facecolor`: Ensured consistent unquoted hex color format
  - `font.family`: Added `sans-serif` to all style files
  - `lines.solid_capstyle`: Fixed enum references to simple strings

### Font Configuration Fixed
- **Issue**: Fonts defaulting to Arial instead of preferred fonts
- **Root Cause**: `font.sans-serif` was set but `font.family` was missing
- **Solution**: Added `font.family: sans-serif` to all style files

Font selection priority:
1. Source Sans 3 (if available)
2. Arial (fallback)
3. DejaVu Sans (further fallback)
4. System fonts

### Examples Reorganization (2025-07-24)
- **Task**: Reorganized example files into structured examples directory
- **Approach**: Based examples on matplotlib's `style_sheets_reference.py` for consistency and comprehensiveness
- **New Structure**:
  - `examples/basic_usage.py`: Demonstrates fundamental usage patterns with LaTeX notation
  - `examples/style_comparison.py`: Complete 120 style combination gallery with matplotlib's reference approach
  - `examples/comprehensive_demo.py`: Advanced demonstrations with 7 plot types and publication-ready examples
  - `examples/README.md`: Complete documentation for all examples
  - `examples/basic_usage_gallery.md`: Visual gallery for basic usage examples
  - `examples/style_comparison_gallery.md`: Complete visual gallery showing all 120 combinations
  - `examples/comprehensive_demo_gallery.md`: Advanced demonstration gallery
  - Legacy files (`example.py`, `example_2.py`) removed after reorganization
- **Output Structure**: Each script generates organized output in dedicated directories
  - `examples/basic_usage_output/`: 3 basic example plots
  - `examples/style_comparison_output/`: 121 plots (120 combinations + 1 context comparison)
  - `examples/comprehensive_demo_output/`: 5 advanced demonstration plots (PNG + PDF formats)
- **Key Features**:
  - All mathematical symbols use proper LaTeX notation
  - Constrained layout for proper title positioning
  - Publication-ready PDF outputs (300 DPI)
  - Complete coverage of all 120 style combinations

## Testing and Development

### Development Workflow
- **IMPORTANT**: Always create a new branch before starting any development work
- Branch naming convention: Use descriptive names like `reorganize-examples`, `fix-font-issues`, etc.
- Create branch with: `git checkout -b <branch-name>`

### Environment Setup
- Use `uv` for package management and Python environment
- Dependencies: matplotlib>=3.5, seaborn>=0.11

### Testing Commands

#### Automated Test Suite (Comprehensive)
```bash
# Install test dependencies
uv sync --extra test

# Run all tests with coverage report
uv run pytest --cov=src/mplstyles_seaborn --cov-report=term-missing

# Run specific test categories
uv run pytest tests/test_api.py          # API function tests (22 tests)
uv run pytest tests/test_integration.py # Matplotlib integration tests (13 tests)
uv run pytest tests/test_styles.py      # Style file validation tests (28 tests)
uv run pytest tests/test_errors.py      # Error handling tests (21 tests)
uv run pytest tests/test_performance.py # Performance tests (11 tests)

# Run with verbose output
uv run pytest -v

# Run fast tests only (exclude slow performance tests)
uv run pytest -m "not slow"
```

#### Manual Testing Commands
```bash
# Test package installation and import
uv run python -c "import mplstyles_seaborn; print(len(mplstyles_seaborn.list_available_styles()))"

# Test specific style
uv run python -c "import matplotlib.pyplot as plt; plt.style.use('seaborn-v0_8-whitegrid-colorblind-talk')"

# Run examples
uv run python examples/basic_usage.py
uv run python examples/style_comparison.py
uv run python examples/comprehensive_demo.py
```

### Key Scripts
- `scripts/build_styles.py`: Combined script to generate and fix all 120 style files from seaborn configurations
  - Default: Generate and fix styles in one workflow
  - `--generate-only`: Only generate new style files
  - `--fix-only`: Only fix existing style files

### Examples Directory
- `examples/basic_usage.py`: Fundamental usage patterns and basic plot types
- `examples/style_comparison.py`: Side-by-side style comparisons based on matplotlib's reference
- `examples/comprehensive_demo.py`: Advanced demonstrations with complex layouts and publication-ready figures
- `examples/README.md`: Comprehensive documentation for all examples

## Current Status
- ✅ 120 style files generated covering all seaborn v0.8 combinations
- ✅ Fixed `axes.prop_cycle` formatting (cycler → comma-separated)
- ✅ Fixed `axes.facecolor` formatting (consistent unquoted hex)
- ✅ Added `font.family: sans-serif` to all styles
- ✅ Fixed `lines.solid_capstyle` enum references
- ✅ Package auto-registers styles with matplotlib
- ✅ Convenience functions for easy style application
- ✅ Reorganized examples into structured directory with comprehensive demonstrations
- ✅ Created examples based on matplotlib's official style reference approach
- ✅ Generated complete visual galleries with 129 total plots (3 basic + 121 comparison + 5 comprehensive)
- ✅ All mathematical symbols use proper LaTeX notation
- ✅ Fixed title positioning issues using constrained_layout approach
- ✅ Publication-ready outputs in both PNG and PDF formats
- ✅ **Comprehensive test suite implemented (2025-07-24)**
- ✅ **CI/CD pipeline with GitHub Actions configured**
- ✅ **100% code coverage achieved (95 tests, all passing)**

### Comprehensive Test Suite Implementation (2025-07-24)

A robust testing framework was implemented to ensure package reliability and maintainability:

#### **Test Infrastructure**
- **Framework**: pytest with coverage reporting (pytest-cov)
- **Structure**: 5 test modules covering different aspects of functionality
- **Configuration**: pytest.ini settings in pyproject.toml with custom markers
- **Fixtures**: Reusable test setup including matplotlib reset and style file paths

#### **Test Coverage Breakdown**
1. **API Tests** (`test_api.py` - 22 tests)
   - Core function validation: `use_style()`, `list_available_styles()`, `register_styles()`
   - Input validation and parameter combinations
   - Constants and exports verification
   - Auto-registration functionality

2. **Integration Tests** (`test_integration.py` - 13 tests)
   - Matplotlib integration and rcParams changes
   - Style persistence and context management
   - Direct matplotlib usage compatibility
   - Color palette and style effects verification

3. **Style Validation Tests** (`test_styles.py` - 28 tests)
   - All 120 style files existence and format validation
   - Matplotlib compatibility and loadability
   - Parameter consistency across all combinations
   - Font configuration and color format verification

4. **Error Handling Tests** (`test_errors.py` - 21 tests)
   - Invalid input handling and appropriate error messages
   - File system error scenarios
   - Edge cases and boundary conditions
   - Concurrent access and threading safety

5. **Performance Tests** (`test_performance.py` - 11 tests)
   - Style loading and switching performance benchmarks
   - Memory usage stability and leak detection
   - Scalability testing with all 120 styles
   - Resource usage efficiency verification

#### **CI/CD Pipeline**
- **GitHub Actions**: Automated testing on Ubuntu, Windows, macOS
- **Python Versions**: 3.11 and 3.12 compatibility testing
- **Coverage Integration**: Codecov reporting for coverage tracking
- **Style Verification**: Automated validation of all style files

#### **Test Results**
- **Total Tests**: 95 tests across all categories
- **Success Rate**: 100% (all tests passing)
- **Code Coverage**: 100% (31/31 statements covered)
- **Performance**: All tests complete within acceptable time limits

#### **Quality Assurance**
- **Comprehensive Coverage**: Every API function and edge case tested
- **Real-world Scenarios**: Tests mirror actual usage patterns  
- **Cross-platform**: Ensures compatibility across different operating systems
- **Automated Validation**: Continuous verification of package integrity

## Package Features
- **Zero seaborn dependency**: Use seaborn-style plots without requiring seaborn
- **Complete coverage**: All seaborn v0.8 style/palette/context combinations
- **Easy integration**: Styles automatically available to matplotlib
- **Type hints**: Full type annotation support
- **Flexible usage**: Multiple ways to apply styles
- **Production ready**: Comprehensive test suite with 100% coverage