# Factory Production Schedule Optimizer

A linear programming-based production scheduling optimizer that maximizes gross margin while respecting inventory, machine capacity, and demand constraints.

## Features

- **Objective**: Maximize total gross margin (revenue - production costs)
- **2-Shift Operation**: Configurable shifts (default: 2 shifts × 8 hours)
- **Constraints**:
  - Machine capacity per shift
  - Inventory balance and limits
  - Demand fulfillment requirements
  - Product-machine compatibility
- **Output**: Day-wise production schedule with shift-level detail
- **Export**: Excel and JSON formats

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `pulp` - Linear programming solver
- `pandas` - Data manipulation and Excel export
- `openpyxl` - Excel file support

## Quick Start

### Basic Usage

```python
from factory_schedule_optimizer import FactoryScheduleOptimizer
from sample_data import get_sample_config

# Load configuration
config = get_sample_config()

# Create and solve
optimizer = FactoryScheduleOptimizer(config)
optimizer.build_model()
status = optimizer.solve()

# View results
if status == "Optimal":
    optimizer.print_solution_summary()
    optimizer.export_to_excel('schedule.xlsx')
    optimizer.export_to_json('schedule.json')
```

### Run Example

```bash
python factory_schedule_optimizer.py
```

## Configuration Structure

### Products

```python
{
    'id': 'P001',                      # Unique product identifier
    'name': 'Widget A',                # Product name
    'selling_price': 150.00,           # Selling price per unit
    'production_cost': 80.00,          # Production cost per unit
    'production_time_hrs': 0.5,        # Hours required per unit
    'initial_inventory': 50,           # Starting inventory
    'min_inventory': 10,               # Minimum inventory to maintain
    'max_inventory': 500,              # Maximum inventory capacity
    'compatible_machines': ['M001', 'M002']  # Machines that can produce this
}
```

### Machines

```python
{
    'id': 'M001',                      # Unique machine identifier
    'name': 'Production Line 1',       # Machine name
    'availability': 1.0                # Availability factor (0.0-1.0)
                                       # 1.0 = 100%, 0.9 = 90% (10% downtime)
}
```

### Demands

```python
{
    'product_id': 'P001',              # Product to be delivered
    'quantity': 80,                    # Quantity required
    'day': 2                           # Due date (day number, 0-indexed)
}
```

### Planning Parameters

```python
{
    'planning_horizon': 14,            # Number of days to plan
    'shifts_per_day': 2,               # Number of shifts per day
    'hours_per_shift': 8               # Hours per shift
}
```

## Mathematical Model

### Decision Variables

- **Production Variables**: `x[p,m,d,s]` = quantity of product `p` produced on machine `m` on day `d` in shift `s`
- **Inventory Variables**: `I[p,d]` = inventory level of product `p` at end of day `d`

### Objective Function

Maximize: `Σ (selling_price[p] - production_cost[p]) × x[p,m,d,s]`

For all products `p`, machines `m`, days `d`, and shifts `s`

### Constraints

#### 1. Machine Capacity
For each machine `m`, day `d`, and shift `s`:

```
Σ (production_time[p] × x[p,m,d,s]) ≤ hours_per_shift × availability[m]
```

#### 2. Inventory Balance
For each product `p` and day `d`:

```
I[p,d] = I[p,d-1] + Σ x[p,m,d,s] - demand[p,d]
        (all machines m, all shifts s)
```

Where `I[p,-1]` = initial inventory of product `p`

#### 3. Demand Fulfillment
For each demand order with product `p`, quantity `q`, and due date `D`:

```
initial_inventory[p] + Σ x[p,m,d,s] ≥ q
                       (all m, d≤D, s)
```

#### 4. Inventory Limits
For each product `p` and day `d`:

```
min_inventory[p] ≤ I[p,d] ≤ max_inventory[p]
```

#### 5. Non-negativity
```
x[p,m,d,s] ≥ 0
I[p,d] ≥ 0
```

## Sample Scenarios

### 1. Standard Configuration
```python
from sample_data import get_sample_config
config = get_sample_config()
```
- 4 products, 3 machines
- 14-day planning horizon
- 2 shifts × 8 hours
- Moderate demand levels

### 2. Tight Capacity
```python
from sample_data import get_tight_capacity_config
config = get_tight_capacity_config()
```
- Higher demand relative to capacity
- Tests optimization under pressure
- More challenging scenario

### 3. Three-Shift Operation
```python
from sample_data import get_multi_shift_config
config = get_multi_shift_config()
```
- 3 shifts × 8 hours (24-hour operation)
- Continuous production lines

## Output Format

### Console Output

The optimizer prints:
- Optimization status and total gross margin
- Production summary by product
- Day-wise schedule with shift details
- Inventory levels over time

### Excel Export

Three sheets:
1. **Production Schedule**: All production activities
2. **Inventory Levels**: Inventory over time
3. **Summary**: Key metrics and parameters

### JSON Export

Structured data including:
- Summary statistics
- Production schedule
- Inventory levels
- Daily schedule grouped by day and shift

## Advanced Usage

### Custom Configuration

```python
config = {
    'products': [...],
    'machines': [...],
    'demands': [...],
    'planning_horizon': 10,
    'shifts_per_day': 2,
    'hours_per_shift': 8
}

optimizer = FactoryScheduleOptimizer(config)
optimizer.build_model()
optimizer.solve()
```

### Solver Options

```python
# Increase time limit for complex problems
status = optimizer.solve(time_limit=600)  # 10 minutes

# Use different solver
status = optimizer.solve(solver_name='GLPK_CMD')
```

### Access Solution Data

```python
# Get solution details
solution = optimizer.solution

# Access production schedule
for item in solution['production_schedule']:
    print(f"Day {item['day']}, Shift {item['shift']}: "
          f"{item['product_name']} - {item['quantity']} units")

# Get daily schedule
daily = optimizer.get_daily_schedule(start_date='2026-01-04')
```

## Performance Considerations

- **Problem Size**: Performance depends on products × machines × days × shifts
- **Solver Time**: Most problems solve in seconds; complex scenarios may take minutes
- **Memory**: Large planning horizons (>30 days) may require more memory

## Troubleshooting

### Infeasible Solution

If the model returns "Infeasible":
- Check if demand exceeds total capacity
- Verify machine-product compatibility
- Ensure initial inventory + production can meet demands
- Review inventory min/max constraints

### Slow Solving

If optimization takes too long:
- Reduce planning horizon
- Decrease number of products or machines
- Increase solver time limit
- Consider using a commercial solver (CPLEX, Gurobi)

## Extending the Model

### Add Setup Times

Modify `_add_machine_capacity_constraints()` to include setup times when switching products.

### Add Overtime Shifts

Add additional shift variables with higher costs.

### Batch Size Constraints

Add minimum/maximum batch size constraints for production runs.

### Multi-Stage Production

Extend to include intermediate products and processing stages.

## License

This production optimizer is provided as-is for factory scheduling optimization.

## Contact

For questions or issues, please refer to the project repository.
