import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, dash_table

from db_handler import DBHandler
# Initialize the Dash app
from loinc_name_fetcher import add_loinc_names_to_csv

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
input_file = "project_db.csv"
output_file = "project_db_with_names.csv"
df = add_loinc_names_to_csv(input_file, output_file)
db = DBHandler("project_db_with_names.csv")
# Layout
app.layout = dbc.Container([
    html.H1("Medical Records System", className="text-center my-4"),

    # Tabs
    dbc.Tabs([
        # Retrieve Tab
        dbc.Tab([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("First Name"),
                            dbc.Input(id="retrieve-first-name", type="text"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Last Name"),
                            dbc.Input(id="retrieve-last-name", type="text"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("LOINC-NUM"),
                            dbc.Input(id="retrieve-loinc", type="text"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Measurement Datetime"),
                            dcc.DatePickerSingle(
                                id="retrieve-measurement-date",
                                display_format="YYYY-MM-DD",
                            ),
                            dcc.Input(
                                id="retrieve-measurement-time",
                                type="text",
                                placeholder="HH:MM:SS (optional)",
                                className="mt-2"
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("From Datetime"),
                            dcc.DatePickerSingle(
                                id="retrieve-from-date",
                                display_format="YYYY-MM-DD",
                            ),
                            dcc.Input(
                                id="retrieve-from-time",
                                type="text",
                                placeholder="HH:MM:SS",
                                className="mt-2"
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("To Datetime"),
                            dcc.DatePickerSingle(
                                id="retrieve-to-date",
                                display_format="YYYY-MM-DD",
                            ),
                            dcc.Input(
                                id="retrieve-to-time",
                                type="text",
                                placeholder="HH:MM:SS",
                                className="mt-2"
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Button("Retrieve", id="retrieve-button", color="primary", className="mb-3"),
                    html.Div(id="retrieve-results")
                ])
            ])
        ], label="Retrieve"),

        # Update Tab
        dbc.Tab([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("First Name"),
                            dbc.Input(id="update-first-name", type="text"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Last Name"),
                            dbc.Input(id="update-last-name", type="text"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("LOINC-NUM"),
                            dbc.Input(id="update-loinc", type="text"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Value"),
                            dbc.Input(id="update-value", type="text"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Update Datetime"),
                            dcc.DatePickerSingle(
                                id="update-date",
                                display_format="YYYY-MM-DD",
                            ),
                            dcc.Input(
                                id="update-time",
                                type="text",
                                placeholder="HH:MM:SS",
                                className="mt-2"
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Measurement Datetime"),
                            dcc.DatePickerSingle(
                                id="update-measurement-date",
                                display_format="YYYY-MM-DD",
                            ),
                            dcc.Input(
                                id="update-measurement-time",
                                type="text",
                                placeholder="HH:MM:SS",
                                className="mt-2"
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Button("Update", id="update-button", color="primary", className="mb-3"),
                    html.Div(id="update-message")
                ])
            ])
        ], label="Update"),

        # Delete Tab
        dbc.Tab([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("First Name"),
                            dbc.Input(id="delete-first-name", type="text"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Last Name"),
                            dbc.Input(id="delete-last-name", type="text"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("LOINC-NUM"),
                            dbc.Input(id="delete-loinc", type="text"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Measurement Datetime"),
                            dcc.DatePickerSingle(
                                id="delete-measurement-date",
                                display_format="YYYY-MM-DD",
                            ),
                            dcc.Input(
                                id="delete-measurement-time",
                                type="text",
                                placeholder="HH:MM:SS (optional)",
                                className="mt-2"
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Update Datetime"),
                            dcc.DatePickerSingle(
                                id="delete-date",
                                display_format="YYYY-MM-DD",
                            ),
                            dcc.Input(
                                id="delete-time",
                                type="text",
                                placeholder="HH:MM:SS",
                                className="mt-2"
                            ),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Button("Delete", id="delete-button", color="primary", className="mb-3"),
                    html.Div(id="delete-message")
                ])
            ])
        ], label="Delete"),
    ])
], fluid=True)


def combine_date_time(date, time):
    if not date:
        return None
    if not time:
        return date
    return f"{date} {time}"


# Callbacks
@app.callback(
    Output("retrieve-results", "children"),
    Input("retrieve-button", "n_clicks"),
    State("retrieve-first-name", "value"),
    State("retrieve-last-name", "value"),
    State("retrieve-loinc", "value"),
    State("retrieve-measurement-date", "date"),
    State("retrieve-measurement-time", "value"),
    State("retrieve-from-date", "date"),
    State("retrieve-from-time", "value"),
    State("retrieve-to-date", "date"),
    State("retrieve-to-time", "value"),
)
def retrieve_records(n_clicks, first_name, last_name, loinc_num, measurement_date, measurement_time,
                     from_date, from_time, to_date, to_time):
    if not n_clicks:
        return ""

    if not all([first_name, last_name, loinc_num, from_date, from_time, to_date, to_time]):
        return dbc.Alert("Please fill in all required fields", color="danger")

    measurement_datetime = combine_date_time(measurement_date, measurement_time)
    from_datetime = combine_date_time(from_date, from_time)
    to_datetime = combine_date_time(to_date, to_time)

    records = db.retrieve_records(
        first_name, last_name, loinc_num,
        measurement_datetime, from_datetime, to_datetime
    )

    if records.empty:
        return dbc.Alert("No records found", color="warning")

    return dash_table.DataTable(
        data=records.to_dict('records'),
        columns=[{"name": i, "id": i} for i in records.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )


@app.callback(
    Output("update-message", "children"),
    Input("update-button", "n_clicks"),
    State("update-first-name", "value"),
    State("update-last-name", "value"),
    State("update-loinc", "value"),
    State("update-value", "value"),
    State("update-date", "date"),
    State("update-time", "value"),
    State("update-measurement-date", "date"),
    State("update-measurement-time", "value"),
)
def update_record(n_clicks, first_name, last_name, loinc_num, value,
                  update_date, update_time, measurement_date, measurement_time):
    if not n_clicks:
        return ""

    if not all([first_name, last_name, loinc_num, value, update_date, update_time,
                measurement_date, measurement_time]):
        return dbc.Alert("Please fill in all required fields", color="danger")

    update_datetime = combine_date_time(update_date, update_time)
    measurement_datetime = combine_date_time(measurement_date, measurement_time)

    success, result = db.update_record(
        first_name, last_name, loinc_num, value,
        update_datetime, measurement_datetime
    )

    if success:
        return dbc.Alert("Record updated successfully", color="success")
    return dbc.Alert(str(result), color="danger")


@app.callback(
    Output("delete-message", "children"),
    Input("delete-button", "n_clicks"),
    State("delete-first-name", "value"),
    State("delete-last-name", "value"),
    State("delete-loinc", "value"),
    State("delete-measurement-date", "date"),
    State("delete-measurement-time", "value"),
    State("delete-date", "date"),
    State("delete-time", "value"),
)
def delete_record(n_clicks, first_name, last_name, loinc_num,
                  measurement_date, measurement_time, update_date, update_time):
    if not n_clicks:
        return ""

    if not all([first_name, last_name, loinc_num, measurement_date, update_date, update_time]):
        return dbc.Alert("Please fill in all required fields", color="danger")

    measurement_datetime = combine_date_time(measurement_date, measurement_time)
    update_datetime = combine_date_time(update_date, update_time)

    success, result = db.delete_record(
        first_name, last_name, loinc_num,
        measurement_datetime, update_datetime
    )

    if success:
        return dbc.Alert("Record deleted successfully", color="success")
    return dbc.Alert(str(result), color="danger")


if __name__ == '__main__':
    app.run_server(debug=True)
