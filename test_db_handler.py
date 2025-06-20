import pytest
import pandas as pd
from datetime import datetime
from db_handler import DBHandler
import os

@pytest.fixture
def sample_data():
    """Fixture: provide a sample DataFrame for testing DBHandler methods"""
    #fixture: provide a sample dataframe for testing dbhandler methods
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
    """Fixture: create a temporary CSV file and initialize DBHandler"""
    #fixture: create a temporary csv file and initialize dbhandler
    db_path = tmp_path / "test_db.csv"
    #write the sample_data dataframe to csv without including an index column
    sample_data.to_csv(db_path, index=False)
    #initialize and return the dbhandler with the path to the temp csv
    return DBHandler(str(db_path))


def test_init(temp_db, sample_data):
    """Test database initialization loads data correctly"""
    assert isinstance(temp_db.df, pd.DataFrame)
    assert len(temp_db.df) == len(sample_data)
    assert all(col in temp_db.df.columns for col in sample_data.columns)
    assert 'LOINC-NAME' in temp_db.df.columns


def test_init_without_loinc_name(tmp_path):
    """Test initialization when LOINC-NAME column is missing"""
    data = pd.DataFrame({
        'first_name': ['John'],
        'last_name': ['Doe'],
        'LOINC-NUM': ['12345'],
        'Value': ['120'],
        'Unit': ['mmHg'],
        'measurement_datetime': ['2024-01-01 10:00:00'],
        'update_datetime': ['2024-01-01 10:00:00']
    })
    #create a dataframe missing the 'loinc-name' column
    db_path = tmp_path / "test_db.csv"
    #save this dataframe to a temporary csv file
    data.to_csv(db_path, index=False)
    #initialize dbhandler which should add the missing 'loinc-name' column
    db = DBHandler(str(db_path))
    #after initialization 'loinc-name' should be present in df.columns
    assert 'LOINC-NAME' in db.df.columns
    #and all entries in that new column should be nan because original data lacked it
    assert db.df['LOINC-NAME'].isna().all()


def test_retrieve_records(temp_db):
    """Test retrieval of records with various filter combinations"""
    #basic retrieval: filter by first/last name loinc-num and date range only
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        None, '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    #should return two records matching john doe within the given interval
    assert len(records) == 2
    assert all(records['first_name'] == 'John')
    assert all(records['last_name'] == 'Doe')
    assert all(records['LOINC-NAME'] == 'Blood Pressure')

    #retrieval with exact measurement datetime filter
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    #should return exactly one record with value '120'
    assert len(records) == 1
    assert records.iloc[0]['Value'] == '120'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    #retrieval for non-existent person should yield an empty result
    records = temp_db.retrieve_records(
        'Nonexistent', 'Person', '12345',
        None, '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    assert len(records) == 0


def test_update_record(temp_db):
    """Test updating of existing records and handling of missing records"""
    #attempt to update john doe's record value to '130'
    success, result = temp_db.update_record(
        'John', 'Doe', '12345', '130',
        '2024-01-04 10:00:00', '2024-01-01 10:00:00'
    )
    #update should succeed returning true and no error message
    assert success
    assert result is None

    #verify that the updated value is reflected in the stored data
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 00:00:00', '2024-01-05 00:00:00'
    )
    #only one record should match and its value field should now be '130'
    assert len(records) == 1
    assert records.iloc[0]['Value'] == '130'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    #attempt to update a non-existent record should fail gracefully
    success, result = temp_db.update_record(
        'Nonexistent', 'Person', '12345', '130',
        '2024-01-04 10:00:00', '2024-01-01 10:00:00'
    )
    assert not success
    #the result message should indicate no matching record found
    assert "No matching record found" in result


def test_delete_record(temp_db):
    """Test deletion of records and handling of missing records"""
    #delete john doe's record from 2024-01-01 to 2024-01-04
    success, result = temp_db.delete_record(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 10:00:00'
    )
    #deletion should succeed
    assert success
    assert result is None

    #after deletion retrieve should mark the record as 'deleted'
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 00:00:00', '2024-01-05 00:00:00'
    )
    assert len(records) == 1
    assert records.iloc[0]['Value'] == 'DELETED'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    #attempt to delete a non-existent record should return an error message
    success, result = temp_db.delete_record(
        'Nonexistent', 'Person', '12345',
        '2024-01-01 10:00:00', '2024-01-04 10:00:00'
    )
    assert not success
    #assert that the result message indicates no matching record found
    assert "No matching record found" in result
