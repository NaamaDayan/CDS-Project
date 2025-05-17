# Medical Records System

A Python-based system for managing medical records with LOINC code integration. The system provides a web interface for retrieving, updating, and deleting medical records while maintaining a history of changes.

## Architecture

### Components

1. **Database Handler (`db_handler.py`)**
   - Manages CSV file operations
   - Handles record retrieval, updates, and deletions
   - Maintains data integrity and history
   - Supports LOINC name integration

2. **LOINC Name Fetcher (`loinc_name_fetcher.py`)**
   - Integrates with UMLS API to fetch LOINC names
   - Provides caching mechanism for efficient API usage
   - Handles API authentication and rate limiting

3. **Web Interface (`app.py`)**
   - Built with Dash and Bootstrap
   - Provides three main operations:
     - Retrieve records with filtering
     - Update records with validation
     - Delete records (soft delete)
   - Features datetime pickers and responsive design

### Data Flow

1. **Record Retrieval**
   ```
   User Input → Web Interface → Database Handler → CSV File → Results Display
   ```

2. **Record Update**
   ```
   User Input → Web Interface → Database Handler → CSV File Update → Confirmation
   ```

3. **Record Deletion**
   ```
   User Input → Web Interface → Database Handler → Mark as Deleted → Confirmation
   ```

4. **LOINC Name Integration**
   ```
   CSV File → LOINC Fetcher → UMLS API → Cached Names → Updated CSV
   ```

## Prerequisites

- Python 3.8 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - pandas==2.1.0
  - dash==2.14.2
  - dash-bootstrap-components==1.5.0
  - dash-core-components==2.0.0
  - python-dateutil==2.8.2
  - requests
  - beautifulsoup4

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Prepare your CSV file:
   - Create a CSV file with the following columns:
     - first_name
     - last_name
     - LOINC-NUM
     - Value
     - Unit
     - measurement_datetime
     - update_datetime

4. Add LOINC names to your CSV:
   ```python
   from loinc_name_fetcher import add_loinc_names_to_csv
   
   # This will create a new file with LOINC names
   add_loinc_names_to_csv("your_input.csv", "your_output.csv")
   ```

## Running the Application

1. Start the web interface:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8050
   ```

## Using the Interface

### Retrieve Records
1. Go to the "Retrieve" tab
2. Enter patient details (First Name, Last Name)
3. Enter LOINC number
4. (Optional) Enter specific measurement datetime
5. Enter date range for updates
6. Click "Retrieve" to see results

### Update Records
1. Go to the "Update" tab
2. Enter patient details
3. Enter LOINC number
4. Enter new value
5. Enter update datetime
6. Enter measurement datetime
7. Click "Update" to save changes

### Delete Records
1. Go to the "Delete" tab
2. Enter patient details
3. Enter LOINC number
4. Enter measurement datetime
5. Enter update datetime
6. Click "Delete" to mark record as deleted

## Testing

Run the test suite:
```bash
pytest
```

Run specific test files:
```bash
pytest test_db_handler.py
pytest test_app.py
```

## Notes

- The system uses soft deletion (records are marked as 'DELETED' rather than being removed)
- All changes are tracked with update timestamps
- LOINC names are cached to minimize API calls
- The interface includes input validation and error handling

## Error Handling

- Invalid datetime formats will show error messages
- Missing required fields will be highlighted
- API errors for LOINC name fetching will be logged
- Database operations include error handling and rollback
