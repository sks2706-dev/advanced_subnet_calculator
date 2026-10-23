"""Multi-site IPv4 planning with per-site VLAN allocation and WAN summaries."""

import ipaddress

from network_planner import build_network_plan


def parse_sites(raw_text):
    """Parse one `Site Name, CIDR` entry per line."""
    sites = []
    for line_number, raw_line in enumerate(raw_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        pieces = [piece.strip() for piece in line.split(",", 1)]
        if len(pieces) != 2 or not all(pieces):
            raise ValueError(f"Line {line_number}: use Site Name, CIDR")
        try:
            network = ipaddress.IPv4Network(pieces[1], strict=False)
        except ValueError as err:
            raise ValueError(f"Line {line_number}: invalid CIDR: {err}") from err
        sites.append({"name": pieces[0], "network": network})
    if not sites:
        raise ValueError("Enter at least one site.")
    return sites


def build_multisite_plan(sites_text, departments_text, growth_pct=20):
    """Build a reusable departmental plan for each non-overlapping site block."""
    sites = parse_sites(sites_text)
    issues = []
    site_names = [site["name"].casefold() for site in sites]
    if len(site_names) != len(set(site_names)):
        issues.append(("error", "Site names must be unique."))
    for index, left in enumerate(sites):
        for right in sites[index + 1:]:
            if left["network"].overlaps(right["network"]):
                issues.append(("error", f"{left['name']} ({left['network']}) overlaps {right['name']} ({right['network']})."))
    if any(level == "error" for level, _ in issues):
        return {"sites": [], "validation": issues, "wan_routes": [], "parent_summary": [], "diagram": {"width": 1200, "height": 500, "nodes": [], "links": []}}

    results = []
    all_networks = []
    for site in sites:
        plan = build_network_plan(str(site["network"]), departments_text, growth_pct)
        errors = [message for level, message in plan["validation"] if level == "error"]
        results.append({"name": site["name"], "cidr": str(site["network"]), "plan": plan, "errors": errors})
        all_networks.append(site["network"])
    wan_routes = [str(network) for network in all_networks]
    parent_summary = [str(network) for network in ipaddress.collapse_addresses(all_networks)]
    if not any(site["errors"] for site in results):
        issues.append(("success", f"Validated {len(results)} sites with independent address space."))
    return {
        "sites": results,
        "validation": issues,
        "wan_routes": wan_routes,
        "parent_summary": parent_summary,
        "diagram": _build_topology(results),
    }


def _build_topology(sites):
    """Return neutral node/link data so the UI can render a complete SVG topology."""
    max_vlans = max((len(site["plan"]["allocations"]) for site in sites), default=0)
    height = max(520, 390 + max_vlans * 78)
    width = max(1000, 300 * len(sites) + 120)
    core = {"id": "wan", "label": "WAN / MPLS Core", "detail": "Route exchange", "type": "core", "x": width // 2, "y": 55}
    nodes, links = [core], []
    for index, site in enumerate(sites, start=1):
        x = round(width * index / (len(sites) + 1))
        router_id, switch_id = f"router-{index}", f"switch-{index}"
        router = {"id": router_id, "label": f"{site['name']} Router", "detail": site["cidr"], "type": "router", "x": x, "y": 170}
        switch = {"id": switch_id, "label": "L3 Switch", "detail": "Inter-VLAN routing", "type": "switch", "x": x, "y": 290}
        nodes.extend([router, switch])
        links.extend([
            {"from_x": core["x"], "from_y": core["y"], "to_x": x, "to_y": router["y"]},
            {"from_x": x, "from_y": router["y"], "to_x": x, "to_y": switch["y"]},
        ])
        for vlan_index, allocation in enumerate(site["plan"]["allocations"]):
            y = 405 + vlan_index * 78
            node = {
                "id": f"vlan-{index}-{allocation['vlan']}",
                "label": f"VLAN {allocation['vlan']} — {allocation['name']}",
                "detail": f"{allocation['subnet']} · GW {allocation['gateway']}",
                "type": "vlan", "x": x, "y": y,
            }
            nodes.append(node)
            links.append({"from_x": x, "from_y": switch["y"], "to_x": x, "to_y": y})
    return {"width": width, "height": height, "nodes": nodes, "links": links}
