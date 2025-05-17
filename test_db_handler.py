import pytest
import pandas as pd
from datetime import datetime
from db_handler import dbhandler
import os

@pytest.fixture
def sample_data():
    """Fixture: provide a sample df for testing dbhandler methods"""
    # Construct a df with repeated LOINC entries and datetime strings
    return pd.df({
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
    """Fixture: create a temporary csv file and initialize dbhandler"""
    #define the temporary file path for the csv databse
    db_path = tmp_path / "test_db.csv"
    # write the sample data df to csv, without including an index 
    sample_data.to_csv(db_path, index=False)
    # init and return the dbhandler with the path to the temp csv
    return dbhandler(str(db_path))


def test_init(temp_db, sample_data):
    """Test database initialization loads data correctly"""
    # the dbhandler should have loaded a df attribute 'df'
    assert isinstance(temp_db.df, pd.df)
    # number of rows in df should match the sample_data length
    assert len(temp_db.df) == len(sample_data)
    # all columns from sample_data should be present in temp_db.df
    assert all(col in temp_db.df.columns for col in sample_data.columns)
    # specifically ensure that the 'LOINC-NAME' column exists
    assert 'LOINC-NAME' in temp_db.df.columns


def test_init_without_loinc_name(tmp_path):
    """Test initialization when LOINC-NAME column is missing"""
    # create a df missing the 'LOINC-NAME' column
    data = pd.df({
        'first_name': ['John'],
        'last_name': ['Doe'],
        'LOINC-NUM': ['12345'],
        'Value': ['120'],
        'Unit': ['mmHg'],
        'measurement_datetime': ['2024-01-01 10:00:00'],
        'update_datetime': ['2024-01-01 10:00:00']
    })
    # save this df to a temporary csv file
    db_path = tmp_path / "test_db.csv"
    data.to_csv(db_path, index=False)
    # initialize dbhandler, which should add the missing 'LOINC-NAME' column
    db = dbhandler(str(db_path))
    # after initialization, 'LOINC-NAME' should be present in df.columns
    assert 'LOINC-NAME' in db.df.columns
    # and all entries in that new column should be NaN (because original data lacked it)
    assert db.df['LOINC-NAME'].isna().all()


def test_retrieve_records(temp_db):
    """Test retrieval of records with various filter combinations"""
    # basic retrieval: filter by first/last name, LOINC-NUM, and date range only
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        None, '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    # should return two records matching John Doe within the given interval
    assert len(records) == 2
    assert all(records['first_name'] == 'John')
    assert all(records['last_name'] == 'Doe')
    assert all(records['LOINC-NAME'] == 'Blood Pressure')

    # retrieval with exact measurement datetime filter
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    # should return exactly one record, with Value '120'
    assert len(records) == 1
    assert records.iloc[0]['Value'] == '120'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    # retrieval for non-existent person should yield an empty result
    records = temp_db.retrieve_records(
        'Nonexistent', 'Person', '12345',
        None, '2024-01-01 00:00:00', '2024-01-04 00:00:00'
    )
    assert len(records) == 0


def test_update_record(temp_db):
    """Test updating of existing records and handling of missing records"""
    # attempt to update John Doe's record value to '130'
    success, result = temp_db.update_record(
        'John', 'Doe', '12345', '130',
        '2024-01-04 10:00:00', '2024-01-01 10:00:00'
    )
    # Uudate should succeed, returning True and no error message
    assert success
    assert result is None

    # verify that the updated value is reflected in the stored data
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 00:00:00', '2024-01-05 00:00:00'
    )
    # only one record should match, and its Value field should now be '130'
    assert len(records) == 1
    assert records.iloc[0]['Value'] == '130'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    # attempt to update a non-existent record should fail gracefully
    success, result = temp_db.update_record(
        'Nonexistent', 'Person', '12345', '130',
        '2024-01-04 10:00:00', '2024-01-01 10:00:00'
    )
    assert not success
    # the result message should indicate no matching record found
    assert "No matching record found" in result


def test_delete_record(temp_db):
    """Test deletion of records and handling of missing records"""
    # delete John Doe's record from 2024-01-01 to 2024-01-04
    success, result = temp_db.delete_record(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 10:00:00'
    )
    # deletion should succeed
    assert success
    assert result is None

    # after deletion, retrieve should mark the record as 'DELETED'
    records = temp_db.retrieve_records(
        'John', 'Doe', '12345',
        '2024-01-01 10:00:00', '2024-01-04 00:00:00', '2024-01-05 00:00:00'
    )
    assert len(records) == 1
    assert records.iloc[0]['Value'] == 'DELETED'
    assert records.iloc[0]['LOINC-NAME'] == 'Blood Pressure'

    # attempt to delete a non-existent record should return an error message
    success, result = temp_db.delete_record(
        'Nonexistent', 'Person', '12345',
        '2024-01-01 10:00:00', '2024-01-04 10:00:00'
    )
    assert not success
    assert "No matching record found" in result
