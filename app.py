import dash
from dash import html, dcc, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pandas as pd
from db_handler import DBHandler
from knowledge_db_handler import KnowledgeDataHandler, Gender
import plotly.express as px
import plotly.graph_objects as go
from typing import List
from models import WBCStateRange, HemoglobinStateRange
from patient_state_calculator import (
    generate_patient_state_timeline,
    generate_hemoglobin_state_timeline,
    calculate_hemoglobin_states,
    calculate_hematological_states,
    calculate_recommendation,
    calculate_grade,
)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
db_handler = DBHandler("project_db_with_names.csv")
knowledge_db = KnowledgeDataHandler()

# Read the project database
project_db = pd.read_csv("project_db_with_names.csv")

# Get unique patient names for dropdown
patient_names = project_db[["first_name", "last_name"]].drop_duplicates()
patient_names["full_name"] = (
    patient_names["first_name"] + " " + patient_names["last_name"]
)
patient_options = [
    {"label": name, "value": name} for name in patient_names["full_name"]
]


app.layout = dbc.Container(
    [
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Patient Database",
                    children=[
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="Retrieve",
                                    children=[
                                        html.H3("Retrieve Records"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("First Name"),
                                                        dbc.Input(
                                                            id="retrieve-first-name",
                                                            type="text",
                                                            placeholder="Enter first name",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Last Name"),
                                                        dbc.Input(
                                                            id="retrieve-last-name",
                                                            type="text",
                                                            placeholder="Enter last name",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("LOINC Number"),
                                                        dbc.Input(
                                                            id="retrieve-loinc",
                                                            type="text",
                                                            placeholder="Enter LOINC number",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Measurement Date"),
                                                        dcc.DatePickerSingle(
                                                            id="retrieve-measurement-date"
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Measurement Time (Optional)"
                                                        ),
                                                        dbc.Input(
                                                            id="retrieve-measurement-time",
                                                            type="text",
                                                            placeholder="HH:MM (e.g., 14:30)",
                                                            pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Update Date Range Start"
                                                        ),
                                                        dcc.DatePickerSingle(
                                                            id="retrieve-update-start-date"
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Start Time (Optional)"
                                                        ),
                                                        dbc.Input(
                                                            id="retrieve-update-start-time",
                                                            type="text",
                                                            placeholder="HH:MM (e.g., 14:30)",
                                                            pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Update Date Range End"
                                                        ),
                                                        dcc.DatePickerSingle(
                                                            id="retrieve-update-end-date"
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "End Time (Optional)"
                                                        ),
                                                        dbc.Input(
                                                            id="retrieve-update-end-time",
                                                            type="text",
                                                            placeholder="HH:MM (e.g., 14:30)",
                                                            pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                            ]
                                        ),
                                        dbc.Button(
                                            "Retrieve",
                                            id="retrieve-button",
                                            color="primary",
                                            className="mt-3",
                                        ),
                                        html.Div(id="retrieve-output"),
                                    ],
                                ),
                                dbc.Tab(
                                    label="Update",
                                    children=[
                                        html.H3("Update Record"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("First Name"),
                                                        dbc.Input(
                                                            id="update-first-name",
                                                            type="text",
                                                            placeholder="Enter first name",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Last Name"),
                                                        dbc.Input(
                                                            id="update-last-name",
                                                            type="text",
                                                            placeholder="Enter last name",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("LOINC Number"),
                                                        dbc.Input(
                                                            id="update-loinc",
                                                            type="text",
                                                            placeholder="Enter LOINC number",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("New Value"),
                                                        dbc.Input(
                                                            id="update-value",
                                                            type="text",
                                                            placeholder="Enter new value",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Update Date"),
                                                        dcc.DatePickerSingle(
                                                            id="update-datetime"
                                                        ),
                                                    ],
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Update Time (Optional)"
                                                        ),
                                                        dbc.Input(
                                                            id="update-time",
                                                            type="text",
                                                            placeholder="HH:MM (e.g., 14:30)",
                                                            pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                                        ),
                                                    ],
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Now",
                                                            id="update-now-button",
                                                            color="secondary",
                                                            size="sm",
                                                            className="mt-4",
                                                        ),
                                                    ],
                                                    width=1,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Measurement Date"),
                                                        dcc.DatePickerSingle(
                                                            id="update-measurement-datetime"
                                                        ),
                                                    ],
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Measurement Time (Optional)"
                                                        ),
                                                        dbc.Input(
                                                            id="update-measurement-time",
                                                            type="text",
                                                            placeholder="HH:MM (e.g., 14:30)",
                                                            pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                                        ),
                                                    ],
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Now",
                                                            id="update-measurement-now-button",
                                                            color="secondary",
                                                            size="sm",
                                                            className="mt-4",
                                                        ),
                                                    ],
                                                    width=1,
                                                ),
                                            ]
                                        ),
                                        dbc.Button(
                                            "Update",
                                            id="update-button",
                                            color="primary",
                                            className="mt-3",
                                        ),
                                        html.Div(id="update-output"),
                                    ],
                                ),
                                dbc.Tab(
                                    label="Delete",
                                    children=[
                                        html.H3("Delete Record"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("First Name"),
                                                        dbc.Input(
                                                            id="delete-first-name",
                                                            type="text",
                                                            placeholder="Enter first name",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Last Name"),
                                                        dbc.Input(
                                                            id="delete-last-name",
                                                            type="text",
                                                            placeholder="Enter last name",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("LOINC Number"),
                                                        dbc.Input(
                                                            id="delete-loinc",
                                                            type="text",
                                                            placeholder="Enter LOINC number",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Measurement Date"),
                                                        dcc.DatePickerSingle(
                                                            id="delete-measurement-datetime"
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Measurement Time (Optional)"
                                                        ),
                                                        dbc.Input(
                                                            id="delete-measurement-time",
                                                            type="text",
                                                            placeholder="HH:MM (e.g., 14:30)",
                                                            pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Update Date"),
                                                        dcc.DatePickerSingle(
                                                            id="delete-update-datetime"
                                                        ),
                                                    ],
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Update Time (Optional)"
                                                        ),
                                                        dbc.Input(
                                                            id="delete-update-time",
                                                            type="text",
                                                            placeholder="HH:MM (e.g., 14:30)",
                                                            pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                                        ),
                                                    ],
                                                    width=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Now",
                                                            id="delete-update-now-button",
                                                            color="secondary",
                                                            size="sm",
                                                            className="mt-4",
                                                        ),
                                                    ],
                                                    width=1,
                                                ),
                                            ]
                                        ),
                                        dbc.Button(
                                            "Delete",
                                            id="delete-button",
                                            color="primary",
                                            className="mt-3",
                                        ),
                                        html.Div(id="delete-output"),
                                    ],
                                ),
                            ]
                        ),
                    ],
                ),
                dbc.Tab(
                    label="Knowledge Database Management",
                    children=[
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="Hemoglobin States",
                                    children=[
                                        html.Div(
                                            [
                                                html.H4("Hemoglobin States"),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Select Gender"
                                                                ),
                                                                dcc.Dropdown(
                                                                    id="hem-gender",
                                                                    options=[
                                                                        {
                                                                            "label": "Female",
                                                                            "value": Gender.FEMALE.value,
                                                                        },
                                                                        {
                                                                            "label": "Male",
                                                                            "value": Gender.MALE.value,
                                                                        },
                                                                    ],
                                                                    value=Gender.FEMALE.value,
                                                                ),
                                                            ],
                                                            width=4,
                                                        )
                                                    ],
                                                    className="mb-3",
                                                ),
                                                html.Div(id="hem-table-container"),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "Add Row",
                                                                    id="hem-add-row-button",
                                                                    color="info",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Reset",
                                                                    id="hem-reset-button",
                                                                    color="warning",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Save Changes",
                                                                    id="hem-save-button",
                                                                    color="success",
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                    className="mt-3",
                                                ),
                                                html.Div(
                                                    id="hem-output", className="mt-3"
                                                ),
                                                html.Div(
                                                    id="hem-refresh-trigger",
                                                    style={"display": "none"},
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                                dbc.Tab(
                                    label="Hematological States",
                                    children=[
                                        html.Div(
                                            [
                                                html.H4("Hematological States"),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Select Gender"
                                                                ),
                                                                dcc.Dropdown(
                                                                    id="hemat-gender",
                                                                    options=[
                                                                        {
                                                                            "label": "Female",
                                                                            "value": Gender.FEMALE.value,
                                                                        },
                                                                        {
                                                                            "label": "Male",
                                                                            "value": Gender.MALE.value,
                                                                        },
                                                                    ],
                                                                    value=Gender.FEMALE.value,
                                                                ),
                                                            ],
                                                            width=4,
                                                        )
                                                    ],
                                                    className="mb-3",
                                                ),
                                                html.Div(id="hemat-table-container"),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "Add Row",
                                                                    id="hemat-add-row-button",
                                                                    color="info",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Reset",
                                                                    id="hemat-reset-button",
                                                                    color="warning",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Save Changes",
                                                                    id="hemat-save-button",
                                                                    color="success",
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                    className="mt-3",
                                                ),
                                                html.Div(
                                                    id="hemat-output", className="mt-3"
                                                ),
                                                html.Div(
                                                    id="hemat-refresh-trigger",
                                                    style={"display": "none"},
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                                dbc.Tab(
                                    label="Systemic Table",
                                    children=[
                                        html.Div(
                                            [
                                                html.H4("Systemic Table"),
                                                html.Div(id="sys-table-container"),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "Add Row",
                                                                    id="sys-add-row-button",
                                                                    color="info",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Reset",
                                                                    id="sys-reset-button",
                                                                    color="warning",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Save Changes",
                                                                    id="sys-save-button",
                                                                    color="success",
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                    className="mt-3",
                                                ),
                                                html.Div(
                                                    id="sys-output", className="mt-3"
                                                ),
                                                html.Div(
                                                    id="sys-refresh-trigger",
                                                    style={"display": "none"},
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                                dbc.Tab(
                                    label="Recommendations",
                                    children=[
                                        html.Div(
                                            [
                                                html.H4("Recommendations"),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Label(
                                                                    "Select Gender"
                                                                ),
                                                                dcc.Dropdown(
                                                                    id="rec-gender",
                                                                    options=[
                                                                        {
                                                                            "label": "Female",
                                                                            "value": Gender.FEMALE.value,
                                                                        },
                                                                        {
                                                                            "label": "Male",
                                                                            "value": Gender.MALE.value,
                                                                        },
                                                                    ],
                                                                    value=Gender.FEMALE.value,
                                                                ),
                                                            ],
                                                            width=4,
                                                        )
                                                    ],
                                                    className="mb-3",
                                                ),
                                                html.Div(id="rec-table-container"),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Button(
                                                                    "Add Row",
                                                                    id="rec-add-row-button",
                                                                    color="info",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Reset",
                                                                    id="rec-reset-button",
                                                                    color="warning",
                                                                    className="me-2",
                                                                ),
                                                                dbc.Button(
                                                                    "Save Changes",
                                                                    id="rec-save-button",
                                                                    color="success",
                                                                ),
                                                            ]
                                                        )
                                                    ],
                                                    className="mt-3",
                                                ),
                                                html.Div(
                                                    id="rec-output", className="mt-3"
                                                ),
                                                html.Div(
                                                    id="rec-refresh-trigger",
                                                    style={"display": "none"},
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                                dbc.Tab(
                                    label="Test Validity",
                                    children=[
                                        html.Div(
                                            [
                                                html.H3("Test Validity Periods"),
                                                html.Div(id="validity-table-container"),
                                                html.Div(
                                                    [
                                                        dbc.Button(
                                                            "Add Row",
                                                            id="validity-add-row-button",
                                                            color="info",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Reset",
                                                            id="validity-reset-button",
                                                            n_clicks=0,
                                                            color="warning",
                                                            className="me-2",
                                                        ),
                                                        dbc.Button(
                                                            "Save Changes",
                                                            id="validity-save-button",
                                                            n_clicks=0,
                                                            color="success",
                                                        ),
                                                    ],
                                                    className="mt-3",
                                                ),
                                                html.Div(
                                                    id="validity-output",
                                                    className="mt-3",
                                                ),
                                                html.Div(
                                                    id="validity-refresh-trigger",
                                                    style={"display": "none"},
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                            ]
                        ),
                    ],
                ),
                dbc.Tab(
                    label="DSS",
                    children=[
                        html.Div(
                            [
                                html.H3("Patient State Analysis"),
                                html.Div(
                                    [
                                        # Patient selection and datetime picker in a row
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label("Select Patient:"),
                                                        dcc.Dropdown(
                                                            id="patient-selector",
                                                            options=patient_options,
                                                            placeholder="Select a patient...",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Select Date and Time (Optional):"
                                                        ),
                                                        dcc.DatePickerSingle(
                                                            id="date-picker",
                                                            placeholder="Select a date...",
                                                            clearable=True,
                                                        ),
                                                        dcc.Input(
                                                            id="time-picker",
                                                            type="text",
                                                            placeholder="Select time...",
                                                            style={
                                                                "marginLeft": "10px"
                                                            },
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                        # Recommendation display
                                        html.Div(
                                            id="recommendation-display",
                                            style={
                                                "marginTop": "20px",
                                                "marginBottom": "20px",
                                            },
                                        ),
                                        html.Hr(),
                                        html.H4("Hemoglobin State Analysis"),
                                        dcc.Graph(id="patient-state-graph"),
                                        html.Hr(),
                                        html.H4("Hematological State Analysis"),
                                        dcc.Graph(id="hematological-state-graph"),
                                    ]
                                ),
                            ]
                        )
                    ],
                ),
                dbc.Tab(
                    label="Overview",
                    children=[
                        html.Div(
                            [
                                html.H3("Patient Overview"),
                                html.Div(
                                    [
                                        # Datetime picker
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Select Date and Time:"
                                                        ),
                                                        dcc.DatePickerSingle(
                                                            id="overview-date-picker",
                                                            placeholder="Select a date...",
                                                            clearable=True,
                                                        ),
                                                        dcc.Input(
                                                            id="overview-time-picker",
                                                            type="text",
                                                            placeholder="Select time (HH:MM)...",
                                                            value="10:00",
                                                            style={
                                                                "marginLeft": "10px"
                                                            },
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ],
                                            className="mb-4",
                                        ),
                                        # Patient cards grid
                                        html.Div(id="overview-cards-container"),
                                    ]
                                ),
                            ]
                        )
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)


# Patient Database Callbacks
@app.callback(
    Output("retrieve-output", "children"),
    [Input("retrieve-button", "n_clicks")],
    [
        State("retrieve-first-name", "value"),
        State("retrieve-last-name", "value"),
        State("retrieve-loinc", "value"),
        State("retrieve-measurement-date", "date"),
        State("retrieve-measurement-time", "value"),
        State("retrieve-update-start-date", "date"),
        State("retrieve-update-start-time", "value"),
        State("retrieve-update-end-date", "date"),
        State("retrieve-update-end-time", "value"),
    ],
)
def retrieve_records(
    n_clicks,
    first_name,
    last_name,
    loinc,
    measurement_date,
    measurement_time,
    start_date,
    start_time,
    end_date,
    end_time,
):
    if n_clicks is None:
        return ""

    try:
        # Combine dates with times if provided
        measurement_datetime = None
        if measurement_date and measurement_time:
            measurement_datetime = f"{measurement_date} {measurement_time}"
        elif measurement_date:
            measurement_datetime = measurement_date

        start_datetime = None
        if start_date and start_time:
            start_datetime = f"{start_date} {start_time}"
        elif start_date:
            start_datetime = start_date

        end_datetime = None
        if end_date and end_time:
            end_datetime = f"{end_date} {end_time}"
        elif end_date:
            end_datetime = end_date

        records = db_handler.retrieve_records(
            first_name,
            last_name,
            loinc,
            measurement_datetime,
            start_datetime,
            end_datetime,
        )
        if records.empty:
            return "No records found."

        return dash_table.DataTable(
            data=records.to_dict("records"),
            columns=[{"name": i, "id": i} for i in records.columns],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "10px"},
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
        )
    except Exception as e:
        return f"Error: {str(e)}"


@app.callback(
    Output("update-output", "children"),
    [Input("update-button", "n_clicks")],
    [
        State("update-first-name", "value"),
        State("update-last-name", "value"),
        State("update-loinc", "value"),
        State("update-value", "value"),
        State("update-datetime", "date"),
        State("update-time", "value"),
        State("update-measurement-datetime", "date"),
        State("update-measurement-time", "value"),
    ],
)
def update_record(
    n_clicks,
    first_name,
    last_name,
    loinc,
    value,
    update_datetime,
    update_time,
    measurement_datetime,
    measurement_time,
):
    if n_clicks is None:
        return ""

    try:
        # Combine dates with times if provided
        update_datetime_combined = None
        if update_datetime and update_time:
            update_datetime_combined = f"{update_datetime} {update_time}"
        elif update_datetime:
            update_datetime_combined = update_datetime

        measurement_datetime_combined = None
        if measurement_datetime and measurement_time:
            measurement_datetime_combined = f"{measurement_datetime} {measurement_time}"
        elif measurement_datetime:
            measurement_datetime_combined = measurement_datetime

        success, message, changed_records = db_handler.update_record(
            first_name,
            last_name,
            loinc,
            value,
            update_datetime_combined,
            measurement_datetime_combined,
        )

        if success:
            # Create the result message
            result = [html.H4("✅ " + message)]

            # Add the changed records table if available
            if changed_records is not None and not changed_records.empty:
                result.append(html.H5("Changed Records:"))
                result.append(
                    dash_table.DataTable(
                        data=changed_records.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in changed_records.columns],
                        style_table={"overflowX": "auto"},
                        style_cell={"textAlign": "left", "padding": "10px"},
                        style_header={
                            "backgroundColor": "rgb(230, 230, 230)",
                            "fontWeight": "bold",
                        },
                    )
                )
            return result
        else:
            return f"❌ {message}"
    except Exception as e:
        return f"Error: {str(e)}"


@app.callback(
    Output("delete-output", "children"),
    [Input("delete-button", "n_clicks")],
    [
        State("delete-first-name", "value"),
        State("delete-last-name", "value"),
        State("delete-loinc", "value"),
        State("delete-measurement-datetime", "date"),
        State("delete-measurement-time", "value"),
        State("delete-update-datetime", "date"),
        State("delete-update-time", "value"),
    ],
)
def delete_record(
    n_clicks,
    first_name,
    last_name,
    loinc,
    measurement_datetime,
    measurement_time,
    update_datetime,
    update_time,
):
    if n_clicks is None:
        return ""

    try:
        # Combine dates with times if provided
        measurement_datetime_combined = None
        if measurement_datetime and measurement_time:
            measurement_datetime_combined = f"{measurement_datetime} {measurement_time}"
        elif measurement_datetime:
            measurement_datetime_combined = measurement_datetime

        update_datetime_combined = None
        if update_datetime and update_time:
            update_datetime_combined = f"{update_datetime} {update_time}"
        elif update_datetime:
            update_datetime_combined = update_datetime

        success, message, changed_records = db_handler.delete_record(
            first_name,
            last_name,
            loinc,
            measurement_datetime_combined,
            update_datetime_combined,
        )

        if success:
            # Create the result message
            result = [html.H4("✅ " + message)]

            # Add the changed records table if available
            if changed_records is not None and not changed_records.empty:
                result.append(html.H5("Changed Records:"))
                result.append(
                    dash_table.DataTable(
                        data=changed_records.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in changed_records.columns],
                        style_table={"overflowX": "auto"},
                        style_cell={"textAlign": "left", "padding": "10px"},
                        style_header={
                            "backgroundColor": "rgb(230, 230, 230)",
                            "fontWeight": "bold",
                        },
                    )
                )
            return result
        else:
            return f"❌ {message}"
    except Exception as e:
        return f"Error: {str(e)}"


# Knowledge Database Callbacks
@app.callback(
    Output("hem-table-container", "children"),
    [Input("hem-gender", "value"), Input("hem-refresh-trigger", "children")],
)
def update_hem_table(gender, refresh_trigger):
    if not gender:
        return "Please select a gender"

    df = knowledge_db.get_hemoglobin_table(Gender(gender))
    return dash_table.DataTable(
        id="hem-table",
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        editable=True,
        row_deletable=True,
    )


@app.callback(
    Output("hemat-table-container", "children"),
    [Input("hemat-gender", "value"), Input("hemat-refresh-trigger", "children")],
)
def update_hemat_table(gender, refresh_trigger):
    if not gender:
        return "Please select a gender"

    df = knowledge_db.get_hematological_table(Gender(gender))

    # Convert interval indices to strings for JSON serialization
    data = []
    for idx, row in df.iterrows():
        row_dict = {}
        # Add row interval information (WBC ranges)
        row_str = (
            f"WBC {idx.left}-{idx.right}"
            if idx.right != float("inf")
            else f"WBC {idx.left}+"
        )
        row_dict["WBC Range"] = row_str
        # Add column data (Hemoglobin ranges)
        for col in df.columns:
            col_str = (
                f"{col.left}-{col.right}"
                if col.right != float("inf")
                else f"{col.left}+"
            )
            row_dict[col_str] = row[col]
        data.append(row_dict)

    # Create columns with string representations of intervals
    columns = [{"name": "WBC Range", "id": "WBC Range"}]  # Add row header column
    for col in df.columns:
        col_str = (
            f"{col.left}-{col.right}" if col.right != float("inf") else f"{col.left}+"
        )
        hb_range = f"Hb {col_str}"
        columns.append({"name": hb_range, "id": col_str})

    return dash_table.DataTable(
        id="hemat-table", data=data, columns=columns, editable=True, row_deletable=True
    )


@app.callback(
    Output("sys-table-container", "children"),
    [Input("sys-reset-button", "n_clicks"), Input("sys-refresh-trigger", "children")],
)
def update_sys_table(n_clicks, refresh_trigger):
    df = knowledge_db.get_systemic_table()
    # Reset index to include condition names as a column
    df = df.reset_index()
    df = df.rename(columns={"index": "Condition"})
    return dash_table.DataTable(
        id="sys-table",
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        editable=True,
        row_deletable=True,
    )


@app.callback(
    Output("rec-table-container", "children"),
    [Input("rec-gender", "value"), Input("rec-refresh-trigger", "children")],
)
def update_rec_table(gender, refresh_trigger):
    if not gender:
        return "Please select a gender"

    df = knowledge_db.get_recommendations(Gender(gender))
    return dash_table.DataTable(
        id="rec-table",
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        editable=True,
        row_deletable=True,
    )


@app.callback(
    Output("validity-table-container", "children"),
    [Input("validity-refresh-trigger", "children")],
)
def update_validity_table(refresh_trigger):
    df = knowledge_db.get_test_validity_table()
    return dash_table.DataTable(
        id="validity-table",
        columns=[
            {"name": "Test Name", "id": "test_name"},
            {"name": "Good Before (hours)", "id": "good-before"},
            {"name": "Good After (hours)", "id": "good-after"},
        ],
        data=df.to_dict("records"),
        editable=True,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
    )


# Save and Reset callbacks for each table
@app.callback(
    [Output("hem-output", "children"), Output("hem-refresh-trigger", "children")],
    [
        Input("hem-save-button", "n_clicks"),
        Input("hem-reset-button", "n_clicks"),
        Input("hem-add-row-button", "n_clicks"),
    ],
    [State("hem-gender", "value"), State("hem-table-container", "children")],
)
def handle_hem_changes(save_clicks, reset_clicks, add_clicks, gender, table_container):
    if not gender:
        return "Please select a gender", ""

    ctx = dash.callback_context
    if not ctx.triggered:
        return "", ""

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "hem-add-row-button":
        try:
            # Get current data from the table
            if (
                table_container
                and isinstance(table_container, dict)
                and "props" in table_container
            ):
                current_data = table_container["props"]["data"]
            else:
                current_data = []

            # Create a new empty row
            new_row = {}
            if current_data:
                # Get column names from existing data
                columns = list(current_data[0].keys())
                for col in columns:
                    new_row[col] = ""
            else:
                # Default columns for hemoglobin states
                new_row = {"state": "", "low_range": "", "high_range": ""}

            # Add the new row
            current_data.append(new_row)

            # Update the knowledge database with the new data
            df = pd.DataFrame(current_data)
            knowledge_db.hemoglobin_tables[Gender(gender)] = df

            return "Row added successfully", "refresh"
        except Exception as e:
            return f"Error adding row: {str(e)}", ""

    if button_id == "hem-reset-button":
        # Reset to initial state
        knowledge_db.reset_table("hemoglobin", Gender(gender))
        return "Table reset to initial state", "refresh"

    if button_id == "hem-save-button":
        try:
            if isinstance(table_container, dict) and "props" in table_container:
                table_data = table_container["props"]["data"]
                df = pd.DataFrame(table_data)
                knowledge_db.hemoglobin_tables[Gender(gender)] = df

                # Save to CSV file
                success, message = knowledge_db.save_all_data()
                if success:
                    return (
                        "Changes saved successfully to memory and CSV files",
                        "refresh",
                    )
                else:
                    return (
                        f"Changes saved to memory but CSV save failed: {message}",
                        "refresh",
                    )
            return "No data to save", ""
        except Exception as e:
            return f"Error saving changes: {str(e)}", ""


@app.callback(
    [Output("hemat-output", "children"), Output("hemat-refresh-trigger", "children")],
    [
        Input("hemat-save-button", "n_clicks"),
        Input("hemat-reset-button", "n_clicks"),
        Input("hemat-add-row-button", "n_clicks"),
    ],
    [State("hemat-gender", "value"), State("hemat-table-container", "children")],
)
def handle_hemat_changes(
    save_clicks, reset_clicks, add_clicks, gender, table_container
):
    if not gender:
        return "Please select a gender", ""

    ctx = dash.callback_context
    if not ctx.triggered:
        return "", ""

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "hemat-add-row-button":
        try:
            # Get current data from the table
            if (
                table_container
                and isinstance(table_container, dict)
                and "props" in table_container
            ):
                current_data = table_container["props"]["data"]
            else:
                current_data = []

            # Create a new empty row
            new_row = {}
            if current_data:
                # Get column names from existing data
                columns = list(current_data[0].keys())
                for col in columns:
                    new_row[col] = ""
            else:
                # Default columns for hematological states
                new_row = {"state": "", "low_range": "", "high_range": ""}

            # Add the new row
            current_data.append(new_row)

            # Update the knowledge database with the new data
            df = pd.DataFrame(current_data)
            knowledge_db.hematological_tables[Gender(gender)] = df

            return "Row added successfully", "refresh"
        except Exception as e:
            return f"Error adding row: {str(e)}", ""

    if button_id == "hemat-reset-button":
        # Reset to initial state
        knowledge_db.reset_table("hematological", Gender(gender))
        return "Table reset to initial state", "refresh"

    if button_id == "hemat-save-button":
        try:
            if isinstance(table_container, dict) and "props" in table_container:
                table_data = table_container["props"]["data"]
                df = pd.DataFrame(table_data)

                # Convert string ranges back to intervals
                new_df = pd.DataFrame(index=df.index)
                for col in df.columns:
                    if "+" in col:
                        low = float(col.replace("+", ""))
                        high = float("inf")
                    else:
                        low, high = map(float, col.split("-"))
                    new_df[pd.Interval(low, high, closed="left")] = df[col]

                knowledge_db.hematological_tables[Gender(gender)] = new_df

                # Save to CSV file
                success, message = knowledge_db.save_all_data()
                if success:
                    return (
                        "Changes saved successfully to memory and CSV files",
                        "refresh",
                    )
                else:
                    return (
                        f"Changes saved to memory but CSV save failed: {message}",
                        "refresh",
                    )
            return "No data to save", ""
        except Exception as e:
            return f"Error saving changes: {str(e)}", ""


@app.callback(
    [Output("sys-output", "children"), Output("sys-refresh-trigger", "children")],
    [
        Input("sys-save-button", "n_clicks"),
        Input("sys-reset-button", "n_clicks"),
        Input("sys-add-row-button", "n_clicks"),
    ],
    [State("sys-table-container", "children")],
)
def handle_sys_changes(save_clicks, reset_clicks, add_clicks, table_container):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "", ""

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "sys-add-row-button":
        try:
            # Get current data from the table
            if (
                table_container
                and isinstance(table_container, dict)
                and "props" in table_container
            ):
                current_data = table_container["props"]["data"]
            else:
                current_data = []

            # Create a new empty row
            new_row = {}
            if current_data:
                # Get column names from existing data
                columns = list(current_data[0].keys())
                for col in columns:
                    new_row[col] = ""
            else:
                # Default columns for systemic table
                new_row = {"test_name": "", "good-before": "", "good-after": ""}

            # Add the new row
            current_data.append(new_row)

            # Update the knowledge database with the new data
            df = pd.DataFrame(current_data)
            knowledge_db.systemic_table = df

            return "Row added successfully", "refresh"
        except Exception as e:
            return f"Error adding row: {str(e)}", ""

    if button_id == "sys-reset-button":
        # Reset to initial state
        knowledge_db.reset_table("systemic")
        return "Table reset to initial state", "refresh"

    if button_id == "sys-save-button":
        try:
            if isinstance(table_container, dict) and "props" in table_container:
                table_data = table_container["props"]["data"]
                df = pd.DataFrame(table_data)
                # Set the condition column as index
                df = df.set_index("Condition")
                knowledge_db.systemic_table = df

                # Save to CSV file
                success, message = knowledge_db.save_all_data()
                if success:
                    return (
                        "Changes saved successfully to memory and CSV files",
                        "refresh",
                    )
                else:
                    return (
                        f"Changes saved to memory but CSV save failed: {message}",
                        "refresh",
                    )
            return "No data to save", ""
        except Exception as e:
            return f"Error saving changes: {str(e)}", ""


@app.callback(
    [Output("rec-output", "children"), Output("rec-refresh-trigger", "children")],
    [
        Input("rec-save-button", "n_clicks"),
        Input("rec-reset-button", "n_clicks"),
        Input("rec-add-row-button", "n_clicks"),
    ],
    [State("rec-gender", "value"), State("rec-table-container", "children")],
)
def handle_rec_changes(save_clicks, reset_clicks, add_clicks, gender, table_container):
    if not gender:
        return "Please select a gender", ""

    ctx = dash.callback_context
    if not ctx.triggered:
        return "", ""

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "rec-add-row-button":
        try:
            # Get current data from the table
            if (
                table_container
                and isinstance(table_container, dict)
                and "props" in table_container
            ):
                current_data = table_container["props"]["data"]
            else:
                current_data = []

            # Create a new empty row
            new_row = {}
            if current_data:
                # Get column names from existing data
                columns = list(current_data[0].keys())
                for col in columns:
                    new_row[col] = ""
            else:
                # Default columns for recommendations
                new_row = {"state": "", "recommendation": "", "color": ""}

            # Add the new row
            current_data.append(new_row)

            # Update the knowledge database with the new data
            df = pd.DataFrame(current_data)
            knowledge_db.recommendations[Gender(gender)] = df

            return "Row added successfully", "refresh"
        except Exception as e:
            return f"Error adding row: {str(e)}", ""

    if button_id == "rec-reset-button":
        # Reset to initial state
        knowledge_db.reset_table("recommendations", Gender(gender))
        return "Table reset to initial state", "refresh"

    if button_id == "rec-save-button":
        try:
            if isinstance(table_container, dict) and "props" in table_container:
                table_data = table_container["props"]["data"]
                df = pd.DataFrame(table_data)
                knowledge_db.recommendations[Gender(gender)] = df

                # Save to CSV file
                success, message = knowledge_db.save_all_data()
                if success:
                    return (
                        "Changes saved successfully to memory and CSV files",
                        "refresh",
                    )
                else:
                    return (
                        f"Changes saved to memory but CSV save failed: {message}",
                        "refresh",
                    )
            return "No data to save", ""
        except Exception as e:
            return f"Error saving changes: {str(e)}", ""


@app.callback(
    [
        Output("validity-output", "children"),
        Output("validity-refresh-trigger", "children"),
    ],
    [
        Input("validity-save-button", "n_clicks"),
        Input("validity-reset-button", "n_clicks"),
        Input("validity-add-row-button", "n_clicks"),
    ],
    [State("validity-table-container", "children")],
)
def handle_validity_changes(save_clicks, reset_clicks, add_clicks, table_container):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "", ""

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "validity-add-row-button":
        try:
            # Get current data from the table
            if (
                table_container
                and isinstance(table_container, dict)
                and "props" in table_container
            ):
                current_data = table_container["props"]["data"]
            else:
                current_data = []

            # Create a new empty row
            new_row = {}
            if current_data:
                # Get column names from existing data
                columns = list(current_data[0].keys())
                for col in columns:
                    new_row[col] = ""
            else:
                # Default columns for test validity
                new_row = {"test_name": "", "good-before": "", "good-after": ""}

            # Add the new row
            current_data.append(new_row)

            # Update the knowledge database with the new data
            df = pd.DataFrame(current_data)
            knowledge_db.test_validity_table = df

            return "Row added successfully", "refresh"
        except Exception as e:
            return f"Error adding row: {str(e)}", ""

    if button_id == "validity-reset-button":
        # Reset to initial state
        knowledge_db.reset_table("test_validity")
        return "Table reset to initial state", "refresh"

    if button_id == "validity-save-button":
        try:
            if isinstance(table_container, dict) and "props" in table_container:
                table_data = table_container["props"]["data"]
                if table_data:
                    df = pd.DataFrame(table_data)

                    # Update each test's validity periods
                    for _, row in df.iterrows():
                        knowledge_db.update_test_validity(
                            row["test_name"],
                            int(row["good-before"]),
                            int(row["good-after"]),
                        )

                    # Save to CSV file
                    success, message = knowledge_db.save_all_data()
                    if success:
                        return (
                            "Changes saved successfully to memory and CSV files",
                            "refresh",
                        )
                    else:
                        return (
                            f"Changes saved to memory but CSV save failed: {message}",
                            "refresh",
                        )
            return "No data to save", ""
        except Exception as e:
            return f"Error saving changes: {str(e)}", ""


@app.callback(
    [
        Output("patient-state-graph", "figure"),
        Output("hematological-state-graph", "figure"),
    ],
    Input("patient-selector", "value"),
)
def update_patient_state_graph(selected_patient):
    if not selected_patient:
        return go.Figure(), go.Figure()  # Return empty figures if no patient selected

    # Calculate states using the new functions
    hb_segments = calculate_hemoglobin_states(
        project_db, knowledge_db, selected_patient
    )
    hema_segments = calculate_hematological_states(
        project_db, knowledge_db, selected_patient
    )

    # --- HEMOGLOBIN STATE GRAPH ---
    fig1 = go.Figure()
    if hb_segments:
        unique_states_hb = set(seg["state"] for seg in hb_segments)
        color_map_hb = {
            state: color
            for state, color in zip(unique_states_hb, px.colors.qualitative.Set2)
        }

        for seg in hb_segments:
            fig1.add_trace(
                go.Scatter(
                    x=[seg["start"], seg["end"]],
                    y=[seg["state"], seg["state"]],
                    mode="lines",
                    line=dict(width=10, color=color_map_hb.get(seg["state"], "gray")),
                    name=seg["state"],
                    showlegend=False,
                )
            )

    fig1.update_layout(
        title=f"Hemoglobin State Transitions for {selected_patient}",
        xaxis_title="Time",
        yaxis_title="State",
        xaxis=dict(showgrid=True),
        yaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=[
                "Severe Anemia",
                "Moderate Anemia",
                "Mild Anemia",
                "Normal Hemoglobin",
                "Polycytemia",
            ],
        ),
        height=400,
    )

    # --- HEMATOLOGICAL STATE GRAPH ---
    fig2 = go.Figure()
    if hema_segments:
        unique_states_hema = set(seg["state"] for seg in hema_segments)
        color_map_hema = {
            state: color
            for state, color in zip(unique_states_hema, px.colors.qualitative.Set2)
        }

        for seg in hema_segments:
            fig2.add_trace(
                go.Scatter(
                    x=[seg["start"], seg["end"]],
                    y=[seg["state"], seg["state"]],
                    mode="lines",
                    line=dict(width=10, color=color_map_hema.get(seg["state"], "gray")),
                    name=seg["state"],
                    showlegend=False,
                )
            )

    fig2.update_layout(
        title=f"Hematological State Transitions for {selected_patient}",
        xaxis_title="Time",
        yaxis_title="State",
        xaxis=dict(showgrid=True),
        yaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=[
                "Pancytopenia",
                "Anemia",
                "Suspected Leukemia",
                "Leukemoid reaction",
                "Suspected Polycytemia Vera",
            ],
        ),
        height=400,
    )

    return fig1, fig2


@app.callback(
    Output("recommendation-display", "children"),
    [
        Input("patient-selector", "value"),
        Input("date-picker", "date"),
        Input("time-picker", "value"),
    ],
)
def update_recommendation(selected_patient, selected_date, selected_time):
    if not selected_patient or not selected_date or not selected_time:
        return None

    try:
        # Combine date and time into a datetime object
        dt = datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M")

        # Calculate recommendation
        recommendation = calculate_recommendation(
            project_db, knowledge_db, selected_patient, dt
        )

        if recommendation:
            return html.Div(
                [
                    html.H4("Recommendation:"),
                    html.P(recommendation, style={"fontSize": "16px", "color": "blue"}),
                ]
            )
        else:
            return html.Div(
                [
                    html.H4("No Recommendation Available"),
                    html.P(
                        "No recommendation could be generated for the selected date and time.",
                        style={"fontSize": "16px", "color": "gray"},
                    ),
                ]
            )
    except Exception as e:
        return html.Div(
            [
                html.H4("Error"),
                html.P(
                    f"Error calculating recommendation: {str(e)}",
                    style={"fontSize": "16px", "color": "red"},
                ),
            ]
        )


@app.callback(
    Output("overview-cards-container", "children"),
    [Input("overview-date-picker", "date"), Input("overview-time-picker", "value")],
)
def update_overview_cards(selected_date, selected_time):
    if not selected_date or not selected_time:
        return html.Div("Please select both date and time to view patient overview.")

    try:
        # Combine date and time into a datetime object
        dt = datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M")

        # Get unique patients
        unique_patients = project_db[
            ["first_name", "last_name", "Gender"]
        ].drop_duplicates()

        cards = []
        for _, patient in unique_patients.iterrows():
            full_name = f"{patient['first_name']} {patient['last_name']}"
            gender = patient["Gender"]

            # Calculate states and grade for this patient
            try:
                hb_states = calculate_hemoglobin_states(
                    project_db, knowledge_db, full_name
                )
                hema_states = calculate_hematological_states(
                    project_db, knowledge_db, full_name
                )

                # Find current hemoglobin state
                hb_state = None
                for seg in hb_states:
                    if seg["start"] <= dt <= seg["end"]:
                        hb_state = seg["state"]
                        break

                # Find current hematological state
                hema_state = None
                for seg in hema_states:
                    if seg["start"] <= dt <= seg["end"]:
                        hema_state = seg["state"]
                        break

                # Calculate grade
                grade = calculate_grade(project_db, knowledge_db, full_name, dt)

                # Calculate recommendation
                recommendation = calculate_recommendation(
                    project_db, knowledge_db, full_name, dt
                )

                # Determine colors
                hb_color = "green" if hb_state == "Normal Hemoglobin" else "red"
                hema_color = "green" if hema_state == "Normal" else "red"

                # Grade color (more red for higher grades)
                if grade is None:
                    grade_color = "gray"
                    grade_text = "N/A"
                else:
                    grade_value = grade.value
                    if grade_value == 1:
                        grade_color = "#90EE90"  # Light green
                    elif grade_value == 2:
                        grade_color = "#FFD700"  # Gold
                    elif grade_value == 3:
                        grade_color = "#FFA500"  # Orange
                    elif grade_value == 4:
                        grade_color = "#FF4500"  # Red-orange
                    else:
                        grade_color = "#FF0000"  # Red
                    grade_text = f"Grade {grade_value}"

                # Create card
                card = dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H5(full_name, className="card-title mb-0"),
                                html.Small(f"Gender: {gender}", className="text-muted"),
                            ]
                        ),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Strong("Hemoglobin State: "),
                                                html.Span(
                                                    hb_state or "N/A",
                                                    style={
                                                        "color": hb_color,
                                                        "fontWeight": "bold",
                                                    },
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                html.Strong("Hematological State: "),
                                                html.Span(
                                                    hema_state or "N/A",
                                                    style={
                                                        "color": hema_color,
                                                        "fontWeight": "bold",
                                                    },
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ],
                                    className="mb-2",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Strong("Grade: "),
                                                html.Span(
                                                    grade_text,
                                                    style={
                                                        "color": grade_color,
                                                        "fontWeight": "bold",
                                                    },
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                html.Hr(),
                                html.Strong("Recommendation: "),
                                html.P(
                                    recommendation or "No recommendation available",
                                    className="mb-0",
                                    style={"fontSize": "14px"},
                                ),
                            ]
                        ),
                    ],
                    className="mb-3",
                    style={"border": "1px solid #ddd"},
                )

                cards.append(dbc.Col(card, width=6, className="mb-3"))

            except Exception as e:
                # Create error card for this patient
                error_card = dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H5(full_name, className="card-title mb-0"),
                                html.Small(f"Gender: {gender}", className="text-muted"),
                            ]
                        ),
                        dbc.CardBody(
                            [
                                html.P(
                                    f"Error calculating states: {str(e)}",
                                    style={"color": "red", "fontSize": "14px"},
                                )
                            ]
                        ),
                    ],
                    className="mb-3",
                    style={"border": "1px solid #ddd"},
                )

                cards.append(dbc.Col(error_card, width=6, className="mb-3"))

        # Create grid layout
        if cards:
            return dbc.Row(cards, className="mt-3")
        else:
            return html.Div("No patients found in the database.")

    except Exception as e:
        return html.Div(f"Error generating overview: {str(e)}", style={"color": "red"})


# Callbacks for "Now" buttons
@app.callback(
    [
        Output("update-datetime", "date"),
        Output("update-time", "value"),
        Output("update-now-button", "color"),
    ],
    [Input("update-now-button", "n_clicks")],
    prevent_initial_call=True,
)
def set_update_now(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    from datetime import datetime

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    return current_date, current_time, "success"


@app.callback(
    [
        Output("update-measurement-datetime", "date"),
        Output("update-measurement-time", "value"),
        Output("update-measurement-now-button", "color"),
    ],
    [Input("update-measurement-now-button", "n_clicks")],
    prevent_initial_call=True,
)
def set_update_measurement_now(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    from datetime import datetime

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    return current_date, current_time, "success"


@app.callback(
    [
        Output("delete-update-datetime", "date"),
        Output("delete-update-time", "value"),
        Output("delete-update-now-button", "color"),
    ],
    [Input("delete-update-now-button", "n_clicks")],
    prevent_initial_call=True,
)
def set_delete_update_now(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    from datetime import datetime

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    return current_date, current_time, "success"


if __name__ == "__main__":
    app.run(debug=True)
