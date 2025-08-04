# EC-PeT: Modern Eddy-Covariance Processing Software

[![License: EUPL v1.2](https://img.shields.io/badge/License-EUPL%20v1.2-blue.svg)](https://joinup.ec.europa.eu/software/page/eupl)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)

**EC-PeT** (*elaboratio concursuum perturbationum Treverensis*) is a modern, Python-based software package for processing eddy-covariance flux measurements from various sonic anemometer and gas analyzer combinations. Developed at the University of Trier, EC-PeT provides both command-line and graphical interfaces for comprehensive turbulence data analysis in atmospheric boundary layer research.

## Overview

EC-PeT is the successor to the widely-used EC-PACK software, offering a complete rewrite in Python that maintains computational compatibility while providing modern usability and performance improvements. The software incorporates the quality control and assessment strategies developed for the German TERENO (Terrestrial Environmental Observatories) network.

### Key Features

- **Dual Interface**: Both command-line interface for automation and graphical user interface for interactive use
- **Multi-Instrument Support**: Compatible with various sonic anemometers and gas analyzers
- **Quality Assessment**: Implements comprehensive QC/QA procedures following established atmospheric science standards
- **Modern Architecture**: Python-based with multiprocessing support for efficient data processing
- **Database Storage**: Uses SQLite3 for project data management and easy result export
- **Industry Compatibility**: Reads Campbell Scientific TOA5 files and outputs in EC-PACK/EC-frame formats

## Scientific Background

The eddy-covariance method is a fundamental technique in micrometeorology for measuring vertical turbulent fluxes of:
- **Energy**: Sensible and latent heat fluxes
- **Momentum**: Surface stress and friction velocity
- **Trace Gases**: CO₂, H₂O, CH₄, and other atmospheric constituents

EC-PeT processes high-frequency (typically 10-20 Hz) measurements to calculate half-hourly flux values with comprehensive error analysis and quality flagging.

## Installation

### Requirements

- Python 3.7 or later
- NumPy, SciPy, Pandas
- wxPython (for GUI)
- matplotlib (for plotting)
- netCDF4, requests
- Additional dependencies listed in requirements

### Install from PyPI

```bash
pip install ecpet
```

## Quick Start

### Command Line Usage

```bash
# Process data with default configuration
ecpet process data_file.dat

# Use custom configuration
ecpet process data_file.dat --config my_config.conf

# Launch GUI
ecpet gui
```


## Quality Assessment

EC-PeT implements the quality control strategy developed for TERENO, which includes:

- **High-frequency tests**: Spike detection, variance analysis, statistical screening
- **Flux tests**: Stationarity tests, integral turbulence characteristics
- **Physical plausibility**: Energy balance closure, footprint analysis
- **Systematic error quantification**: Based on energy balance closure deficit

Results are assigned quality flags following established conventions:
- **0**: High-quality data suitable for all applications
- **1**: Moderate quality data requiring careful interpretation
- **2**: Low-quality data recommended for exclusion


## Documentation

Comprehensive documentation is available at:
- **User Guide**: [https://druee.gitlab-pages.uni-trier.de/ecpet/](https://druee.gitlab-pages.uni-trier.de/ecpet/)
- **API Reference**: [https://druee.gitlab-pages.uni-trier.de/ecpet/technical/](https://druee.gitlab-pages.uni-trier.de/ecpet/technical/)

## Citation

If you use EC-PeT in your research, please cite:

```
Drüe, C. (2023). EC-PeT: A modern eddy-covariance software package. 
University of Trier, Environmental Meteorology Group.
```

For the underlying quality assessment methodology, please also cite:

```
Mauder, M., Cuntz, M., Drüe, C., Graf, A., Rebmann, C., Schmid, H.P., 
Schmidt, M., Steinbrecher, R. (2013). A strategy for quality and uncertainty 
assessment of long-term eddy-covariance measurements. Agricultural and Forest 
Meteorology, 169, 122-135. https://doi.org/10.1016/j.agrformet.2012.09.006
```

## License

EC-PeT is released under the European Union Public Licence (EUPL) v1.2. See [LICENSE.txt](LICENSE.txt) for details.

---

*EC-PeT: From the Latin "elaboratio concursuum perturbationum Treverensis" - eddy-covariance software from Trier, honoring the Roman heritage of Germany's oldest city.*