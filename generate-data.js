const XLSX = require('xlsx');

// Sample data for Resources sheet
const resources = [
    { ResourceID: 'R001', ResourceName: 'Alice Johnson', PrimarySkill: 'Frontend', SecondarySkill: 'UI/UX', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40, CostRate: 150 },
    { ResourceID: 'R002', ResourceName: 'Bob Smith', PrimarySkill: 'Backend', SecondarySkill: 'DevOps', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40, CostRate: 160 },
    { ResourceID: 'R003', ResourceName: 'Carol Williams', PrimarySkill: 'Data Science', SecondarySkill: 'Python', Department: 'Analytics', Status: 'Active', HoursPerWeek: 40, CostRate: 175 },
    { ResourceID: 'R004', ResourceName: 'David Brown', PrimarySkill: 'Project Management', SecondarySkill: 'Agile', Department: 'PMO', Status: 'Active', HoursPerWeek: 40, CostRate: 140 },
    { ResourceID: 'R005', ResourceName: 'Eva Martinez', PrimarySkill: 'Backend', SecondarySkill: 'Database', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40, CostRate: 155 },
    { ResourceID: 'R006', ResourceName: 'Frank Lee', PrimarySkill: 'Frontend', SecondarySkill: 'React', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40, CostRate: 145 },
    { ResourceID: 'R007', ResourceName: 'Grace Chen', PrimarySkill: 'DevOps', SecondarySkill: 'Cloud', Department: 'Infrastructure', Status: 'Active', HoursPerWeek: 40, CostRate: 165 },
    { ResourceID: 'R008', ResourceName: 'Henry Wilson', PrimarySkill: 'QA', SecondarySkill: 'Automation', Department: 'Quality', Status: 'Active', HoursPerWeek: 40, CostRate: 130 },
    { ResourceID: 'R009', ResourceName: 'Ivy Taylor', PrimarySkill: 'UI/UX', SecondarySkill: 'Design', Department: 'Design', Status: 'Active', HoursPerWeek: 40, CostRate: 140 },
    { ResourceID: 'R010', ResourceName: 'Jack Anderson', PrimarySkill: 'Data Science', SecondarySkill: 'ML', Department: 'Analytics', Status: 'Active', HoursPerWeek: 40, CostRate: 180 },
    { ResourceID: 'R011', ResourceName: 'Karen White', PrimarySkill: 'Backend', SecondarySkill: 'API', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40, CostRate: 150 },
    { ResourceID: 'R012', ResourceName: 'Leo Garcia', PrimarySkill: 'Frontend', SecondarySkill: 'Vue', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40, CostRate: 145 },
    { ResourceID: 'R013', ResourceName: 'Maria Santos', PrimarySkill: 'Backend', SecondarySkill: 'Microservices', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40, CostRate: 160 },
    { ResourceID: 'R014', ResourceName: 'Nathan Park', PrimarySkill: 'DevOps', SecondarySkill: 'Kubernetes', Department: 'Infrastructure', Status: 'Active', HoursPerWeek: 40, CostRate: 170 },
    { ResourceID: 'R015', ResourceName: 'Olivia Kim', PrimarySkill: 'QA', SecondarySkill: 'Performance', Department: 'Quality', Status: 'Active', HoursPerWeek: 40, CostRate: 135 },
];

// Sample data for Projects sheet - with ProjectType (Active/Planned) and Probability
const projects = [
    // Active Projects (100% probability - confirmed)
    { ProjectID: 'P001', ProjectName: 'E-Commerce Platform', Client: 'RetailCorp', ProjectType: 'Active', Probability: 100, Priority: 'High', StartDate: '2025-01-15', EndDate: '2025-06-30', Budget: 150000, RequiredFTE: 4 },
    { ProjectID: 'P002', ProjectName: 'Mobile Banking App', Client: 'FinanceHub', ProjectType: 'Active', Probability: 100, Priority: 'Critical', StartDate: '2025-02-01', EndDate: '2025-08-31', Budget: 200000, RequiredFTE: 5 },
    { ProjectID: 'P003', ProjectName: 'CRM Integration', Client: 'SalesForce Plus', ProjectType: 'Active', Probability: 100, Priority: 'High', StartDate: '2025-01-01', EndDate: '2025-05-31', Budget: 120000, RequiredFTE: 3 },
    { ProjectID: 'P004', ProjectName: 'HR Portal', Client: 'Internal', ProjectType: 'Active', Probability: 100, Priority: 'Medium', StartDate: '2025-02-15', EndDate: '2025-06-30', Budget: 60000, RequiredFTE: 2 },

    // Planned Projects (with probability)
    { ProjectID: 'P005', ProjectName: 'Analytics Dashboard', Client: 'DataDriven Inc', ProjectType: 'Planned', Probability: 85, Priority: 'High', StartDate: '2025-04-01', EndDate: '2025-08-15', Budget: 80000, RequiredFTE: 3 },
    { ProjectID: 'P006', ProjectName: 'Cloud Migration', Client: 'TechStart', ProjectType: 'Planned', Probability: 70, Priority: 'Medium', StartDate: '2025-05-01', EndDate: '2025-10-31', Budget: 250000, RequiredFTE: 4 },
    { ProjectID: 'P007', ProjectName: 'AI Chatbot', Client: 'ServiceNow', ProjectType: 'Planned', Probability: 60, Priority: 'Medium', StartDate: '2025-06-01', EndDate: '2025-11-30', Budget: 180000, RequiredFTE: 4 },
    { ProjectID: 'P008', ProjectName: 'Inventory System', Client: 'WarehousePro', ProjectType: 'Planned', Probability: 90, Priority: 'High', StartDate: '2025-04-15', EndDate: '2025-07-31', Budget: 90000, RequiredFTE: 2 },
    { ProjectID: 'P009', ProjectName: 'Payment Gateway', Client: 'PaySecure', ProjectType: 'Planned', Probability: 75, Priority: 'Critical', StartDate: '2025-05-15', EndDate: '2025-09-30', Budget: 140000, RequiredFTE: 3 },
    { ProjectID: 'P010', ProjectName: 'Customer Portal', Client: 'RetailCorp', ProjectType: 'Planned', Probability: 50, Priority: 'Low', StartDate: '2025-07-01', EndDate: '2025-12-31', Budget: 100000, RequiredFTE: 3 },
    { ProjectID: 'P011', ProjectName: 'Data Warehouse', Client: 'DataDriven Inc', ProjectType: 'Planned', Probability: 40, Priority: 'Medium', StartDate: '2025-08-01', EndDate: '2026-01-31', Budget: 200000, RequiredFTE: 4 },
];

// Sample data for Allocations sheet - covering Jan 2025 to Dec 2025
// Resources can have partial chargeability across multiple projects
const months = ['Jan-2025', 'Feb-2025', 'Mar-2025', 'Apr-2025', 'May-2025', 'Jun-2025', 'Jul-2025', 'Aug-2025', 'Sep-2025', 'Oct-2025', 'Nov-2025', 'Dec-2025'];

const allocations = [
    // Alice Johnson - Frontend - split across projects
    { AllocationID: 'A001', ResourceID: 'R001', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 50, Role: 'Lead Developer' },
    { AllocationID: 'A002', ResourceID: 'R001', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 30, Role: 'Developer' },
    { AllocationID: 'A003', ResourceID: 'R001', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 60, Role: 'Lead Developer' },
    { AllocationID: 'A004', ResourceID: 'R001', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 30, Role: 'Developer' },
    { AllocationID: 'A005', ResourceID: 'R001', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 70, Role: 'Lead Developer' },
    { AllocationID: 'A006', ResourceID: 'R001', ProjectID: 'P004', Month: 'Mar-2025', AllocationPercent: 20, Role: 'Developer' },
    { AllocationID: 'A007', ResourceID: 'R001', ProjectID: 'P001', Month: 'Apr-2025', AllocationPercent: 60, Role: 'Lead Developer' },
    { AllocationID: 'A008', ResourceID: 'R001', ProjectID: 'P005', Month: 'Apr-2025', AllocationPercent: 30, Role: 'Developer' },
    { AllocationID: 'A009', ResourceID: 'R001', ProjectID: 'P001', Month: 'May-2025', AllocationPercent: 50, Role: 'Lead Developer' },
    { AllocationID: 'A010', ResourceID: 'R001', ProjectID: 'P005', Month: 'May-2025', AllocationPercent: 40, Role: 'Developer' },
    { AllocationID: 'A011', ResourceID: 'R001', ProjectID: 'P001', Month: 'Jun-2025', AllocationPercent: 40, Role: 'Lead Developer' },
    { AllocationID: 'A012', ResourceID: 'R001', ProjectID: 'P005', Month: 'Jun-2025', AllocationPercent: 50, Role: 'Developer' },

    // Bob Smith - Backend - high utilization
    { AllocationID: 'A013', ResourceID: 'R002', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 40, Role: 'Backend Developer' },
    { AllocationID: 'A014', ResourceID: 'R002', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 40, Role: 'Backend Developer' },
    { AllocationID: 'A015', ResourceID: 'R002', ProjectID: 'P003', Month: 'Jan-2025', AllocationPercent: 20, Role: 'Developer' },
    { AllocationID: 'A016', ResourceID: 'R002', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 50, Role: 'Backend Developer' },
    { AllocationID: 'A017', ResourceID: 'R002', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 40, Role: 'Backend Developer' },
    { AllocationID: 'A018', ResourceID: 'R002', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 40, Role: 'Backend Developer' },
    { AllocationID: 'A019', ResourceID: 'R002', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 50, Role: 'Backend Developer' },
    { AllocationID: 'A020', ResourceID: 'R002', ProjectID: 'P002', Month: 'Apr-2025', AllocationPercent: 60, Role: 'Backend Developer' },
    { AllocationID: 'A021', ResourceID: 'R002', ProjectID: 'P005', Month: 'Apr-2025', AllocationPercent: 30, Role: 'Developer' },
    { AllocationID: 'A022', ResourceID: 'R002', ProjectID: 'P002', Month: 'May-2025', AllocationPercent: 50, Role: 'Backend Developer' },
    { AllocationID: 'A023', ResourceID: 'R002', ProjectID: 'P006', Month: 'May-2025', AllocationPercent: 40, Role: 'Developer' },
    { AllocationID: 'A024', ResourceID: 'R002', ProjectID: 'P002', Month: 'Jun-2025', AllocationPercent: 40, Role: 'Backend Developer' },
    { AllocationID: 'A025', ResourceID: 'R002', ProjectID: 'P006', Month: 'Jun-2025', AllocationPercent: 50, Role: 'Developer' },

    // Carol Williams - Data Science - lower utilization early, ramps up
    { AllocationID: 'A026', ResourceID: 'R003', ProjectID: 'P003', Month: 'Jan-2025', AllocationPercent: 30, Role: 'Data Analyst' },
    { AllocationID: 'A027', ResourceID: 'R003', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 40, Role: 'Data Analyst' },
    { AllocationID: 'A028', ResourceID: 'R003', ProjectID: 'P003', Month: 'Mar-2025', AllocationPercent: 50, Role: 'Data Analyst' },
    { AllocationID: 'A029', ResourceID: 'R003', ProjectID: 'P005', Month: 'Apr-2025', AllocationPercent: 60, Role: 'Lead Data Scientist' },
    { AllocationID: 'A030', ResourceID: 'R003', ProjectID: 'P005', Month: 'May-2025', AllocationPercent: 70, Role: 'Lead Data Scientist' },
    { AllocationID: 'A031', ResourceID: 'R003', ProjectID: 'P005', Month: 'Jun-2025', AllocationPercent: 80, Role: 'Lead Data Scientist' },
    { AllocationID: 'A032', ResourceID: 'R003', ProjectID: 'P007', Month: 'Jun-2025', AllocationPercent: 20, Role: 'ML Engineer' },

    // David Brown - Project Management - spread across projects
    { AllocationID: 'A033', ResourceID: 'R004', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 25, Role: 'Project Manager' },
    { AllocationID: 'A034', ResourceID: 'R004', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 30, Role: 'Project Manager' },
    { AllocationID: 'A035', ResourceID: 'R004', ProjectID: 'P003', Month: 'Jan-2025', AllocationPercent: 25, Role: 'Project Manager' },
    { AllocationID: 'A036', ResourceID: 'R004', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 25, Role: 'Project Manager' },
    { AllocationID: 'A037', ResourceID: 'R004', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 30, Role: 'Project Manager' },
    { AllocationID: 'A038', ResourceID: 'R004', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 20, Role: 'Project Manager' },
    { AllocationID: 'A039', ResourceID: 'R004', ProjectID: 'P004', Month: 'Feb-2025', AllocationPercent: 15, Role: 'Project Manager' },
    { AllocationID: 'A040', ResourceID: 'R004', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 20, Role: 'Project Manager' },
    { AllocationID: 'A041', ResourceID: 'R004', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 30, Role: 'Project Manager' },
    { AllocationID: 'A042', ResourceID: 'R004', ProjectID: 'P004', Month: 'Mar-2025', AllocationPercent: 20, Role: 'Project Manager' },
    { AllocationID: 'A043', ResourceID: 'R004', ProjectID: 'P005', Month: 'Apr-2025', AllocationPercent: 30, Role: 'Project Manager' },
    { AllocationID: 'A044', ResourceID: 'R004', ProjectID: 'P002', Month: 'Apr-2025', AllocationPercent: 30, Role: 'Project Manager' },
    { AllocationID: 'A045', ResourceID: 'R004', ProjectID: 'P004', Month: 'Apr-2025', AllocationPercent: 20, Role: 'Project Manager' },

    // Eva Martinez - Backend - focused on CRM
    { AllocationID: 'A046', ResourceID: 'R005', ProjectID: 'P003', Month: 'Jan-2025', AllocationPercent: 80, Role: 'Lead Developer' },
    { AllocationID: 'A047', ResourceID: 'R005', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 90, Role: 'Lead Developer' },
    { AllocationID: 'A048', ResourceID: 'R005', ProjectID: 'P003', Month: 'Mar-2025', AllocationPercent: 80, Role: 'Lead Developer' },
    { AllocationID: 'A049', ResourceID: 'R005', ProjectID: 'P003', Month: 'Apr-2025', AllocationPercent: 70, Role: 'Lead Developer' },
    { AllocationID: 'A050', ResourceID: 'R005', ProjectID: 'P004', Month: 'Apr-2025', AllocationPercent: 20, Role: 'Developer' },
    { AllocationID: 'A051', ResourceID: 'R005', ProjectID: 'P003', Month: 'May-2025', AllocationPercent: 50, Role: 'Lead Developer' },
    { AllocationID: 'A052', ResourceID: 'R005', ProjectID: 'P009', Month: 'May-2025', AllocationPercent: 40, Role: 'Developer' },

    // Frank Lee - Frontend - available capacity
    { AllocationID: 'A053', ResourceID: 'R006', ProjectID: 'P004', Month: 'Feb-2025', AllocationPercent: 50, Role: 'Frontend Developer' },
    { AllocationID: 'A054', ResourceID: 'R006', ProjectID: 'P004', Month: 'Mar-2025', AllocationPercent: 60, Role: 'Frontend Developer' },
    { AllocationID: 'A055', ResourceID: 'R006', ProjectID: 'P004', Month: 'Apr-2025', AllocationPercent: 50, Role: 'Frontend Developer' },
    { AllocationID: 'A056', ResourceID: 'R006', ProjectID: 'P008', Month: 'Apr-2025', AllocationPercent: 30, Role: 'Developer' },
    { AllocationID: 'A057', ResourceID: 'R006', ProjectID: 'P004', Month: 'May-2025', AllocationPercent: 40, Role: 'Frontend Developer' },
    { AllocationID: 'A058', ResourceID: 'R006', ProjectID: 'P008', Month: 'May-2025', AllocationPercent: 40, Role: 'Developer' },

    // Grace Chen - DevOps
    { AllocationID: 'A059', ResourceID: 'R007', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 30, Role: 'DevOps Engineer' },
    { AllocationID: 'A060', ResourceID: 'R007', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 20, Role: 'DevOps Engineer' },
    { AllocationID: 'A061', ResourceID: 'R007', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 40, Role: 'DevOps Engineer' },
    { AllocationID: 'A062', ResourceID: 'R007', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 20, Role: 'DevOps Engineer' },
    { AllocationID: 'A063', ResourceID: 'R007', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 50, Role: 'DevOps Engineer' },
    { AllocationID: 'A064', ResourceID: 'R007', ProjectID: 'P006', Month: 'May-2025', AllocationPercent: 60, Role: 'Lead DevOps' },
    { AllocationID: 'A065', ResourceID: 'R007', ProjectID: 'P006', Month: 'Jun-2025', AllocationPercent: 80, Role: 'Lead DevOps' },

    // Henry Wilson - QA
    { AllocationID: 'A066', ResourceID: 'R008', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 30, Role: 'QA Engineer' },
    { AllocationID: 'A067', ResourceID: 'R008', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 30, Role: 'QA Engineer' },
    { AllocationID: 'A068', ResourceID: 'R008', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 40, Role: 'QA Engineer' },
    { AllocationID: 'A069', ResourceID: 'R008', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 30, Role: 'QA Engineer' },
    { AllocationID: 'A070', ResourceID: 'R008', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 20, Role: 'QA Engineer' },
    { AllocationID: 'A071', ResourceID: 'R008', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 50, Role: 'QA Engineer' },
    { AllocationID: 'A072', ResourceID: 'R008', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 40, Role: 'QA Engineer' },

    // Ivy Taylor - UI/UX
    { AllocationID: 'A073', ResourceID: 'R009', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 40, Role: 'UI Designer' },
    { AllocationID: 'A074', ResourceID: 'R009', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 30, Role: 'UX Designer' },
    { AllocationID: 'A075', ResourceID: 'R009', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 30, Role: 'UI Designer' },
    { AllocationID: 'A076', ResourceID: 'R009', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 40, Role: 'UX Designer' },
    { AllocationID: 'A077', ResourceID: 'R009', ProjectID: 'P004', Month: 'Feb-2025', AllocationPercent: 20, Role: 'UI Designer' },
    { AllocationID: 'A078', ResourceID: 'R009', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 50, Role: 'UX Designer' },
    { AllocationID: 'A079', ResourceID: 'R009', ProjectID: 'P004', Month: 'Mar-2025', AllocationPercent: 30, Role: 'UI Designer' },

    // Jack Anderson - Data Science
    { AllocationID: 'A080', ResourceID: 'R010', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 30, Role: 'ML Engineer' },
    { AllocationID: 'A081', ResourceID: 'R010', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 40, Role: 'ML Engineer' },
    { AllocationID: 'A082', ResourceID: 'R010', ProjectID: 'P007', Month: 'Jun-2025', AllocationPercent: 50, Role: 'Lead ML Engineer' },
    { AllocationID: 'A083', ResourceID: 'R010', ProjectID: 'P005', Month: 'Apr-2025', AllocationPercent: 30, Role: 'Data Scientist' },
    { AllocationID: 'A084', ResourceID: 'R010', ProjectID: 'P005', Month: 'May-2025', AllocationPercent: 40, Role: 'Data Scientist' },

    // Karen White - Backend - low utilization
    { AllocationID: 'A085', ResourceID: 'R011', ProjectID: 'P004', Month: 'Mar-2025', AllocationPercent: 30, Role: 'Backend Developer' },
    { AllocationID: 'A086', ResourceID: 'R011', ProjectID: 'P004', Month: 'Apr-2025', AllocationPercent: 40, Role: 'Backend Developer' },
    { AllocationID: 'A087', ResourceID: 'R011', ProjectID: 'P008', Month: 'Apr-2025', AllocationPercent: 20, Role: 'Developer' },

    // Leo Garcia - Frontend
    { AllocationID: 'A088', ResourceID: 'R012', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 50, Role: 'Frontend Developer' },
    { AllocationID: 'A089', ResourceID: 'R012', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 60, Role: 'Frontend Developer' },
    { AllocationID: 'A090', ResourceID: 'R012', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 30, Role: 'Frontend Developer' },
    { AllocationID: 'A091', ResourceID: 'R012', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 50, Role: 'Frontend Developer' },
    { AllocationID: 'A092', ResourceID: 'R012', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 40, Role: 'Frontend Developer' },

    // Maria Santos - Backend
    { AllocationID: 'A093', ResourceID: 'R013', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 60, Role: 'Backend Developer' },
    { AllocationID: 'A094', ResourceID: 'R013', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 70, Role: 'Backend Developer' },
    { AllocationID: 'A095', ResourceID: 'R013', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 60, Role: 'Backend Developer' },
    { AllocationID: 'A096', ResourceID: 'R013', ProjectID: 'P009', Month: 'May-2025', AllocationPercent: 50, Role: 'Developer' },

    // Nathan Park - DevOps
    { AllocationID: 'A097', ResourceID: 'R014', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 30, Role: 'DevOps Engineer' },
    { AllocationID: 'A098', ResourceID: 'R014', ProjectID: 'P003', Month: 'Jan-2025', AllocationPercent: 30, Role: 'DevOps Engineer' },
    { AllocationID: 'A099', ResourceID: 'R014', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 30, Role: 'DevOps Engineer' },
    { AllocationID: 'A100', ResourceID: 'R014', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 40, Role: 'DevOps Engineer' },
    { AllocationID: 'A101', ResourceID: 'R014', ProjectID: 'P006', Month: 'May-2025', AllocationPercent: 50, Role: 'DevOps Engineer' },

    // Olivia Kim - QA
    { AllocationID: 'A102', ResourceID: 'R015', ProjectID: 'P003', Month: 'Jan-2025', AllocationPercent: 40, Role: 'QA Engineer' },
    { AllocationID: 'A103', ResourceID: 'R015', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 50, Role: 'QA Engineer' },
    { AllocationID: 'A104', ResourceID: 'R015', ProjectID: 'P003', Month: 'Mar-2025', AllocationPercent: 40, Role: 'QA Engineer' },
    { AllocationID: 'A105', ResourceID: 'R015', ProjectID: 'P004', Month: 'Mar-2025', AllocationPercent: 30, Role: 'QA Engineer' },
];

// Create workbook
const wb = XLSX.utils.book_new();

// Add Resources sheet
const wsResources = XLSX.utils.json_to_sheet(resources);
XLSX.utils.book_append_sheet(wb, wsResources, 'Resources');

// Add Projects sheet
const wsProjects = XLSX.utils.json_to_sheet(projects);
XLSX.utils.book_append_sheet(wb, wsProjects, 'Projects');

// Add Allocations sheet
const wsAllocations = XLSX.utils.json_to_sheet(allocations);
XLSX.utils.book_append_sheet(wb, wsAllocations, 'Allocations');

// Write the file
XLSX.writeFile(wb, 'resource_planning_data.xlsx');

console.log('Excel file created: resource_planning_data.xlsx');
console.log(`- Resources: ${resources.length} records`);
console.log(`- Projects: ${projects.length} records (${projects.filter(p => p.ProjectType === 'Active').length} Active, ${projects.filter(p => p.ProjectType === 'Planned').length} Planned)`);
console.log(`- Allocations: ${allocations.length} records`);
