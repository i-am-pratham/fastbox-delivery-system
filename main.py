import argparse
import json
import os

from delivery_system import (
    load_data,
    simulate_deliveries,
    build_report,
    save_report,
    ascii_visualize,
    export_top_performer_csv,
)


def main():
    parser = argparse.ArgumentParser(description="FastBox delivery simulator")
    parser.add_argument("input", help="Path to input JSON file, e.g. data/test_case_1.json")
    parser.add_argument("--out", default="report.json", help="Where to save the report")
    parser.add_argument("--ascii", action="store_true", help="Print an ASCII route map")
    parser.add_argument("--csv", default=None, help="Path to export top performer as CSV")
    args = parser.parse_args()

    data = load_data(args.input)
    stats = simulate_deliveries(data)
    report = build_report(stats, total_packages=len(data["packages"]))
    save_report(report, args.out)

    print()
    print(json.dumps(report, indent=2))

    if args.ascii:
        map_text = ascii_visualize(data["warehouses"], data["agents"])
        print()
        print(map_text)

        # put the map file in the same folder as the report, just with
        # a different name — safer than string-replacing "report"
        folder = os.path.dirname(args.out) or "."
        base_name = os.path.basename(args.out).replace(".json", "")
        map_path = os.path.join(folder, f"{base_name}_route_map.txt")

        with open(map_path, "w") as f:
            f.write(map_text)
        print(f"\nRoute map saved to {map_path}")

    if args.csv:
        export_top_performer_csv(report, args.csv)


if __name__ == "__main__":
    main()