# FastBox — Mystery Delivery System

A logistics simulator for a fictional delivery company. Assigns packages
to the nearest available agent, simulates a day of deliveries, and
produces a performance report per agent.

## Structure
```text
fastbox-delivery-system/
├── delivery_system.py # core logic: parsing, distance, simulation, report
├── main.py # command-line entry point
├── verify_all.py # runs every file in data/ and checks totals
├── data/ # input JSON files
├── reports/ # generated report.json / CSV outputs
└── README.md

```
## Usage

```bash
python main.py data/base_case.json
python main.py data/test_case_1.json --out reports/test_case_1_report.json
python main.py data/base_case.json --ascii --csv reports/top_performer.csv
python verify_all.py   # runs every test file and confirms all packages are delivered
```

## Assumptions

The brief left some logic undefined. Per the instructions in the
assignment email, here's what I assumed and why, instead of stopping to ask:

1. **Input format.** The sample `data.json` uses a list-of-objects shape
   for warehouses/agents (`[{"id": "W1", "location": [0,0]}]`) and
   `"warehouse_id"` for packages. The provided `test_case_*.json` files use
   a dict shape (`{"W1": [0,0]}`) and `"warehouse"`. `load_data()`
   normalizes both into one consistent shape so the same code handles
   every input file without special-casing.

2. **Assignment order.** Packages are processed in the order they appear
   in the file (standing in for the order they became ready that day).

3. **"Nearest agent."** Distance is measured from each agent's *current*
   position — starting position, or wherever their last delivery left
   them — not a fixed starting position. This is more realistic: a real
   dispatcher tracks where agents currently are, not just where they
   started the day.

4. **Total distance.** Includes both legs: current position → warehouse
   (pickup) and warehouse → destination (delivery). An agent that has to
   travel to reach the warehouse really does cover that distance.

5. **`efficiency`.** Taken literally from the brief's sample report:
   `total_distance / packages_delivered` — average distance per delivery,
   so lower is better.

6. **`best_agent`.** The agent with the lowest `efficiency` among agents
   who delivered at least one package.

## Bonus features implemented

- **ASCII route map** — `--ascii` prints a scaled text-grid of warehouse
  and agent positions, with warehouses as letters (A, B, C...) and agents
  as numbers (1, 2, 3...), plus a legend.
- **Export top performer to CSV** — `--csv path.csv` writes the best
  agent's stats to a CSV file.

## Testing

`verify_all.py` runs the simulator against every file in `data/`
(base case + all 10 test cases) and confirms `packages_delivered` sums to
the total package count for each — all 11 pass.

## Author

Prathamesh Sarode