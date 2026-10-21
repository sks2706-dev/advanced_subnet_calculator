import pytest
from core import calculate_subnet
from vlsm import vlsm_plan


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
