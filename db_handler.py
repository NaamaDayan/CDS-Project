import pandas as pd
from datetime import datetime
from dateutil import parser


class DBHandler:
    def __init__(self, csv_path):
        """Initialize the database handler with the CSV file path."""
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)

        # Convert datetime columns to datetime objects
        self.df["measurement_datetime"] = pd.to_datetime(
            self.df["measurement_datetime"]
        )
        self.df["update_datetime"] = pd.to_datetime(self.df["update_datetime"])

        # Ensure LOINC-NAME column exists
        if "LOINC-NAME" not in self.df.columns:
            self.df["LOINC-NAME"] = None

    def retrieve_records(
        self,
        first_name,
        last_name,
        loinc_num,
        measurement_datetime=None,
        from_datetime=None,
        to_datetime=None,
    ):
        """
        Retrieve records based on the given criteria.
        Returns a copy of the filtered DataFrame.
        """
        # Create a copy of the dataframe
        filtered_df = self.df.copy()

        # Apply filters
        mask = (
            (filtered_df["first_name"] == first_name)
            & (filtered_df["last_name"] == last_name)
            & (filtered_df["LOINC-NUM"] == loinc_num)
        )

        if measurement_datetime:
            measurement_datetime_parsed = parser.parse(measurement_datetime)
            # Check if the input contains time information
            if (
                " " in measurement_datetime
                and ":" in measurement_datetime.split(" ")[1]
            ):
                # Full datetime provided, do exact comparison
                mask &= (
                    filtered_df["measurement_datetime"] == measurement_datetime_parsed
                )
            else:
                # Date only provided, compare only dates
                mask &= (
                    filtered_df["measurement_datetime"].dt.date
                    == measurement_datetime_parsed.date()
                )

        if from_datetime:
            from_datetime_parsed = parser.parse(from_datetime)
            # Check if the input contains time information
            if " " in from_datetime and ":" in from_datetime.split(" ")[1]:
                # Full datetime provided, do exact comparison
                mask &= filtered_df["update_datetime"] >= from_datetime_parsed
            else:
                # Date only provided, compare only dates
                mask &= (
                    filtered_df["update_datetime"].dt.date
                    >= from_datetime_parsed.date()
                )

        if to_datetime:
            to_datetime_parsed = parser.parse(to_datetime)
            # Check if the input contains time information
            if " " in to_datetime and ":" in to_datetime.split(" ")[1]:
                # Full datetime provided, do exact comparison
                mask &= filtered_df["update_datetime"] <= to_datetime_parsed
            else:
                # Date only provided, compare only dates
                mask &= (
                    filtered_df["update_datetime"].dt.date <= to_datetime_parsed.date()
                )

        return filtered_df[mask]

    def update_record(
        self,
        first_name,
        last_name,
        loinc_num,
        value,
        update_datetime,
        measurement_datetime,
    ):
        """
        Update a record with the given criteria.
        Returns (success, result, changed_records) tuple.
        """
        try:
            # Convert datetime strings to datetime objects
            update_datetime_parsed = parser.parse(update_datetime)
            measurement_datetime_parsed = parser.parse(measurement_datetime)

            # Find the record to update
            mask = (
                (self.df["first_name"] == first_name)
                & (self.df["last_name"] == last_name)
                & (self.df["LOINC-NUM"] == loinc_num)
            )

            # Check if measurement_datetime contains time information
            if (
                " " in measurement_datetime
                and ":" in measurement_datetime.split(" ")[1]
            ):
                # Full datetime provided, do exact comparison
                mask &= self.df["measurement_datetime"] == measurement_datetime_parsed
            else:
                # Date only provided, compare only dates
                mask &= (
                    self.df["measurement_datetime"].dt.date
                    == measurement_datetime_parsed.date()
                )

            if not any(mask):
                return False, "No matching record found", None

            # Get the most recent record based on update_datetime
            matching_records = self.df[mask]
            # Sort by update_datetime in descending order (most recent first) and take the first record
            most_recent_record = matching_records.sort_values(
                "update_datetime", ascending=False
            ).iloc[0]

            # Create a new record with the updated value
            new_record = most_recent_record.copy()
            new_record["Value"] = value
            new_record["update_datetime"] = update_datetime_parsed

            # Append the new record
            self.df = pd.concat(
                [self.df, pd.DataFrame([new_record])], ignore_index=True
            )

            # Save to CSV
            self.df.to_csv(self.csv_path, index=False)

            # Return the changed records (original and updated)
            changed_records = pd.DataFrame([most_recent_record, new_record])
            return True, "Record updated successfully", changed_records

        except Exception as e:
            return False, str(e), None

    def delete_record(
        self, first_name, last_name, loinc_num, measurement_datetime, update_datetime
    ):
        """
        Mark a record as deleted by creating a new record with 'DELETED' value.
        Returns (success, result, changed_records) tuple.
        """
        try:
            # Convert datetime strings to datetime objects
            update_datetime_parsed = parser.parse(update_datetime)
            measurement_datetime_parsed = parser.parse(measurement_datetime)

            # Find the record to delete
            mask = (
                (self.df["first_name"] == first_name)
                & (self.df["last_name"] == last_name)
                & (self.df["LOINC-NUM"] == loinc_num)
            )

            # Check if measurement_datetime contains time information
            if (
                " " in measurement_datetime
                and ":" in measurement_datetime.split(" ")[1]
            ):
                # Full datetime provided, do exact comparison
                mask &= self.df["measurement_datetime"] == measurement_datetime_parsed
            else:
                # Date only provided, compare only dates
                mask &= (
                    self.df["measurement_datetime"].dt.date
                    == measurement_datetime_parsed.date()
                )

            if not any(mask):
                return False, "No matching record found", None

            # Get the most recent record based on update_datetime
            matching_records = self.df[mask]
            # Sort by update_datetime in descending order (most recent first) and take the first record
            most_recent_record = matching_records.sort_values(
                "update_datetime", ascending=False
            ).iloc[0]

            # Create a new record with 'DELETED' value
            new_record = most_recent_record.copy()
            new_record["Value"] = "DELETED"
            new_record["update_datetime"] = update_datetime_parsed

            # Append the new record
            self.df = pd.concat(
                [self.df, pd.DataFrame([new_record])], ignore_index=True
            )

            # Save to CSV
            self.df.to_csv(self.csv_path, index=False)

            # Return the changed records (original and deleted)
            changed_records = pd.DataFrame([most_recent_record, new_record])
            return True, "Record deleted successfully", changed_records

        except Exception as e:
            return False, str(e), None
