#!/usr/bin/env python
"""
Script to run the factory schedule optimizer with a configuration file.

Usage:
    python run_optimizer.py                          # Use default sample config
    python run_optimizer.py config.json              # Use custom JSON config
    python run_optimizer.py --tight                  # Use tight capacity scenario
    python run_optimizer.py --multi-shift            # Use 3-shift scenario
"""

import sys
import json
import argparse
from factory_schedule_optimizer import FactoryScheduleOptimizer
from sample_data import (
    get_sample_config,
    get_tight_capacity_config,
    get_multi_shift_config
)


def load_config_from_file(filename):
    """Load configuration from a JSON file."""
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
        print(f"Configuration loaded from {filename}")
        return config
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Factory Production Schedule Optimizer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        Run with default sample configuration
  %(prog)s config.json            Run with custom JSON configuration file
  %(prog)s --tight                Run with tight capacity scenario
  %(prog)s --multi-shift          Run with 3-shift operation scenario
  %(prog)s -o output.xlsx         Specify output Excel filename
        """
    )

    parser.add_argument(
        'config_file',
        nargs='?',
        help='Path to JSON configuration file (optional)'
    )

    parser.add_argument(
        '--tight',
        action='store_true',
        help='Use tight capacity scenario'
    )

    parser.add_argument(
        '--multi-shift',
        action='store_true',
        help='Use 3-shift operation scenario'
    )

    parser.add_argument(
        '-o', '--output',
        default='production_schedule.xlsx',
        help='Output Excel filename (default: production_schedule.xlsx)'
    )

    parser.add_argument(
        '-j', '--json-output',
        help='Output JSON filename (optional)'
    )

    parser.add_argument(
        '-t', '--time-limit',
        type=int,
        default=300,
        help='Solver time limit in seconds (default: 300)'
    )

    parser.add_argument(
        '--no-export',
        action='store_true',
        help='Skip exporting to files'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed output, show only summary'
    )

    args = parser.parse_args()

    # Determine which configuration to use
    if args.config_file:
        config = load_config_from_file(args.config_file)
    elif args.tight:
        print("Using tight capacity scenario")
        config = get_tight_capacity_config()
    elif args.multi_shift:
        print("Using 3-shift operation scenario")
        config = get_multi_shift_config()
    else:
        print("Using default sample configuration")
        config = get_sample_config()

    # Create optimizer
    optimizer = FactoryScheduleOptimizer(config)

    # Build and solve the model
    if not args.quiet:
        print("\nBuilding optimization model...")
    optimizer.build_model()

    if not args.quiet:
        print("Solving optimization model...")
    status = optimizer.solve(time_limit=args.time_limit)

    if not args.quiet:
        print(f"\nOptimization Status: {status}\n")

    # Display results
    if status == "Optimal":
        if args.quiet:
            # Show only summary
            print(f"Status: {optimizer.solution['status']}")
            print(f"Total Gross Margin: ${optimizer.solution['objective_value']:,.2f}")
            print(f"Planning Horizon: {optimizer.planning_horizon} days")
        else:
            # Show full details
            optimizer.print_solution_summary()

        # Export results
        if not args.no_export:
            optimizer.export_to_excel(args.output)

            if args.json_output:
                optimizer.export_to_json(args.json_output)
            elif not args.quiet:
                # Default JSON export only if not quiet
                json_file = args.output.replace('.xlsx', '.json')
                optimizer.export_to_json(json_file)

        return 0

    elif status == "Infeasible":
        print("\n" + "="*80)
        print("ERROR: The problem is INFEASIBLE")
        print("="*80)
        print("\nPossible reasons:")
        print("1. Demand exceeds total production capacity")
        print("2. Machine-product compatibility issues")
        print("3. Inventory constraints are too restrictive")
        print("4. Insufficient initial inventory to meet early demands")
        print("\nSuggestions:")
        print("- Increase planning horizon")
        print("- Reduce demand quantities or extend due dates")
        print("- Increase machine availability")
        print("- Check initial inventory levels")
        print("- Review min/max inventory constraints")
        return 1

    else:
        print(f"\nOptimization failed with status: {status}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
