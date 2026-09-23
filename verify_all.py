import glob
import json

from delivery_system import load_data, simulate_deliveries, build_report, save_report


def verify_all():
    test_files = sorted(glob.glob("data/test_case_*.json"))
    test_files.append("data/base_case.json")

    all_passed = True

    for path in test_files:
        filename = path.split("/")[-1].split("\\")[-1]  # windows/mac paths, just in case
        try:
            data = load_data(path)
            stats = simulate_deliveries_silent(data)
            report = build_report(stats, total_packages=len(data["packages"]))

            delivered_total = sum(
                v["packages_delivered"] for k, v in report.items() if k != "best_agent"
            )
            expected_total = len(data["packages"])

            if delivered_total == expected_total:
                print(f"[PASS] {filename}: {delivered_total}/{expected_total} packages delivered, best_agent={report['best_agent']}")
            else:
                print(f"[FAIL] {filename}: only {delivered_total}/{expected_total} packages delivered!")
                all_passed = False

            out_name = filename.replace(".json", "_report.json")
            save_report(report, f"reports/{out_name}")

        except Exception as e:
            print(f"[ERROR] {filename}: {e}")
            all_passed = False

    print()
    if all_passed:
        print("All test cases passed.")
    else:
        print("Some test cases failed — see above.")


def simulate_deliveries_silent(data):
    # same as simulate_deliveries, just mutes the per-package prints
    # so this script's output isn't a wall of text
    import builtins
    original_print = builtins.print
    builtins.print = lambda *a, **k: None
    try:
        result = simulate_deliveries(data)
    finally:
        builtins.print = original_print
    return result


if __name__ == "__main__":
    verify_all()