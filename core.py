import ipaddress


def _to_dotted_binary(addr):
    """Format an IPv4 address into 8-bit binary chunks separated by dots."""
    return ".".join(f"{b:08b}" for b in addr.packed)


def calculate_subnet(ip_cidr):
    """Calculate IPv4 subnet details from an IP/CIDR string."""
    if not isinstance(ip_cidr, str):
        raise ValueError(f"Invalid input type: expected str, got {type(ip_cidr).__name__}")

    raw_input = ip_cidr.strip()
    if not raw_input:
        raise ValueError("Input string cannot be empty")

    if "/" not in raw_input:
        raise ValueError(f"Invalid CIDR notation '{ip_cidr}': missing prefix length (e.g., '/24')")

    try:
        interface = ipaddress.IPv4Interface(raw_input)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as err:
        raise ValueError(f"Invalid IPv4 CIDR notation '{ip_cidr}': {err}") from err

    network = interface.network
    prefix = network.prefixlen

    ip_str = str(interface.ip)
    mask_str = str(network.netmask)
    wildcard_str = str(network.hostmask)
    network_str = str(network.network_address)
    broadcast_str = str(network.broadcast_address)

    if prefix == 32:
        # /32 (1 usable host)
        first_host_str = network_str
        last_host_str = network_str
        num_hosts = 1
    elif prefix == 31:
        # /31 (2 usable hosts per RFC 3021)
        first_host_str = network_str
        last_host_str = broadcast_str
        num_hosts = 2
    else:
        # Standard subnets (/1 to /30) and /0 (entire IPv4 space)
        first_host_str = str(network.network_address + 1)
        last_host_str = str(network.broadcast_address - 1)
        num_hosts = network.num_addresses - 2

    return {
        "ip": ip_str,
        "prefix": prefix,
        "mask": mask_str,
        "wildcard": wildcard_str,
        "network": network_str,
        "broadcast": broadcast_str,
        "first_host": first_host_str,
        "last_host": last_host_str,
        "num_hosts": num_hosts,
    }


def get_ip_class(ip_str):
    """Return IPv4 class ('A', 'B', 'C', 'D', or 'E') based on the first octet."""
    if not isinstance(ip_str, str):
        raise ValueError(f"Invalid input type: expected str, got {type(ip_str).__name__}")

    raw_ip = ip_str.strip()
    if not raw_ip:
        raise ValueError("IP address string cannot be empty")

    ip_candidate = raw_ip.split("/")[0].strip()
    try:
        addr = ipaddress.IPv4Address(ip_candidate)
    except (ipaddress.AddressValueError, ValueError) as err:
        raise ValueError(f"Invalid IPv4 address '{ip_str}': {err}") from err

    first_octet = int(addr.packed[0])
    if 0 <= first_octet <= 127:
        return "A"
    elif 128 <= first_octet <= 191:
        return "B"
    elif 192 <= first_octet <= 223:
        return "C"
    elif 224 <= first_octet <= 239:
        return "D"
    else:
        return "E"


def binary_visualization(ip_cidr):
    """Return a formatted string showing binary IP, Mask, Network (AND), and Broadcast (OR)."""
    if not isinstance(ip_cidr, str):
        raise ValueError(f"Invalid input type: expected str, got {type(ip_cidr).__name__}")

    raw_input = ip_cidr.strip()
    if not raw_input:
        raise ValueError("Input string cannot be empty")

    if "/" not in raw_input:
        raise ValueError(f"Invalid CIDR notation '{ip_cidr}': missing prefix length (e.g., '/24')")

    try:
        interface = ipaddress.IPv4Interface(raw_input)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as err:
        raise ValueError(f"Invalid IPv4 CIDR notation '{ip_cidr}': {err}") from err

    network = interface.network
    net_addr = ipaddress.IPv4Address(int(interface.ip) & int(network.netmask))
    bcast_addr = ipaddress.IPv4Address(int(interface.ip) | int(network.hostmask))

    ip_bin = _to_dotted_binary(interface.ip)
    mask_bin = _to_dotted_binary(network.netmask)
    net_bin = _to_dotted_binary(net_addr)
    bcast_bin = _to_dotted_binary(bcast_addr)

    return (
        f"IP:             {ip_bin}\n"
        f"Subnet Mask:    {mask_bin}\n"
        f"Network (AND):  {net_bin}\n"
        f"Broadcast (OR): {bcast_bin}"
    )
