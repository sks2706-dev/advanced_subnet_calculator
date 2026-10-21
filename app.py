from flask import Flask, request, render_template_string
from core import calculate_subnet, get_ip_class, binary_visualization
from vlsm import vlsm_plan
from splitter import split_subnet
from summarizer import summarize_routes

app = Flask(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>IPv4 Network & Subnet Tools</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 30px auto; padding: 0 15px; line-height: 1.5; color: #333; }
        h1 { text-align: center; margin-bottom: 25px; }
        h2 { margin-top: 0; color: #222; border-bottom: 1px solid #ccc; padding-bottom: 6px; }
        .card { background-color: #fafafa; border: 1px solid #ddd; border-radius: 4px; padding: 20px; margin-bottom: 30px; }
        .form-group { margin-bottom: 12px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input[type="text"] { width: 100%; box-sizing: border-box; padding: 8px; font-size: 15px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #007bff; color: white; border: none; padding: 8px 16px; font-size: 15px; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .error { color: #d9534f; font-weight: bold; margin-top: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; }
        th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
        th { background-color: #f7f7f7; }
        pre { background-color: #f4f4f4; padding: 12px; border: 1px solid #ccc; border-radius: 4px; overflow-x: auto; font-family: monospace; font-size: 14px; }
        ul { margin: 10px 0; padding-left: 20px; }
        li { margin-bottom: 4px; }
    </style>
</head>
<body>
    <h1>IPv4 Subnet & Network Toolkit</h1>

    <!-- 1. Subnet Calculator -->
    <div class="card">
        <h2>Subnet Calculator</h2>
        <form method="POST">
            <input type="hidden" name="action" value="calculate">
            <div class="form-group">
                <label for="calc_ip">Enter IP/CIDR:</label>
                <input type="text" id="calc_ip" name="calc_ip" value="{{ calc_ip }}" placeholder="e.g., 192.168.1.1/24" required>
            </div>
            <button type="submit">Calculate</button>
        </form>

        {% if calc_error %}
            <p class="error">{{ calc_error }}</p>
        {% endif %}

        {% if calc_result %}
            <h3>Subnet Information</h3>
            <table>
                <tr><th style="width: 35%;">IP Address</th><td>{{ calc_result.ip }}</td></tr>
                <tr><th>IP Class</th><td>Class {{ calc_class }}</td></tr>
                <tr><th>Prefix</th><td>/{{ calc_result.prefix }}</td></tr>
                <tr><th>Subnet Mask</th><td>{{ calc_result.mask }}</td></tr>
                <tr><th>Wildcard Mask</th><td>{{ calc_result.wildcard }}</td></tr>
                <tr><th>Network Address</th><td>{{ calc_result.network }}</td></tr>
                <tr><th>Broadcast Address</th><td>{{ calc_result.broadcast }}</td></tr>
                <tr><th>First Usable Host</th><td>{{ calc_result.first_host }}</td></tr>
                <tr><th>Last Usable Host</th><td>{{ calc_result.last_host }}</td></tr>
                <tr><th>Usable Hosts</th><td>{{ calc_result.num_hosts }}</td></tr>
            </table>

            <h3>Binary Visualization</h3>
            <pre>{{ calc_binary }}</pre>
        {% endif %}
    </div>

    <!-- 2. VLSM Planner -->
    <div class="card">
        <h2>VLSM Planner</h2>
        <form method="POST">
            <input type="hidden" name="action" value="vlsm">
            <div class="form-group">
                <label for="vlsm_base">Base CIDR:</label>
                <input type="text" id="vlsm_base" name="vlsm_base" value="{{ vlsm_base }}" placeholder="e.g., 192.168.1.0/24" required>
            </div>
            <div class="form-group">
                <label for="vlsm_hosts">Host Requirements (comma-separated):</label>
                <input type="text" id="vlsm_hosts" name="vlsm_hosts" value="{{ vlsm_hosts }}" placeholder="e.g., 120, 60, 30" required>
            </div>
            <button type="submit">Plan Subnets</button>
        </form>

        {% if vlsm_error %}
            <p class="error">{{ vlsm_error }}</p>
        {% endif %}

        {% if vlsm_result %}
            <h3>Allocations</h3>
            <table>
                <thead>
                    <tr>
                        <th>Subnet</th>
                        <th>Requested Hosts</th>
                        <th>Usable Hosts</th>
                        <th>Wasted Addresses</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in vlsm_result.allocations %}
                    <tr>
                        <td>{{ item.subnet }}</td>
                        <td>{{ item.requested_hosts }}</td>
                        <td>{{ item.usable_hosts }}</td>
                        <td>{{ item.wasted_addresses }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <p><strong>Waste Percentage:</strong> {{ "%.2f"|format(vlsm_result.waste_pct) }}%</p>
        {% endif %}
    </div>

    <!-- 3. Subnet Splitter -->
    <div class="card">
        <h2>Subnet Splitter</h2>
        <form method="POST">
            <input type="hidden" name="action" value="split">
            <div class="form-group">
                <label for="split_base">Base CIDR:</label>
                <input type="text" id="split_base" name="split_base" value="{{ split_base }}" placeholder="e.g., 192.168.1.0/24" required>
            </div>
            <div class="form-group">
                <label for="split_prefix">New Prefix Length:</label>
                <input type="text" id="split_prefix" name="split_prefix" value="{{ split_prefix }}" placeholder="e.g., 26" required>
            </div>
            <button type="submit">Split Subnet</button>
        </form>

        {% if split_error %}
            <p class="error">{{ split_error }}</p>
        {% endif %}

        {% if split_result %}
            <h3>New Subnets ({{ split_result.count }})</h3>
            <ul>
                {% for sub in split_result.subnets %}
                <li>{{ sub }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    </div>

    <!-- 4. Route Summarizer -->
    <div class="card">
        <h2>Route Summarizer</h2>
        <form method="POST">
            <input type="hidden" name="action" value="summarize">
            <div class="form-group">
                <label for="sum_cidrs">CIDRs to Summarize (comma-separated):</label>
                <input type="text" id="sum_cidrs" name="sum_cidrs" value="{{ sum_cidrs }}" placeholder="e.g., 192.168.0.0/24, 192.168.1.0/24" required>
            </div>
            <button type="submit">Summarize Routes</button>
        </form>

        {% if sum_error %}
            <p class="error">{{ sum_error }}</p>
        {% endif %}

        {% if sum_result %}
            <h3>Summarized Routes</h3>
            <ul>
                {% for route in sum_result.summarized_list %}
                <li>{{ route }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    </div>
</body>
</html>
"""


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

    return render_template_string(
        HTML_TEMPLATE,
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
    )


if __name__ == "__main__":
    app.run(debug=True)
