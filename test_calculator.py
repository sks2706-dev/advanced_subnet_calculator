import pytest
from core import calculate_subnet
from vlsm import vlsm_plan
from overlap import check_overlaps
from network_planner import build_network_plan
from multisite import build_multisite_plan


def test_standard_subnet():
    result = calculate_subnet("192.168.1.10/24")
    assert result["num_hosts"] == 254


def test_31_edge_case():
    result = calculate_subnet("192.168.1.0/31")
    assert result["num_hosts"] == 2


def test_invalid_ip():
    with pytest.raises(ValueError):
        calculate_subnet("invalid_ip")


def test_vlsm_overflow():
    result = vlsm_plan("192.168.1.0/24", [200, 100])
    assert result["error"] == "Insufficient address space"


def test_overlap_checker():
    conflicts = check_overlaps(["192.168.1.0/24", "192.168.1.128/25"])
    assert conflicts == [("192.168.1.0/24", "192.168.1.128/25")]


def test_network_planner_allocates_vlans_and_generates_config():
    plan = build_network_plan("10.10.0.0/22", "Engineering, 20, 180\nHR, 10, 45", 20)
    assert plan["validation"][-1][0] == "success"
    assert plan["allocations"][0]["subnet"] == "10.10.0.0/24"
    assert plan["allocations"][1]["subnet"] == "10.10.1.0/26"
    assert "interface vlan 20" in plan["config"]


def test_network_planner_rejects_duplicate_vlan():
    plan = build_network_plan("10.10.0.0/24", "HR, 10, 20\nFinance, 10, 20")
    assert plan["allocations"] == []
    assert plan["validation"][0][0] == "error"


def test_multisite_plan_produces_site_routes_and_allocations():
    plan = build_multisite_plan(
        "HQ, 10.10.0.0/16\nBranch A, 10.20.0.0/16\nBranch B, 10.30.0.0/16",
        "Engineering, 20, 180\nHR, 10, 45",
    )
    assert plan["wan_routes"] == ["10.10.0.0/16", "10.20.0.0/16", "10.30.0.0/16"]
    assert len(plan["sites"]) == 3
    assert plan["sites"][0]["plan"]["allocations"][0]["vlan"] == 20
    assert any(node["type"] == "core" for node in plan["diagram"]["nodes"])
    assert len(plan["diagram"]["links"]) == 12


def test_multisite_plan_rejects_overlapping_sites():
    plan = build_multisite_plan("HQ, 10.10.0.0/16\nBranch, 10.10.1.0/24", "HR, 10, 10")
    assert plan["sites"] == []
    assert plan["validation"][0][0] == "error"
