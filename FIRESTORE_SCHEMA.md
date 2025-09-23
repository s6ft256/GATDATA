# Firestore Schema Documentation

This document describes the Firestore schema used by the Safety Data Management system.

## Core Collections

### 1. Incidents

Stores safety incident data from various incident tracking sheets.

**Structure:**
```
Incidents/{incidentId}
├── id (string) - Document ID (auto-generated)
├── date (timestamp) - Date and time of incident
├── location (string) - Location where incident occurred
├── department (string) - Department involved
├── description (string) - Description of the incident
├── severity (string) - Severity level (Low/Medium/High/Critical)
├── category (string) - Incident category/type
├── reported_by (string) - Person who reported the incident
├── status (string) - Current status (Open/In Progress/Resolved/Closed)
└── ... (other fields from Excel sheets)
```

### 2. Inspections

Stores safety inspection and audit data.

**Structure:**
```
Inspections/{inspectionId}
├── id (string) - Document ID (auto-generated)
├── date (timestamp) - Date of inspection
├── location (string) - Location inspected
├── inspector (string) - Person who conducted inspection
├── findings (array) - List of findings
├── compliance_status (string) - Compliance status (Compliant/Non-Compliant)
├── corrective_actions (array) - List of corrective actions
├── due_date (timestamp) - Due date for corrective actions
└── ... (other fields from Excel sheets)
```

### 3. Trainings

Stores employee training and competency data.

**Structure:**
```
Trainings/{trainingId}
├── id (string) - Document ID (auto-generated)
├── employee_name (string) - Name of employee
├── employee_id (string) - Employee ID
├── training_name (string) - Name of training program
├── training_date (timestamp) - Date of training
├── trainer (string) - Person who conducted training
├── completion_status (string) - Completion status (Completed/In Progress/Not Started)
├── competency_level (string) - Competency level achieved
├── expiry_date (timestamp) - Expiry date of training
└── ... (other fields from Excel sheets)
```

## Extended Analytics Collections

These collections are used for advanced analytics but are not part of the core structured data:

### Maintenance Records

Stores equipment maintenance data for correlation analysis.

### Near-Miss Reports

Stores near-miss incident reports for root cause analysis.

### Safety Violations

Stores safety violation data for trend analysis.

### Audit Results

Stores detailed audit results for compliance tracking.

### Environmental Conditions

Stores environmental monitoring data (weather, temperature, etc.).

### Equipment Logs

Stores equipment usage and condition logs.

## Field Naming Conventions

1. All field names are sanitized to be Firestore-compatible:
   - Alphanumeric characters and underscores only
   - No spaces or special characters
   - Lowercase preferred
   - Maximum 1500 characters

2. Common field mappings:
   - "Date" → "date"
   - "Location" → "location"
   - "Department" → "department"
   - "Status" → "status"
   - "ID" → Removed (not stored)

## Data Types

1. **Timestamps** - Stored as Firestore timestamp objects
2. **Strings** - Text data
3. **Numbers** - Numeric data (integers and floats)
4. **Booleans** - True/False values
5. **Arrays** - Lists of values
6. **Maps** - Nested objects

## Security Rules

See `firestore.rules` for detailed security configuration.

## Indexes

Firestore automatically creates indexes for all fields. For complex queries, composite indexes may be required.