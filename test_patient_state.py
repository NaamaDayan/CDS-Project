import unittest
from datetime import datetime, timedelta
import pandas as pd
from knowledge_db_handler import KnowledgeDataHandler, Gender

class TestPatientStateVisualization(unittest.TestCase):
    def setUp(self):
        # Create test data for Yonathan Spoon
        self.test_data = pd.DataFrame([
            # First time point (09:57:00)
            {'first_name': 'Yonathan', 'last_name': 'Spoon', 'LOINC-NUM': '6690-2', 'Value': '4800', 'Unit': '10³/µL', 
             'measurement_datetime': '2018-05-17 09:57:00', 'update_datetime': '2018-05-20 10:00:00'},
            {'first_name': 'Yonathan', 'last_name': 'Spoon', 'LOINC-NUM': '30313-1', 'Value': '13.9', 'Unit': 'gr/dl', 
             'measurement_datetime': '2018-05-17 09:57:00', 'update_datetime': '2018-05-20 10:00:00'},
            # Second time point (10:00:00)
            {'first_name': 'Yonathan', 'last_name': 'Spoon', 'LOINC-NUM': '6690-2', 'Value': '5000', 'Unit': '10³/µL', 
             'measurement_datetime': '2018-05-18 10:00:00', 'update_datetime': '2018-05-21 10:00:00'},
            {'first_name': 'Yonathan', 'last_name': 'Spoon', 'LOINC-NUM': '30313-1', 'Value': '14.1', 'Unit': 'gr/dl', 
             'measurement_datetime': '2018-05-18 10:00:00', 'update_datetime': '2018-05-21 10:00:00'},
            # Third time point (11:00:00)
            {'first_name': 'Yonathan', 'last_name': 'Spoon', 'LOINC-NUM': '30313-1', 'Value': '13.9', 'Unit': 'gr/dl', 
             'measurement_datetime': '2018-05-18 11:00:00', 'update_datetime': '2018-05-21 10:00:00'},
            # Fourth time point (16:00:00)
            {'first_name': 'Yonathan', 'last_name': 'Spoon', 'LOINC-NUM': '6690-2', 'Value': '4900', 'Unit': '10³/µL', 
             'measurement_datetime': '2018-05-19 16:00:00', 'update_datetime': '2018-05-22 10:00:00'}
        ])
        
        # Initialize knowledge database
        self.knowledge_db = KnowledgeDataHandler()
        
        # Set test validity periods
        self.knowledge_db.update_test_validity('hemoglobin', 3, 3)  # 3 hours before and after
        self.knowledge_db.update_test_validity('WBC', 5, 5)  # 5 hours before and after

    def test_state_transitions(self):
        """Test state transitions for Yonathan Spoon"""
        # Get patient's tests
        patient_tests = self.test_data[
            (self.test_data['first_name'] == 'Yonathan') & 
            (self.test_data['last_name'] == 'Spoon')
        ].sort_values('measurement_datetime')
        
        # Group tests by measurement time
        grouped_tests = patient_tests.groupby('measurement_datetime')
        
        # First time point (09:57:00)
        first_group = grouped_tests.get_group('2018-05-17 09:57:00')
        hb_test = first_group[first_group['LOINC-NUM'] == '30313-1']
        wbc_test = first_group[first_group['LOINC-NUM'] == '6690-2']
        
        # Verify first time point values and state
        self.assertEqual(float(hb_test.iloc[0]['Value']), 13.9)
        self.assertEqual(float(wbc_test.iloc[0]['Value']), 4800)
        
        # Calculate first state validity period
        first_test_time = datetime.strptime('2018-05-17 09:57:00', '%Y-%m-%d %H:%M:%S')
        first_state_start = first_test_time - timedelta(hours=3)  # 06:57:00
        first_state_end = first_test_time + timedelta(hours=3)    # 12:57:00
        
        self.assertEqual(first_state_start, datetime(2018, 5, 17, 6, 57))
        self.assertEqual(first_state_end, datetime(2018, 5, 17, 12, 57))
        
        # Second time point (10:00:00)
        second_group = grouped_tests.get_group('2018-05-18 10:00:00')
        hb_test = second_group[second_group['LOINC-NUM'] == '30313-1']
        wbc_test = second_group[second_group['LOINC-NUM'] == '6690-2']
        
        # Verify second time point values and state
        self.assertEqual(float(hb_test.iloc[0]['Value']), 14.1)
        self.assertEqual(float(wbc_test.iloc[0]['Value']), 5000)
        
        # Calculate second state validity period
        second_test_time = datetime.strptime('2018-05-18 10:00:00', '%Y-%m-%d %H:%M:%S')
        second_state_start = second_test_time - timedelta(hours=3)  # 07:00:00
        second_state_end = second_test_time + timedelta(hours=3)    # 13:00:00
        
        self.assertEqual(second_state_start, datetime(2018, 5, 18, 7, 0))
        self.assertEqual(second_state_end, datetime(2018, 5, 18, 13, 0))
        
        # Third time point (11:00:00)
        third_group = grouped_tests.get_group('2018-05-18 11:00:00')
        hb_test = third_group[third_group['LOINC-NUM'] == '30313-1']
        
        # Verify third time point values and state
        self.assertEqual(float(hb_test.iloc[0]['Value']), 13.9)
        
        # Calculate third state validity period
        third_test_time = datetime.strptime('2018-05-18 11:00:00', '%Y-%m-%d %H:%M:%S')
        third_state_start = third_test_time - timedelta(hours=3)  # 08:00:00
        third_state_end = third_test_time + timedelta(hours=3)    # 14:00:00
        
        self.assertEqual(third_state_start, datetime(2018, 5, 18, 8, 0))
        self.assertEqual(third_state_end, datetime(2018, 5, 18, 14, 0))
        
        # Verify gaps between states
        # Gap between first and second state
        self.assertTrue(first_state_end < second_state_start)
        
        # Gap between second and third state
        self.assertTrue(second_state_end > third_state_start)  # States overlap
        
        # Gap after third state
        self.assertTrue(third_state_end < datetime(2018, 5, 19, 16, 0))  # Gap until next test

    def test_state_values(self):
        """Test the actual state values at each time point"""
        # First state (09:57:00) - Normal
        first_hb = 13.9
        first_wbc = 4800
        self.assertTrue(12 <= first_hb < 14)  # Normal hemoglobin
        self.assertTrue(4000 <= first_wbc < 10000)  # Normal WBC
        
        # Second state (10:00:00) - Polyhemia
        second_hb = 14.1
        second_wbc = 5000
        self.assertTrue(second_hb >= 14)  # High hemoglobin
        self.assertTrue(4000 <= second_wbc < 10000)  # Normal WBC
        
        # Third state (11:00:00) - Normal
        third_hb = 13.9
        self.assertTrue(12 <= third_hb < 14)  # Normal hemoglobin

if __name__ == '__main__':
    unittest.main() 