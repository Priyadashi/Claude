# n8n Integration Guide - Factory Schedule Optimizer with SAP S/4HANA

This guide provides step-by-step instructions for integrating the Factory Schedule Optimizer with SAP S/4HANA using n8n workflow automation.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [n8n Workflow Configuration](#n8n-workflow-configuration)
5. [SAP S/4HANA Connection](#sap-s4hana-connection)
6. [Testing the Integration](#testing-the-integration)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│  SAP S/4HANA    │         │     n8n      │         │   Optimizer     │
│                 │         │   Workflow   │         │   API Server    │
├─────────────────┤         ├──────────────┤         ├─────────────────┤
│                 │         │              │         │                 │
│  PP Module      │────────▶│  Extract     │         │  Optimization   │
│  - BOM          │  OData  │  Transform   │────────▶│  Engine         │
│  - Routing      │         │  Load        │  REST   │  (PuLP/CBC)     │
│                 │         │              │         │                 │
│  MM Module      │────────▶│  Schedule    │◀────────│  Results        │
│  - Materials    │         │  Monitor     │         │  & Schedule     │
│  - Inventory    │         │  Notify      │         │                 │
│                 │         │              │         │                 │
└─────────────────┘         └──────────────┘         └─────────────────┘
         │                         │                         │
         │                         ▼                         │
         │                  ┌──────────────┐                │
         │                  │  PostgreSQL  │                │
         └─────────────────▶│  (n8n DB)    │◀───────────────┘
                            └──────────────┘
```

## Prerequisites

### Software Requirements

- **Python 3.8+** with pip
- **Node.js 16+** and npm
- **n8n** (latest version)
- **PostgreSQL** (optional but recommended for production)
- **SAP S/4HANA** with OData services enabled

### SAP Requirements

- SAP S/4HANA Cloud or On-Premise (1709 FPS02 or higher)
- OAuth 2.0 configured for API access
- OData services enabled for:
  - `API_MATERIAL_SRV` (Material Master - MM)
  - `API_MATERIAL_STOCK_SRV` (Inventory - MM)
  - `API_WORKCENTER_SRV` (Work Centers - PP)
  - `API_BOM_SRV` (Bill of Materials - PP)
  - `API_ROUTING_SRV` (Routing - PP)

### Network Requirements

- Connectivity between n8n and SAP S/4HANA
- Connectivity between n8n and Optimizer API
- Ports:
  - 8000: Optimizer API
  - 5678: n8n (default)
  - PostgreSQL: 5432 (if used)

---

## Installation & Setup

### Step 1: Install Optimizer Dependencies

```bash
cd /home/user/Claude

# Install Python dependencies
pip install -r requirements.txt

# Install additional FastAPI dependencies
pip install fastapi uvicorn python-multipart
```

### Step 2: Install n8n

#### Option A: Using npm (Recommended for Development)

```bash
npm install -g n8n
```

#### Option B: Using Docker (Recommended for Production)

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

#### Option C: Using Docker Compose with PostgreSQL

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    restart: always
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -h localhost -U n8n']
      interval: 5s
      timeout: 5s
      retries: 10

  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - '5678:5678'
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=your_secure_password
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_n8n_password
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      postgres:
        condition: service_healthy

  optimizer:
    build: .
    restart: always
    ports:
      - '8000:8000'
    command: uvicorn api_server:app --host 0.0.0.0 --port 8000
    environment:
      - PYTHONUNBUFFERED=1

volumes:
  postgres_data:
  n8n_data:
```

Start services:

```bash
docker-compose up -d
```

### Step 3: Start the Optimizer API

```bash
# Start the FastAPI server
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

Verify API is running:
```bash
curl http://localhost:8000/api/health
```

### Step 4: Access n8n

Open your browser and navigate to:
- Local: http://localhost:5678
- Docker: http://your-server-ip:5678

Create an account if first time.

---

## n8n Workflow Configuration

### Step 1: Import the Workflow

1. Open n8n web interface (http://localhost:5678)
2. Click **"Workflows"** in the left menu
3. Click **"Import from File"**
4. Select `n8n_workflows/sap_to_optimizer_workflow.json`
5. Click **"Import"**

### Step 2: Configure SAP S/4HANA Credentials

#### Create OAuth2 Credentials for SAP

1. In n8n, click **"Credentials"** → **"Add Credential"**
2. Select **"OAuth2 API"**
3. Configure:

   ```
   Name: SAP S/4HANA OAuth2
   Grant Type: Authorization Code
   Authorization URL: https://your-sap-system.com/oauth/authorize
   Access Token URL: https://your-sap-system.com/oauth/token
   Client ID: <your-client-id>
   Client Secret: <your-client-secret>
   Scope: API_MATERIAL_SRV API_MATERIAL_STOCK_SRV API_WORKCENTER_SRV API_BOM_SRV API_ROUTING_SRV
   Auth URI Query Parameters:
   Authentication: Header
   ```

4. Click **"Connect my account"**
5. Authorize in SAP

#### Alternative: Basic Authentication

If OAuth2 is not configured, you can use Basic Auth:

1. Select **"Basic Auth"**
2. Configure:
   ```
   Name: SAP S/4HANA Basic
   User: your-sap-username
   Password: your-sap-password
   ```

### Step 3: Update SAP OData URLs

In each HTTP Request node, update the URLs to match your SAP system:

1. **Get SAP Material Stock (MM)** node:
   ```
   URL: https://<your-sap-system>.com/sap/opu/odata/sap/API_MATERIAL_STOCK_SRV/MaterialStock
   ```

2. **Get SAP Materials (MM)** node:
   ```
   URL: https://<your-sap-system>.com/sap/opu/odata/sap/API_MATERIAL_SRV/A_Product
   ```

3. **Get Work Centers (PP)** node:
   ```
   URL: https://<your-sap-system>.com/sap/opu/odata/sap/API_WORKCENTER_SRV/WorkCenter
   ```

4. **Get BOM Data (PP)** node:
   ```
   URL: https://<your-sap-system>.com/sap/opu/odata/sap/API_BOM_SRV/BillOfMaterial
   ```

5. **Get Routing Data (PP)** node:
   ```
   URL: https://<your-sap-system>.com/sap/opu/odata/sap/API_ROUTING_SRV/Routing
   ```

### Step 4: Configure Optimizer API URL

Update the **Call Optimizer API** node:

```
URL: http://localhost:8000/api/webhook/optimize
```

If running in Docker or remote server, replace `localhost` with the appropriate hostname/IP.

### Step 5: Configure Email Notifications

1. Click **"Credentials"** → **"Add Credential"**
2. Select **"SMTP"**
3. Configure your email server:
   ```
   Name: SMTP Account
   Host: smtp.gmail.com  (or your SMTP server)
   Port: 587
   User: your-email@company.com
   Password: your-app-password
   SSL/TLS: true
   ```

4. Update **Send Email Notification** node with recipient email

### Step 6: Configure Schedule Trigger

The workflow is set to run every 6 hours. To change:

1. Click on **Schedule Trigger** node
2. Modify interval (e.g., daily at 6 AM):
   ```
   Mode: Every Day
   Hour: 6
   Minute: 0
   ```

---

## SAP S/4HANA Connection

### Setting Up OAuth 2.0 in SAP

#### For SAP S/4HANA Cloud:

1. Log in to SAP BTP Cockpit
2. Navigate to **Security** → **OAuth**
3. Click **"Create"** for new OAuth Client
4. Configure:
   - Application Name: "Production Optimizer"
   - Grant Types: Authorization Code
   - Redirect URI: `http://localhost:5678/rest/oauth2-credential/callback`
   - Scopes: Select all required OData services
5. Save and note down **Client ID** and **Client Secret**

#### For SAP S/4HANA On-Premise:

1. Execute transaction **SICF**
2. Navigate to `/default_host/sap/bc/sec/oauth2`
3. Right-click → **Activate Service**
4. Execute transaction **SOAUTH2**
5. Create new OAuth 2.0 Client
6. Configure scopes and redirect URI

### Testing SAP Connection

Test each OData service independently:

```bash
# Test Material Master API
curl -u username:password \
  "https://your-sap-system.com/sap/opu/odata/sap/API_MATERIAL_SRV/A_Product?\$top=5"

# Test Stock API
curl -u username:password \
  "https://your-sap-system.com/sap/opu/odata/sap/API_MATERIAL_STOCK_SRV/MaterialStock?\$top=5"
```

---

## Testing the Integration

### Step 1: Test with Sample Data

Before connecting to SAP, test with sample data:

1. In n8n, disable all SAP HTTP Request nodes
2. Modify **Transform SAP Data** node to use static data:

```javascript
return {
  json: {
    scenario: 'sample',
    time_limit: 300
  }
};
```

3. Click **"Execute Workflow"** button
4. Verify results in **Get Results** node

### Step 2: Test SAP Data Extraction

1. Re-enable one SAP HTTP Request node (e.g., Get SAP Materials)
2. Execute that node individually
3. Verify data is returned correctly
4. Check data format matches expected structure

### Step 3: Full End-to-End Test

1. Ensure all services are running:
   - SAP S/4HANA is accessible
   - Optimizer API is running
   - n8n is running

2. Execute the complete workflow:
   - Click **"Execute Workflow"**
   - Monitor each node's execution
   - Check for errors in **Executions** tab

3. Verify results:
   - Check if optimization job was created
   - Wait for completion
   - Verify email notification was sent
   - Check optimizer web UI for results

---

## Production Deployment

### Security Best Practices

1. **Use HTTPS for all connections**
   - Set up SSL/TLS for n8n
   - Use HTTPS for Optimizer API
   - Ensure SAP uses HTTPS

2. **Secure Credentials**
   - Use environment variables for secrets
   - Enable n8n credential encryption
   - Rotate passwords regularly

3. **Network Security**
   - Use VPN or private network between services
   - Implement firewall rules
   - Limit IP access to APIs

### High Availability Setup

1. **Run Optimizer API with multiple workers**:
   ```bash
   gunicorn api_server:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

2. **Use Load Balancer** (nginx):
   ```nginx
   upstream optimizer {
       server optimizer1:8000;
       server optimizer2:8000;
   }

   server {
       listen 80;
       location / {
           proxy_pass http://optimizer;
       }
   }
   ```

3. **Set up n8n in Queue Mode** for scaling:
   ```bash
   docker-compose -f docker-compose-queue.yml up -d
   ```

### Monitoring

1. **Set up health checks**:
   - Monitor `/api/health` endpoint
   - Set up alerts for failures

2. **Log aggregation**:
   - Use ELK stack or similar
   - Monitor n8n execution logs
   - Track optimization performance

3. **Metrics to monitor**:
   - Optimization success rate
   - Average optimization time
   - SAP API response times
   - Queue length

---

## Troubleshooting

### Common Issues

#### 1. SAP Connection Failed

**Symptoms**: HTTP 401, 403, or connection timeout

**Solutions**:
- Verify OAuth credentials are correct
- Check SAP OData services are activated (SICF)
- Ensure network connectivity
- Verify user has proper authorizations in SAP

**Test**:
```bash
curl -v -u username:password \
  "https://your-sap-system.com/sap/opu/odata/sap/API_MATERIAL_SRV/\$metadata"
```

#### 2. Optimizer API Not Responding

**Symptoms**: Connection refused, timeout

**Solutions**:
- Verify API is running: `curl http://localhost:8000/api/health`
- Check for port conflicts
- Review API logs for errors
- Ensure dependencies are installed

**Restart API**:
```bash
pkill -f api_server
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Optimization Fails

**Symptoms**: Job status shows "failed"

**Solutions**:
- Check job error message via API: `GET /api/jobs/{job_id}`
- Verify data format is correct
- Check for infeasible constraints (demand > capacity)
- Review optimizer logs

**Debug**:
```bash
# Get job details
curl http://localhost:8000/api/jobs/<job_id>

# Check API logs
tail -f /var/log/optimizer/api.log
```

#### 4. n8n Workflow Errors

**Symptoms**: Workflow execution fails

**Solutions**:
- Check execution log in n8n UI
- Verify all nodes are properly configured
- Test each node individually
- Check credential expiration

#### 5. Data Transformation Issues

**Symptoms**: Invalid data format sent to optimizer

**Solutions**:
- Review Transform SAP Data node output
- Validate against expected schema
- Add error handling in transformation code
- Log intermediate results

**Debug transformation**:
```javascript
// In Transform SAP Data node, add logging:
console.log('Materials:', materials);
console.log('Transformed:', transformedData);
return { json: transformedData };
```

### Getting Help

- **API Documentation**: http://localhost:8000/api/docs
- **n8n Documentation**: https://docs.n8n.io
- **SAP API Business Hub**: https://api.sap.com
- **Check logs**:
  ```bash
  # n8n logs
  docker logs n8n

  # Optimizer logs
  tail -f optimizer.log

  # System logs
  journalctl -u optimizer
  ```

---

## Advanced Configurations

### Custom Demand Extraction

To extract demands from SAP Sales Orders:

1. Add new HTTP Request node:
   ```
   URL: https://your-sap-system.com/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder
   Filter: $filter=SalesOrderDate ge datetime'2026-01-01T00:00:00'
   ```

2. Transform to demands format:
   ```javascript
   const salesOrders = $json.d.results;
   const demands = salesOrders.map(so => ({
     product_id: so.Material,
     quantity: parseFloat(so.RequestedQuantity),
     day: Math.ceil((new Date(so.RequestedDeliveryDate) - new Date()) / (1000 * 60 * 60 * 24))
   }));
   ```

### Multi-Plant Support

To optimize multiple plants:

1. Modify filter to include multiple plants:
   ```
   $filter=Plant eq '1000' or Plant eq '2000'
   ```

2. Run separate optimizations per plant or combine

### Webhook Triggers

For on-demand optimization triggered by SAP events:

1. Create webhook workflow in n8n
2. Configure SAP Event Mesh or workflow to call webhook
3. Process event and trigger optimization

---

## Appendix

### Sample n8n Environment Variables

```bash
# .env file for n8n
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=secure_password
N8N_ENCRYPTION_KEY=your_encryption_key_here
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=postgres_password
WEBHOOK_URL=https://your-n8n-instance.com
```

### Optimizer API Environment Variables

```bash
# .env file for Optimizer API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=*
MAX_WORKERS=4
```

### Useful SAP Transactions

- **SE80**: Object Navigator (development)
- **SICF**: ICF Service Maintenance
- **SOAUTH2**: OAuth 2.0 Administration
- **SM59**: RFC Destinations
- **SU01**: User Maintenance
- **PFCG**: Role Maintenance

---

## Next Steps

1. ✅ Set up development environment
2. ✅ Test with sample data
3. ✅ Configure SAP connection
4. ✅ Test with real SAP data
5. ⬜ Deploy to production
6. ⬜ Set up monitoring
7. ⬜ Train users
8. ⬜ Document custom workflows

For questions or support, refer to the project documentation or contact the development team.
