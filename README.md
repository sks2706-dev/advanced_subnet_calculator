# Advanced Subnet Calculator

A clean, beginner-friendly IPv4 subnetting and network planning toolkit built with Python's standard `ipaddress` module. It features an interactive command-line interface (CLI) and a lightweight web interface built with Flask.

---

## Features

- **Subnet Calculations**: Computes network address, broadcast address, subnet mask, wildcard mask, usable host range, and total usable hosts.
- **Edge Case Support**:
  - `/32` (Single host / loopback)
  - `/31` (Point-to-point links per RFC 3021, 2 usable hosts)
  - `/0` (Entire IPv4 address space evaluated in $O(1)$)
- **IP Class Identification**: Classifies addresses into Class A, B, C, D, or E based on the first octet.
- **Binary Visualization**: Formats 32-bit addresses into 8-bit dot-separated binary representations showing bitwise AND (network) and bitwise OR (broadcast).
- **VLSM Planning**: Uses First-Fit Decreasing (largest to smallest) to allocate subnets without boundary fragmentation and tracks address waste.
- **Subnet Splitting**: Divides a larger network block into smaller, equal-sized subnets.
- **Route Summarization**: Combines contiguous or overlapping subnets into minimal supernet routes.
- **Overlap Detection**: Scans a list of CIDRs and detects any overlapping or conflicting address spaces.

---

## Project Structure

```text
cn-subnet-calc/
├── core.py               # Core subnet calculations, IP classification, and binary visualization
├── vlsm.py               # VLSM planning using First-Fit Decreasing
├── splitter.py           # Subnet splitting into smaller subnets
├── summarizer.py         # Route summarization and address collapsing
├── overlap.py            # Overlap and conflict detection across subnets
├── cli.py                # Interactive command-line menu interface
├── app.py                # Flask web interface for all calculator tools
├── templates/
│   └── index.html        # Flask HTML template
├── static/
│   └── style.css         # CSS styles for the web UI
├── test_calculator.py    # Unit test suite written with pytest
└── requirements.txt      # Project dependencies (Flask, pytest)
```

---

## Installation

1. Make sure you have Python 3.8+ installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Interactive Terminal CLI

Run the text-based menu loop in your terminal:

```bash
python cli.py
```

Follow the on-screen options:
1. **Calculate Subnet** (e.g., `192.168.1.1/24`)
2. **VLSM Plan** (e.g., base `192.168.1.0/24` with hosts `120, 60, 30`)
3. **Split Subnet** (e.g., base `192.168.1.0/24` with new prefix `26`)
4. **Summarize Routes** (e.g., `192.168.0.0/24, 192.168.1.0/24`)
5. **Check Overlaps** (e.g., `192.168.1.0/24, 192.168.1.128/25`)
6. **Exit**

---

### 2. Web Application

Launch the Flask development server:

```bash
python app.py
```

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

From the web UI, you can use all four tools (Subnet Calculator, VLSM Planner, Subnet Splitter, and Route Summarizer) directly through clean forms.

---

## Running Tests

Execute the unit tests using `pytest`:

```bash
python -m pytest
```
