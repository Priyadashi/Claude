"""
FastAPI REST API Server for Factory Schedule Optimizer

Provides endpoints for:
- Running optimization
- Managing configurations
- Viewing schedules
- SAP data integration
- Health checks

Usage:
    uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import json
import uuid
import os

from factory_schedule_optimizer import FactoryScheduleOptimizer
from sample_data import get_sample_config, get_tight_capacity_config, get_multi_shift_config
from sap_integration import (
    create_optimizer_config_from_sap,
    load_sap_sample_data,
    MaterialMaster,
    StorageLocationStock,
    WorkCenter,
    RoutingHeader,
    RoutingOperation
)

# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="Factory Schedule Optimizer API",
    description="Production scheduling optimization API with SAP S/4HANA integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models for API
# ============================================================================

class Product(BaseModel):
    id: str
    name: str
    selling_price: float
    production_cost: float
    production_time_hrs: float
    initial_inventory: float = 0
    min_inventory: float = 0
    max_inventory: float = 999999
    compatible_machines: List[str] = []


class Machine(BaseModel):
    id: str
    name: str
    availability: float = 1.0


class Demand(BaseModel):
    product_id: str
    quantity: float
    day: int


class OptimizationConfig(BaseModel):
    products: List[Product]
    machines: List[Machine]
    demands: List[Demand]
    planning_horizon: int = 14
    shifts_per_day: int = 2
    hours_per_shift: float = 8.0


class SAPDataInput(BaseModel):
    """SAP S/4HANA data input model"""
    materials: List[Dict[str, Any]]
    stock_data: List[Dict[str, Any]]
    work_centers: List[Dict[str, Any]]
    routing_headers: List[Dict[str, Any]]
    routing_operations: List[Dict[str, Any]]
    demands: List[Demand]
    planning_horizon: int = 14
    shifts_per_day: int = 2
    hours_per_shift: float = 8.0


class OptimizationRequest(BaseModel):
    config: Optional[OptimizationConfig] = None
    sap_data: Optional[SAPDataInput] = None
    scenario: Optional[str] = None  # 'sample', 'tight', 'multi-shift'
    time_limit: int = Field(default=300, ge=10, le=600)
    start_date: Optional[str] = None


class OptimizationResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


# ============================================================================
# In-Memory Job Storage (Use Redis/DB in production)
# ============================================================================

jobs_storage = {}


def create_job(config: Dict) -> str:
    """Create a new optimization job"""
    job_id = str(uuid.uuid4())
    jobs_storage[job_id] = {
        'job_id': job_id,
        'status': 'pending',
        'progress': 0.0,
        'config': config,
        'result': None,
        'error': None,
        'created_at': datetime.now().isoformat(),
        'completed_at': None
    }
    return job_id


def update_job(job_id: str, **kwargs):
    """Update job status"""
    if job_id in jobs_storage:
        jobs_storage[job_id].update(kwargs)


def run_optimization_job(job_id: str, config: Dict, time_limit: int, start_date: Optional[str]):
    """Background task to run optimization"""
    try:
        update_job(job_id, status='running', progress=0.1)

        # Create optimizer
        optimizer = FactoryScheduleOptimizer(config)

        update_job(job_id, progress=0.3)

        # Build model
        optimizer.build_model()

        update_job(job_id, progress=0.5)

        # Solve
        status = optimizer.solve(time_limit=time_limit)

        update_job(job_id, progress=0.9)

        if status == "Optimal":
            # Get results
            solution = optimizer.solution
            daily_schedule = optimizer.get_daily_schedule(start_date)

            result = {
                'status': status,
                'objective_value': solution['objective_value'],
                'production_schedule': solution['production_schedule'],
                'inventory_levels': solution['inventory_levels'],
                'daily_schedule': daily_schedule,
                'summary': {
                    'planning_horizon': optimizer.planning_horizon,
                    'shifts_per_day': optimizer.shifts_per_day,
                    'hours_per_shift': optimizer.hours_per_shift,
                    'total_products': len(optimizer.products),
                    'total_machines': len(optimizer.machines)
                }
            }

            update_job(
                job_id,
                status='completed',
                progress=1.0,
                result=result,
                completed_at=datetime.now().isoformat()
            )
        else:
            update_job(
                job_id,
                status='failed',
                progress=1.0,
                error=f"Optimization failed with status: {status}",
                completed_at=datetime.now().isoformat()
            )

    except Exception as e:
        update_job(
            job_id,
            status='failed',
            progress=1.0,
            error=str(e),
            completed_at=datetime.now().isoformat()
        )


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Factory Schedule Optimizer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len([j for j in jobs_storage.values() if j['status'] == 'running'])
    }


@app.post("/api/optimize", response_model=OptimizationResponse)
async def optimize(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """
    Run optimization with provided configuration or scenario

    - Accepts direct config, SAP data, or scenario name
    - Returns job_id for tracking progress
    """
    try:
        # Determine configuration source
        if request.sap_data:
            # Convert SAP data to config
            from sap_integration import (
                SAPToOptimizerConverter,
                MaterialMaster,
                StorageLocationStock,
                WorkCenter,
                RoutingHeader,
                RoutingOperation
            )

            # Convert dict data to dataclasses
            materials = [MaterialMaster(**m) for m in request.sap_data.materials]
            stock_data = [StorageLocationStock(**s) for s in request.sap_data.stock_data]
            work_centers = [WorkCenter(**w) for w in request.sap_data.work_centers]
            routing_headers = [RoutingHeader(**r) for r in request.sap_data.routing_headers]
            routing_operations = [RoutingOperation(**r) for r in request.sap_data.routing_operations]

            sap_data_obj = {
                'materials': materials,
                'stock_data': stock_data,
                'work_centers': work_centers,
                'routing_headers': routing_headers,
                'routing_operations': routing_operations
            }

            demands = [d.dict() for d in request.sap_data.demands]

            config = create_optimizer_config_from_sap(
                sap_data_obj,
                demands,
                request.sap_data.planning_horizon,
                request.sap_data.shifts_per_day,
                request.sap_data.hours_per_shift
            )

        elif request.config:
            # Use provided config
            config = request.config.dict()

        elif request.scenario:
            # Use predefined scenario
            scenario_map = {
                'sample': get_sample_config,
                'tight': get_tight_capacity_config,
                'multi-shift': get_multi_shift_config
            }

            if request.scenario not in scenario_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid scenario. Choose from: {list(scenario_map.keys())}"
                )

            config = scenario_map[request.scenario]()

        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide config, sap_data, or scenario"
            )

        # Create job
        job_id = create_job(config)

        # Run optimization in background
        background_tasks.add_task(
            run_optimization_job,
            job_id,
            config,
            request.time_limit,
            request.start_date
        )

        return OptimizationResponse(
            job_id=job_id,
            status="submitted",
            message="Optimization job submitted successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get status of an optimization job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs_storage[job_id]


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs"""
    return {
        "jobs": list(jobs_storage.values()),
        "total": len(jobs_storage)
    }


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    del jobs_storage[job_id]
    return {"message": "Job deleted successfully"}


@app.get("/api/scenarios")
async def list_scenarios():
    """List available predefined scenarios"""
    return {
        "scenarios": [
            {
                "id": "sample",
                "name": "Standard Configuration",
                "description": "4 products, 3 machines, 14-day horizon"
            },
            {
                "id": "tight",
                "name": "Tight Capacity",
                "description": "Challenging scenario with high demand"
            },
            {
                "id": "multi-shift",
                "name": "Three-Shift Operation",
                "description": "24-hour continuous production"
            }
        ]
    }


@app.get("/api/sap/sample-data")
async def get_sap_sample_data():
    """Get sample SAP data structure"""
    sap_data = load_sap_sample_data()

    # Convert dataclasses to dicts
    return {
        'materials': [vars(m) for m in sap_data['materials']],
        'stock_data': [vars(s) for s in sap_data['stock_data']],
        'work_centers': [vars(w) for w in sap_data['work_centers']],
        'routing_headers': [vars(r) for r in sap_data['routing_headers']],
        'routing_operations': [vars(r) for r in sap_data['routing_operations']]
    }


@app.post("/api/sap/validate")
async def validate_sap_data(sap_data: SAPDataInput):
    """Validate SAP data structure"""
    try:
        # Attempt to convert
        from sap_integration import (
            MaterialMaster,
            StorageLocationStock,
            WorkCenter,
            RoutingHeader,
            RoutingOperation
        )

        materials = [MaterialMaster(**m) for m in sap_data.materials]
        stock_data = [StorageLocationStock(**s) for s in sap_data.stock_data]
        work_centers = [WorkCenter(**w) for w in sap_data.work_centers]
        routing_headers = [RoutingHeader(**r) for r in sap_data.routing_headers]
        routing_operations = [RoutingOperation(**r) for r in sap_data.routing_operations]

        return {
            "valid": True,
            "message": "SAP data structure is valid",
            "counts": {
                "materials": len(materials),
                "stock_records": len(stock_data),
                "work_centers": len(work_centers),
                "routing_headers": len(routing_headers),
                "routing_operations": len(routing_operations)
            }
        }

    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation failed: {str(e)}"
        }


@app.get("/api/results/{job_id}/excel")
async def download_excel(job_id: str):
    """Download optimization results as Excel file"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_storage[job_id]

    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed")

    # Create optimizer with results
    config = job['config']
    optimizer = FactoryScheduleOptimizer(config)

    # Set the solution directly
    optimizer.solution = job['result']

    # Export to Excel
    filename = f"schedule_{job_id}.xlsx"
    optimizer.export_to_excel(filename)

    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"production_schedule_{job_id}.xlsx"
    )


@app.get("/api/results/{job_id}/json")
async def download_json(job_id: str):
    """Download optimization results as JSON file"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_storage[job_id]

    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed")

    return JSONResponse(content=job['result'])


# ============================================================================
# Webhook Support for n8n Integration
# ============================================================================

@app.post("/api/webhook/optimize")
async def webhook_optimize(data: Dict, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for n8n integration

    Accepts flexible input format and triggers optimization
    """
    try:
        # Extract config or scenario from webhook data
        if 'scenario' in data:
            request = OptimizationRequest(scenario=data['scenario'])
        elif 'sap_data' in data:
            request = OptimizationRequest(sap_data=SAPDataInput(**data['sap_data']))
        elif 'config' in data:
            request = OptimizationRequest(config=OptimizationConfig(**data['config']))
        else:
            # Default to sample scenario
            request = OptimizationRequest(scenario='sample')

        # Set optional parameters
        if 'time_limit' in data:
            request.time_limit = data['time_limit']
        if 'start_date' in data:
            request.start_date = data['start_date']

        # Run optimization
        response = await optimize(request, background_tasks)

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Static Files for Frontend
# ============================================================================

@app.get("/ui")
async def serve_ui():
    """Serve the web UI"""
    return FileResponse("static/index.html")


# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("="*80)
    print("Factory Schedule Optimizer API Server")
    print("="*80)
    print(f"Started at: {datetime.now().isoformat()}")
    print("API Documentation: http://localhost:8000/api/docs")
    print("Web UI: http://localhost:8000/ui")
    print("="*80)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
