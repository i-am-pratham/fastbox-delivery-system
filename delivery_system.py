import json
import math
import csv


def euclidean(point_a, point_b):
    # straight line distance between two points
    x1, y1 = point_a
    x2, y2 = point_b
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def load_data(path):
    # loads the json and normalizes it since the sample data.json and the
    # test_case files don't use the same structure
    with open(path, "r") as f:
        raw = json.load(f)

    warehouses = normalize_locations(raw["warehouses"])
    agents = normalize_locations(raw["agents"])
    packages = normalize_packages(raw["packages"])

    return {"warehouses": warehouses, "agents": agents, "packages": packages}


def normalize_locations(entries):
    # handles both formats:
    # base_case.json -> [{"id": "W1", "location": [0, 0]}, ...]
    # test_case_*.json -> {"W1": [0, 0], ...}
    if isinstance(entries, dict):
        return {key: tuple(value) for key, value in entries.items()}

    if isinstance(entries, list):
        return {item["id"]: tuple(item["location"]) for item in entries}

    raise ValueError("Unexpected format for warehouses/agents")


def normalize_packages(packages):
    # some files use "warehouse", others use "warehouse_id"
    normalized = []
    for pkg in packages:
        warehouse_id = pkg.get("warehouse", pkg.get("warehouse_id"))
        normalized.append({
            "id": pkg["id"],
            "warehouse": warehouse_id,
            "destination": tuple(pkg["destination"]),
        })
    return normalized


def find_nearest_agent(agent_positions, warehouse_location):
    # just loops through every agent and keeps the closest one
    best_agent = None
    best_distance = None

    for agent_id, agent_pos in agent_positions.items():
        dist = euclidean(agent_pos, warehouse_location)
        if best_distance is None or dist < best_distance:
            best_distance = dist
            best_agent = agent_id

    return best_agent


def simulate_deliveries(data):
    warehouses = data["warehouses"]
    packages = data["packages"]

    # agents move as they deliver, so we track live positions here
    # instead of just using their starting spot for every assignment
    current_position = dict(data["agents"])

    stats = {}
    for agent_id in data["agents"]:
        stats[agent_id] = {"packages_delivered": 0, "total_distance": 0.0}

    for pkg in packages:
        warehouse_loc = warehouses[pkg["warehouse"]]
        destination = pkg["destination"]

        agent_id = find_nearest_agent(current_position, warehouse_loc)
        agent_current_pos = current_position[agent_id]

        # agent goes current spot -> warehouse -> destination
        pickup_leg = euclidean(agent_current_pos, warehouse_loc)
        delivery_leg = euclidean(warehouse_loc, destination)

        stats[agent_id]["packages_delivered"] += 1
        stats[agent_id]["total_distance"] += pickup_leg + delivery_leg

        # agent is now at the destination, next assignment uses this
        current_position[agent_id] = destination

        print(f"{pkg['id']}: assigned to {agent_id} "
              f"(pickup {pickup_leg:.2f} + delivery {delivery_leg:.2f})")

    return stats


def build_report(stats, total_packages):
    report = {}

    for agent_id, s in stats.items():
        delivered = s["packages_delivered"]
        distance = round(s["total_distance"], 2)
        efficiency = round(distance / delivered, 2) if delivered > 0 else 0.0

        report[agent_id] = {
            "packages_delivered": delivered,
            "total_distance": distance,
            "efficiency": efficiency,
        }

    # make sure nothing got dropped
    delivered_total = sum(v["packages_delivered"] for v in report.values())
    assert delivered_total == total_packages, "Some packages went missing!"

    # best agent = lowest avg distance per delivery, ignore agents who got nothing
    agents_who_delivered = {a: v for a, v in report.items() if v["packages_delivered"] > 0}
    best_agent = min(agents_who_delivered, key=lambda a: agents_who_delivered[a]["efficiency"])

    report["best_agent"] = best_agent
    return report


def save_report(report, path="report.json"):
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {path}")


def ascii_visualize(warehouses, agents, width=50, height=20):
    # rough text-map, scales real coords down to fit the grid
    all_points = list(warehouses.values()) + list(agents.values())
    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1)
    span_y = max(max_y - min_y, 1)

    grid = [[" " for _ in range(width)] for _ in range(height)]

    def to_cell(point):
        x, y = point
        col = int((x - min_x) / span_x * (width - 1))
        row = int((max_y - y) / span_y * (height - 1))  # flip y, text grids print top-down
        return row, col

    legend = {}

    # warehouses get letters, agents get numbers so nothing collides
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, (wh_id, loc) in enumerate(warehouses.items()):
        symbol = letters[i] if i < len(letters) else "?"
        legend[symbol] = f"warehouse {wh_id}"
        row, col = to_cell(loc)
        grid[row][col] = symbol

    digits = "123456789"
    for i, (agent_id, loc) in enumerate(agents.items()):
        symbol = digits[i] if i < len(digits) else "?"
        legend[symbol] = f"agent {agent_id}"
        row, col = to_cell(loc)
        if grid[row][col] == " ":
            grid[row][col] = symbol

    border = "+" + "-" * width + "+"
    lines = [border]
    for row in grid:
        lines.append("|" + "".join(row) + "|")
    lines.append(border)

    lines.append("Legend:")
    for symbol, name in legend.items():
        lines.append(f"  {symbol} = {name}")

    return "\n".join(lines)


def export_top_performer_csv(report, path):
    best = report.get("best_agent")
    if best is None:
        return

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["agent_id", "packages_delivered", "total_distance", "efficiency"])
        stats = report[best]
        writer.writerow([best, stats["packages_delivered"], stats["total_distance"], stats["efficiency"]])

    print(f"Top performer exported to {path}")