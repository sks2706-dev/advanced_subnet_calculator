"""Constraint-aware IPv4 network-plan generator."""

import ipaddress
import math


def _required_prefix(hosts):
    """Return the smallest conventional subnet prefix that can hold hosts."""
    host_bits = 2
    while (1 << host_bits) - 2 < hosts:
        host_bits += 1
    return 32 - host_bits


def parse_departments(raw_text):
    """Parse `Name, VLAN ID, hosts` lines into validated requirement dictionaries."""
    departments = []
    for line_number, raw_line in enumerate(raw_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        pieces = [piece.strip() for piece in line.split(",")]
        if len(pieces) != 3 or not all(pieces):
            raise ValueError(f"Line {line_number}: use Name, VLAN ID, Hosts")
        name, vlan_text, host_text = pieces
        try:
            vlan, hosts = int(vlan_text), int(host_text)
        except ValueError as err:
            raise ValueError(f"Line {line_number}: VLAN ID and hosts must be integers") from err
        if not 1 <= vlan <= 4094:
            raise ValueError(f"Line {line_number}: VLAN ID must be between 1 and 4094")
        if hosts < 1:
            raise ValueError(f"Line {line_number}: hosts must be at least 1")
        departments.append({"name": name, "vlan": vlan, "hosts": hosts})
    if not departments:
        raise ValueError("Enter at least one department or VLAN.")
    return departments


def _parse_reserved(raw_text):
    values = [item.strip() for item in raw_text.replace(",", " ").split() if item.strip()]
    try:
        return [ipaddress.IPv4Network(item, strict=False) for item in values]
    except ValueError as err:
        raise ValueError(f"Invalid reserved CIDR: {err}") from err


def _next_available_subnet(base, prefix, occupied):
    for candidate in base.subnets(new_prefix=prefix):
        if not any(candidate.overlaps(used) for used in occupied):
            return candidate
    return None


def build_network_plan(base_cidr, departments_text, growth_pct=20, reserved_text=""):
    """Allocate named VLANs and return an address plan plus Cisco SVI configuration."""
    try:
        base = ipaddress.IPv4Network(base_cidr, strict=False)
    except ValueError as err:
        raise ValueError(f"Invalid base CIDR: {err}") from err
    try:
        growth = float(growth_pct)
    except (TypeError, ValueError) as err:
        raise ValueError("Growth reserve must be a number from 0 to 500.") from err
    if not 0 <= growth <= 500:
        raise ValueError("Growth reserve must be between 0 and 500 percent.")

    departments, reserved = parse_departments(departments_text), _parse_reserved(reserved_text)
    validation = []
    names, vlans = [item["name"].casefold() for item in departments], [item["vlan"] for item in departments]
    if len(names) != len(set(names)):
        validation.append(("error", "Department names must be unique."))
    if len(vlans) != len(set(vlans)):
        validation.append(("error", "VLAN IDs must be unique."))
    outside_reserved = [str(net) for net in reserved if not net.subnet_of(base)]
    if outside_reserved:
        validation.append(("notice", "Ignored reserved ranges outside the base network: " + ", ".join(outside_reserved)))
        reserved = [net for net in reserved if net.subnet_of(base)]
    if any(level == "error" for level, _ in validation):
        return {"allocations": [], "validation": validation, "config": "", "base": str(base), "unallocated_addresses": base.num_addresses}

    work = []
    for department in departments:
        planned_hosts = math.ceil(department["hosts"] * (1 + growth / 100))
        work.append({**department, "planned_hosts": planned_hosts, "prefix": _required_prefix(planned_hosts)})
    work.sort(key=lambda item: (item["prefix"], item["vlan"]))
    occupied, allocated_by_vlan = list(reserved), {}
    for item in work:
        if item["prefix"] < base.prefixlen:
            validation.append(("error", f"{item['name']} needs a /{item['prefix']}, larger than the base network."))
            continue
        subnet = _next_available_subnet(base, item["prefix"], occupied)
        if subnet is None:
            validation.append(("error", f"Insufficient space to allocate {item['name']}."))
            continue
        occupied.append(subnet)
        allocated_by_vlan[item["vlan"]] = {
            **item, "subnet": str(subnet), "gateway": str(subnet.network_address + 1),
            "dhcp_start": str(subnet.network_address + 10) if subnet.num_addresses >= 16 else str(subnet.network_address + 1),
            "dhcp_end": str(subnet.broadcast_address - 1), "usable_hosts": subnet.num_addresses - 2,
            "growth_headroom": subnet.num_addresses - 2 - item["hosts"], "address_count": subnet.num_addresses,
        }
    allocations = [allocated_by_vlan[item["vlan"]] for item in departments if item["vlan"] in allocated_by_vlan]
    if allocations and not any(level == "error" for level, _ in validation):
        validation.append(("success", f"All {len(allocations)} VLANs fit inside {base}."))
    used = sum(item["address_count"] for item in allocations) + sum(net.num_addresses for net in reserved)
    config_lines = ["! Generated by IPv4 Network Planner", f"! Base network: {base}"]
    for item in allocations:
        network = ipaddress.IPv4Network(item["subnet"])
        config_lines.extend([f"! {item['name']} - VLAN {item['vlan']}", f"vlan {item['vlan']}", f" name {item['name'].replace(' ', '_')}", f"interface vlan {item['vlan']}", f" ip address {item['gateway']} {network.netmask}", " no shutdown", "!"])
    return {"base": str(base), "allocations": allocations, "validation": validation, "config": "\n".join(config_lines), "unallocated_addresses": max(0, base.num_addresses - used)}
