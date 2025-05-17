import pytest
import pandas as pd
from datetime import datetime
from db_handler import DBHandler
import os

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'first_name': ['John', 'Jane', 'John'],
        'last_name': ['Doe', 'Smith', 'Doe'],
        'LOINC-NUM': ['12345', '12345', '12345'],
        'LOINC-NAME': ['Blood Pressure', 'Blood Pressure', 'Blood Pressure'],
        'Value': ['120', '110', '125'],
        'Unit': ['mmHg', 'mmHg', 'mmHg'],
        'measurement_datetime': [
            '2024-01-01 10:00:00',
            '2024-01-02 10:00:00',
            '2024-01-03 10:00:00'
        ],
        'update_datetime': [
            '2024-01-01 10:00:00',
            '2024-01-02 10:00:00',
            '2024-01-03 10:00:00'
        ]
    })

@pytest.fixture
def temp_db(sample_data, tmp_path):
    # Create a temporary CSV file
    db_path = tmp_path / "test_db.csv"
    sample_data.to_csv(db_path, index=False)
    return DBHandler(str(db_path))

def test_init(temp_db, sample_data):
    """Test database initialization"""
    assert isinstance(temp_db.df, pd.DataFrame)
    assert len(temp_db.df) == len(sample_data)
    assert all(col in temp_db.df.columns for col in sample_data.columns)
    assert 'LOINC-NAME' in temp_db.df.columns

def test_init_without_loinc_name(tmp_path):
    """Test database initialization when LOINC-NAME column is missing"""
    # Create sample data without LOINC-NAME
    data = pd.DataFrame({
        'first_name': ['John'],
        'last_name': ['Doe'],
        'LOINC-NUM': ['12345'],
        'Value': ['120'],
        'Unit': ['mmHg'],
        'measurement_datetime': ['2024-01-01 10:00:00'],
        'update_datetime': ['2024-01-01 10:00:00']
    })
    
    # Save to temporary file
    db_path = tmp_path / "test_db.csv"
    data.to_csv(db_path, index=False)
    
    # Initialize DBHandler
    db = DBHandler(str(db_path))
    
    # Check if LOINC-NAME column was added
    assert 'LOINC-NAME' in db.df.columns
    assert db.df['LOINC-NAME'].isna().all()

def test_retrieve_records(temp_db):
    """Test record retrieval with various filters"""
    # Test basic retrieval
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        None, '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    assert len(records) == 2
    assert all(records['first_name'] == 'John')
    assert all(records['last_name'] == 'Doe')
    assert all(records['LOINC-NAME'] == 'Blood Pressure')

    # Test with measurement datetime
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    assert len(records) == 1
    assert records.iloc[0]['Value'] == '120'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    # Test with no results
    records = temp_db.retrieve_records(
        'Nonexistent', 'Person', '12345',
        None, '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    assert len(records) == 0

def test_update_record(temp_db):
    """Test record updates"""
    # Test successful update
    success, result = temp_db.update_record(
        'John', 'Doe', '12345', '130',
        '2024-01-04 10:00:00', '2024-01-01 10:00:00'
    )
    assert success
    assert result is None

    # Verify update
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 00:00:00', '2024-01-05 00:00:00'
    )
    assert len(records) == 1
    assert records.iloc[0]['Value'] == '130'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    # Test update with non-existent record
    success, result = temp_db.update_record(
        'Nonexistent', 'Person', '12345', '130',
        '2024-01-04 10:00:00', '2024-01-01 10:00:00'
    )
    assert not success
    assert "No matching record found" in result

def test_delete_record(temp_db):
    """Test record deletion"""
    # Test successful deletion
    success, result = temp_db.delete_record(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 10:00:00'
    )
    assert success
    assert result is None

    # Verify deletion
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 00:00:00', '2024-01-05 00:00:00'
    )
    assert len(records) == 1
    assert records.iloc[0]['Value'] == 'DELETED'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    # Test deletion with non-existent record
    success, result = temp_db.delete_record(
        'Nonexistent', 'Person', '12345',
        '2024-01-01 10:00:00', '2024-01-04 10:00:00'
    )
    assert not success
    assert "No matching record found" in result 