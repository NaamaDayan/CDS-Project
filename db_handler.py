import pandas as pd
from datetime import datetime
from dateutil import parser

class DBHandler:
    def __init__(self, csv_path):
        """Initialize the database handler with the CSV file path."""
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        
        # Convert datetime columns to datetime objects
        self.df['measurement_datetime'] = pd.to_datetime(self.df['measurement_datetime'])
        self.df['update_datetime'] = pd.to_datetime(self.df['update_datetime'])
        
        # Ensure LOINC-NAME column exists
        if 'LOINC-NAME' not in self.df.columns:
            self.df['LOINC-NAME'] = None

    def retrieve_records(self, first_name, last_name, loinc_num, measurement_datetime=None,
                        from_datetime=None, to_datetime=None):
        """
        Retrieve records based on the given criteria.
        Returns a copy of the filtered DataFrame.
        """
        # Create a copy of the dataframe
        filtered_df = self.df.copy()
        
        # Apply filters
        mask = (
            (filtered_df['first_name'] == first_name) &
            (filtered_df['last_name'] == last_name) &
            (filtered_df['LOINC-NUM'] == loinc_num)
        )
        
        if measurement_datetime:
            measurement_datetime = parser.parse(measurement_datetime)
            mask &= (filtered_df['measurement_datetime'] == measurement_datetime)
        
        if from_datetime:
            from_datetime = parser.parse(from_datetime)
            mask &= (filtered_df['update_datetime'] >= from_datetime)
        
        if to_datetime:
            to_datetime = parser.parse(to_datetime)
            mask &= (filtered_df['update_datetime'] <= to_datetime)
        
        return filtered_df[mask]

    def update_record(self, first_name, last_name, loinc_num, value,
                     update_datetime, measurement_datetime):
        """
        Update a record with the given criteria.
        Returns (success, result) tuple.
        """
        try:
            # Convert datetime strings to datetime objects
            update_datetime = parser.parse(update_datetime)
            measurement_datetime = parser.parse(measurement_datetime)
            
            # Find the record to update
            mask = (
                (self.df['first_name'] == first_name) &
                (self.df['last_name'] == last_name) &
                (self.df['LOINC-NUM'] == loinc_num) &
                (self.df['measurement_datetime'] == measurement_datetime)
            )
            
            if not any(mask):
                return False, "No matching record found"
            
            # Create a new record with the updated value
            new_record = self.df[mask].iloc[0].copy()
            new_record['Value'] = value
            new_record['update_datetime'] = update_datetime
            
            # Append the new record
            self.df = pd.concat([self.df, pd.DataFrame([new_record])], ignore_index=True)
            
            # Save to CSV
            self.df.to_csv(self.csv_path, index=False)
            
            return True, None
            
        except Exception as e:
            return False, str(e)

    def delete_record(self, first_name, last_name, loinc_num,
                     measurement_datetime, update_datetime):
        """
        Mark a record as deleted by creating a new record with 'DELETED' value.
        Returns (success, result) tuple.
        """
        try:
            # Convert datetime strings to datetime objects
            update_datetime = parser.parse(update_datetime)
            measurement_datetime = parser.parse(measurement_datetime)
            
            # Find the record to delete
            mask = (
                (self.df['first_name'] == first_name) &
                (self.df['last_name'] == last_name) &
                (self.df['LOINC-NUM'] == loinc_num) &
                (self.df['measurement_datetime'] == measurement_datetime)
            )
            
            if not any(mask):
                return False, "No matching record found"
            
            # Create a new record with 'DELETED' value
            new_record = self.df[mask].iloc[0].copy()
            new_record['Value'] = 'DELETED'
            new_record['update_datetime'] = update_datetime
            
            # Append the new record
            self.df = pd.concat([self.df, pd.DataFrame([new_record])], ignore_index=True)
            
            # Save to CSV
            self.df.to_csv(self.csv_path, index=False)
            
            return True, None
            
        except Exception as e:
            return False, str(e) 