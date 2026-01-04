"""
Example usage scenarios for the factory schedule optimizer.

This script demonstrates different ways to use the optimizer with various configurations.
"""

from factory_schedule_optimizer import FactoryScheduleOptimizer
from sample_data import (
    get_sample_config,
    get_tight_capacity_config,
    get_multi_shift_config
)


def example_1_basic():
    """Example 1: Basic usage with standard configuration."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Usage - Standard Configuration")
    print("="*80)

    # Load standard configuration
    config = get_sample_config()

    # Create optimizer
    optimizer = FactoryScheduleOptimizer(config)

    # Build and solve
    print("\nBuilding model...")
    optimizer.build_model()

    print("Solving model...")
    status = optimizer.solve(time_limit=300)

    print(f"\nSolution Status: {status}")

    if status == "Optimal":
        optimizer.print_solution_summary()
        optimizer.export_to_excel('example1_schedule.xlsx')
        optimizer.export_to_json('example1_schedule.json')
    else:
        print(f"Could not find optimal solution: {status}")


def example_2_tight_capacity():
    """Example 2: Challenging scenario with tight capacity."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Tight Capacity Scenario")
    print("="*80)

    config = get_tight_capacity_config()

    optimizer = FactoryScheduleOptimizer(config)
    optimizer.build_model()

    print("\nSolving challenging scenario with tight capacity...")
    status = optimizer.solve(time_limit=300)

    print(f"\nSolution Status: {status}")

    if status == "Optimal":
        optimizer.print_solution_summary()
        optimizer.export_to_excel('example2_tight_capacity.xlsx')
    else:
        print(f"Solution status: {status}")
        print("\nThis scenario may be infeasible due to tight capacity constraints.")
        print("Consider: reducing demand, increasing machine availability, or extending planning horizon.")


def example_3_three_shifts():
    """Example 3: Three-shift (24-hour) operation."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Three-Shift Operation (24/7)")
    print("="*80)

    config = get_multi_shift_config()

    optimizer = FactoryScheduleOptimizer(config)
    optimizer.build_model()

    print("\nSolving 3-shift operation model...")
    status = optimizer.solve(time_limit=300)

    print(f"\nSolution Status: {status}")

    if status == "Optimal":
        optimizer.print_solution_summary()
        optimizer.export_to_excel('example3_three_shifts.xlsx')


def example_4_custom_dates():
    """Example 4: Generate schedule with specific start date."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Schedule with Specific Start Date")
    print("="*80)

    config = get_sample_config()

    optimizer = FactoryScheduleOptimizer(config)
    optimizer.build_model()

    print("\nSolving model...")
    status = optimizer.solve()

    if status == "Optimal":
        # Get daily schedule starting from a specific date
        daily_schedule = optimizer.get_daily_schedule(start_date='2026-02-01')

        print(f"\nProduction Schedule starting from 2026-02-01:")
        print("-" * 80)

        for day_info in daily_schedule[:5]:  # Show first 5 days
            print(f"\nDate: {day_info['date']} (Day {day_info['day']})")
            for shift_num in range(optimizer.shifts_per_day):
                shift_items = day_info['shifts'][shift_num]
                if shift_items:
                    print(f"  Shift {shift_num + 1}:")
                    for item in shift_items:
                        print(f"    - {item['product']} on {item['machine']}: {item['quantity']:.2f} units")


def example_5_custom_config():
    """Example 5: Create custom configuration from scratch."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Custom Configuration")
    print("="*80)

    # Define custom configuration
    custom_config = {
        'products': [
            {
                'id': 'CUSTOM_A',
                'name': 'Custom Product A',
                'selling_price': 500.00,
                'production_cost': 250.00,
                'production_time_hrs': 2.0,
                'initial_inventory': 10,
                'min_inventory': 5,
                'max_inventory': 100,
                'compatible_machines': ['LINE_1']
            },
            {
                'id': 'CUSTOM_B',
                'name': 'Custom Product B',
                'selling_price': 300.00,
                'production_cost': 150.00,
                'production_time_hrs': 1.0,
                'initial_inventory': 20,
                'min_inventory': 5,
                'max_inventory': 150,
                'compatible_machines': ['LINE_1', 'LINE_2']
            }
        ],

        'machines': [
            {
                'id': 'LINE_1',
                'name': 'Assembly Line 1',
                'availability': 0.95
            },
            {
                'id': 'LINE_2',
                'name': 'Assembly Line 2',
                'availability': 0.90
            }
        ],

        'demands': [
            {'product_id': 'CUSTOM_A', 'quantity': 50, 'day': 5},
            {'product_id': 'CUSTOM_B', 'quantity': 100, 'day': 5},
            {'product_id': 'CUSTOM_A', 'quantity': 60, 'day': 10},
            {'product_id': 'CUSTOM_B', 'quantity': 120, 'day': 10},
        ],

        'planning_horizon': 10,
        'shifts_per_day': 2,
        'hours_per_shift': 8
    }

    optimizer = FactoryScheduleOptimizer(custom_config)
    optimizer.build_model()

    print("\nSolving custom configuration...")
    status = optimizer.solve()

    if status == "Optimal":
        print(f"\nOptimal solution found!")
        print(f"Total Gross Margin: ${optimizer.solution['objective_value']:,.2f}")

        # Show production summary
        print("\nProduction Summary:")
        for item in optimizer.solution['production_schedule'][:10]:  # First 10 items
            print(f"  Day {item['day']}, Shift {item['shift']}: "
                  f"{item['product_name']} - {item['quantity']:.2f} units on {item['machine_name']}")


def example_6_analyze_solution():
    """Example 6: Deep dive into solution analysis."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Solution Analysis")
    print("="*80)

    config = get_sample_config()
    optimizer = FactoryScheduleOptimizer(config)
    optimizer.build_model()
    status = optimizer.solve()

    if status == "Optimal":
        solution = optimizer.solution

        # Analyze machine utilization
        print("\nMachine Utilization Analysis:")
        print("-" * 80)

        machine_hours = {}
        for item in solution['production_schedule']:
            machine_id = item['machine_id']
            if machine_id not in machine_hours:
                machine_hours[machine_id] = {
                    'name': item['machine_name'],
                    'total_hours': 0
                }

            product = optimizer.products[item['product_id']]
            hours = product['production_time_hrs'] * item['quantity']
            machine_hours[machine_id]['total_hours'] += hours

        total_available = optimizer.planning_horizon * optimizer.shifts_per_day * optimizer.hours_per_shift

        for machine_id, data in machine_hours.items():
            machine = optimizer.machines[machine_id]
            available = total_available * machine['availability']
            utilization = (data['total_hours'] / available) * 100
            print(f"{data['name']} ({machine_id}):")
            print(f"  Used: {data['total_hours']:.2f} hrs / Available: {available:.2f} hrs")
            print(f"  Utilization: {utilization:.1f}%")

        # Analyze product profitability
        print("\nProduct Profitability Analysis:")
        print("-" * 80)

        product_profit = {}
        for item in solution['production_schedule']:
            prod_id = item['product_id']
            if prod_id not in product_profit:
                product = optimizer.products[prod_id]
                product_profit[prod_id] = {
                    'name': item['product_name'],
                    'total_quantity': 0,
                    'unit_margin': product['selling_price'] - product['production_cost'],
                    'total_margin': 0
                }

            product_profit[prod_id]['total_quantity'] += item['quantity']

        for prod_id, data in product_profit.items():
            data['total_margin'] = data['unit_margin'] * data['total_quantity']
            print(f"{data['name']} ({prod_id}):")
            print(f"  Total Production: {data['total_quantity']:.2f} units")
            print(f"  Unit Margin: ${data['unit_margin']:.2f}")
            print(f"  Total Contribution: ${data['total_margin']:,.2f}")


def run_all_examples():
    """Run all examples."""
    examples = [
        ("Example 1: Basic Usage", example_1_basic),
        ("Example 2: Tight Capacity", example_2_tight_capacity),
        ("Example 3: Three Shifts", example_3_three_shifts),
        ("Example 4: Custom Dates", example_4_custom_dates),
        ("Example 5: Custom Config", example_5_custom_config),
        ("Example 6: Solution Analysis", example_6_analyze_solution),
    ]

    print("\n" + "="*80)
    print("FACTORY SCHEDULE OPTIMIZER - ALL EXAMPLES")
    print("="*80)

    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\nError in {name}: {str(e)}")
            import traceback
            traceback.print_exc()

        if i < len(examples):
            input("\nPress Enter to continue to next example...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples_map = {
            '1': example_1_basic,
            '2': example_2_tight_capacity,
            '3': example_3_three_shifts,
            '4': example_4_custom_dates,
            '5': example_5_custom_config,
            '6': example_6_analyze_solution,
            'all': run_all_examples
        }

        if example_num in examples_map:
            examples_map[example_num]()
        else:
            print(f"Invalid example number. Use 1-6 or 'all'")
    else:
        print("Usage: python examples.py [1-6|all]")
        print("\nAvailable examples:")
        print("  1 - Basic Usage")
        print("  2 - Tight Capacity Scenario")
        print("  3 - Three-Shift Operation")
        print("  4 - Custom Start Date")
        print("  5 - Custom Configuration")
        print("  6 - Solution Analysis")
        print("  all - Run all examples")
        print("\nRunning Example 1 by default...\n")
        example_1_basic()
