from core import calculate_subnet, get_ip_class
from vlsm import vlsm_plan
from splitter import split_subnet
from summarizer import summarize_routes


def main():
    while True:
        print("\n=== Subnet Calculator Menu ===")
        print("1. Calculate Subnet")
        print("2. VLSM Plan")
        print("3. Split Subnet")
        print("4. Summarize Routes")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            ip_cidr = input("Enter IP/CIDR (e.g., 192.168.1.1/24): ").strip()
            try:
                res = calculate_subnet(ip_cidr)
                ip_class = get_ip_class(res["ip"])
                print("\n--- Subnet Details ---")
                print(f"IP Address:      {res['ip']}")
                print(f"IP Class:        Class {ip_class}")
                print(f"Prefix:          /{res['prefix']}")
                print(f"Subnet Mask:     {res['mask']}")
                print(f"Wildcard Mask:   {res['wildcard']}")
                print(f"Network Address: {res['network']}")
                print(f"Broadcast:       {res['broadcast']}")
                print(f"First Host:      {res['first_host']}")
                print(f"Last Host:       {res['last_host']}")
                print(f"Usable Hosts:    {res['num_hosts']}")
            except ValueError as e:
                print(f"\nError: {e}")

        elif choice == "2":
            base_cidr = input("Enter Base CIDR (e.g., 192.168.1.0/24): ").strip()
            hosts_input = input("Enter host requirements separated by commas or spaces: ").strip()
            raw_reqs = hosts_input.replace(",", " ").split()
            try:
                reqs = [int(x) for x in raw_reqs]
                res = vlsm_plan(base_cidr, reqs)
                if res.get("error"):
                    print(f"\nError: {res['error']}")
                else:
                    print("\n--- VLSM Allocation Plan ---")
                    for a in res["allocations"]:
                        print(
                            f"Subnet: {a['subnet']:<18} | "
                            f"Needed: {a['requested_hosts']:<4} | "
                            f"Usable: {a['usable_hosts']:<4} | "
                            f"Wasted: {a['wasted_addresses']:<4}"
                        )
                    print(f"\nUtilization: {res['utilization_pct']:.2f}%")
                    print(f"Waste:       {res['waste_pct']:.2f}%")
            except ValueError as e:
                print(f"\nError: Invalid host numbers: {e}")

        elif choice == "3":
            base_cidr = input("Enter Base CIDR to split (e.g., 192.168.1.0/24): ").strip()
            new_prefix = input("Enter new prefix length (e.g., 26): ").strip()
            try:
                res = split_subnet(base_cidr, new_prefix)
                print(f"\nOriginal Network: {res['original_network']}")
                print(f"New Prefix:       /{res['new_prefix']}")
                print(f"Subnets Created:  {res['count']}")
                print("Subnets:")
                for sub in res["subnets"]:
                    print(f"  - {sub}")
            except ValueError as e:
                print(f"\nError: {e}")

        elif choice == "4":
            routes_input = input("Enter CIDRs to summarize separated by commas or spaces: ").strip()
            cidrs = [c.strip() for c in routes_input.replace(",", " ").split() if c.strip()]
            if not cidrs:
                print("\nError: No CIDRs entered.")
                continue
            try:
                res = summarize_routes(cidrs)
                print(f"\nOriginal Routes ({res['original_count']}):")
                for r in res["original_list"]:
                    print(f"  - {r}")
                print(f"Summarized Routes ({res['new_count']}):")
                for r in res["summarized_list"]:
                    print(f"  - {r}")
            except ValueError as e:
                print(f"\nError: {e}")

        elif choice == "5":
            print("\nExiting. Goodbye!")
            break

        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
