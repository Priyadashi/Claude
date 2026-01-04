# Factory Schedule Optimizer - SAP S/4HANA Edition

Production scheduling optimization system with full SAP S/4HANA integration, modern web UI, and n8n workflow automation.

## 🚀 Key Features

- **SAP S/4HANA Integration**: Direct integration with PP (Production Planning) and MM (Materials Management) modules
- **Linear Programming Optimization**: Maximizes gross margin while respecting all constraints
- **Modern Web UI**: Beautiful, responsive dashboard for configuration and results
- **REST API**: Full-featured FastAPI backend for seamless integration
- **n8n Workflow Automation**: Automated data extraction, optimization, and notification
- **Real-time Monitoring**: Track optimization progress and results
- **Multiple Export Formats**: Excel, JSON, and PDF reports

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [SAP Integration](#sap-integration)
- [Web UI](#web-ui)
- [API Documentation](#api-documentation)
- [n8n Workflows](#n8n-workflows)
- [Deployment](#deployment)
- [Examples](#examples)

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     SAP S/4HANA System                        │
├───────────────────────────────────────────────────────────────┤
│  PP Module (Production)          MM Module (Materials)        │
│  ├─ BOM (STKO/STPO)               ├─ Material Master (MARA)  │
│  ├─ Routing (PLKO/PLPO)           ├─ Inventory (MARD)        │
│  └─ Work Centers (CRHD)           └─ Stock (MBEW)            │
└─────────────────┬─────────────────────────────────────────────┘
                  │ OData APIs
                  ▼
┌───────────────────────────────────────────────────────────────┐
│                      n8n Workflow Engine                      │
├───────────────────────────────────────────────────────────────┤
│  ├─ Scheduled Data Extraction                                │
│  ├─ Data Transformation                                       │
│  ├─ Optimization Triggering                                   │
│  └─ Results Distribution                                      │
└─────────────────┬─────────────────────────────────────────────┘
                  │ REST API
                  ▼
┌───────────────────────────────────────────────────────────────┐
│              Factory Schedule Optimizer                       │
├───────────────────────────────────────────────────────────────┤
│  FastAPI Server          Optimization Engine                  │
│  ├─ /api/optimize        ├─ Linear Programming (PuLP)        │
│  ├─ /api/jobs            ├─ Constraint Solver (CBC)          │
│  ├─ /api/results         └─ Gross Margin Maximization        │
│  └─ /api/sap                                                  │
└─────────────────┬─────────────────────────────────────────────┘
                  │
                  ▼
┌───────────────────────────────────────────────────────────────┐
│                      Web Dashboard                            │
├───────────────────────────────────────────────────────────────┤
│  Modern React-like UI │ Real-time Updates │ Export Features  │
└───────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Priyadashi/Claude.git
cd Claude

# Install Python dependencies
pip install -r requirements.txt

# Install n8n (optional)
npm install -g n8n
```

### 2. Start the API Server

```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the Web UI

Open your browser and navigate to:
- **Web Dashboard**: http://localhost:8000/ui
- **API Documentation**: http://localhost:8000/api/docs

### 4. Run Your First Optimization

#### Option A: Using Web UI

1. Open http://localhost:8000/ui
2. Click "Standard" scenario button
3. Click "Run Optimization"
4. View results in real-time

#### Option B: Using API

```bash
curl -X POST "http://localhost:8000/api/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "sample",
    "time_limit": 300
  }'
```

#### Option C: Using Python

```python
from factory_schedule_optimizer import FactoryScheduleOptimizer
from sample_data import get_sample_config

config = get_sample_config()
optimizer = FactoryScheduleOptimizer(config)
optimizer.build_model()
status = optimizer.solve()

if status == "Optimal":
    optimizer.print_solution_summary()
    optimizer.export_to_excel('schedule.xlsx')
```

---

## 🔗 SAP Integration

### Data Structure Mapping

The system maps SAP S/4HANA data structures to optimizer format:

| SAP Module | SAP Table | Optimizer Entity | Description |
|------------|-----------|------------------|-------------|
| MM | MARA/MARC | Products | Material master with costs |
| MM | MARD | Inventory | Stock levels by location |
| PP | STKO/STPO | BOM | Bill of materials structure |
| PP | PLKO/PLPO | Routing | Production operations & times |
| PP | CRHD/CRCA | Machines | Work centers & capacity |

### Using SAP Data

#### 1. Load Sample SAP Data

```python
from sap_integration import load_sap_sample_data, create_optimizer_config_from_sap

# Load sample SAP data
sap_data = load_sap_sample_data()

# Define demands
demands = [
    {'product_id': 'FG001', 'quantity': 100, 'day': 5},
    {'product_id': 'FG002', 'quantity': 150, 'day': 7}
]

# Create optimizer config
config = create_optimizer_config_from_sap(sap_data, demands)

# Run optimization
from factory_schedule_optimizer import FactoryScheduleOptimizer
optimizer = FactoryScheduleOptimizer(config)
optimizer.build_model()
optimizer.solve()
optimizer.print_solution_summary()
```

#### 2. Via API

```bash
curl -X POST "http://localhost:8000/api/optimize" \
  -H "Content-Type: application/json" \
  -d @sap_data.json
```

#### 3. Via Web UI

1. Click "SAP S/4HANA Integration"
2. Click "Load SAP Sample Data" or "Upload SAP JSON"
3. Configure parameters
4. Run optimization

### SAP OData Integration

The system expects SAP data via OData APIs:

- **Material Master**: `API_MATERIAL_SRV`
- **Inventory**: `API_MATERIAL_STOCK_SRV`
- **Work Centers**: `API_WORKCENTER_SRV`
- **BOM**: `API_BOM_SRV`
- **Routing**: `API_ROUTING_SRV`

See [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md) for detailed setup.

---

## 🎨 Web UI

### Features

- **Modern Design**: Dark theme with gradient accents
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live optimization progress tracking
- **Interactive Visualizations**: Schedule timeline, statistics
- **Multiple Views**:
  - Optimize: Configure and run optimizations
  - Results: View metrics and download reports
  - SAP Data: Manage SAP master data
  - Schedule: Day-wise production plan

### Screenshots

#### Dashboard
```
┌─────────────────────────────────────────────────────┐
│  🏭 Factory Schedule Optimizer        ● Connected  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Quick Start                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐│
│  │ 📊 Standard  │  │ ⚡ High      │  │ 🌙 24/7  ││
│  │ 4 products   │  │ Demand      │  │ Operation││
│  └──────────────┘  └──────────────┘  └──────────┘│
│                                                     │
│  SAP S/4HANA Integration                           │
│  ┌─────────────────────────────────────────────┐  │
│  │ Load SAP Sample Data                        │  │
│  │ Upload SAP JSON                             │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 📡 API Documentation

### Endpoints

#### Optimization

```http
POST /api/optimize
Content-Type: application/json

{
  "scenario": "sample",  // or "tight", "multi-shift"
  "time_limit": 300,
  "start_date": "2026-01-04"
}

Response: {
  "job_id": "uuid",
  "status": "submitted",
  "message": "Optimization job submitted successfully"
}
```

#### Job Status

```http
GET /api/jobs/{job_id}

Response: {
  "job_id": "uuid",
  "status": "completed",  // pending, running, completed, failed
  "progress": 1.0,
  "result": {
    "objective_value": 84371.0,
    "production_schedule": [...],
    "daily_schedule": [...]
  }
}
```

#### Download Results

```http
GET /api/results/{job_id}/excel
GET /api/results/{job_id}/json
```

#### SAP Integration

```http
GET /api/sap/sample-data
POST /api/sap/validate
POST /api/webhook/optimize
```

### Full API Documentation

Visit http://localhost:8000/api/docs for interactive Swagger documentation.

---

## 🔄 n8n Workflows

### Automated SAP Integration

The included n8n workflow automates:

1. **Data Extraction** from SAP S/4HANA (every 6 hours)
2. **Data Transformation** to optimizer format
3. **Optimization Execution** via API
4. **Results Distribution** via email

### Setup Instructions

1. **Install n8n**:
   ```bash
   npm install -g n8n
   # or
   docker run -d -p 5678:5678 --name n8n n8nio/n8n
   ```

2. **Import Workflow**:
   - Open n8n (http://localhost:5678)
   - Import `n8n_workflows/sap_to_optimizer_workflow.json`

3. **Configure SAP Credentials**:
   - Add OAuth2 or Basic Auth credentials
   - Update SAP OData URLs

4. **Activate Workflow**:
   - Click "Active" toggle
   - Workflow will run on schedule

**Detailed guide**: See [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md)

### Workflow Architecture

```
Trigger (Every 6h)
     │
     ├──► Get Materials (MM)
     ├──► Get Inventory (MM)
     ├──► Get Work Centers (PP)
     ├──► Get BOM (PP)
     ├──► Get Routing (PP)
     │
     └──► Transform Data
           │
           └──► Call Optimizer API
                 │
                 └──► Poll Status
                       │
                       └──► Send Results Email
```

---

## 🚀 Deployment

### Development

```bash
# Start API server
uvicorn api_server:app --reload

# Start n8n
n8n start

# Access services
# - Web UI: http://localhost:8000/ui
# - API Docs: http://localhost:8000/api/docs
# - n8n: http://localhost:5678
```

### Production with Docker

```bash
# Build and start all services
docker-compose up -d

# Services:
# - optimizer: Port 8000
# - n8n: Port 5678
# - postgres: Port 5432
```

### Docker Compose

See `docker-compose.yml` in the repository for full configuration.

### Environment Variables

```bash
# Optimizer API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com

# n8n
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=secure_password
```

---

## 📊 Examples

### Example 1: Standard Scenario

```python
from factory_schedule_optimizer import FactoryScheduleOptimizer
from sample_data import get_sample_config

config = get_sample_config()
optimizer = FactoryScheduleOptimizer(config)
optimizer.build_model()
optimizer.solve()
optimizer.print_solution_summary()
```

**Result**: $84,371 gross margin, 260 units produced across 4 products

### Example 2: SAP Data

```python
from sap_integration import load_sap_sample_data, create_optimizer_config_from_sap

sap_data = load_sap_sample_data()
demands = [
    {'product_id': 'FG001', 'quantity': 100, 'day': 5}
]

config = create_optimizer_config_from_sap(sap_data, demands)
optimizer = FactoryScheduleOptimizer(config)
optimizer.solve()
```

### Example 3: Custom Configuration

```python
config = {
    'products': [
        {
            'id': 'P001',
            'name': 'Product A',
            'selling_price': 200.0,
            'production_cost': 100.0,
            'production_time_hrs': 1.0,
            'initial_inventory': 50,
            'compatible_machines': ['M001']
        }
    ],
    'machines': [
        {
            'id': 'M001',
            'name': 'Line 1',
            'availability': 0.95
        }
    ],
    'demands': [
        {'product_id': 'P001', 'quantity': 100, 'day': 5}
    ],
    'planning_horizon': 10,
    'shifts_per_day': 2,
    'hours_per_shift': 8
}

optimizer = FactoryScheduleOptimizer(config)
optimizer.solve()
```

---

## 📦 Project Structure

```
Claude/
├── api_server.py                 # FastAPI REST API server
├── factory_schedule_optimizer.py # Core optimization engine
├── sap_integration.py            # SAP S/4HANA data models & conversion
├── sample_data.py                # Sample configurations
├── examples.py                   # Usage examples
├── run_optimizer.py              # CLI script
├── requirements.txt              # Python dependencies
│
├── static/                       # Web UI
│   ├── index.html               # Main dashboard
│   ├── styles.css               # Modern styling
│   └── app.js                   # Frontend JavaScript
│
├── n8n_workflows/               # n8n automation
│   └── sap_to_optimizer_workflow.json
│
├── OPTIMIZATION_README.md        # Core optimizer docs
├── N8N_INTEGRATION_GUIDE.md      # Integration guide
└── README_SAP_INTEGRATION.md     # This file
```

---

## 🔧 Configuration

### Optimizer Parameters

- **planning_horizon**: Number of days to optimize (1-30)
- **shifts_per_day**: Number of shifts (1-3)
- **hours_per_shift**: Hours per shift (1-12)
- **time_limit**: Maximum solver time in seconds

### Constraints

- **Inventory**: Min/max levels, initial stock
- **Machine Capacity**: Hours per shift, availability %
- **Demand**: Quantity, due date
- **Product-Machine Compatibility**: Which machines can produce which products

### Objective Function

Maximize: `Σ (selling_price - production_cost) × production_quantity`

---

## 🛠️ Troubleshooting

### Common Issues

1. **API Not Starting**
   ```bash
   # Check if port 8000 is in use
   lsof -i:8000

   # Use different port
   uvicorn api_server:app --port 8001
   ```

2. **Optimization Infeasible**
   - Check if demand exceeds capacity
   - Verify machine-product compatibility
   - Review inventory constraints

3. **SAP Connection Failed**
   - Verify OData services are activated
   - Check OAuth credentials
   - Test with curl/Postman first

4. **n8n Workflow Errors**
   - Review execution log in n8n UI
   - Test each node individually
   - Verify credentials are valid

---

## 📚 Documentation

- **[Core Optimizer](OPTIMIZATION_README.md)**: Mathematical model, usage, examples
- **[n8n Integration](N8N_INTEGRATION_GUIDE.md)**: Step-by-step setup, SAP connection, troubleshooting
- **[API Documentation](http://localhost:8000/api/docs)**: Interactive Swagger docs

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is provided as-is for production scheduling optimization.

---

## 🙏 Acknowledgments

- **PuLP**: Linear programming library
- **FastAPI**: Modern web framework
- **n8n**: Workflow automation platform
- **SAP S/4HANA**: Enterprise resource planning system

---

## 📞 Support

For questions or issues:

1. Check [OPTIMIZATION_README.md](OPTIMIZATION_README.md)
2. Review [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md)
3. Check API docs at `/api/docs`
4. Review execution logs

---

**Built with ❤️ for optimizing factory production schedules**
