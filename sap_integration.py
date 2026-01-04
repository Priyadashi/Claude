"""
SAP S/4HANA Integration Module

This module provides data models and integration utilities for SAP S/4HANA:
- PP Module: BOM (Bill of Materials), Routing (Work Centers, Operations)
- MM Module: Material Master, Inventory Management

The models align with SAP S/4HANA table structures:
- MARA/MARC: Material Master
- STKO/STPO: BOM Header/Item
- PLKO/PLPO: Routing Header/Operations
- MARD: Storage Location Stock
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


# ============================================================================
# SAP MM Module - Material Master & Inventory
# ============================================================================

@dataclass
class MaterialMaster:
    """
    Material Master Data (SAP MARA/MARC tables)

    Key fields from SAP:
    - MATNR: Material Number
    - MAKTX: Material Description
    - MEINS: Base Unit of Measure
    - WERKS: Plant
    """
    MATNR: str  # Material Number
    MAKTX: str  # Material Description
    MEINS: str  # Base Unit of Measure (EA, KG, etc.)
    WERKS: str  # Plant
    MTART: str  # Material Type (FERT=Finished, HALB=Semi-finished, ROH=Raw)
    MATKL: Optional[str] = None  # Material Group
    EKGRP: Optional[str] = None  # Purchasing Group
    DISMM: str = "PD"  # MRP Type (PD=MRP, VB=Manual)
    DISPO: Optional[str] = None  # MRP Controller

    # Costing Data
    VPRSV: str = "S"  # Price Control (S=Standard, V=Moving Average)
    STPRS: float = 0.0  # Standard Price
    PEINH: int = 1  # Price Unit

    # Sales Data
    VKORG: Optional[str] = None  # Sales Organization
    VTWEG: Optional[str] = None  # Distribution Channel
    VK_PRICE: float = 0.0  # Selling Price


@dataclass
class StorageLocationStock:
    """
    Storage Location Stock (SAP MARD table)

    Represents inventory at storage location level
    """
    MATNR: str  # Material Number
    WERKS: str  # Plant
    LGORT: str  # Storage Location
    LABST: float = 0.0  # Valuated Unrestricted-Use Stock
    INSME: float = 0.0  # Stock in Quality Inspection
    SPEME: float = 0.0  # Blocked Stock
    EINME: str = "EA"  # Unit of Entry


# ============================================================================
# SAP PP Module - BOM (Bill of Materials)
# ============================================================================

@dataclass
class BOMHeader:
    """
    BOM Header (SAP STKO table)

    Defines the BOM structure
    """
    STLNR: str  # BOM Number
    STLAL: str  # Alternative BOM
    MATNR: str  # Material Number
    WERKS: str  # Plant
    STLAN: str  # BOM Usage (1=Production, 3=Universal)
    BMENG: float = 1.0  # Base Quantity
    BMEIN: str = "EA"  # Base Unit of Measure
    STLST: str = "01"  # BOM Status (01=Active)
    DATUV: Optional[str] = None  # Valid-From Date


@dataclass
class BOMItem:
    """
    BOM Item (SAP STPO table)

    Individual components in a BOM
    """
    STLNR: str  # BOM Number
    STLAL: str  # Alternative BOM
    POSNR: str  # Item Number (0010, 0020, etc.)
    IDNRK: str  # Component Material Number
    MENGE: float  # Component Quantity
    MEINS: str  # Component Unit
    POSTP: str = "L"  # Item Category (L=Stock Item, N=Non-Stock)
    ALPRF: float = 0.0  # Percentage of Quantity (for alternative items)
    SANKA: str = ""  # Costing Relevance


# ============================================================================
# SAP PP Module - Routing
# ============================================================================

@dataclass
class RoutingHeader:
    """
    Routing Header (SAP PLKO table)

    Defines production routing/recipe
    """
    PLNNR: str  # Routing Group Number
    PLNAL: str  # Group Counter (Alternative)
    MATNR: str  # Material Number
    WERKS: str  # Plant
    PLNTY: str = "N"  # Task List Type (N=Normal Routing)
    VERWE: str = "1"  # Task List Usage (1=Production)
    STATU: str = "4"  # Status (4=Released)
    DATUV: Optional[str] = None  # Valid-From Date
    BMSCH: float = 1.0  # Lot Size From
    BMEIN: str = "EA"  # Lot Size Unit


@dataclass
class RoutingOperation:
    """
    Routing Operation (SAP PLPO table)

    Individual operations in a routing
    """
    PLNNR: str  # Routing Group Number
    PLNAL: str  # Group Counter
    PLNFL: str  # Sequence Number
    VORNR: str  # Operation Number (0010, 0020, etc.)
    WERKS: str  # Plant
    STEUS: str  # Control Key (PP01=Internal Processing)

    # Work Center
    ARBPL: str  # Work Center
    WERKS_ARBPL: Optional[str] = None  # Work Center Plant

    # Times (in minutes typically)
    VGW01: float = 0.0  # Standard Value 1 (Setup Time)
    VGE01: str = "MIN"  # Unit for Standard Value 1
    VGW02: float = 0.0  # Standard Value 2 (Machine Time)
    VGE02: str = "MIN"  # Unit for Standard Value 2
    VGW03: float = 0.0  # Standard Value 3 (Labor Time)
    VGE03: str = "MIN"  # Unit for Standard Value 3

    # Base Quantity
    BMSCH: float = 1.0  # Base Quantity
    MEINH: str = "EA"  # Base Unit of Measure

    # Description
    LTXA1: str = ""  # Operation Short Text


@dataclass
class WorkCenter:
    """
    Work Center Master (SAP CRHD/CRCA tables)

    Defines production resources/machines
    """
    ARBPL: str  # Work Center
    WERKS: str  # Plant
    KTEXT: str  # Description
    VERWE: str = "001"  # Usage (001=Production)

    # Capacity
    KALID: Optional[str] = None  # Factory Calendar
    SHIFT_HOURS: float = 8.0  # Hours per Shift
    SHIFTS_PER_DAY: int = 2  # Number of Shifts

    # Availability
    KAPAR: float = 1.0  # Capacity (Number of Individual Capacities)
    AUERU: float = 100.0  # Utilization (%)
    AVAILABLE_CAPACITY_PERCENT: float = 100.0  # Availability Factor

    # Costing
    KOSTL: Optional[str] = None  # Cost Center
    LOHNART: Optional[str] = None  # Activity Type


# ============================================================================
# Converter: SAP to Optimizer Format
# ============================================================================

class SAPToOptimizerConverter:
    """
    Converts SAP S/4HANA data structures to optimizer-compatible format
    """

    @staticmethod
    def convert_materials_and_inventory(
        materials: List[MaterialMaster],
        stock_data: List[StorageLocationStock]
    ) -> List[Dict]:
        """
        Convert SAP Material Master and Stock to optimizer products

        Args:
            materials: List of MaterialMaster objects
            stock_data: List of StorageLocationStock objects

        Returns:
            List of product dictionaries for optimizer
        """
        products = []

        # Create stock lookup
        stock_lookup = {}
        for stock in stock_data:
            key = (stock.MATNR, stock.WERKS, stock.LGORT)
            stock_lookup[key] = stock.LABST

        for material in materials:
            # Only process finished goods or semi-finished goods
            if material.MTART not in ['FERT', 'HALB']:
                continue

            # Get total stock for this material
            total_stock = sum(
                qty for (matnr, werks, lgort), qty in stock_lookup.items()
                if matnr == material.MATNR and werks == material.WERKS
            )

            product = {
                'id': material.MATNR,
                'name': material.MAKTX,
                'selling_price': material.VK_PRICE if material.VK_PRICE > 0 else material.STPRS * 1.5,
                'production_cost': material.STPRS,
                'production_time_hrs': 1.0,  # Will be overridden by routing data
                'initial_inventory': total_stock,
                'min_inventory': 0,  # Can be set from safety stock (EISBE)
                'max_inventory': 999999,
                'compatible_machines': [],  # Will be populated from routing
                'unit': material.MEINS,
                'plant': material.WERKS,
                'material_type': material.MTART
            }

            products.append(product)

        return products

    @staticmethod
    def convert_routings_to_production_time(
        routing_headers: List[RoutingHeader],
        routing_operations: List[RoutingOperation],
        products: List[Dict]
    ) -> List[Dict]:
        """
        Extract production time and work centers from routing data

        Args:
            routing_headers: List of RoutingHeader objects
            routing_operations: List of RoutingOperation objects
            products: List of product dictionaries

        Returns:
            Updated products list with production times and compatible machines
        """
        # Group operations by routing
        routing_ops = {}
        for op in routing_operations:
            key = (op.PLNNR, op.PLNAL)
            if key not in routing_ops:
                routing_ops[key] = []
            routing_ops[key].append(op)

        # Create routing lookup by material
        routing_by_material = {}
        for header in routing_headers:
            routing_by_material[header.MATNR] = (header.PLNNR, header.PLNAL, header.BMSCH)

        # Update products with routing info
        updated_products = []
        for product in products:
            if product['id'] in routing_by_material:
                plnnr, plnal, base_qty = routing_by_material[product['id']]
                operations = routing_ops.get((plnnr, plnal), [])

                # Calculate total production time
                total_setup_time = 0.0
                total_machine_time = 0.0
                work_centers = set()

                for op in operations:
                    # Setup time (VGW01) - per lot
                    setup_time_min = op.VGW01

                    # Machine/labor time (VGW02/VGW03) - per base quantity
                    machine_time_min = max(op.VGW02, op.VGW03)

                    total_setup_time += setup_time_min
                    total_machine_time += machine_time_min
                    work_centers.add(op.ARBPL)

                # Convert to hours per unit
                # Assuming base_qty from routing header
                if base_qty > 0:
                    # Setup time amortized over typical lot size (e.g., 100 units)
                    typical_lot_size = max(base_qty, 100)
                    setup_per_unit = total_setup_time / typical_lot_size / 60  # to hours
                    machine_per_unit = total_machine_time / base_qty / 60  # to hours

                    product['production_time_hrs'] = setup_per_unit + machine_per_unit
                    product['compatible_machines'] = list(work_centers)
                    product['routing_number'] = plnnr
                    product['routing_alternative'] = plnal

            updated_products.append(product)

        return updated_products

    @staticmethod
    def convert_work_centers(
        work_centers: List[WorkCenter]
    ) -> List[Dict]:
        """
        Convert SAP Work Centers to optimizer machines

        Args:
            work_centers: List of WorkCenter objects

        Returns:
            List of machine dictionaries for optimizer
        """
        machines = []

        for wc in work_centers:
            # Calculate availability factor (considering utilization and capacity)
            availability = (wc.AVAILABLE_CAPACITY_PERCENT / 100.0) * (wc.AUERU / 100.0) * wc.KAPAR

            machine = {
                'id': wc.ARBPL,
                'name': wc.KTEXT,
                'availability': min(availability, 1.0),  # Cap at 100%
                'plant': wc.WERKS,
                'shift_hours': wc.SHIFT_HOURS,
                'shifts_per_day': wc.SHIFTS_PER_DAY,
                'cost_center': wc.KOSTL
            }

            machines.append(machine)

        return machines


# ============================================================================
# SAP Data Loader (Mock/Template)
# ============================================================================

def load_sap_sample_data() -> Dict:
    """
    Load sample SAP data (simulates extraction from SAP)

    In production, this would connect to SAP via:
    - OData API
    - RFC/BAPI calls
    - CDS Views
    - Flat file extract
    """

    # Sample Materials
    materials = [
        MaterialMaster(
            MATNR="FG001",
            MAKTX="Premium Widget Assembly",
            MEINS="EA",
            WERKS="1000",
            MTART="FERT",
            STPRS=150.00,
            VK_PRICE=300.00,
            VPRSV="S"
        ),
        MaterialMaster(
            MATNR="FG002",
            MAKTX="Standard Widget Assembly",
            MEINS="EA",
            WERKS="1000",
            MTART="FERT",
            STPRS=100.00,
            VK_PRICE=200.00,
            VPRSV="S"
        ),
        MaterialMaster(
            MATNR="FG003",
            MAKTX="Economy Widget Assembly",
            MEINS="EA",
            WERKS="1000",
            MTART="FERT",
            STPRS=75.00,
            VK_PRICE=150.00,
            VPRSV="S"
        ),
    ]

    # Sample Stock Data
    stock_data = [
        StorageLocationStock(MATNR="FG001", WERKS="1000", LGORT="0001", LABST=50.0, EINME="EA"),
        StorageLocationStock(MATNR="FG002", WERKS="1000", LGORT="0001", LABST=100.0, EINME="EA"),
        StorageLocationStock(MATNR="FG003", WERKS="1000", LGORT="0001", LABST=150.0, EINME="EA"),
    ]

    # Sample Work Centers
    work_centers = [
        WorkCenter(
            ARBPL="ASSY01",
            WERKS="1000",
            KTEXT="Assembly Line 1",
            SHIFT_HOURS=8.0,
            SHIFTS_PER_DAY=2,
            AVAILABLE_CAPACITY_PERCENT=95.0,
            AUERU=100.0,
            KAPAR=1.0
        ),
        WorkCenter(
            ARBPL="ASSY02",
            WERKS="1000",
            KTEXT="Assembly Line 2",
            SHIFT_HOURS=8.0,
            SHIFTS_PER_DAY=2,
            AVAILABLE_CAPACITY_PERCENT=90.0,
            AUERU=100.0,
            KAPAR=1.0
        ),
        WorkCenter(
            ARBPL="TEST01",
            WERKS="1000",
            KTEXT="Testing Station",
            SHIFT_HOURS=8.0,
            SHIFTS_PER_DAY=2,
            AVAILABLE_CAPACITY_PERCENT=100.0,
            AUERU=95.0,
            KAPAR=1.0
        ),
    ]

    # Sample Routing Headers
    routing_headers = [
        RoutingHeader(PLNNR="50000001", PLNAL="1", MATNR="FG001", WERKS="1000", BMSCH=1.0),
        RoutingHeader(PLNNR="50000002", PLNAL="1", MATNR="FG002", WERKS="1000", BMSCH=1.0),
        RoutingHeader(PLNNR="50000003", PLNAL="1", MATNR="FG003", WERKS="1000", BMSCH=1.0),
    ]

    # Sample Routing Operations
    routing_operations = [
        # Routing for FG001 - Premium Widget
        RoutingOperation(
            PLNNR="50000001", PLNAL="1", PLNFL="001", VORNR="0010",
            ARBPL="ASSY01", WERKS="1000", STEUS="PP01",
            VGW01=15.0, VGW02=45.0, VGW03=45.0,  # Setup 15min, Machine 45min
            BMSCH=1.0, LTXA1="Premium Assembly"
        ),
        RoutingOperation(
            PLNNR="50000001", PLNAL="1", PLNFL="002", VORNR="0020",
            ARBPL="TEST01", WERKS="1000", STEUS="PP01",
            VGW01=5.0, VGW02=15.0, VGW03=15.0,  # Setup 5min, Test 15min
            BMSCH=1.0, LTXA1="Quality Testing"
        ),

        # Routing for FG002 - Standard Widget
        RoutingOperation(
            PLNNR="50000002", PLNAL="1", PLNFL="001", VORNR="0010",
            ARBPL="ASSY01", WERKS="1000", STEUS="PP01",
            VGW01=10.0, VGW02=30.0, VGW03=30.0,
            BMSCH=1.0, LTXA1="Standard Assembly"
        ),
        RoutingOperation(
            PLNNR="50000002", PLNAL="1", PLNFL="002", VORNR="0020",
            ARBPL="ASSY02", WERKS="1000", STEUS="PP01",
            VGW01=10.0, VGW02=30.0, VGW03=30.0,
            BMSCH=1.0, LTXA1="Alternate Assembly"
        ),

        # Routing for FG003 - Economy Widget
        RoutingOperation(
            PLNNR="50000003", PLNAL="1", PLNFL="001", VORNR="0010",
            ARBPL="ASSY02", WERKS="1000", STEUS="PP01",
            VGW01=5.0, VGW02=20.0, VGW03=20.0,
            BMSCH=1.0, LTXA1="Economy Assembly"
        ),
    ]

    return {
        'materials': materials,
        'stock_data': stock_data,
        'work_centers': work_centers,
        'routing_headers': routing_headers,
        'routing_operations': routing_operations
    }


def create_optimizer_config_from_sap(
    sap_data: Dict,
    demands: List[Dict],
    planning_horizon: int = 14,
    shifts_per_day: int = 2,
    hours_per_shift: float = 8.0
) -> Dict:
    """
    Create complete optimizer configuration from SAP data

    Args:
        sap_data: Dictionary with SAP data (materials, stock, work centers, routings)
        demands: List of demand orders
        planning_horizon: Planning horizon in days
        shifts_per_day: Number of shifts per day
        hours_per_shift: Hours per shift

    Returns:
        Configuration dictionary for optimizer
    """
    converter = SAPToOptimizerConverter()

    # Convert materials and inventory
    products = converter.convert_materials_and_inventory(
        sap_data['materials'],
        sap_data['stock_data']
    )

    # Add routing information
    products = converter.convert_routings_to_production_time(
        sap_data['routing_headers'],
        sap_data['routing_operations'],
        products
    )

    # Convert work centers
    machines = converter.convert_work_centers(sap_data['work_centers'])

    # Create configuration
    config = {
        'products': products,
        'machines': machines,
        'demands': demands,
        'planning_horizon': planning_horizon,
        'shifts_per_day': shifts_per_day,
        'hours_per_shift': hours_per_shift
    }

    return config


def export_sap_structure_template(filename: str = 'sap_data_template.json'):
    """Export a template showing SAP data structure for external systems"""
    sap_data = load_sap_sample_data()

    # Convert dataclasses to dictionaries
    template = {
        'materials': [vars(m) for m in sap_data['materials']],
        'stock_data': [vars(s) for s in sap_data['stock_data']],
        'work_centers': [vars(w) for w in sap_data['work_centers']],
        'routing_headers': [vars(r) for r in sap_data['routing_headers']],
        'routing_operations': [vars(r) for r in sap_data['routing_operations']],
        'demands': [
            {'product_id': 'FG001', 'quantity': 100, 'day': 5},
            {'product_id': 'FG002', 'quantity': 150, 'day': 7},
            {'product_id': 'FG003', 'quantity': 200, 'day': 10},
        ]
    }

    with open(filename, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"SAP data template exported to {filename}")


if __name__ == "__main__":
    # Example: Load SAP data and create optimizer config
    sap_data = load_sap_sample_data()

    # Define demands
    demands = [
        {'product_id': 'FG001', 'quantity': 100, 'day': 5},
        {'product_id': 'FG002', 'quantity': 150, 'day': 7},
        {'product_id': 'FG003', 'quantity': 200, 'day': 10},
    ]

    # Create optimizer config
    config = create_optimizer_config_from_sap(sap_data, demands)

    print("Optimizer Configuration from SAP Data:")
    print(json.dumps(config, indent=2))

    # Export template
    export_sap_structure_template()
