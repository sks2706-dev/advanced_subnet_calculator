import ipaddress


def _extract_requirements(host_requirements):
    """Extract host requirements into a list of integers."""
    if isinstance(host_requirements, dict):
        return [int(v) for v in host_requirements.values()]
    reqs = []
    for item in host_requirements:
        if isinstance(item, dict):
            val = item.get("hosts", item.get("requested_hosts", item.get("size")))
            reqs.append(int(val))
        else:
            reqs.append(int(item))
    return reqs


def vlsm_plan(base_cidr, host_requirements):
    """Generate a VLSM plan using First-Fit Decreasing."""
    try:
        base_net = ipaddress.IPv4Network(base_cidr, strict=False)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError, TypeError) as err:
        return {
            "allocations": [],
            "error": f"Invalid base CIDR: {err}",
            "utilization_pct": 0.0,
            "waste_pct": 0.0,
        }

    try:
        reqs = _extract_requirements(host_requirements)
    except (ValueError, TypeError) as err:
        return {
            "allocations": [],
            "error": f"Invalid host requirements: {err}",
            "utilization_pct": 0.0,
            "waste_pct": 0.0,
        }

    if not reqs:
        return {
            "allocations": [],
            "error": None,
            "utilization_pct": 0.0,
            "waste_pct": 0.0,
        }

    if any(r < 1 for r in reqs):
        return {
            "allocations": [],
            "error": "Host requirements must be positive integers",
            "utilization_pct": 0.0,
            "waste_pct": 0.0,
        }

    # First-Fit Decreasing: sort largest to smallest
    sorted_reqs = sorted(reqs, reverse=True)

    current_ip = int(base_net.network_address)
    base_end_ip = int(base_net.broadcast_address)
    allocations = []
    total_allocated_addresses = 0
    total_requested_hosts = sum(sorted_reqs)

    for req in sorted_reqs:
        # Determine host bits h such that 2^h - 2 >= req (minimum h = 2)
        h = 2
        while (2 ** h - 2) < req:
            h += 1
            if h > 32:
                break

        prefix = 32 - h
        if prefix < base_net.prefixlen or h > 32:
            return {
                "allocations": [],
                "error": "Insufficient address space",
                "utilization_pct": 0.0,
                "waste_pct": 0.0,
            }

        block_size = 1 << h

        # Align to block boundary if necessary
        if current_ip % block_size != 0:
            current_ip += block_size - (current_ip % block_size)

        # Check if allocation fits within the base network
        if current_ip + block_size - 1 > base_end_ip:
            return {
                "allocations": [],
                "error": "Insufficient address space",
                "utilization_pct": 0.0,
                "waste_pct": 0.0,
            }

        subnet_net = ipaddress.IPv4Network((current_ip, prefix))
        usable_hosts = (1 << h) - 2
        wasted = usable_hosts - req

        allocations.append({
            "subnet": str(subnet_net),
            "requested_hosts": req,
            "usable_hosts": usable_hosts,
            "wasted_addresses": wasted,
        })

        total_allocated_addresses += block_size
        current_ip += block_size

    if total_allocated_addresses > 0:
        utilization_pct = (total_requested_hosts / total_allocated_addresses) * 100.0
        waste_pct = 100.0 - utilization_pct
    else:
        utilization_pct = 0.0
        waste_pct = 0.0

    return {
        "allocations": allocations,
        "error": None,
        "utilization_pct": utilization_pct,
        "waste_pct": waste_pct,
    }


def split_subnet(base_cidr, new_prefix):
    """Split a network into smaller subnets using IPv4Network.subnets()."""
    net = ipaddress.IPv4Network(base_cidr, strict=False)

    if isinstance(new_prefix, str):
        target_prefix = int(new_prefix.lstrip("/"))
    else:
        target_prefix = int(new_prefix)

    subnets_list = [str(s) for s in net.subnets(new_prefix=target_prefix)]

    return {
        "original_network": str(net),
        "new_prefix": target_prefix,
        "count": len(subnets_list),
        "subnets": subnets_list,
    }


def summarize_routes(cidrs):
    """Summarize a list of network strings using ipaddress.collapse_addresses()."""
    networks = [ipaddress.IPv4Network(c, strict=False) for c in cidrs]
    summarized_list = [str(net) for net in ipaddress.collapse_addresses(networks)]
    original_list = [str(c) for c in cidrs]

    return {
        "original_list": original_list,
        "summarized_list": summarized_list,
        "original_count": len(original_list),
        "new_count": len(summarized_list),
    }
