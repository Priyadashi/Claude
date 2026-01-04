"""
Sample data configuration for the factory schedule optimizer.

This module provides sample data including:
- Product definitions with costs and selling prices
- Machine configurations with capacities
- Demand orders
- Planning parameters
"""


def get_sample_config():
    """
    Returns a sample configuration for the factory optimizer.

    Returns:
        Dictionary containing products, machines, demands, and planning parameters
    """

    config = {
        # Products with their characteristics
        'products': [
            {
                'id': 'P001',
                'name': 'Widget A',
                'selling_price': 150.00,
                'production_cost': 80.00,
                'production_time_hrs': 0.5,  # Hours per unit
                'initial_inventory': 50,
                'min_inventory': 10,
                'max_inventory': 500,
                'compatible_machines': ['M001', 'M002']
            },
            {
                'id': 'P002',
                'name': 'Widget B',
                'selling_price': 200.00,
                'production_cost': 110.00,
                'production_time_hrs': 0.75,
                'initial_inventory': 30,
                'min_inventory': 5,
                'max_inventory': 400,
                'compatible_machines': ['M002', 'M003']
            },
            {
                'id': 'P003',
                'name': 'Widget C',
                'selling_price': 250.00,
                'production_cost': 140.00,
                'production_time_hrs': 1.0,
                'initial_inventory': 20,
                'min_inventory': 5,
                'max_inventory': 300,
                'compatible_machines': ['M001', 'M003']
            },
            {
                'id': 'P004',
                'name': 'Widget D',
                'selling_price': 180.00,
                'production_cost': 95.00,
                'production_time_hrs': 0.6,
                'initial_inventory': 40,
                'min_inventory': 10,
                'max_inventory': 350,
                'compatible_machines': ['M001', 'M002', 'M003']
            }
        ],

        # Machines with their capabilities
        'machines': [
            {
                'id': 'M001',
                'name': 'Production Line 1',
                'availability': 1.0,  # 100% available (can be reduced for maintenance)
            },
            {
                'id': 'M002',
                'name': 'Production Line 2',
                'availability': 0.95,  # 95% available (5% downtime)
            },
            {
                'id': 'M003',
                'name': 'Production Line 3',
                'availability': 0.90,  # 90% available (10% downtime)
            }
        ],

        # Demand orders with due dates
        'demands': [
            # Day 0-2 demands
            {'product_id': 'P001', 'quantity': 80, 'day': 2},
            {'product_id': 'P002', 'quantity': 50, 'day': 2},

            # Day 3-5 demands
            {'product_id': 'P001', 'quantity': 100, 'day': 5},
            {'product_id': 'P003', 'quantity': 60, 'day': 5},
            {'product_id': 'P004', 'quantity': 70, 'day': 5},

            # Day 6-8 demands
            {'product_id': 'P002', 'quantity': 80, 'day': 8},
            {'product_id': 'P003', 'quantity': 50, 'day': 8},
            {'product_id': 'P004', 'quantity': 90, 'day': 8},

            # Day 9-10 demands
            {'product_id': 'P001', 'quantity': 120, 'day': 10},
            {'product_id': 'P002', 'quantity': 70, 'day': 10},

            # Day 11-14 demands
            {'product_id': 'P003', 'quantity': 100, 'day': 14},
            {'product_id': 'P004', 'quantity': 110, 'day': 14},
        ],

        # Planning parameters
        'planning_horizon': 14,  # 14 days
        'shifts_per_day': 2,     # 2 shifts
        'hours_per_shift': 8,    # 8 hours per shift
    }

    return config


def get_tight_capacity_config():
    """
    Returns a configuration with tighter capacity constraints for testing.

    This scenario has higher demand relative to capacity, making the optimization
    more challenging and interesting.
    """

    config = {
        'products': [
            {
                'id': 'P001',
                'name': 'Premium Widget',
                'selling_price': 300.00,
                'production_cost': 150.00,
                'production_time_hrs': 1.5,
                'initial_inventory': 20,
                'min_inventory': 5,
                'max_inventory': 200,
                'compatible_machines': ['M001']
            },
            {
                'id': 'P002',
                'name': 'Standard Widget',
                'selling_price': 150.00,
                'production_cost': 80.00,
                'production_time_hrs': 0.8,
                'initial_inventory': 50,
                'min_inventory': 10,
                'max_inventory': 300,
                'compatible_machines': ['M001', 'M002']
            },
            {
                'id': 'P003',
                'name': 'Economy Widget',
                'selling_price': 100.00,
                'production_cost': 60.00,
                'production_time_hrs': 0.5,
                'initial_inventory': 80,
                'min_inventory': 20,
                'max_inventory': 400,
                'compatible_machines': ['M002']
            }
        ],

        'machines': [
            {
                'id': 'M001',
                'name': 'High-End Production Line',
                'availability': 0.85,  # 15% downtime for maintenance
            },
            {
                'id': 'M002',
                'name': 'General Production Line',
                'availability': 0.90,  # 10% downtime
            }
        ],

        'demands': [
            {'product_id': 'P001', 'quantity': 100, 'day': 3},
            {'product_id': 'P002', 'quantity': 150, 'day': 3},
            {'product_id': 'P003', 'quantity': 200, 'day': 5},
            {'product_id': 'P001', 'quantity': 120, 'day': 7},
            {'product_id': 'P002', 'quantity': 180, 'day': 7},
            {'product_id': 'P003', 'quantity': 250, 'day': 10},
            {'product_id': 'P001', 'quantity': 150, 'day': 10},
        ],

        'planning_horizon': 10,
        'shifts_per_day': 2,
        'hours_per_shift': 8,
    }

    return config


def get_multi_shift_config():
    """
    Returns a configuration for a 3-shift operation.

    Demonstrates the flexibility of the optimizer for different shift configurations.
    """

    config = {
        'products': [
            {
                'id': 'P001',
                'name': '24/7 Product A',
                'selling_price': 200.00,
                'production_cost': 100.00,
                'production_time_hrs': 0.5,
                'initial_inventory': 100,
                'min_inventory': 20,
                'max_inventory': 500,
                'compatible_machines': ['M001', 'M002']
            },
            {
                'id': 'P002',
                'name': '24/7 Product B',
                'selling_price': 250.00,
                'production_cost': 130.00,
                'production_time_hrs': 0.75,
                'initial_inventory': 80,
                'min_inventory': 15,
                'max_inventory': 400,
                'compatible_machines': ['M001', 'M002']
            }
        ],

        'machines': [
            {
                'id': 'M001',
                'name': 'Continuous Line 1',
                'availability': 0.95,
            },
            {
                'id': 'M002',
                'name': 'Continuous Line 2',
                'availability': 0.95,
            }
        ],

        'demands': [
            {'product_id': 'P001', 'quantity': 200, 'day': 3},
            {'product_id': 'P002', 'quantity': 150, 'day': 3},
            {'product_id': 'P001', 'quantity': 250, 'day': 7},
            {'product_id': 'P002', 'quantity': 200, 'day': 7},
        ],

        'planning_horizon': 7,
        'shifts_per_day': 3,  # 3 shifts for 24-hour operation
        'hours_per_shift': 8,
    }

    return config


def load_config_from_dict(custom_config):
    """
    Validate and return a custom configuration.

    Args:
        custom_config: Dictionary with configuration data

    Returns:
        Validated configuration dictionary

    Raises:
        ValueError: If required fields are missing
    """
    required_keys = ['products', 'machines', 'demands', 'planning_horizon']

    for key in required_keys:
        if key not in custom_config:
            raise ValueError(f"Missing required configuration key: {key}")

    # Set defaults for optional parameters
    if 'shifts_per_day' not in custom_config:
        custom_config['shifts_per_day'] = 2

    if 'hours_per_shift' not in custom_config:
        custom_config['hours_per_shift'] = 8

    return custom_config


if __name__ == "__main__":
    # Print sample configurations
    import json

    print("=" * 80)
    print("SAMPLE CONFIGURATION")
    print("=" * 80)
    config = get_sample_config()
    print(json.dumps(config, indent=2))

    print("\n" + "=" * 80)
    print("TIGHT CAPACITY CONFIGURATION")
    print("=" * 80)
    config_tight = get_tight_capacity_config()
    print(json.dumps(config_tight, indent=2))

    print("\n" + "=" * 80)
    print("MULTI-SHIFT (3-SHIFT) CONFIGURATION")
    print("=" * 80)
    config_multi = get_multi_shift_config()
    print(json.dumps(config_multi, indent=2))
