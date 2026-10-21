import ipaddress


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
