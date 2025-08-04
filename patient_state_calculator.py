import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from models import WBCStateRange, HemoglobinStateRange
from knowledge_db_handler import Gender, Grade


def process_hematological_data(patient_tests: pd.DataFrame, validity: pd.DataFrame):
    wbc_data = []
    hb_data = []
    hb_tests = patient_tests[patient_tests['LOINC-NUM'] == '30313-1']
    wbc_tests = patient_tests[patient_tests['LOINC-NUM'] == '6690-2']

    for _, row in hb_tests.iterrows():
        hb_data.append(HemoglobinStateRange(
            datetime.strptime(row['measurement_datetime'], '%Y-%m-%d %H:%M:%S'),
            float(row['Value']),
            float(validity[validity['test_name'] == 'hemoglobin'].iloc[0]['good-before']),
            float(validity[validity['test_name'] == 'hemoglobin'].iloc[0]['good-after'])
        ))
    for _, row in wbc_tests.iterrows():
        wbc_data.append(WBCStateRange(
            datetime.strptime(row['measurement_datetime'], '%Y-%m-%d %H:%M:%S'),
            float(row['Value']),
            float(validity[validity['test_name'] == 'WBC'].iloc[0]['good-before']),
            float(validity[validity['test_name'] == 'WBC'].iloc[0]['good-after'])
        ))
    return wbc_data, hb_data

def find_overlapping_states(wbc_ranges: List[WBCStateRange], hb_ranges: List[HemoglobinStateRange], table: pd.DataFrame):
    raw_intervals = []

    for wbc in wbc_ranges:
        for hb in hb_ranges:
            overlap_start = max(wbc.start, hb.start)
            overlap_end = min(wbc.end, hb.end)
            if overlap_start < overlap_end:
                wbc_interval = table.index.get_indexer([wbc.value])[0]
                hb_interval = table.columns.get_indexer([hb.value])[0]
                if wbc_interval == -1 or hb_interval == -1:
                    continue
                state = table.iloc[wbc_interval, hb_interval]
                raw_intervals.append((overlap_start, overlap_end, state))
    
    return raw_intervals

def resolve_conflicts(raw_intervals):
    if not raw_intervals:
        return []

    # Sort intervals by start time
    raw_intervals.sort()
    result = []

    for interval in raw_intervals:
        if not result:
            result.append(interval)
            continue

        last_start, last_end, last_state = result[-1]
        curr_start, curr_end, curr_state = interval

        if curr_start >= last_end:
            result.append(interval)
        else:
            # Conflict - split at midpoint
            midpoint = last_end - (last_end - curr_start) / 2
            result[-1] = (last_start, midpoint, last_state)
            result.append((midpoint, curr_end, curr_state))

    return result

def fill_gaps(intervals):
    if not intervals:
        return []

    filled = []
    for i in range(len(intervals)):
        start, end, state = intervals[i]
        if i > 0:
            prev_end = intervals[i-1][1]
            if prev_end < start:
                filled.append((prev_end, start, None))
        filled.append((start, end, state))
    return filled

def generate_patient_state_timeline(
    wbc_ranges: List[WBCStateRange],
    hb_ranges: List[HemoglobinStateRange],
    table: pd.DataFrame
):
    raw = find_overlapping_states(wbc_ranges, hb_ranges, table)
    resolved = resolve_conflicts(raw)
    complete = fill_gaps(resolved)
    return complete

def generate_hemoglobin_state_timeline(
    hb_ranges: List[HemoglobinStateRange],
    table: pd.DataFrame
):
    """Generate a timeline of hemoglobin states based on hemoglobin ranges and table."""
    raw_intervals = []
    
    # Create intervals with states from the table
    for hb in hb_ranges:
        hb_state = None
        for _, row in table.iterrows():
            if row['low_range'] <= hb.value < row['high_range']:
                hb_state = row['state']
                break
        if hb_state is not None:
            raw_intervals.append((hb.start, hb.end, hb_state))
    
    # Resolve conflicts
    resolved = resolve_conflicts(raw_intervals)
    
    # Fill gaps
    complete = fill_gaps(resolved)
    
    return complete

def calculate_grade(project_db: pd.DataFrame, knowledge_db, full_name: str, dt: datetime) -> Grade:
    """
    Calculate the systemic grade for a patient at a given datetime.
    Args:
        project_db (pd.DataFrame): The project database containing test results
        knowledge_db: The knowledge database handler
        full_name (str): Patient's full name ("First Last")
        dt (datetime): The datetime to check
    Returns:
        Grade: The maximal grade value (as in systemic_table)
    """
    first_name, last_name = full_name.split(' ', 1)
    # Map test names to LOINC and vice versa
    test_map = {
        'fever': '8310-5',
        'chills': '75275-8',
        'skin-look': '39106-0',
        'allergic state': '56840-2',
    }
    # Get validity periods
    validity = knowledge_db.get_test_validity_table().set_index('test_name')
    # Collect most recent value for each test within the valid window
    values = {}
    for test, loinc in test_map.items():
        good_before = int(validity.loc[test, 'good-before'])
        good_after = int(validity.loc[test, 'good-after'])
        window_start = dt - timedelta(hours=good_before)
        window_end = dt + timedelta(hours=good_after)
        # Filter for patient, test, and time window
        mask = (
            (project_db['first_name'] == first_name) &
            (project_db['last_name'] == last_name) &
            (project_db['LOINC-NUM'] == loinc) &
            (pd.to_datetime(project_db['measurement_datetime']) >= window_start) &
            (pd.to_datetime(project_db['measurement_datetime']) <= window_end)
        )
        test_df = project_db[mask]
        if not test_df.empty:
            # Take the most recent (max) measurement_datetime
            idx = pd.to_datetime(test_df['measurement_datetime']).idxmax()
            values[test] = test_df.loc[idx, 'Value']
        else:
            values[test] = None
    # Now, for each test, determine the grade from systemic_table
    grade_idx = -1
    for i, test in enumerate(['fever', 'chills', 'skin-look', 'allergic state']):
        val = values[test]
        if val is None:
            continue
        # Go left to right in systemic_table row for this test
        row = knowledge_db.systemic_table.loc[test]
        for j, col in enumerate(knowledge_db.systemic_table.columns):
            if str(row[col]) == str(val):
                grade_idx = max(grade_idx, j)
                break
    # Return the grade
    if grade_idx == -1:
        return None
    return Grade(grade_idx + 1)

def get_patient_gender(project_db: pd.DataFrame, full_name: str) -> Optional[str]:
    first_name, last_name = full_name.split(' ', 1)
    row = project_db[(project_db['first_name'] == first_name) & (project_db['last_name'] == last_name)]
    if not row.empty and 'gender' in row.columns:
        return row.iloc[0]['gender'].lower()
    return None

def calculate_hemoglobin_states(project_db: pd.DataFrame, knowledge_db, selected_patient: str) -> List[Dict[str, Any]]:
    """
    Calculate hemoglobin states for a patient.
    Args:
        project_db (pd.DataFrame): The project database
        knowledge_db: The knowledge database handler
        selected_patient (str): Patient's full name
    Returns:
        List[Dict[str, Any]]: List of segments with start, end, and state
    """
    first_name, last_name = selected_patient.split(' ')
    gender_str = get_patient_gender(project_db, selected_patient)
    gender = Gender.FEMALE if gender_str == 'female' else Gender.MALE
    
    # Get patient's hemoglobin tests
    patient_tests = project_db[
        (project_db['first_name'] == first_name) & 
        (project_db['last_name'] == last_name) & 
        (project_db['LOINC-NUM'] == '30313-1')
    ].sort_values('measurement_datetime')

    patient_tests = patient_tests[patient_tests['Value'] != 'DELETED']

    if patient_tests.empty:
        return []
    
    # Get test validity periods
    validity = knowledge_db.get_test_validity_table()
    
    # Process the data to create state ranges
    _, hb_data = process_hematological_data(patient_tests, validity)
    
    # Generate hemoglobin state timeline
    hb_timeline = generate_hemoglobin_state_timeline(
        hb_data,
        knowledge_db.get_hemoglobin_table(gender)
    )
    
    # Create time points
    hb_time_points = []
    for start, end, state in hb_timeline:
        if state is not None:
            hb_time_points.append({'time': start, 'state': state})
            hb_time_points.append({'time': end, 'state': state})
    
    # Convert to DataFrame and create segments
    df_hb = pd.DataFrame(hb_time_points)
    segments = []
    for i in range(1, len(df_hb)):
        prev, curr = df_hb.iloc[i - 1], df_hb.iloc[i]
        if prev['state'] == curr['state']:
            segments.append({'start': prev['time'], 'end': curr['time'], 'state': prev['state']})
    
    return segments

def calculate_hematological_states(project_db: pd.DataFrame, knowledge_db, selected_patient: str) -> List[Dict[str, Any]]:
    """
    Calculate hematological states for a patient.
    Args:
        project_db (pd.DataFrame): The project database
        knowledge_db: The knowledge database handler
        selected_patient (str): Patient's full name
    Returns:
        List[Dict[str, Any]]: List of segments with start, end, and state
    """
    first_name, last_name = selected_patient.split(' ')
    gender_str = get_patient_gender(project_db, selected_patient)
    gender = Gender.FEMALE if gender_str == 'female' else Gender.MALE
    
    # Get patient's hemoglobin and WBC tests
    patient_tests = project_db[
        (project_db['first_name'] == first_name) & 
        (project_db['last_name'] == last_name) & 
        (project_db['LOINC-NUM'].isin(['30313-1', '6690-2']))
    ].sort_values('measurement_datetime')

    patient_tests = patient_tests[patient_tests['Value'] != 'DELETED']

    if patient_tests.empty:
        return []
    
    # Get test validity periods
    validity = knowledge_db.get_test_validity_table()
    
    # Process the data to create state ranges
    wbc_data, hb_data = process_hematological_data(patient_tests, validity)
    
    # Generate hematological state timeline
    state_timeline = generate_patient_state_timeline(
        wbc_data,
        hb_data,
        knowledge_db.get_hematological_table(gender)
    )
    
    # Create time points
    hematological_time_points = []
    for start, end, state in state_timeline:
        if state is not None:
            hematological_time_points.append({'time': start, 'state': state})
            hematological_time_points.append({'time': end, 'state': state})
    
    # Convert to DataFrame and create segments
    df_hema = pd.DataFrame(hematological_time_points)
    segments = []
    for i in range(1, len(df_hema)):
        prev, curr = df_hema.iloc[i - 1], df_hema.iloc[i]
        if prev['state'] == curr['state']:
            segments.append({'start': prev['time'], 'end': curr['time'], 'state': prev['state']})
    
    return segments

def calculate_recommendation(project_db: pd.DataFrame, knowledge_db, full_name: str, dt: datetime) -> Optional[str]:
    """
    Calculate recommendation for a patient at a given datetime based on their states and grade.
    Args:
        project_db (pd.DataFrame): The project database
        knowledge_db: The knowledge database handler
        full_name (str): Patient's full name
        dt (datetime): The datetime to check
    Returns:
        Optional[str]: The recommendation string if found, None otherwise
    """
    # Get the grade
    grade = calculate_grade(project_db, knowledge_db, full_name, dt)
    if grade is None:
        return None
    
    gender_str = get_patient_gender(project_db, full_name)
    gender = Gender.FEMALE if gender_str == 'female' else Gender.MALE
    
    # Get hemoglobin and hematological states
    hb_segments = calculate_hemoglobin_states(project_db, knowledge_db, full_name)
    hema_segments = calculate_hematological_states(project_db, knowledge_db, full_name)
    
    # Find the relevant hemoglobin state for the given datetime
    hb_state = None
    for segment in hb_segments:
        if segment['start'] <= dt <= segment['end']:
            hb_state = segment['state']
            break
    
    # Find the relevant hematological state for the given datetime
    hema_state = None
    for segment in hema_segments:
        if segment['start'] <= dt <= segment['end']:
            hema_state = segment['state']
            break
    
    # If we don't have all required states, return None
    if hb_state is None or hema_state is None:
        return None
    
    # Get recommendations table for the patient's gender (using FEMALE for simplicity)
    recommendations = knowledge_db.recommendations[gender]
    
    # Find matching recommendation
    matching_rec = recommendations[
        (recommendations['Hemoglobinstate'] == hb_state) &
        (recommendations['Hematologicalstate'] == hema_state) &
        (recommendations['Systematic Toxicity'] == f'GRADE {grade.value}')
    ]
    
    if matching_rec.empty:
        return None
    
    return matching_rec.iloc[0]['Recommendation']
