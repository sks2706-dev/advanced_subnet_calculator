# IPv4 Subnet & Network Toolkit

A Python-based IPv4 addressing toolkit for **Classless IP Addressing (CIDR)**. It includes an interactive terminal CLI and a Flask web interface with seven tools for subnet analysis, address planning, and multi-site design.

---

## Features

- **Subnet Calculator** — Computes network address, broadcast address, subnet mask, wildcard mask, usable host range, total usable hosts, and IP class from any CIDR input. Includes a **binary visualization** that color-codes network bits (blue) vs. host bits (orange).
- **VLSM Planner** — Allocates subnets of varying sizes from a base network using Variable Length Subnet Masking (First-Fit Decreasing). Reports wasted address space and renders a proportional address space map.
- **Subnet Splitter** — Divides any network block into equal-sized subnets by specifying a new prefix length. Renders a visual bar showing the split.
- **Route Summarizer** — Collapses a list of CIDR blocks into the smallest set of covering supernet routes.
- **Overlap Checker** — Scans a list of CIDRs and reports any conflicting (overlapping) address spaces.
- **Network Design Planner** — Converts named departments and VLAN requirements into a growth-aware VLSM plan, validates duplicate VLANs/reserved ranges, assigns gateways and DHCP ranges, and produces Cisco SVI configuration.
- **Multi-Site WAN Planner** — Validates non-overlapping HQ/branch blocks, produces a per-site VLAN plan, and lists both individual and collapsed route advertisements.

**Edge cases handled:** `/31` (point-to-point links, RFC 3021), `/32` (host routes), `/0` (entire IPv4 space).

---

## File Structure

```
cn-subnet-calc/
│
├── core.py              # Core IP math: subnet info, binary representation, IP class
├── vlsm.py              # VLSM planner: sorts requirements, allocates greedily
├── splitter.py          # Subnet splitter: divides a network into equal sub-blocks
├── summarizer.py        # Route summarizer: finds the supernet covering a set of CIDRs
├── overlap.py           # Overlap checker: finds conflicting networks in a list
├── network_planner.py   # Constraint-aware VLAN/address-plan generator
├── multisite.py         # Multi-site validation, allocation, and WAN route summaries
│
├── cli.py               # Interactive terminal interface (menu-driven)
├── app.py               # Flask web application (POST-based, server-rendered)
│
├── templates/
│   └── index.html       # Single-page Jinja2 template with all seven tool panels
├── static/
│   ├── style.css        # Styles: layout, typography, binary bit colors, subnet bars
│   └── script.js        # Vanilla JS: tab navigation, animations, binary colorizer
│
├── test_calculator.py   # Pytest test suite
├── requirements.txt     # Python dependencies (Flask, pytest)
└── README.md            # This file
```

---

## Installation

**Requirements:** Python 3.8+

1. Clone the repository and navigate into it:

```bash
git clone https://github.com/your-username/cn-subnet-calc.git
cd cn-subnet-calc
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage — CLI

Run the interactive terminal interface:

```bash
python cli.py
```

Follow the on-screen menu to pick a tool:

1. **Calculate Subnet** — e.g., `192.168.1.1/24`
2. **VLSM Plan** — e.g., base `10.0.0.0/24`, hosts `120 60 30`
3. **Split Subnet** — e.g., base `192.168.0.0/22`, new prefix `24`
4. **Summarize Routes** — e.g., `192.168.0.0/24` and `192.168.1.0/24`
5. **Check Overlaps** — e.g., `10.0.0.0/8` and `10.1.0.0/16`
6. **Exit**

---

## Usage — Web Interface

Start the Flask development server:

```bash
python app.py
```

Open your browser and go to:

```
http://127.0.0.1:5000
```

Use the sidebar to switch between all seven tools. The Network Design Planner and Multi-Site WAN Planner are available in the web interface; they add VLAN allocations, gateway/DHCP plans, Cisco SVI configuration, WAN route summaries, and a generated topology view.

---

## Testing

Run the full Pytest suite:

```bash
python -m pytest
```

For verbose output showing each test case:

```bash
python -m pytest -v
```
