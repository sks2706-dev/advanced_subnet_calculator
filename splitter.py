import ipaddress


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
