from datetime import datetime, timedelta

class HemoglobinStateRange:
    def __init__(self, current_datetime: datetime, value: float, hours_before: float, hours_after: float):
        self.current_datetime = current_datetime
        self.value = value
        self.hours_before = hours_before
        self.hours_after = hours_after
        self.start = current_datetime - timedelta(hours=float(hours_before))
        self.end = current_datetime + timedelta(hours=float(hours_after))

class WBCStateRange:
    def __init__(self, current_datetime: datetime, value: float, hours_before: float, hours_after: float):
        self.current_datetime = current_datetime
        self.value = value
        self.hours_before = hours_before
        self.hours_after = hours_after
        self.start = current_datetime - timedelta(hours=float(hours_before))
        self.end = current_datetime + timedelta(hours=float(hours_after))
