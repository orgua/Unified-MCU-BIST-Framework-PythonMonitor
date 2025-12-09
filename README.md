# BISTMon

A serial monitor and analysis tool for the [BIST-Framework](https://github.com/tim-carlo/Unified-MCU-BIST-Framework), a framework for generalized built-in self-tests of microcontroller-boards utilizing the MCUs itself.

The monitor handles real-time data monitoring, matrix calculations, and XML data management.

## Installation & Setup

This project uses can be installed via

```bash
pip install .
```

It is recommended to use a tool like uv, poetry or pipenv to work inside a virtual environment.

### Instructions for UV

Navigate to the

### Instructions for Poetry

1.  **Install dependencies:**

    ```bash
    poetry install
    ```

2.  **Activate the virtual environment:**

    ```bash
    poetry shell
    ```

## Usage

Ensure your virtual environment is active (e.g. via `poetry shell`) or prepend `poetry run` to the commands below.

### 1\. Live Monitor Mode

Determine the available serial ports

```bash
bistmon list
```

Select one port from the list and start monitoring.

```bash
bistmon serial tty.usbmodem11102
```

### 2\. File Analysis Mode

Loads and analyzes a previously saved XML dataset.

```bash
bistmon load ./raw_data/my_data.xml
```

## Interactive Commands

The following commands are available in both Live and File Analysis modes:

  * **'s':** Save the entire output log to a `.txt` file.
  * **'r':** Save the raw data as an XML file.
  * **'v':** Visualize the data (generates charts using pandas).

## Core Logic (data\_storage.py)

The main processing occurs in `data_storage.py` and includes:

  * **Matrix Calculations:** Computation logic for incoming data.
  * **Vector Representations:** Computes vector representations of the data.
  * **Visualization:** Data display and rendering.
  * **I/O:** Import and export functionality for XML files.
  * **Filtering:** Data filter functions.

## Tooling

Linters, formatters and other tooling can be run via

```bash
pre-commit run -a
```

If not already installed, you can add the `dev`-flavor of this package, i.e.

```bash
pip install testsoftware-monitor[dev]
```
