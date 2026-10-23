from flask import Flask, request, render_template
from core import calculate_subnet, get_ip_class, binary_visualization
from vlsm import vlsm_plan
from splitter import split_subnet
from summarizer import summarize_routes
from overlap import check_overlaps
from network_planner import build_network_plan
from multisite import build_multisite_plan

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    calc_ip = ""
    calc_result = None
    calc_class = None
    calc_binary = None
    calc_error = None

    vlsm_base = ""
    vlsm_hosts = ""
    vlsm_result = None
    vlsm_error = None

    split_base = ""
    split_prefix = ""
    split_result = None
    split_error = None

    sum_cidrs = ""
    sum_result = None
    sum_error = None

    overlap_cidrs = ""
    overlap_conflicts = None
    overlap_checked = False
    overlap_error = None

    planner_base = ""
    planner_departments = ""
    planner_growth = "20"
    planner_reserved = ""
    planner_result = None
    planner_error = None

    multisite_sites = ""
    multisite_departments = ""
    multisite_growth = "20"
    multisite_result = None
    multisite_error = None

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "calculate":
            calc_ip = request.form.get("calc_ip", "").strip()
            try:
                calc_result = calculate_subnet(calc_ip)
                calc_class = get_ip_class(calc_result["ip"])
                calc_binary = binary_visualization(calc_ip)
            except ValueError as err:
                calc_error = str(err)

        elif action == "vlsm":
            vlsm_base = request.form.get("vlsm_base", "").strip()
            vlsm_hosts = request.form.get("vlsm_hosts", "").strip()
            try:
                raw_hosts = [int(h.strip()) for h in vlsm_hosts.replace(",", " ").split() if h.strip()]
                if not raw_hosts:
                    vlsm_error = "Please enter at least one host requirement."
                else:
                    plan = vlsm_plan(vlsm_base, raw_hosts)
                    if plan.get("error"):
                        vlsm_error = plan["error"]
                    else:
                        vlsm_result = plan
            except ValueError as err:
                vlsm_error = f"Invalid host requirement: {err}"

        elif action == "split":
            split_base = request.form.get("split_base", "").strip()
            split_prefix = request.form.get("split_prefix", "").strip()
            try:
                split_result = split_subnet(split_base, split_prefix)
            except ValueError as err:
                split_error = str(err)

        elif action == "summarize":
            sum_cidrs = request.form.get("sum_cidrs", "").strip()
            try:
                cidrs_list = [c.strip() for c in sum_cidrs.replace(",", " ").split() if c.strip()]
                if not cidrs_list:
                    sum_error = "Please enter at least one CIDR."
                else:
                    sum_result = summarize_routes(cidrs_list)
            except ValueError as err:
                sum_error = str(err)

        elif action == "overlap":
            overlap_cidrs = request.form.get("overlap_cidrs", "").strip()
            try:
                cidrs_list = [c.strip() for c in overlap_cidrs.replace(",", " ").split() if c.strip()]
                if not cidrs_list:
                    overlap_error = "Please enter at least one CIDR."
                else:
                    overlap_conflicts = check_overlaps(cidrs_list)
                    overlap_checked = True
            except ValueError as err:
                overlap_error = str(err)

        elif action == "planner":
            planner_base = request.form.get("planner_base", "").strip()
            planner_departments = request.form.get("planner_departments", "").strip()
            planner_growth = request.form.get("planner_growth", "20").strip()
            planner_reserved = request.form.get("planner_reserved", "").strip()
            try:
                planner_result = build_network_plan(
                    planner_base, planner_departments, planner_growth, planner_reserved
                )
            except ValueError as err:
                planner_error = str(err)

        elif action == "multisite":
            multisite_sites = request.form.get("multisite_sites", "").strip()
            multisite_departments = request.form.get("multisite_departments", "").strip()
            multisite_growth = request.form.get("multisite_growth", "20").strip()
            try:
                multisite_result = build_multisite_plan(
                    multisite_sites, multisite_departments, multisite_growth
                )
            except ValueError as err:
                multisite_error = str(err)

    return render_template(
        "index.html",
        calc_ip=calc_ip,
        calc_result=calc_result,
        calc_class=calc_class,
        calc_binary=calc_binary,
        calc_error=calc_error,
        vlsm_base=vlsm_base,
        vlsm_hosts=vlsm_hosts,
        vlsm_result=vlsm_result,
        vlsm_error=vlsm_error,
        split_base=split_base,
        split_prefix=split_prefix,
        split_result=split_result,
        split_error=split_error,
        sum_cidrs=sum_cidrs,
        sum_result=sum_result,
        sum_error=sum_error,
        overlap_cidrs=overlap_cidrs,
        overlap_conflicts=overlap_conflicts,
        overlap_checked=overlap_checked,
        overlap_error=overlap_error,
        planner_base=planner_base,
        planner_departments=planner_departments,
        planner_growth=planner_growth,
        planner_reserved=planner_reserved,
        planner_result=planner_result,
        planner_error=planner_error,
        multisite_sites=multisite_sites,
        multisite_departments=multisite_departments,
        multisite_growth=multisite_growth,
        multisite_result=multisite_result,
        multisite_error=multisite_error,
    )


if __name__ == "__main__":
    app.run(debug=True)
