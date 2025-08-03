# Ethopy

[![PyPI Version](https://img.shields.io/pypi/v/ethopy.svg)](https://pypi.python.org/pypi/ethopy)
[![Python Versions](https://img.shields.io/pypi/pyversions/ethopy.svg)](https://pypi.org/project/ethopy/)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://ef-lab.github.io/ethopy_package/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Ethopy is a state control system for automated, high-throughput behavioral training based on Python. It provides a flexible framework for designing and running behavioral experiments with:

- Tight integration with database storage & control using [Datajoint](https://docs.datajoint.org/python/)
- Cross-platform support (Linux, macOS, Windows)
- Optimized for Raspberry Pi boards
- Modular architecture with overridable components
- Built-in support for various experiment types, stimuli, and behavioral interfaces

## Features

- **Modular Design**: Comprised of several overridable modules that define the structure of experiments, stimuli, and behavioral control
- **Database Integration**: Automatic storage and management of experimental data using Datajoint
- **Multiple Experiment Types**: Support for various experiment paradigms (Go-NoGo, 2AFC, open field, etc.)
- **Hardware Integration**: Interfaces with multiple hardwares (raspberry, arduino, desktop computer, screen, camera etc.)
- **Stimulus Control**: Various stimulus types supported (Gratings, Movies, Olfactory, 3D Objects)
- **Real-time Control**: State-based experiment control with precise timing
- **Extensible**: Easy to add new experiment types, stimuli, or behavioral interfaces

## System Architecture

The following diagram illustrates the relationship between the core modules:

<img src="http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/ef-lab/EthoPy/master/utils/plantuml/modules.iuml">

[Datajoint]: https://github.com/datajoint/datajoint-python

--- 
## Installation & Setup

For a step-by-step guide of installation procedure see [here](getting_started.md)

### Requirements

- Python 3.8 or higher
- Maria DB Database (instructions for [database setup](database_setup.md))


### Basic Installation

```bash
pip install ethopy
```
For more detailed instructions follow the [Installation](installation.md)

### Running Experiments

1. **Service Mode**: Controlled by the Control table in the database
2. **Direct Mode**: Run a specific task directly

Example of running a task:
```bash
# Run a grating test experiment
ethopy -p grating_test.py

# Run a specific task by ID
ethopy --task-idx 1
```

---

## Core Architecture

Understanding Ethopy's core architecture is essential for both using the system effectively and extending it for your needs. Ethopy is built around five core modules that work together to provide a flexible and extensible experimental framework. Each module handles a specific aspect of the experiment, from controlling the overall flow to managing stimuli and recording behavior.

### 1. Experiment Module

The base experiment module defines the state control system. Each experiment is composed of multiple states, with Entry and Exit states being mandatory.

<img src="http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/ef-lab/EthoPy/master/utils/plantuml/states.iuml">

Each state has four overridable functions that control its behavior:

<img src="http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/ef-lab/EthoPy/master/utils/plantuml/state_functions.iuml">

#### Available Experiment Types

- **MatchPort**: Stimulus-port matching experiments
- **Passive**: Passive stimulus presentation
- **FreeWater**: Water delivery experiments
- **Calibrate**: Port calibration for water delivery

Experiment parameters are defined in Python configuration files and stored in the `Task` table within the `lab_experiments` schema.

### 2. Behavior Module

Handles animal behavior tracking and response processing.

#### Available Behavior Types

- **MultiPort**: Standard setup with lick detection, liquid delivery, and proximity sensing
- **HeadFixed**: Passive head fixed setup
> **Important**: Regular liquid calibration is essential for accurate reward delivery. We recommend calibrating at least once per week to ensure consistent reward volumes and reliable experimental results.

### 3. Stimulus Module

Controls stimulus presentation and management.

#### Available Stimulus Types

- **Visual**
  - Grating: Orientation gratings
  - Bar: Moving bars for retinotopic mapping
  - Dot: Moving dots

### 4. Interface Module (Non-overridable)
Manages hardware communication and control.

#### Configuration

Experiments require setup configuration through:
- `SetupConfiguration`
- `SetupConfiguration.Port`
- `SetupConfiguration.Screen`
Configuration files are stored within the `lab_interface` schema.

### 5. Logger Module (Non-overridable)
Manages all database interactions across modules. Data is stored in three schemas:

**lab_experiments**:  
<img src="http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/ef-lab/EthoPy/master/utils/plantuml/experiments.iuml">

**lab_behavior**:  
<img src="http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/ef-lab/EthoPy/master/utils/plantuml/behavior.iuml">

**lab_stimuli**:  
<img src="http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/ef-lab/EthoPy/master/utils/plantuml/stimuli.iuml">


## Development & Contributing
Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given. Please follow thse [instructions] (https://github.com/ef-lab/ethopy_package/blob/main/docs/contributing.md) for contributions.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/ef-lab/ethopy_package/blob/master/LICENSE) file for details.

## Support

For questions and support:

- Open an issue on [GitHub](https://github.com/ef-lab/ethopy_package/issues)
