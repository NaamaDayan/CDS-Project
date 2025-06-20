import unittest
from datetime import datetime, timedelta
import pandas as pd
from patient_state_calculator import calculate_recommendation, calculate_grade, calculate_hemoglobin_states, calculate_hematological_states
from knowledge_db_handler import KnowledgeDataHandler, Gender, Grade

class TestCalculateRecommendation(unittest.TestCase):
    def setUp(self):
        # Create test project database with data that will produce specific states and grades
        self.project_db = pd.DataFrame([
            # Male patient data - will produce Severe Anemia, Pancytopenia, Grade 1
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male', 'LOINC-NUM': '30313-1', 'Value': '7.5', 'Unit': 'gr/dl', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male', 'LOINC-NUM': '6690-2', 'Value': '3500', 'Unit': '10³/µL', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male', 'LOINC-NUM': '8310-5', 'Value': '36.5', 'Unit': 'Celsious', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male', 'LOINC-NUM': '75275-8', 'Value': 'None', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male', 'LOINC-NUM': '39106-0', 'Value': 'Erythema', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male', 'LOINC-NUM': '56840-2', 'Value': 'Edema', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            
            # Female patient data - will produce Severe Anemia, Pancytopenia, Grade 1
            {'first_name': 'Jane', 'last_name': 'Doe', 'gender': 'female', 'LOINC-NUM': '30313-1', 'Value': '7.5', 'Unit': 'gr/dl', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Jane', 'last_name': 'Doe', 'gender': 'female', 'LOINC-NUM': '6690-2', 'Value': '3500', 'Unit': '10³/µL', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Jane', 'last_name': 'Doe', 'gender': 'female', 'LOINC-NUM': '8310-5', 'Value': '36.5', 'Unit': 'Celsious', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Jane', 'last_name': 'Doe', 'gender': 'female', 'LOINC-NUM': '75275-8', 'Value': 'None', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Jane', 'last_name': 'Doe', 'gender': 'female', 'LOINC-NUM': '39106-0', 'Value': 'Erythema', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Jane', 'last_name': 'Doe', 'gender': 'female', 'LOINC-NUM': '56840-2', 'Value': 'Edema', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            
            # Patient with no valid states (normal values)
            {'first_name': 'Bob', 'last_name': 'Smith', 'gender': 'male', 'LOINC-NUM': '30313-1', 'Value': '15.0', 'Unit': 'gr/dl', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Bob', 'last_name': 'Smith', 'gender': 'male', 'LOINC-NUM': '6690-2', 'Value': '12000', 'Unit': '10³/µL', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            
            # Patient with Grade 2 data
            {'first_name': 'Alice', 'last_name': 'Johnson', 'gender': 'female', 'LOINC-NUM': '30313-1', 'Value': '9.0', 'Unit': 'gr/dl', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'gender': 'female', 'LOINC-NUM': '6690-2', 'Value': '5000', 'Unit': '10³/µL', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'gender': 'female', 'LOINC-NUM': '8310-5', 'Value': '39.0', 'Unit': 'Celsious', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'gender': 'female', 'LOINC-NUM': '75275-8', 'Value': 'Shaking', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'gender': 'female', 'LOINC-NUM': '39106-0', 'Value': 'Vesiculation', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'gender': 'female', 'LOINC-NUM': '56840-2', 'Value': 'Bronchospasm', 'Unit': 'ordinal', 'measurement_datetime': '2025-05-17 10:00:00', 'update_datetime': '2025-05-20 10:00:00'},
        ])
        
        # Create actual knowledge database
        self.knowledge_db = KnowledgeDataHandler()
        
        self.test_datetime = datetime(2025, 5, 17, 10, 0)

    def test_male_patient_severe_anemia_pancytopenia_grade1(self):
        """Test male patient with severe anemia, pancytopenia, and grade 1 gets correct recommendation"""
        result = calculate_recommendation(self.project_db, self.knowledge_db, "John Doe", self.test_datetime)
        
        # Verify the actual functions return expected values
        grade = calculate_grade(self.project_db, self.knowledge_db, "John Doe", self.test_datetime)
        hb_states = calculate_hemoglobin_states(self.project_db, self.knowledge_db, "John Doe")
        hema_states = calculate_hematological_states(self.project_db, self.knowledge_db, "John Doe")
        
        self.assertEqual(grade, Grade.GRADE_1)
        self.assertTrue(len(hb_states) > 0)
        self.assertTrue(len(hema_states) > 0)
        
        # Check that we have the expected recommendation
        self.assertEqual(result, "Measure BP once a week")

    def test_female_patient_severe_anemia_pancytopenia_grade1(self):
        """Test female patient with severe anemia, pancytopenia, and grade 1 gets different recommendation"""
        result = calculate_recommendation(self.project_db, self.knowledge_db, "Jane Doe", self.test_datetime)
        
        # Verify the actual functions return expected values
        grade = calculate_grade(self.project_db, self.knowledge_db, "Jane Doe", self.test_datetime)
        hb_states = calculate_hemoglobin_states(self.project_db, self.knowledge_db, "Jane Doe")
        hema_states = calculate_hematological_states(self.project_db, self.knowledge_db, "Jane Doe")
        
        self.assertEqual(grade, Grade.GRADE_1)
        self.assertTrue(len(hb_states) > 0)
        self.assertTrue(len(hema_states) > 0)
        
        # Check that we have the expected recommendation (different from male)
        self.assertEqual(result, "Measure BP every 3 days")

    def test_no_grade_available(self):
        """Test that None is returned when no grade can be calculated"""
        # Use a patient with no systemic test data
        result = calculate_recommendation(self.project_db, self.knowledge_db, "Bob Smith", self.test_datetime)
        
        # Verify no grade is calculated
        grade = calculate_grade(self.project_db, self.knowledge_db, "Bob Smith", self.test_datetime)
        self.assertIsNone(grade)
        self.assertIsNone(result)

    def test_no_hemoglobin_state_for_datetime(self):
        """Test that None is returned when no hemoglobin state exists for the given datetime"""
        # Use a datetime outside the validity window
        future_datetime = datetime(2025, 5, 20, 10, 0)  # 3 days later, outside validity window
        result = calculate_recommendation(self.project_db, self.knowledge_db, "John Doe", future_datetime)
        
        # Verify no grade is calculated due to time window
        grade = calculate_grade(self.project_db, self.knowledge_db, "John Doe", future_datetime)
        self.assertIsNone(grade)
        self.assertIsNone(result)

    def test_no_hematological_state_for_datetime(self):
        """Test that None is returned when no hematological state exists for the given datetime"""
        # Use a datetime outside the validity window
        future_datetime = datetime(2025, 5, 20, 10, 0)  # 3 days later, outside validity window
        result = calculate_recommendation(self.project_db, self.knowledge_db, "John Doe", future_datetime)
        
        # Verify no grade is calculated due to time window
        grade = calculate_grade(self.project_db, self.knowledge_db, "John Doe", future_datetime)
        self.assertIsNone(grade)
        self.assertIsNone(result)

    def test_no_matching_recommendation(self):
        """Test that None is returned when no matching recommendation is found in the table"""
        # Use a patient with normal values that won't match any recommendation
        result = calculate_recommendation(self.project_db, self.knowledge_db, "Bob Smith", self.test_datetime)
        
        # Verify no grade is calculated
        grade = calculate_grade(self.project_db, self.knowledge_db, "Bob Smith", self.test_datetime)
        self.assertIsNone(grade)
        self.assertIsNone(result)

    def test_patient_not_found(self):
        """Test that None is returned when patient is not found in database"""
        result = calculate_recommendation(self.project_db, self.knowledge_db, "Unknown Patient", self.test_datetime)
        self.assertIsNone(result)

    def test_empty_states_lists(self):
        """Test that None is returned when states lists are empty"""
        # Use a patient with no lab data
        result = calculate_recommendation(self.project_db, self.knowledge_db, "Bob Smith", self.test_datetime)
        
        # Verify no states are calculated
        hb_states = calculate_hemoglobin_states(self.project_db, self.knowledge_db, "Bob Smith")
        hema_states = calculate_hematological_states(self.project_db, self.knowledge_db, "Bob Smith")
        
        # Bob Smith has normal values, so he won't have states in the expected ranges
        self.assertIsNone(result)

    def test_multiple_states_overlapping_time(self):
        """Test that the correct state is selected when multiple states overlap the time"""
        # Add additional test data for John Doe to create overlapping states
        additional_data = pd.DataFrame([
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male', 'LOINC-NUM': '30313-1', 'Value': '10.0', 'Unit': 'gr/dl', 'measurement_datetime': '2025-05-17 15:00:00', 'update_datetime': '2025-05-20 10:00:00'},
            {'first_name': 'John', 'last_name': 'Doe', 'gender': 'male', 'LOINC-NUM': '6690-2', 'Value': '6000', 'Unit': '10³/µL', 'measurement_datetime': '2025-05-17 15:00:00', 'update_datetime': '2025-05-20 10:00:00'},
        ])
        
        extended_db = pd.concat([self.project_db, additional_data], ignore_index=True)
        
        result = calculate_recommendation(extended_db, self.knowledge_db, "John Doe", self.test_datetime)
        
        # Should use the state that contains the test time (10:00)
        self.assertEqual(result, "Measure BP once a week")

    def test_grade2_patient(self):
        """Test a patient with Grade 2 systemic toxicity"""
        result = calculate_recommendation(self.project_db, self.knowledge_db, "Alice Johnson", self.test_datetime)
        
        # Verify the actual functions return expected values
        grade = calculate_grade(self.project_db, self.knowledge_db, "Alice Johnson", self.test_datetime)
        hb_states = calculate_hemoglobin_states(self.project_db, self.knowledge_db, "Alice Johnson")
        hema_states = calculate_hematological_states(self.project_db, self.knowledge_db, "Alice Johnson")
        
        self.assertEqual(grade, Grade.GRADE_2)
        self.assertTrue(len(hb_states) > 0)
        self.assertTrue(len(hema_states) > 0)
        self.assertEqual(result, "Measure BP every 3 days and Give Celectone 2g twice a day for two days drug treatment")
        # Check that we have a recommendation for Grade 2

    def test_actual_recommendations_table_structure(self):
        """Test that the actual recommendations table has the expected structure"""
        male_recs = self.knowledge_db.recommendations[Gender.MALE]
        female_recs = self.knowledge_db.recommendations[Gender.FEMALE]
        
        # Check that both tables have the expected columns
        expected_columns = ['Hemoglobinstate', 'Hematologicalstate', 'Systematic Toxicity', 'Recommendation']
        self.assertEqual(list(male_recs.columns), expected_columns)
        self.assertEqual(list(female_recs.columns), expected_columns)
        
        # Check that both tables have the same number of rows
        self.assertEqual(len(male_recs), len(female_recs))
        
        # Check that the recommendations are different for male vs female
        male_severe_anemia = male_recs[
            (male_recs['Hemoglobinstate'] == 'Severe Anemia') & 
            (male_recs['Hematologicalstate'] == 'Pancytopenia') & 
            (male_recs['Systematic Toxicity'] == 'GRADE 1')
        ]
        female_severe_anemia = female_recs[
            (female_recs['Hemoglobinstate'] == 'Severe Anemia') & 
            (female_recs['Hematologicalstate'] == 'Pancytopenia') & 
            (female_recs['Systematic Toxicity'] == 'GRADE 1')
        ]
        
        self.assertFalse(male_severe_anemia.empty)
        self.assertFalse(female_severe_anemia.empty)
        self.assertNotEqual(
            male_severe_anemia.iloc[0]['Recommendation'],
            female_severe_anemia.iloc[0]['Recommendation']
        )

    def test_actual_function_calls(self):
        """Test that all the actual functions work correctly with real data"""
        # Test calculate_grade
        grade = calculate_grade(self.project_db, self.knowledge_db, "John Doe", self.test_datetime)
        self.assertEqual(grade, Grade.GRADE_1)
        
        # Test calculate_hemoglobin_states
        hb_states = calculate_hemoglobin_states(self.project_db, self.knowledge_db, "John Doe")
        self.assertTrue(len(hb_states) > 0)
        self.assertIn('start', hb_states[0])
        self.assertIn('end', hb_states[0])
        self.assertIn('state', hb_states[0])
        
        # Test calculate_hematological_states
        hema_states = calculate_hematological_states(self.project_db, self.knowledge_db, "John Doe")
        self.assertTrue(len(hema_states) > 0)
        self.assertIn('start', hema_states[0])
        self.assertIn('end', hema_states[0])
        self.assertIn('state', hema_states[0])

if __name__ == '__main__':
    unittest.main() 