import pandas as pd
import numpy as np
from enum import Enum
from datetime import timedelta, datetime

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"

class Grade(Enum):
    GRADE_1 = 1
    GRADE_2 = 2
    GRADE_3 = 3
    GRADE_4 = 4
    GRADE_5 = 5

class KnowledgeDataHandler:
    def __init__(self):
        # Initialize systemic table
        conditions = ['fever', 'chills', 'skin-look', 'allergic state']
        systemic_data = {
            'fever': ['0-38.5', '38.5-40.0', '40.0+', '40.0'],
            'chills': ['None', 'Shaking', 'Rigor', 'Rigor'],
            'skin-look': ['Erythema', 'Vesiculation', 'Desquamation', 'Exfoliation'],
            'allergic state': ['Edema', 'Bronchospasm', 'Sever-Bronchospasm', 'Anaphylactic-Shock']
        }
        self.systemic_table = pd.DataFrame(index=conditions, columns=[f'grade {i}' for i in range(1, 5)])
        for condition, values in systemic_data.items():
            for grade, value in enumerate(values, 1):
                self.systemic_table.loc[condition, f'grade {grade}'] = value
        
        # Initialize test validity table
        self.test_validity_table = pd.DataFrame([
            {'test_name': 'hemoglobin', 'good-before': 3, 'good-after': 3},
            {'test_name': 'WBC', 'good-before': 5, 'good-after': 5},
            {'test_name': 'fever', 'good-before': 3, 'good-after': 3},
            {'test_name': 'chills', 'good-before': 3, 'good-after': 3},
            {'test_name': 'skin-look', 'good-before': 3, 'good-after': 3},
            {'test_name': 'allergic state', 'good-before': 3, 'good-after': 3}
        ])
        
        # Initialize hemoglobin tables
        self.hemoglobin_tables = {
            Gender.MALE: pd.DataFrame([
                {'low_range': 0, 'high_range': 9, 'state': 'Severe Anemia'},
                {'low_range': 9, 'high_range': 11, 'state': 'Moderate Anemia'},
                {'low_range': 11, 'high_range': 13, 'state': 'Mild Anemia'},
                {'low_range': 13, 'high_range': 16, 'state': 'Normal Hemoglobin'},
                {'low_range': 16, 'high_range': np.inf, 'state': 'Polyhemia'}
            ]),
            Gender.FEMALE: pd.DataFrame([
                {'low_range': 0, 'high_range': 8, 'state': 'Severe Anemia'},
                {'low_range': 8, 'high_range': 10, 'state': 'Moderate Anemia'},
                {'low_range': 10, 'high_range': 12, 'state': 'Mild Anemia'},
                {'low_range': 12, 'high_range': 14, 'state': 'Normal Hemoglobin'},
                {'low_range': 14, 'high_range': np.inf, 'state': 'Polycytemia'}
            ])
        }
        
        # Initialize hematological tables
        wbc_intervals = pd.IntervalIndex.from_tuples([
            (0, 4000), 
            (4000, 10000), 
            (10000, np.inf)
        ], closed="left")

        # Female hematological table
        female_hb_intervals = pd.IntervalIndex.from_tuples([
            (0, 8), 
            (8, 10), 
            (10, 12), 
            (12, 14), 
            (14, np.inf)
        ], closed="left")
        
        female_hematological_data = [
            ['Pancytopenia', 'Pancytopenia', 'Pancytopenia', 'Leukopenia', 'Suspected Polycytemia Vera'],
            ['Anemia', 'Anemia', 'Anemia', 'Normal', 'Polyhemia'],
            ['Suspected Leukemia', 'Suspected Leukemia', 'Suspected Leukemia', 'Leukemoid reaction', 'Suspected Polycytemia Vera']
        ]
        self.hematological_tables = {
            Gender.FEMALE: pd.DataFrame(female_hematological_data, index=wbc_intervals, columns=female_hb_intervals)
        }
        self.hematological_tables[Gender.FEMALE].index.name = "WBC"
        self.hematological_tables[Gender.FEMALE].columns.name = "Hemoglobin"
        
        # Male hematological table
        male_hb_intervals = pd.IntervalIndex.from_tuples([
            (0, 9), 
            (9, 11), 
            (11, 13), 
            (13, 16), 
            (16, np.inf)
        ], closed="left")
        
        male_hematological_data = [
            ['Pancytopenia', 'Pancytopenia', 'Pancytopenia', 'Leukopenia', 'Suspected Polycytemia Vera'],
            ['Anemia', 'Anemia', 'Anemia', 'Normal', 'Polyhemia'],
            ['Suspected Leukemia', 'Suspected Leukemia', 'Suspected Leukemia', 'Leukemoid reaction', 'Suspected Polycytemia Vera']
        ]
        self.hematological_tables[Gender.MALE] = pd.DataFrame(male_hematological_data, index=wbc_intervals, columns=male_hb_intervals)
        self.hematological_tables[Gender.MALE].index.name = "WBC"
        self.hematological_tables[Gender.MALE].columns.name = "Hemoglobin"
        
        # Initialize recommendations tables
        self.recommendations = {
            Gender.MALE: pd.DataFrame([
                {'Hemoglobinstate': 'Severe Anemia', 'Hematologicalstate': 'Pancytopenia', 'Systematic Toxicity': 'GRADE 1', 'Recommendation': 'Measure BP once a week'},
                {'Hemoglobinstate': 'Moderate Anemia', 'Hematologicalstate': 'Anemia', 'Systematic Toxicity': 'GRADE 2', 'Recommendation': 'Measure BP every 3 days. Give aspirin 5g twice a week'},
                {'Hemoglobinstate': 'Mild Anemia', 'Hematologicalstate': 'Suspected Leukemia', 'Systematic Toxicity': 'GRADE 3', 'Recommendation': 'Measure BP every day, Give aspirin 15g every day. Diet consultation'},
                {'Hemoglobinstate': 'Normal Hemoglobin', 'Hematologicalstate': 'Leukemoid reaction', 'Systematic Toxicity': 'GRADE 4', 'Recommendation': 'Measure BP twice a day. Give aspirin 15g every day. Exercise consultation. Diet consultation'},
                {'Hemoglobinstate': 'Polyhemia', 'Hematologicalstate': 'Suspected Polycytemia Vera', 'Systematic Toxicity': 'GRADE 4', 'Recommendation': 'Measure BP every hour. Give 1 gr magnesium every hour. Exercise consultation. Call family'}
            ]),
            Gender.FEMALE: pd.DataFrame([
                {'Hemoglobinstate': 'Severe Anemia', 'Hematologicalstate': 'Pancytopenia', 'Systematic Toxicity': 'GRADE 1', 'Recommendation': 'Measure BP every 3 days'},
                {'Hemoglobinstate': 'Moderate Anemia', 'Hematologicalstate': 'Anemia', 'Systematic Toxicity': 'GRADE 2', 'Recommendation': 'Measure BP every 3 days and Give Celectone 2g twice a day for two days drug treatment'},
                {'Hemoglobinstate': 'Mild Anemia', 'Hematologicalstate': 'Suspected Leukemia', 'Systematic Toxicity': 'GRADE 3', 'Recommendation': 'Measure BP every day and Give 1 gr magnesium every 3 hours. Diet consultation'},
                {'Hemoglobinstate': 'Normal Hemoglobin', 'Hematologicalstate': 'Leukemoid reaction', 'Systematic Toxicity': 'GRADE 4', 'Recommendation': 'Measure BP twice a day, Give 1 gr magnesium every hour. Exercise consultation. Diet consultation'},
                {'Hemoglobinstate': 'Polyhemia', 'Hematologicalstate': 'Suspected Polycytemia Vera', 'Systematic Toxicity': 'GRADE 4', 'Recommendation': 'Measure BP every hour. Give 1 gr magnesium every hour. Exercise consultation. Call help'}
            ])
        }

        # Store initial states
        self._initial_states = {
            'hemoglobin': {
                Gender.FEMALE: self.hemoglobin_tables[Gender.FEMALE].copy(),
                Gender.MALE: self.hemoglobin_tables[Gender.MALE].copy()
            },
            'hematological': {
                Gender.FEMALE: self.hematological_tables[Gender.FEMALE].copy(),
                Gender.MALE: self.hematological_tables[Gender.MALE].copy()
            },
            'systemic': self.systemic_table.copy(),
            'recommendations': {
                Gender.FEMALE: self.recommendations[Gender.FEMALE].copy(),
                Gender.MALE: self.recommendations[Gender.MALE].copy()
            },
            'test_validity': self.test_validity_table.copy()
        }
    
    def update_systemic_grade(self, condition: str, grade: int, value: str):
        """Update a grade value in the systemic table"""
        if condition not in self.systemic_table.index:
            raise ValueError(f"Invalid condition: {condition}")
        if grade not in range(1, 5):
            raise ValueError(f"Invalid grade: {grade}")
        
        self.systemic_table.loc[condition, f'grade {grade}'] = value
    
    def get_hemoglobin_table(self, gender: Gender) -> pd.DataFrame:
        """Get the hemoglobin state table for a specific gender"""
        return self.hemoglobin_tables[gender]
    
    def get_hematological_table(self, gender: Gender) -> pd.DataFrame:
        """Get the hematological state table for a specific gender"""
        return self.hematological_tables[gender]
    
    def get_recommendations(self, gender: Gender) -> pd.DataFrame:
        """Get the recommendations table for a specific gender"""
        return self.recommendations[gender]
    
    def get_systemic_table(self) -> pd.DataFrame:
        """Get the shared systemic table"""
        return self.systemic_table

    def get_test_validity_table(self) -> pd.DataFrame:
        """Get the test validity table"""
        return self.test_validity_table

    def update_test_validity(self, test_name: str, good_before: int, good_after: int):
        """Update validity periods for a test"""
        if test_name not in self.test_validity_table['test_name'].values:
            raise ValueError(f"Invalid test name: {test_name}")
        
        self.test_validity_table.loc[self.test_validity_table['test_name'] == test_name, 'good-before'] = good_before
        self.test_validity_table.loc[self.test_validity_table['test_name'] == test_name, 'good-after'] = good_after

    def reset_table(self, table_type: str, gender: Gender = None):
        """Reset a table to its initial state"""
        if table_type == 'systemic':
            self.systemic_table = self._initial_states['systemic'].copy()
        elif table_type == 'test_validity':
            self.test_validity_table = self._initial_states['test_validity'].copy()
        elif gender is not None:
            if table_type == 'hemoglobin':
                self.hemoglobin_tables[gender] = self._initial_states['hemoglobin'][gender].copy()
            elif table_type == 'hematological':
                self.hematological_tables[gender] = self._initial_states['hematological'][gender].copy()
            elif table_type == 'recommendations':
                self.recommendations[gender] = self._initial_states['recommendations'][gender].copy()
        else:
            raise ValueError("Gender must be provided for gender-specific tables")
