const XLSX = require('xlsx');

// Sample data for Resources sheet
const resources = [
    { ResourceID: 'R001', ResourceName: 'Alice Johnson', PrimarySkill: 'Frontend', SecondarySkill: 'UI/UX', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R002', ResourceName: 'Bob Smith', PrimarySkill: 'Backend', SecondarySkill: 'DevOps', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R003', ResourceName: 'Carol Williams', PrimarySkill: 'Data Science', SecondarySkill: 'Python', Department: 'Analytics', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R004', ResourceName: 'David Brown', PrimarySkill: 'Project Management', SecondarySkill: 'Agile', Department: 'PMO', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R005', ResourceName: 'Eva Martinez', PrimarySkill: 'Backend', SecondarySkill: 'Database', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R006', ResourceName: 'Frank Lee', PrimarySkill: 'Frontend', SecondarySkill: 'React', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R007', ResourceName: 'Grace Chen', PrimarySkill: 'DevOps', SecondarySkill: 'Cloud', Department: 'Infrastructure', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R008', ResourceName: 'Henry Wilson', PrimarySkill: 'QA', SecondarySkill: 'Automation', Department: 'Quality', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R009', ResourceName: 'Ivy Taylor', PrimarySkill: 'UI/UX', SecondarySkill: 'Design', Department: 'Design', Status: 'On Leave', HoursPerWeek: 40 },
    { ResourceID: 'R010', ResourceName: 'Jack Anderson', PrimarySkill: 'Data Science', SecondarySkill: 'ML', Department: 'Analytics', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R011', ResourceName: 'Karen White', PrimarySkill: 'Backend', SecondarySkill: 'API', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40 },
    { ResourceID: 'R012', ResourceName: 'Leo Garcia', PrimarySkill: 'Frontend', SecondarySkill: 'Vue', Department: 'Engineering', Status: 'Active', HoursPerWeek: 40 },
];

// Sample data for Projects sheet
const projects = [
    { ProjectID: 'P001', ProjectName: 'E-Commerce Platform', Client: 'RetailCorp', Status: 'In Progress', Priority: 'High', StartDate: '2025-01-15', EndDate: '2025-06-30', Budget: 150000, RequiredFTE: 4 },
    { ProjectID: 'P002', ProjectName: 'Mobile Banking App', Client: 'FinanceHub', Status: 'In Progress', Priority: 'Critical', StartDate: '2025-02-01', EndDate: '2025-08-31', Budget: 200000, RequiredFTE: 5 },
    { ProjectID: 'P003', ProjectName: 'Analytics Dashboard', Client: 'DataDriven Inc', Status: 'Planning', Priority: 'Medium', StartDate: '2025-03-01', EndDate: '2025-07-15', Budget: 80000, RequiredFTE: 3 },
    { ProjectID: 'P004', ProjectName: 'CRM Integration', Client: 'SalesForce Plus', Status: 'In Progress', Priority: 'High', StartDate: '2025-01-01', EndDate: '2025-04-30', Budget: 120000, RequiredFTE: 3 },
    { ProjectID: 'P005', ProjectName: 'Cloud Migration', Client: 'TechStart', Status: 'On Hold', Priority: 'Low', StartDate: '2025-04-01', EndDate: '2025-09-30', Budget: 250000, RequiredFTE: 4 },
    { ProjectID: 'P006', ProjectName: 'AI Chatbot', Client: 'ServiceNow', Status: 'Planning', Priority: 'Medium', StartDate: '2025-05-01', EndDate: '2025-10-31', Budget: 180000, RequiredFTE: 4 },
    { ProjectID: 'P007', ProjectName: 'Inventory System', Client: 'WarehousePro', Status: 'Completed', Priority: 'Medium', StartDate: '2024-10-01', EndDate: '2025-01-31', Budget: 90000, RequiredFTE: 2 },
    { ProjectID: 'P008', ProjectName: 'HR Portal', Client: 'Internal', Status: 'In Progress', Priority: 'High', StartDate: '2025-02-15', EndDate: '2025-05-31', Budget: 60000, RequiredFTE: 2 },
];

// Sample data for Allocations sheet
const allocations = [
    // Alice Johnson - Frontend - high utilization
    { AllocationID: 'A001', ResourceID: 'R001', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 60, Role: 'Lead Developer', HoursAllocated: 96 },
    { AllocationID: 'A002', ResourceID: 'R001', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 50, Role: 'Developer', HoursAllocated: 80 },
    { AllocationID: 'A003', ResourceID: 'R001', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 70, Role: 'Lead Developer', HoursAllocated: 112 },
    { AllocationID: 'A004', ResourceID: 'R001', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 40, Role: 'Developer', HoursAllocated: 64 },
    { AllocationID: 'A005', ResourceID: 'R001', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 80, Role: 'Lead Developer', HoursAllocated: 128 },
    { AllocationID: 'A006', ResourceID: 'R001', ProjectID: 'P008', Month: 'Mar-2025', AllocationPercent: 30, Role: 'Developer', HoursAllocated: 48 },

    // Bob Smith - Backend - overloaded
    { AllocationID: 'A007', ResourceID: 'R002', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 50, Role: 'Backend Developer', HoursAllocated: 80 },
    { AllocationID: 'A008', ResourceID: 'R002', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 40, Role: 'Backend Developer', HoursAllocated: 64 },
    { AllocationID: 'A009', ResourceID: 'R002', ProjectID: 'P004', Month: 'Jan-2025', AllocationPercent: 30, Role: 'Developer', HoursAllocated: 48 },
    { AllocationID: 'A010', ResourceID: 'R002', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 60, Role: 'Backend Developer', HoursAllocated: 96 },
    { AllocationID: 'A011', ResourceID: 'R002', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 50, Role: 'Backend Developer', HoursAllocated: 80 },
    { AllocationID: 'A012', ResourceID: 'R002', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 40, Role: 'Backend Developer', HoursAllocated: 64 },
    { AllocationID: 'A013', ResourceID: 'R002', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 60, Role: 'Backend Developer', HoursAllocated: 96 },

    // Carol Williams - Data Science - low utilization
    { AllocationID: 'A014', ResourceID: 'R003', ProjectID: 'P003', Month: 'Jan-2025', AllocationPercent: 20, Role: 'Data Analyst', HoursAllocated: 32 },
    { AllocationID: 'A015', ResourceID: 'R003', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 30, Role: 'Data Analyst', HoursAllocated: 48 },
    { AllocationID: 'A016', ResourceID: 'R003', ProjectID: 'P003', Month: 'Mar-2025', AllocationPercent: 40, Role: 'Data Analyst', HoursAllocated: 64 },
    { AllocationID: 'A017', ResourceID: 'R003', ProjectID: 'P006', Month: 'Mar-2025', AllocationPercent: 20, Role: 'ML Engineer', HoursAllocated: 32 },

    // David Brown - Project Management - moderate
    { AllocationID: 'A018', ResourceID: 'R004', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 30, Role: 'Project Manager', HoursAllocated: 48 },
    { AllocationID: 'A019', ResourceID: 'R004', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 40, Role: 'Project Manager', HoursAllocated: 64 },
    { AllocationID: 'A020', ResourceID: 'R004', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 25, Role: 'Project Manager', HoursAllocated: 40 },
    { AllocationID: 'A021', ResourceID: 'R004', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 45, Role: 'Project Manager', HoursAllocated: 72 },
    { AllocationID: 'A022', ResourceID: 'R004', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 20, Role: 'Project Manager', HoursAllocated: 32 },
    { AllocationID: 'A023', ResourceID: 'R004', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 20, Role: 'Project Manager', HoursAllocated: 32 },
    { AllocationID: 'A024', ResourceID: 'R004', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 50, Role: 'Project Manager', HoursAllocated: 80 },
    { AllocationID: 'A025', ResourceID: 'R004', ProjectID: 'P003', Month: 'Mar-2025', AllocationPercent: 30, Role: 'Project Manager', HoursAllocated: 48 },

    // Eva Martinez - Backend - moderate
    { AllocationID: 'A026', ResourceID: 'R005', ProjectID: 'P004', Month: 'Jan-2025', AllocationPercent: 80, Role: 'Lead Developer', HoursAllocated: 128 },
    { AllocationID: 'A027', ResourceID: 'R005', ProjectID: 'P004', Month: 'Feb-2025', AllocationPercent: 90, Role: 'Lead Developer', HoursAllocated: 144 },
    { AllocationID: 'A028', ResourceID: 'R005', ProjectID: 'P004', Month: 'Mar-2025', AllocationPercent: 70, Role: 'Lead Developer', HoursAllocated: 112 },
    { AllocationID: 'A029', ResourceID: 'R005', ProjectID: 'P008', Month: 'Mar-2025', AllocationPercent: 30, Role: 'Developer', HoursAllocated: 48 },

    // Frank Lee - Frontend - low utilization
    { AllocationID: 'A030', ResourceID: 'R006', ProjectID: 'P008', Month: 'Feb-2025', AllocationPercent: 40, Role: 'Frontend Developer', HoursAllocated: 64 },
    { AllocationID: 'A031', ResourceID: 'R006', ProjectID: 'P008', Month: 'Mar-2025', AllocationPercent: 50, Role: 'Frontend Developer', HoursAllocated: 80 },

    // Grace Chen - DevOps - varied
    { AllocationID: 'A032', ResourceID: 'R007', ProjectID: 'P005', Month: 'Jan-2025', AllocationPercent: 30, Role: 'DevOps Engineer', HoursAllocated: 48 },
    { AllocationID: 'A033', ResourceID: 'R007', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 20, Role: 'DevOps Engineer', HoursAllocated: 32 },
    { AllocationID: 'A034', ResourceID: 'R007', ProjectID: 'P005', Month: 'Feb-2025', AllocationPercent: 25, Role: 'DevOps Engineer', HoursAllocated: 40 },
    { AllocationID: 'A035', ResourceID: 'R007', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 30, Role: 'DevOps Engineer', HoursAllocated: 48 },
    { AllocationID: 'A036', ResourceID: 'R007', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 40, Role: 'DevOps Engineer', HoursAllocated: 64 },

    // Henry Wilson - QA - overloaded in Feb
    { AllocationID: 'A037', ResourceID: 'R008', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 40, Role: 'QA Engineer', HoursAllocated: 64 },
    { AllocationID: 'A038', ResourceID: 'R008', ProjectID: 'P002', Month: 'Jan-2025', AllocationPercent: 30, Role: 'QA Engineer', HoursAllocated: 48 },
    { AllocationID: 'A039', ResourceID: 'R008', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 50, Role: 'QA Engineer', HoursAllocated: 80 },
    { AllocationID: 'A040', ResourceID: 'R008', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 40, Role: 'QA Engineer', HoursAllocated: 64 },
    { AllocationID: 'A041', ResourceID: 'R008', ProjectID: 'P004', Month: 'Feb-2025', AllocationPercent: 25, Role: 'QA Engineer', HoursAllocated: 40 },
    { AllocationID: 'A042', ResourceID: 'R008', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 60, Role: 'QA Engineer', HoursAllocated: 96 },
    { AllocationID: 'A043', ResourceID: 'R008', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 50, Role: 'QA Engineer', HoursAllocated: 80 },

    // Jack Anderson - Data Science - moderate
    { AllocationID: 'A044', ResourceID: 'R010', ProjectID: 'P006', Month: 'Jan-2025', AllocationPercent: 20, Role: 'ML Engineer', HoursAllocated: 32 },
    { AllocationID: 'A045', ResourceID: 'R010', ProjectID: 'P003', Month: 'Feb-2025', AllocationPercent: 50, Role: 'Data Scientist', HoursAllocated: 80 },
    { AllocationID: 'A046', ResourceID: 'R010', ProjectID: 'P006', Month: 'Feb-2025', AllocationPercent: 30, Role: 'ML Engineer', HoursAllocated: 48 },
    { AllocationID: 'A047', ResourceID: 'R010', ProjectID: 'P003', Month: 'Mar-2025', AllocationPercent: 60, Role: 'Data Scientist', HoursAllocated: 96 },
    { AllocationID: 'A048', ResourceID: 'R010', ProjectID: 'P006', Month: 'Mar-2025', AllocationPercent: 40, Role: 'ML Engineer', HoursAllocated: 64 },

    // Karen White - Backend - low utilization
    { AllocationID: 'A049', ResourceID: 'R011', ProjectID: 'P008', Month: 'Feb-2025', AllocationPercent: 30, Role: 'Backend Developer', HoursAllocated: 48 },
    { AllocationID: 'A050', ResourceID: 'R011', ProjectID: 'P008', Month: 'Mar-2025', AllocationPercent: 40, Role: 'Backend Developer', HoursAllocated: 64 },

    // Leo Garcia - Frontend - moderate
    { AllocationID: 'A051', ResourceID: 'R012', ProjectID: 'P001', Month: 'Jan-2025', AllocationPercent: 50, Role: 'Frontend Developer', HoursAllocated: 80 },
    { AllocationID: 'A052', ResourceID: 'R012', ProjectID: 'P001', Month: 'Feb-2025', AllocationPercent: 60, Role: 'Frontend Developer', HoursAllocated: 96 },
    { AllocationID: 'A053', ResourceID: 'R012', ProjectID: 'P002', Month: 'Feb-2025', AllocationPercent: 30, Role: 'Frontend Developer', HoursAllocated: 48 },
    { AllocationID: 'A054', ResourceID: 'R012', ProjectID: 'P001', Month: 'Mar-2025', AllocationPercent: 50, Role: 'Frontend Developer', HoursAllocated: 80 },
    { AllocationID: 'A055', ResourceID: 'R012', ProjectID: 'P002', Month: 'Mar-2025', AllocationPercent: 40, Role: 'Frontend Developer', HoursAllocated: 64 },
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
console.log(`- Projects: ${projects.length} records`);
console.log(`- Allocations: ${allocations.length} records`);
