"""
Factory Production Schedule Optimizer

This module implements a production optimization model for factory scheduling that:
- Maximizes gross margin
- Respects inventory constraints
- Considers machine availability
- Meets demand requirements
- Plans for 2-shift operation (8 hours per shift)
"""

import pulp
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json


class FactoryScheduleOptimizer:
    """
    Production scheduling optimizer using linear programming.

    Optimizes production schedule to maximize gross margin while respecting:
    - Machine capacity constraints
    - Inventory level constraints
    - Demand fulfillment requirements
    """

    def __init__(self, config: Dict):
        """
        Initialize the optimizer with configuration data.

        Args:
            config: Dictionary containing:
                - products: List of product definitions
                - machines: List of machine definitions
                - demands: List of demand orders
                - planning_horizon: Number of days to plan
                - shifts_per_day: Number of shifts (default: 2)
                - hours_per_shift: Hours per shift (default: 8)
        """
        self.products = {p['id']: p for p in config['products']}
        self.machines = {m['id']: m for m in config['machines']}
        self.demands = config['demands']
        self.planning_horizon = config['planning_horizon']
        self.shifts_per_day = config.get('shifts_per_day', 2)
        self.hours_per_shift = config.get('hours_per_shift', 8)

        self.model = None
        self.production_vars = {}
        self.inventory_vars = {}
        self.solution = None

    def build_model(self):
        """Build the linear programming model."""
        # Create the optimization model
        self.model = pulp.LpProblem("Factory_Schedule_Optimizer", pulp.LpMaximize)

        # Create decision variables
        self._create_variables()

        # Set objective function
        self._set_objective()

        # Add constraints
        self._add_machine_capacity_constraints()
        self._add_inventory_balance_constraints()
        self._add_demand_constraints()
        self._add_inventory_limit_constraints()

    def _create_variables(self):
        """Create decision variables for production and inventory."""
        # Production variables: production[product, machine, day, shift]
        for prod_id in self.products:
            for machine_id in self.machines:
                # Check if this machine can produce this product
                product = self.products[prod_id]
                if machine_id in product.get('compatible_machines', []):
                    for day in range(self.planning_horizon):
                        for shift in range(self.shifts_per_day):
                            var_name = f"prod_{prod_id}_{machine_id}_d{day}_s{shift}"
                            self.production_vars[(prod_id, machine_id, day, shift)] = \
                                pulp.LpVariable(var_name, lowBound=0, cat='Continuous')

        # Inventory variables: inventory[product, day]
        for prod_id in self.products:
            for day in range(self.planning_horizon + 1):  # +1 for end inventory
                var_name = f"inv_{prod_id}_d{day}"
                self.inventory_vars[(prod_id, day)] = \
                    pulp.LpVariable(var_name, lowBound=0, cat='Continuous')

    def _set_objective(self):
        """Set the objective function to maximize gross margin."""
        gross_margin = 0

        for (prod_id, machine_id, day, shift), var in self.production_vars.items():
            product = self.products[prod_id]
            selling_price = product['selling_price']
            production_cost = product['production_cost']
            margin_per_unit = selling_price - production_cost

            gross_margin += margin_per_unit * var

        self.model += gross_margin, "Total_Gross_Margin"

    def _add_machine_capacity_constraints(self):
        """Add constraints for machine capacity (hours available per shift)."""
        for machine_id in self.machines:
            machine = self.machines[machine_id]
            available_hours = self.hours_per_shift * machine.get('availability', 1.0)

            for day in range(self.planning_horizon):
                for shift in range(self.shifts_per_day):
                    # Total production time on this machine for this day-shift
                    total_time = 0

                    for prod_id in self.products:
                        key = (prod_id, machine_id, day, shift)
                        if key in self.production_vars:
                            product = self.products[prod_id]
                            time_per_unit = product.get('production_time_hrs', 0)
                            total_time += time_per_unit * self.production_vars[key]

                    # Constraint: total time <= available time
                    constraint_name = f"capacity_{machine_id}_d{day}_s{shift}"
                    self.model += total_time <= available_hours, constraint_name

    def _add_inventory_balance_constraints(self):
        """Add inventory balance constraints."""
        for prod_id in self.products:
            product = self.products[prod_id]
            initial_inventory = product.get('initial_inventory', 0)

            for day in range(self.planning_horizon):
                # Inventory balance: inv[day] = inv[day-1] + production[day] - demand[day]
                prev_inventory = self.inventory_vars[(prod_id, day - 1)] if day > 0 else initial_inventory
                curr_inventory = self.inventory_vars[(prod_id, day)]

                # Total production on this day (all machines, all shifts)
                total_production = 0
                for machine_id in self.machines:
                    for shift in range(self.shifts_per_day):
                        key = (prod_id, machine_id, day, shift)
                        if key in self.production_vars:
                            total_production += self.production_vars[key]

                # Demand on this day
                demand_on_day = sum(
                    d['quantity'] for d in self.demands
                    if d['product_id'] == prod_id and d['day'] == day
                )

                # Balance equation
                constraint_name = f"inv_balance_{prod_id}_d{day}"
                if day == 0:
                    self.model += curr_inventory == initial_inventory + total_production - demand_on_day, constraint_name
                else:
                    self.model += curr_inventory == prev_inventory + total_production - demand_on_day, constraint_name

    def _add_demand_constraints(self):
        """Add constraints to meet demand requirements."""
        # Group demands by product and due date
        for demand in self.demands:
            prod_id = demand['product_id']
            due_day = demand['day']
            quantity = demand['quantity']

            # Cumulative production up to due date must meet demand
            cumulative_production = 0
            for day in range(due_day + 1):
                for machine_id in self.machines:
                    for shift in range(self.shifts_per_day):
                        key = (prod_id, machine_id, day, shift)
                        if key in self.production_vars:
                            cumulative_production += self.production_vars[key]

            # Add initial inventory
            initial_inventory = self.products[prod_id].get('initial_inventory', 0)

            constraint_name = f"demand_{prod_id}_d{due_day}"
            self.model += cumulative_production + initial_inventory >= quantity, constraint_name

    def _add_inventory_limit_constraints(self):
        """Add minimum and maximum inventory level constraints."""
        for prod_id in self.products:
            product = self.products[prod_id]
            min_inventory = product.get('min_inventory', 0)
            max_inventory = product.get('max_inventory', float('inf'))

            for day in range(self.planning_horizon + 1):
                inv_var = self.inventory_vars[(prod_id, day)]

                # Minimum inventory constraint
                if min_inventory > 0:
                    constraint_name = f"min_inv_{prod_id}_d{day}"
                    self.model += inv_var >= min_inventory, constraint_name

                # Maximum inventory constraint
                if max_inventory < float('inf'):
                    constraint_name = f"max_inv_{prod_id}_d{day}"
                    self.model += inv_var <= max_inventory, constraint_name

    def solve(self, solver_name='PULP_CBC_CMD', time_limit=300):
        """
        Solve the optimization model.

        Args:
            solver_name: Name of the solver to use
            time_limit: Maximum time in seconds for solving

        Returns:
            Status of the solution
        """
        if self.model is None:
            self.build_model()

        # Solve the model
        solver = pulp.getSolver(solver_name, timeLimit=time_limit)
        status = self.model.solve(solver)

        if status == pulp.LpStatusOptimal:
            self._extract_solution()
            return "Optimal"
        elif status == pulp.LpStatusNotSolved:
            return "Not Solved"
        elif status == pulp.LpStatusInfeasible:
            return "Infeasible"
        elif status == pulp.LpStatusUnbounded:
            return "Unbounded"
        else:
            return "Unknown"

    def _extract_solution(self):
        """Extract solution from the solved model."""
        self.solution = {
            'status': pulp.LpStatus[self.model.status],
            'objective_value': pulp.value(self.model.objective),
            'production_schedule': [],
            'inventory_levels': []
        }

        # Extract production schedule
        for (prod_id, machine_id, day, shift), var in self.production_vars.items():
            quantity = var.varValue
            if quantity and quantity > 0.001:  # Only include non-zero production
                self.solution['production_schedule'].append({
                    'product_id': prod_id,
                    'product_name': self.products[prod_id]['name'],
                    'machine_id': machine_id,
                    'machine_name': self.machines[machine_id]['name'],
                    'day': day,
                    'shift': shift,
                    'quantity': round(quantity, 2)
                })

        # Extract inventory levels
        for (prod_id, day), var in self.inventory_vars.items():
            quantity = var.varValue
            if quantity is not None:
                self.solution['inventory_levels'].append({
                    'product_id': prod_id,
                    'product_name': self.products[prod_id]['name'],
                    'day': day,
                    'quantity': round(quantity, 2)
                })

    def get_daily_schedule(self, start_date=None):
        """
        Get formatted daily schedule.

        Args:
            start_date: Starting date for the schedule (default: today)

        Returns:
            List of daily schedules
        """
        if self.solution is None:
            return None

        if start_date is None:
            start_date = datetime.now().date()
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        # Group by day
        daily_schedule = {}
        for item in self.solution['production_schedule']:
            day = item['day']
            if day not in daily_schedule:
                date = start_date + timedelta(days=day)
                daily_schedule[day] = {
                    'day': day,
                    'date': date.strftime('%Y-%m-%d'),
                    'shifts': {i: [] for i in range(self.shifts_per_day)}
                }

            shift = item['shift']
            daily_schedule[day]['shifts'][shift].append({
                'product': f"{item['product_name']} ({item['product_id']})",
                'machine': f"{item['machine_name']} ({item['machine_id']})",
                'quantity': item['quantity']
            })

        return [daily_schedule[day] for day in sorted(daily_schedule.keys())]

    def print_solution_summary(self):
        """Print a summary of the solution."""
        if self.solution is None:
            print("No solution available. Please solve the model first.")
            return

        print("\n" + "="*80)
        print("FACTORY PRODUCTION SCHEDULE OPTIMIZATION SUMMARY")
        print("="*80)
        print(f"\nStatus: {self.solution['status']}")
        print(f"Total Gross Margin: ${self.solution['objective_value']:,.2f}")
        print(f"Planning Horizon: {self.planning_horizon} days")
        print(f"Shifts per Day: {self.shifts_per_day} ({self.hours_per_shift} hours each)")

        # Production summary
        print("\n" + "-"*80)
        print("PRODUCTION SUMMARY BY PRODUCT")
        print("-"*80)

        prod_summary = {}
        for item in self.solution['production_schedule']:
            prod_id = item['product_id']
            if prod_id not in prod_summary:
                prod_summary[prod_id] = {
                    'name': item['product_name'],
                    'total_quantity': 0
                }
            prod_summary[prod_id]['total_quantity'] += item['quantity']

        for prod_id, summary in prod_summary.items():
            product = self.products[prod_id]
            total_qty = summary['total_quantity']
            margin = (product['selling_price'] - product['production_cost']) * total_qty
            print(f"{summary['name']} ({prod_id}):")
            print(f"  Total Production: {total_qty:.2f} units")
            print(f"  Gross Margin: ${margin:,.2f}")

        # Daily schedule
        print("\n" + "-"*80)
        print("DAILY PRODUCTION SCHEDULE")
        print("-"*80)

        daily_schedule = self.get_daily_schedule()
        for day_info in daily_schedule:
            print(f"\nDay {day_info['day']} ({day_info['date']}):")
            for shift_num in range(self.shifts_per_day):
                shift_name = f"Shift {shift_num + 1}"
                shift_items = day_info['shifts'][shift_num]
                if shift_items:
                    print(f"  {shift_name}:")
                    for item in shift_items:
                        print(f"    - {item['product']} on {item['machine']}: {item['quantity']:.2f} units")
                else:
                    print(f"  {shift_name}: No production scheduled")

        # Inventory levels
        print("\n" + "-"*80)
        print("INVENTORY LEVELS")
        print("-"*80)

        inv_by_product = {}
        for item in self.solution['inventory_levels']:
            prod_id = item['product_id']
            if prod_id not in inv_by_product:
                inv_by_product[prod_id] = {
                    'name': item['product_name'],
                    'levels': []
                }
            inv_by_product[prod_id]['levels'].append({
                'day': item['day'],
                'quantity': item['quantity']
            })

        for prod_id, inv_data in inv_by_product.items():
            print(f"\n{inv_data['name']} ({prod_id}):")
            levels = sorted(inv_data['levels'], key=lambda x: x['day'])
            for level in levels:
                print(f"  Day {level['day']}: {level['quantity']:.2f} units")

        print("\n" + "="*80 + "\n")

    def export_to_excel(self, filename='production_schedule.xlsx'):
        """Export the solution to an Excel file."""
        if self.solution is None:
            print("No solution available. Please solve the model first.")
            return

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Production schedule
            df_prod = pd.DataFrame(self.solution['production_schedule'])
            if not df_prod.empty:
                df_prod = df_prod.sort_values(['day', 'shift', 'product_id'])
            df_prod.to_excel(writer, sheet_name='Production Schedule', index=False)

            # Inventory levels
            df_inv = pd.DataFrame(self.solution['inventory_levels'])
            if not df_inv.empty:
                df_inv = df_inv.sort_values(['day', 'product_id'])
            df_inv.to_excel(writer, sheet_name='Inventory Levels', index=False)

            # Summary
            summary_data = {
                'Metric': ['Status', 'Total Gross Margin', 'Planning Horizon (days)',
                          'Shifts per Day', 'Hours per Shift'],
                'Value': [self.solution['status'],
                         f"${self.solution['objective_value']:,.2f}",
                         self.planning_horizon,
                         self.shifts_per_day,
                         self.hours_per_shift]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)

        print(f"Solution exported to {filename}")

    def export_to_json(self, filename='production_schedule.json'):
        """Export the solution to a JSON file."""
        if self.solution is None:
            print("No solution available. Please solve the model first.")
            return

        output = {
            'summary': {
                'status': self.solution['status'],
                'total_gross_margin': self.solution['objective_value'],
                'planning_horizon_days': self.planning_horizon,
                'shifts_per_day': self.shifts_per_day,
                'hours_per_shift': self.hours_per_shift
            },
            'production_schedule': self.solution['production_schedule'],
            'inventory_levels': self.solution['inventory_levels'],
            'daily_schedule': self.get_daily_schedule()
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        print(f"Solution exported to {filename}")


def main():
    """Example usage of the factory schedule optimizer."""
    # Load configuration (you can replace this with loading from a file)
    from sample_data import get_sample_config

    config = get_sample_config()

    # Create optimizer
    optimizer = FactoryScheduleOptimizer(config)

    # Build and solve the model
    print("Building optimization model...")
    optimizer.build_model()

    print("Solving optimization model...")
    status = optimizer.solve(time_limit=300)

    print(f"Optimization Status: {status}")

    if status == "Optimal":
        # Print solution summary
        optimizer.print_solution_summary()

        # Export to files
        optimizer.export_to_excel('production_schedule.xlsx')
        optimizer.export_to_json('production_schedule.json')
    else:
        print(f"Could not find optimal solution. Status: {status}")


if __name__ == "__main__":
    main()
