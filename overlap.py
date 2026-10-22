import ipaddress


def check_overlaps(cidr_list):
    """Check if any two networks in the list overlap. Return a list of conflicting pairs."""
    networks = []
    for cidr in cidr_list:
        net = ipaddress.ip_network(cidr, strict=False)
        networks.append((str(cidr), net))

    conflicts = []
    for i in range(len(networks)):
        for j in range(i + 1, len(networks)):
            str1, net1 = networks[i]
            str2, net2 = networks[j]
            try:
                if net1.overlaps(net2):
                    conflicts.append((str1, str2))
            except TypeError:
                continue

    return conflicts
