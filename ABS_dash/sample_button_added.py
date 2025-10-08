"""
This file creates a dash app that will eventually be publicly hosted.
It will allow users to manually input loans, and define a tranche structure.
Using those user defined inputs, it then produces the payment Waterfall.
"""




import dash.exceptions
# === App Imports ===
# from PIL.EpsImagePlugin import field
from dash import Dash, dcc, html, Input, Output, State, callback, no_update, ctx
from dash.dependencies import MATCH, ALL, ALLSMALLER



# === Waterfall Implementation Imports ===
# Loan functionality
from loan.loan_pool import LoanPool
from loan.loans import FixedRateLoan, VariableRateLoan
from loan.house_derived_classes import PrimaryHome, VacationHome
from loan.car_class import Car

# Tranche functionality
from Tranches.structured_securities_class import StructuredSecurities
from Tranches.waterfall_function import doWaterfall
from loan.mortgage import VariableMortgage, FixedMortgage

app = Dash(__name__, suppress_callback_exceptions=True)

server = app.server



# --- Loan Creation Dropdown Option Maps ---

CAR_MODELS = [
    # Car Models
    {"label": "Civic", "value": "civic"},
    {"label": "Lexus", "value": "lexus"},
    {"label": "Lambo", "value": "lambo"},
    {"label": "Toyota", "value": "toyota"},
    {"label": "Ferrari", "value": "ferrari"},
    {"label": "Other", "value": "car_other"},
]

HOUSE_TYPES = [
    # House Models
    {"label": "PrimaryHome", "value": "primary_home"},
    {"label": "VacationHome", "value": "vacation_home"}
]


LOAN_PRODUCTS_CAR = [
    # Car Loans
    # {"label": "AutoLoan", "value": "auto_loan"}, --- just a repeat of FixedRateLoan, see mortgage.py
    {"label": "FixedRateLoan", "value": "fixed_rate"},
    {"label": "VariableRateLoan", "value": "variable_rate"}
]

LOAN_PRODUCTS_HOUSE = [
    # House Loans
    {"label": "FixedMortgage", "value": "fixed_mortgage"},
    {"label": "VariableMortgage", "value": "variable_mortgage"}
]

LOAN_PRODUCTS_ALL = LOAN_PRODUCTS_CAR + LOAN_PRODUCTS_HOUSE


# --- Tranche Option Maps and helpers ---

WATERFALL_MODES = [
    {"label": "Sequential", "value": "sequential"},
    {"label": "Pro Rata", "value": "pro_rata"}
]

def _index_to_label(n: int) -> str:
    # 1 -> A, 2 -> B, ..., 27 -> AA,...
    s=""
    while n > 0:
        n, r = divmod(n-1, 26)
        s=chr(65 + r) + s
    return s


# --- Preset loader button data (sample 5 loans + 2 tranches) ---

SAMPLE_PRESET = {
    "mode": "sequential",
    "loans": [
        # Fixed mortgage
        {"asset_type": "house", "asset_subtype": "primary_home",
         "product": "fixed_mortgage", "face": 300000, "term_years": 30.0, "var_ranges": []},

        # Fixed mortgage
        {"asset_type": "house", "asset_subtype": "vacation_home",
         "product": "fixed_mortgage", "face": 200000, "term_years": 30.0, "var_ranges": []},

        # Fixed car
        {"asset_type": "car", "asset_subtype": "civic",
         "product": "fixed_rate", "face": 22000, "term_years": 5.0, "var_ranges": []},

        # Fixed car
        {"asset_type": "car", "asset_subtype": "lexus",
         "product": "fixed_rate", "face": 28000, "term_years": 5.0, "var_ranges": []},

        # Variable car – two-range example so “Edit Ranges” shows both
        {"asset_type": "car", "asset_subtype": "toyota",
         "product": "variable_rate", "face": 18000, "term_years": 5.0,
         "var_ranges": [
             {"uid": 1, "start": 1,  "end": 30, "rate": 0.065},
             {"uid": 2, "start": 31, "end": 60, "rate": 0.072},
         ]},
    ],
    "tranches": [
        {"label": "A", "notional": 80000, "rate": 0.08},
        {"label": "B", "notional": 20000, "rate": 0.02},
    ],
}







# Function for adding loans button; adds loan trio of type, subtype, loan product
def make_loan_row(
        idx: int,
        *,
        default_asset_type=None,
        default_asset_subtype=None,
        default_product=None,
        default_face=None,
        default_term_years=None,
        default_var_ranges=None,
):


    subtype_opts = []
    product_opts = []
    if default_asset_type == "car":
        subtype_opts = CAR_MODELS
        product_opts = LOAN_PRODUCTS_CAR
    elif default_asset_type == "house":
        subtype_opts = HOUSE_TYPES
        product_opts = LOAN_PRODUCTS_HOUSE


    return html.Div(
        [
            # --- Header: dropdown trio + toggle + remove ---
            html.Div(
                [
                    dcc.Dropdown(
                        id={"type": "asset-type", "index": idx},
                        options=[
                            {"label": "Car", "value": "car"},
                            {"label": "House", "value": "house"},
                        ],
                        placeholder="Select Asset Type...",
                        value=default_asset_type,
                        style={"flex": "1"},
                        persistence=True,
                        persistence_type="session"
                    ),
                    dcc.Dropdown(
                        id={"type": "asset-subtype", "index": idx},
                        # options=[], # Will be filled by callback based on asset-type
                        options = (subtype_opts if default_asset_type else []),
                        placeholder="Select Model / House Type...",
                        value=default_asset_subtype,
                        style={"flex": "1"},
                        persistence=True,
                        persistence_type="session"
                    ),
                    dcc.Dropdown(
                        id={"type": "loan-product", "index": idx},
                        # options=[], # Will be filled by callback based on asset-type
                        options=(product_opts if default_asset_type else []),
                        placeholder="Select Loan Product...",
                        value=default_product,
                        style={"flex": "1"},
                        persistence=True,
                        persistence_type="session"
                    ),

                    # Erm
                    html.Button(
                        "Details",
                        id={"type": "toggle-details", "index": idx},
                        n_clicks=0,
                        style={"marginLeft": "8px", "height": "36px"},
                    ),

                    # Remove button
                    html.Button(
                        "Remove",
                        id={"type": "remove-loan", "index": idx},
                        n_clicks=0,
                        style={"marginLeft": "8px", "height": "36px"}
                    )

                ],
                # style={"display": "flex", "gap": "6px", "marginTop": "8px"},
                style={"display": "flex", "gap": "6px", "flex": "1", "alignItems": "center"},
            ),


            # --- Collapsible details body ---
            html.Div(
                [
                    # Basic numeric inputs; Face + Term
                    html.Div(
                        [
                            dcc.Input(
                                id={"type": "face", "index": idx},
                                type="number",
                                placeholder="Face... (e.g., 200,000)",
                                value=default_face,
                                style={"flex": "1", "minWidth": "180px"},
                                persistence=True,
                                persistence_type="session"
                            ),
                            dcc.Input(
                                id={"type": "term", "index": idx},
                                type="number",
                                placeholder="Term...",
                                value=default_term_years,
                                style={"flex": "1", "minWidth": "160px"},
                                persistence=True,
                                persistence_type="session"
                            ),

                            # === RATE AREA PLACEHOLDER ===
                            # This container has:
                            # If fixed selected, simple one box (decimal rate)
                            # If variable selected, "Edit Ranges" button for collapsible clicker instead of box
                            html.Div(
                                id={"type": "rate-area", "index": idx},
                                style={"flex": "1", "minWidth": "160px"},
                            ),


                        ],
                        style={"display": "flex", "gap": "8px", "flexWrap": "wrap"},
                    ),

                    # --- VARIABLE RATE RANGES EDITORS (collapsible) ---
                    # Appears ONLY if variable selected, and AFTER clicking "Edit Ranges" button
                    html.Div(
                        [
                            # Placeholder first
                            html.P("This will contain ranges to edit...", style={"opacity": 0.7, "margin": 0}),

                            # Top utility bar
                            html.Div(
                                [
                                    html.Button(
                                        "Add Range",
                                        id={"type": "var-add", "index": idx},
                                        n_clicks=0,
                                        style={"height": "32px"},
                                        title="Add a new rate range row",
                                        disabled=True # See callback further down; def enable_add_range
                                    )
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "flex-start",
                                    "gap": "8px",
                                    "marginBottom": "8px",
                                },
                            ),


                            # Dynamic rows container - fully rendered from var-store (see dcc.Store docu)
                            html.Div(
                                id={"type": "var-rows", "index": idx},
                                style={"display": "flex", "flexDirection": "column", "gap": "6px"},
                            ),

                            # Hidden store; holds ranges list
                            dcc.Store(
                                id={"type": "var-store", "index": idx},
                                data=(default_var_ranges or []), # List of dicts: [{"uid":1, "start":None, "end":None, "rate":None}, ...]
                                storage_type="memory",
                            ),
                        ],
                        id={"type": "var-editor", "index": idx},
                        style={
                            "display": "none", # Hidden by default; activates on variable + "Edit Ranges" toggle
                            "marginTop": "10px",
                            "padding": "12px",
                            "border": "1px solid #ddd",
                            "borderRadius": "10px",
                            "background": "#fafafa",
                        },
                    ),

                ],
                id={"type": "loan-details", "index": idx},
                style={
                    "display": "none", # Toggled using Details button; see above
                    "marginTop": "10px",
                    "padding": "12px",
                    "border": "1px solid #ddd",
                    "borderRadius": "10px",
                    "background": "#fafafa"
                },
            ),

        ],
        style={"display": "flex", "flexDirection": "column", "gap": "6px", "marginTop": "12px"},
        id={"type": "loan-row", "index": idx},

    )



# Tranche trio
def make_tranche_row(
        idx: int,
        *,
        default_notional=None,
        default_rate=None,
        default_label=None,
):
    default_label = _index_to_label(idx)
    return html.Div(
        [
            # Header: Notional / Rate / Label / Details / Remove
            html.Div(
                [
                    dcc.Input(
                        id={"type": "tranche-notional", "index": idx},
                        type="number",
                        # value=0,
                        placeholder="Notional...",
                        value=default_notional,
                        style={"flex": "1", "minWidth": "160px"},
                        persistence=True,
                        persistence_type="session"
                    ),
                    dcc.Input(
                        id={"type": "tranche-rate", "index": idx},
                        type="number",
                        placeholder="Rate (decimal)...",
                        value=default_rate,
                        style={"flex": "1", "minWidth": "160px"},
                        persistence=True,
                        persistence_type="session",
                    ),
                    dcc.Input(
                        id={"type": "tranche-label", "index": idx},
                        type="text",
                        value=(default_label or _index_to_label(idx)),
                        placeholder="Label... ",
                        style={"flex": "1", "minWidth": "140px"},
                        persistence=True,
                        persistence_type="session"
                    ),

                    html.Button(
                        "Details",
                        id={"type": "tranche-toggle-details", "index": idx},
                        n_clicks=0,
                        style={"marginLeft": "8px", "height": "36px"},
                    ),
                    html.Button(
                        "Remove",
                        id={"type": "tranche-remove", "index": idx},
                        n_clicks=0,
                        style={"marginLeft": "8px", "height": "36px"},
                    ),
                ],
                style={"display": "flex", "gap": "6px", "flex": "1", "alignItems": "center"},
            ),


            # Collapsible details (mode / reserve)
            html.Div(
                [
                    html.Div(
                        [
                            # dcc.Dropdown(
                            #     id={"type": "tranche-mode", "index": idx},
                            #     options = WATERFALL_MODES,
                            #     value="sequential",
                            #     style={"flex": "1", "minWidth": "200px"},
                            #     persistence=True,
                            #     persistence_type="session"
                            # ),
                            html.Label(
                                "Cash Reserve:",
                                # htmlFor={"type": "tranche-reserve", "index": idx},
                                style={"marginRight": "8px", "whiteSpace": "nowrap"}
                            ),
                            dcc.Input(
                                id={"type": "tranche-reserve", "index": idx},
                                type="number",
                                value=0,
                                placeholder="Reserve",
                                style={"width": "50%", "minWidth": "120px"},
                                persistence=True,
                                persistence_type="session"
                            ),
                        ],
                        style={"display": "flex", "gap": "8px", "flexWrap": "wrap"},
                    ),
                ],
                id={"type": "tranche-details", "index": idx},
                style={
                    "display": "none",
                    "marginTop": "10px",
                    "padding": "12px",
                    "border": "1px solid #ddd",
                    "borderRadius": "10px",
                    "background": "#fafafa"
                },
            ),
        ],
        style={"display": "flex", "flexDirection": "column", "gap": "6px", "marginTop": "12px"},
        id={"type": "tranche-row", "index": idx}
    )






app.layout = html.Div([

    # TOP STRIP (full width) + adding waterfall button now
    # html.Div([
    #     html.H1("ABS Dashboard"),
    #     html.P("This is a test sentence. Description of how to use site will come here (placeholder)"),
    # ], style={"padding": "20px"}),


    html.Div([
        html.Div([
            html.H1("ABS Dashboard"),
            # html.P("This is a test sentence. Description of how to use site will come here (placeholder)",
            #        style={"margin": "4px 0 0 0"}),
            # html.P("This app simulates cash flow payments received from Loans to pay out investment Tranches.\n "
            #        "After successful inputs, the user can click the “Run Waterfall” button to display the following "
            #        "parameters: Interest Due, Interest Paid, any Interest Shortfall, Principal Paid, and remaining "
            #        "Tranche Balance. This Waterfall continues until the end of all Loans, or until all Tranches have "
            #        "been paid out in full. ",
            #                    style={"margin": "4px 0 0 0", "maxWidth": "50%"}),
            html.P("This app simulates cash flow payments received from Loans to pay out investment Tranches.",
                   style={"margin": "4px 0 0 0", "maxWidth": "100%"}),
            html.P("After successful inputs, the user can click the “Run Waterfall” button"
                   " to display the following parameters: ",
                   style={"margin": "4px 0 0 0", "maxWidth": "100%"}),
            html.P("[Interest Due, Interest Paid, Interest Shortfall, Principal Paid, Remaining Tranche Balance]",
                   style={"margin": "4px 0 0 0", "maxWidth": "100%", "paddingLeft": "10px", "fontWeight": "bold"}),
            html.P("This Waterfall continues until the end of all Loans, or until all Tranches have been paid out in full.",
                   style={"margin": "4px 0 0 0", "maxWidth": "100%"})
        ], style={"display": "flex", "flexDirection": "column"}),

        html.Div([
            html.Button(
                "Run Waterfall",
                id="run-waterfall",
                n_clicks=0,
                style={
                    "height": "44px",
                    "padding": "0 18px",
                    "fontWeight": "600",
                    "borderRadius": "10px",
                    "border": "1px solid #333"
                },
                disabled=True, #Enabled by callback
            ),
            html.Button(
                "Populate Sample Waterfall",
                id="btn-populate-sample",
                n_clicks=0,
                style={
                    "height": "44px",
                    "padding": "0 18px",
                    "marginLeft": "12px",
                    "borderRadius": "10px",
                    "border": "1px solid #343a40",
                    "backgroundColor": "#343a40",
                    "color": "white",
                    "fontWeight": "600"
                },
                title="Insert a fixed example (5 loans + 2 tranches)"
            ),

            html.Span(id="run-status", style={"marginLeft": "10px", "opacity": 0.7}),
        ], style={"display": "flex", "alignItems": "center"})
    ], style={"padding": "20px", "display": "flex", "justifyContent": "space-between", "alignItems": "center"}),


    # Stores for pass-through (inputs snapshot/computed results)
    dcc.Store(id="app-input-snapshot", storage_type="memory"),
    dcc.Store(id="waterfall-results", storage_type="memory"),



    # HORIZONTAL LINE DIVIDER
    html.Hr(style = {"border": "1px solid black", "margin": 0}),


    html.Div([


    # LEFT HALF (LOAN HALF)
    html.Div([
        # Header + Add button
        html.Div([
            html.H3("Loans"),
            html.Button("Add Loan", id="add-loan", n_clicks=0, style={"marginTop": "6px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),

        #Dynamic rows container: starts with ONE tyrio, switch children to [] for empty page start
        html.Div(
            id="loan-rows",
            children=[ make_loan_row(1) ],
            style={"marginTop": "12px"}
        ),
    ], style={"width": "50%", "padding": "20px"}),





    # RIGHT HALF (TRANCHE HALF)
    html.Div([
        html.Div([
            html.H3("Tranches"),
            html.Button("Add Tranche", id="add-tranche", n_clicks=0, style={"marginTop": "6px"}),

            # Spacer to right justify
            html.Div(style={"flex": "1"}),

            html.Label(
                "Payment Mode: ",
                style={"marginRight": "8px", "whiteSpace": "nowrap"}
            ),
            dcc.Dropdown(
                id="global-mode",
                options=WATERFALL_MODES,
                value="sequential",
                clearable=False,
                style={"width": "220px"}
            ),
        ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),

        html.Div(
            id="tranche-rows",
            children=[make_tranche_row(1)],
            style={"marginTop": "12px"}
        ),

    ], style={"width": "50%", "padding": "20px", "border-left": "1px solid #eee"})


], style = {"display": "flex", "alignItems": "flex-start"}),


# === Waterfall Results (bottom block aligned past loan + tranche halves)

html.Div(
    id="waterfall-output",
    children=[],
    style={
        "padding": "20px",
        "marginTop": "10px",
        "borderTop": "1px solid #ddd"
    }
),



])

# --- Callbacks ---


# Filter 2nd dropdown based on 1st (subtype based on type), per row
@callback(
    Output({"type": "asset-subtype", "index": MATCH}, "options"),
    Output({"type": "asset-subtype", "index": MATCH}, "value"),
    Input({"type": "asset-type", "index": MATCH}, "value"),
)
#Same as first run
def filter_asset_subtype(asset_type):
    if asset_type == "car":
        return CAR_MODELS, no_update
    if asset_type == "house":
        return HOUSE_TYPES, no_update
    return [], None



# Filter 3rd dropdown based on 1st (loan product based on type), per row
@callback(
    Output({"type": "loan-product", "index": MATCH}, "options"),
    Output({"type": "loan-product", "index": MATCH}, "value"),
    Input({"type": "asset-type", "index": MATCH}, "value"),
)
#Same as first run
def filter_loan_product(asset_type):
    if asset_type == 'car':
        return LOAN_PRODUCTS_CAR, no_update
    if asset_type == 'house':
        return LOAN_PRODUCTS_HOUSE, no_update
    return [], None


# Added callbank (append rows)
## UPDATE: add or remove loan split
# --- Add loan ---
@callback(
    Output("loan-rows", "children", allow_duplicate=True),
    Input("add-loan", "n_clicks"),
    State("loan-rows", "children"),
    prevent_initial_call=True
)

def add_loan(add_clicks, children):
    children = children or []

    def next_index(items):
        if not items:
            return 1
        indices = []
        for c in items:
            cid = (c.get("props", {}).get("id") if isinstance(c, dict) else getattr(c, "id", None))
            if isinstance(cid, dict) and isinstance(cid.get("index"), int):
                indices.append(cid["index"])
        return (max(indices) + 1) if indices else 1

    return children + [make_loan_row(next_index(children))]

# --- Remove loan ---

@callback(
    Output({"type": "loan-row", "index": MATCH}, "style"),
    Input({"type": "remove-loan", "index": MATCH}, "n_clicks"),
    State({"type": "loan-row", "index": MATCH}, "style"),
    prevent_initial_call=True,
)

def remove_loan_this_row(n_clicks, style):
    style = style or {}
    if (n_clicks or 0) > 0:
        new_style = dict(style)
        new_style["display"] = "none"
        return new_style
    return style




## Changed to above
# @callback(
#     Output("loan-rows", "children", allow_duplicate=True),
#     Input({"type": "remove-loan", "index": ALL}, "n_clicks"),
#     State("loan-rows", "children"),
#     prevent_initial_call=True
# )
# def remove_loan(remove_clicks, children):
#     children = children or []
#     trig = ctx.triggered_id # dict like {"type": "remove-loan", "index": <int>} or None
#
#     if isinstance(trig, dict) and trig.get("type") == "remove-loan":
#         remove_idx = trig.get("index")
#         new_children = []
#         for c in children:
#             cid = (c.get("props", {}).get("id") if isinstance(c, dict) else getattr(c, "id", None))
#             if not (isinstance(cid, dict) and cid.get("index") == remove_idx):
#                 new_children.append(c)
#         return new_children
#
#     return children











# Toggle details section based on click count
@callback(
    Output({"type": "loan-details", "index": MATCH}, "style"),
    Input({"type": "toggle-details", "index": MATCH}, "n_clicks"),
    State({"type": "loan-details", "index": MATCH}, "style"),
)

def toggle_details(n_clicks, current_style):
    current_style = current_style or {}
    # Visible when n_clicks is odd
    visible = (n_clicks or 0) % 2 == 1
    new_style = dict(current_style)
    new_style["display"] = "block" if visible else "none"
    return new_style






@callback(
    Output({"type": "rate-area", "index": MATCH}, "children"),
    Input({"type": "loan-product", "index": MATCH}, "value"),
    State({"type": "rate-area", "index": MATCH}, "id")
)

# Decides: Fixed rate box VS "Edit Ranges" collapsible
def render_rate_area(product_value, rate_area_id):
    idx = rate_area_id["index"]
    # Check for variable
    is_variable = bool(product_value) and ("variable" in str(product_value).lower())

    # No variable ==> fixed box display
    if not is_variable:
        # Return exact box we had before, while using variable placeholder (copy pasted from previous iteration into return)
        return dcc.Input(
            # id={"type": "fixed-rate", "index": ctx.triggered_id["index"] if isinstance(ctx.triggered_id, dict) else 0},
            id={"type": "fixed-rate", "index": idx},
            type="number",
            placeholder="Fixed Rate... (decimal)",
            style={"width": "100%"},
            persistence=True,
            persistence_type="session"
        )

    # Else, return "Edit Ranges"
    return html.Button(
        "Edit Ranges",
        # id={"type": "var-toggle", "index": ctx.triggered_id["index"] if isinstance(ctx.triggered_id, dict) else 0},
        id={"type": "var-toggle", "index": idx},
        n_clicks=0,
        style={"width": "100%", "height": "36px"},
        title="Open/close the variable-rate ranges editor for this loan",
    )




@callback(
    Output({"type": "var-editor", "index": MATCH}, "style"),
    Input({"type": "var-toggle", "index": MATCH}, "n_clicks"),
    State({"type": "var-editor", "index": MATCH}, "style"),
    prevent_initial_call=True
)
def toggle_var_editor(n_clicks, cur_style):
    # Show/hide editor box when "Edit Ranges" is clicked
    style = dict(cur_style or {})
    visible = (n_clicks or 0) % 2 == 1
    style["display"] = "block" if visible else "none"
    return style







# @callback(
#     Output({"type": "var-editor", "index": MATCH}, "style"),
#     Input({"type": "loan-product", "index": MATCH}, "value"),
#     Input({"type": "var-toggle", "index": ALLSMALLER}, "n_clicks"),
#     State({"type": "var-editor", "index": MATCH}, "style")
# )
# def control_var_editor(product_value, toggle_clicks_list, cur_style):
#     # Single controller; Fixed --> forces hide, Variable --> active while "Edit Ranges" is up
#     cur_style = cur_style or {}
#     is_variable = bool(product_value) and ("variable" in str(product_value).lower())
#
#     style = dict(cur_style or {})
#     if not is_variable:
#         style["display"] = "none"
#         return style
#
#     # no toggle button yet ==> treat as 0 clicks
#     clicks = (toggle_clicks_list[-1] if toggle_clicks_list else 0)
#     style["display"] = "block" if (clicks or 0) % 2 == 1 else "none"
#     return style





    # visible = (toggle_clicks or 0) % 2 == 1
    # style["display"] = "block" if visible else "none"
    # return style






### Render range rows from per-loan dcc.Store
# Builds UI rows from dcc.Store (includes yellow/red validation highlights + "!" next to offending input)
def _input_with_warning(component_id, value, placeholder, width_px, warn=None, error=None, min_value=None):
    base_style = {
        "minWidth": f"{width_px}px",
        "width": f"{width_px}px",
        "padding": "6px"
    }

    # Warn/Error coloring + hoverable icon
    if error:
        field_style = {**base_style, "border": "1px solid #e53935", "background": "#fdecea"} # rojo
        icon = html.Span("❗", title=error, style={"marginLeft": "6px", "cursor": "help", "color": "#e53935"})
    elif warn:
        field_style = {**base_style, "border": "1px solid #f1c232", "background": "#fff7d6"} # jaune
        icon = html.Span("❗", title=warn, style={"marginLeft": "6px", "cursor": "help", "color": "#f1c232"})
    else:
        field_style = base_style
        icon = html.Span() # keep spacing

    return html.Div(
        [
            dcc.Input(
                id=component_id,
                type="number",
                value=value,
                placeholder=placeholder,
                style=field_style,
                **({"min": min_value} if min_value is not None else {}),
            ),
            icon,
        ],
        style={"display": "flex", "alignItems": "center"},
    )

@callback(
    Output({"type": "var-rows", "index": MATCH}, "children"),
    Input({"type": "var-store", "index": MATCH}, "data"),
    State({"type": "term", "index": MATCH}, "value"),
    State({"type": "var-rows", "index": MATCH}, "id")
)

def render_var_rows(store_data, term_years, var_rows_id):
    # Renders all rows from stored data: Start, End<, Rate, RHS tools (fill/delete)
    idx = var_rows_id["index"]
    ranges = store_data or []

    # Total periods (term_months)
    term_months = int(term_years * 12) if term_years else None

    rows = []
    prev_end = 0
    for i, r in enumerate(ranges):
        uid = r.get("uid")
        start = r.get("start")
        end = r.get("end")
        rate = r.get("rate")

        # Next row start (for fill button)
        next_start = ranges[i + 1].get("start") if i + 1 < len(ranges) else None

        # --- DECIDE WARNING COLORS ---
        warn_start = None
        error_start = None
        warn_end = None
        error_end = None

        ## Red:
        # Out of bounds
        if term_months:
            if start is not None and (start < 1 or start > term_months):
                error_start = f"Start must be in [1, {term_months}]"
            if end is not None and (end < 1 or end > term_months):
                error_end = f"End must be in [1, {term_months}]"
        # Start > End
        if start is not None and end is not None and start > end:
            error_start = error_start or "Start > End (invalid input)"
            error_end = error_end or "Start > End (invalid input)"


        ## Yellow:
        # Overlap/out-of-order OR gaps (use prev_end)
        if start is not None:
            if start <= prev_end:
                warn_start = f"Start overlaps/out-of-order (prev end = {prev_end})"
            elif start > prev_end + 1:
                warn_start = (
                    f"Gap after previous end {prev_end}. "
                    f"Tip: Click 'Fill remaining' on the previous row to set End to {start-1}. "
                )



        # Build inputs
        start_input = _input_with_warning(
            {"type": "var-range-start", "index": idx, "uid": uid},
            start,
            placeholder=(str(prev_end + 1) if prev_end else "1"),
            width_px=100,
            warn=warn_start,
            error=error_start,
            min_value=1,
        )
        end_input = _input_with_warning(
            {"type": "var-range-end", "index": idx, "uid": uid},
            end,
            placeholder=(str(next_start - 1) if next_start else (str(term_months) if term_months else "End")),
            width_px=100,
            warn=warn_end,
            error=error_end,
            min_value=1
        )
        rate_input = _input_with_warning(
            {"type": "var-range-rate", "index": idx, "uid": uid},
            rate,
            placeholder="Rate (decimal)",
            width_px=140,
            warn=None,
            error=None,
            min_value=None, # all decimals allowed
        )



        # RHS per-row controls
        rhs_controls = html.Div(
            [
                html.Button(
                    "Fill Remaining",
                    id={"type": "var-fill", "index": idx, "uid": uid},
                    n_clicks=0,
                    title=(
                        f"Set End to {next_start - 1}" if (next_start is not None) else
                        (f"Set End to {term_months}" if term_months else "Set End to Term")
                    ),
                    style={"height": "30px", "marginRight": "8px"},
                ),
                html.Button(
                    "🗑️ Delete",
                    id={"type": "var-delete", "index": idx, "uid": uid},
                    n_clicks=0,
                    title="Delete this range",
                    style={"height": "30px", "color": "#e53935"},
                ),
            ],
            style={"display": "flex", "alignItems": "center"},
        )

        row = html.Div(
            [
                start_input,
                end_input,
                rate_input,
                html.Div(style={"flex": "1"}), #spacer
                rhs_controls,
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "auto auto auto 1fr auto",
                "gap": "8px",
                "alignItems": "center",
                "background": "#fff",
                "border": "1px solid #eee",
                "borderRadius": "8px",
                "padding": "8px",
            },
            id={"type": "var-row", "index": idx, "uid": uid}
        )
        rows.append(row)


        # Update prev_end for next row's warnings
        prev_end = end if (end is not None) else prev_end

    return rows



@callback(
    Output({"type": "var-store", "index": MATCH}, "data"),
    Input({"type": "var-add",         "index": MATCH}, "n_clicks"),
    Input({"type": "var-delete",      "index": MATCH, "uid": ALL}, "n_clicks"),
    Input({"type": "var-fill",        "index": MATCH, "uid": ALL}, "n_clicks"),
    Input({"type": "var-range-start", "index": MATCH, "uid": ALL}, "value"),
    Input({"type": "var-range-end",   "index": MATCH, "uid": ALL}, "value"),
    Input({"type": "var-range-rate",  "index": MATCH, "uid": ALL}, "value"),
    State({"type": "var-store",       "index": MATCH}, "data"),
    State({"type": "term",            "index": MATCH}, "value"),
    prevent_initial_call=True,
)

def update_var_store(add_clicks, del_clicks, fill_clicks, starts, ends, rates, store_data, term_years):
    # Updates all things relevant to ranges (add, delete, filling, editing boxes)
    data = list(store_data or [])
    trig = ctx.triggered_id
    term_months = int(term_years * 12) if term_years else None

    # Helper: next unique UID
    def next_uid(items):
        if not items:
            return 1
        return max((r.get("uid", 0) for r in items), default=0) + 1

    # Index helpers
    order = [r.get("uid") for r in data]
    uid_to_index = {u: i for i, u in enumerate(order)}


    # No trigger ==> return as is
    if trig is None:
        return data

    # Button/Input handling
    if isinstance(trig, dict):
        ttype = trig.get("type")

        # 1) Add new empty range
        if ttype == "var-add":
            data.append({"uid": next_uid(data), "start": None, "end": None, "rate": None})
            return data


        trig_uid = trig.get("uid")
        if trig_uid is None:
            # No uid, cant do anything
            return data

        i = uid_to_index.get(trig_uid, None)
        if i is None:
            # Not found, possibly removed tho
            return data

        # 2) Delete row
        if ttype == "var-delete":
            data = [r for r in data if r.get("uid") != trig_uid]
            return data

        # 3) Fill remaining
        if ttype == "var-fill":
            next_start = data[i + 1].get("start") if (i + 1 < len(data)) else None
            if next_start is not None:
                data[i]["end"] = int(next_start) - 1
            elif term_months:
                data[i]["end"] = term_months
            return data


        # 4) Start/End/Rate
        if ttype == "var-range-start":
            val = starts[i] if (starts and i < len(starts)) else None
            data[i]["start"] = int(val) if val is not None else None
            return data

        if ttype == "var-range-end":
            val = ends[i] if (ends and i < len(ends)) else None
            data[i]["end"] = int(val) if val is not None else None
            return data

        if ttype == "var-range-rate":
            val = rates[i] if (rates and i < len(rates)) else None
            data[i]["rate"] = float(val) if val is not None else None
            return data


    # Fallback
    return data



# Disables range adding until term is input (see make_loan_row)
@callback(
    Output({"type": "var-add", "index": MATCH}, "disabled"),
    Input({"type": "term", "index": MATCH}, "value")
)
def enable_add_range(term):
    try:
        return not (float(term) > 0)
    except (TypeError, ValueError):
        return True








# =========== TRANCHE CALLBACKS ===========

# --- Tranche: add row ---
@callback(
    Output("tranche-rows", "children", allow_duplicate=True),
    Input("add-tranche", "n_clicks"),
    State("tranche-rows", "children"),
    prevent_initial_call=True
)
def add_tranche(n_add, children):
    children = children or []

    def next_index(items):
        if not items:
            return 1
        indices = []
        for c in items:
            cid = (c.get("props", {}).get("id") if isinstance(c, dict) else getattr(c, "id", None))
            if isinstance(cid, dict) and isinstance(cid.get("index"), int):
                indices.append(cid["index"])
        return (max(indices) + 1) if indices else 1

    return children + [make_tranche_row(next_index(children))]



# --- Tranche: remove row ---
@callback(
    Output({"type": "tranche-row", "index": MATCH}, "style"),
    Input({"type": "tranche-remove", "index": MATCH}, "n_clicks"),
    State({"type": "tranche-row", "index": MATCH}, "style"),
    prevent_initial_call=True
)
def remove_tranche_this_row(n_clicks, style):
    style = style or {}
    if (n_clicks or 0) > 0:
        new_style = dict(style)
        new_style["display"] = "none"
        return new_style
    return style



# --- Tranche: details toggle ---
@callback(
    Output({"type": "tranche-details", "index": MATCH}, "style"),
    Input({"type": "tranche-toggle-details", "index": MATCH}, "n_clicks"),
    State({"type": "tranche-details", "index": MATCH}, "style",)
)
def toggle_tranche_details(n_clicks, cur_style):
    cur_style = cur_style or {}
    visible = (n_clicks or 0) % 2 == 1
    new_style = dict(cur_style)
    new_style["display"] = "block" if visible else "none"
    return new_style


# --- Tranche: light warnign style when Notional is 0
@callback(
    Output({"type": "tranche-notional", "index": MATCH}, "style"),
    Input({"type": "tranche-notional", "index": MATCH}, "value"),
    State({"type": "tranche-notional", "index": MATCH}, "style")
)
def warn_zero_notional(val, cur_style):
    base = {"flex": "1", "minWidth" : "160px"}
    style = dict(cur_style or base)
    # Reset to base first
    style.update(base)
    if val == 0:
        style.update({"border": "1px solid #f1c232", "background": "#fff7d6"})
    return style




# =========== SAMPLE BUTTON CALLBACKS ===========
@callback(
    Output("loan-rows", "children"),
    Output("tranche-rows", "children"),
    Output("global-mode", "value"),
    Input("btn-populate-sample", "n_clicks"),
    prevent_initial_call=True,
)
def populate_sample(n_clicks):
    if not n_clicks:
        return no_update, no_update, no_update

    # Build loan rows from preset (index from 1)
    loan_children = []
    for i, L in enumerate(SAMPLE_PRESET["loans"], start=1):
        loan_children.append(
            make_loan_row(
                i,
                default_asset_type=L.get("asset_type"),
                default_asset_subtype=L.get("asset_subtype"),
                default_product=L.get("product"),
                default_face=L.get("face"),
                default_term_years=L.get("term_years"),
                default_var_ranges=L.get("var_ranges")
            )
        )

    # Build tranche rows from preset (index from 1)
    tranche_children = []
    for j, T in enumerate(SAMPLE_PRESET["tranches"], start=1):
        tranche_children.append(
            make_tranche_row(
                j,
                default_notional=T.get("notional"),
                default_rate=T.get("rate"),
                default_label=T.get("label")
            )
        )


    # Return both
    return loan_children, tranche_children, SAMPLE_PRESET["mode"]



# =========== LOAN BUILDERS ===========

def _is_visible(style_dict):
    #True if row style visible; similar things done before
    if not style_dict:
        return True
    disp = style_dict.get("display")
    return disp is None or disp != "none"

def _label_rank_key(lbl: str):
    return (str(lbl or "").strip().upper(),)

def _compute_subordination_order(labels):
    # Return dict: label -> sub_rank
    enumerated = list(enumerate(labels))

    sorted_pairs = sorted(enumerated, key=lambda p: (_label_rank_key(p[1]), p[0]))

    # Assign sorted order
    order = {}
    for rank, (idx, label) in enumerate(sorted_pairs, start=1):
        order[label] = rank


    return order


# def _build_asset(asset_type, subtype_value):
#     ## Build asset type from UI selection
#     # Houses
#     if asset_type == "house":
#         if str(subtype_value) == "primary_home":
#             return PrimaryHome
#         elif str(subtype_value) == "vacation_home":
#             return VacationHome
#         # Default
#         else:
#             return PrimaryHome
#
#     if asset_type == "car":
#         return Car


# Fixing
def _build_asset(asset_type, subtype_value, face):
    try:
        iv = float(face)
    except Exception:
        iv = 0.0


    if asset_type == "house":
        if str(subtype_value) == "vacation_home":
            return VacationHome(initial_value=iv) if iv is not None else VacationHome(0.0)
        # Default to primary (currently same functionality)
        return PrimaryHome(initial_value=iv) if iv is not None else PrimaryHome(0.0)


    if asset_type == "car":
        model_map = {
            "civic": "Civic",
            "lexus": "Lexus",
            "lambo": "Lambo",
            "toyota": "Toyota",
            "ferrari": "Ferrari",
            "car_other": "Other",
            None: "Other", # Default also
        }
        model = model_map.get(str(subtype_value), "Other")
        return Car(initial_value=iv, model=model)

    # Fallback
    return PrimaryHome(initial_value=iv)






def _build_loan(asset_type, product_value, asset_obj, face, term_years, fixed_rate_value, var_ranges, term_required=True):
    # Creates loan instance from UI field inputs
    term_years = float(term_years)
    face = float(face)

    # Fixed vs variable
    is_variable = bool(product_value) and ("variable" in str(product_value).lower())


    # Houses
    if asset_type == "house":
        if is_variable:
            # Variable ==> rateDict must be built
            rate_dict = {}
            for r in (var_ranges or []):
                start = r.get("start")
                rate = r.get("rate")
                if start is not None and rate is not None:
                    rate_dict[int(start)] = float(rate)
            return VariableMortgage(asset_obj, face, rate_dict, term_years)
        # Fixed (flat rate)
        else:
            rate = float(fixed_rate_value)
            return FixedMortgage(asset_obj, face, rate, term_years)


    # Cars
    if is_variable:
        rate_dict = {}
        for r in (var_ranges or []):
            start = r.get("start")
            rate = r.get("rate")
            if start is not None and rate is not None:
                rate_dict[int(start)] = float(rate)
        return VariableRateLoan(asset_obj, face, rate_dict, term_years)
    else:
        rate = float(fixed_rate_value)
        return FixedRateLoan(asset_obj, face, rate, term_years)




# Enable/Disable Run Waterfall
@callback(
    Output("run-waterfall", "disabled"),
    Output("run-status", "children"),
    # Loan check
    Input({"type": "loan-row", "index": ALL}, "style"),
    Input({"type": "asset-type", "index": ALL}, "value"),
    Input({"type": "loan-product", "index": ALL}, "value"),
    Input({"type": "face", "index": ALL}, "value"),
    Input({"type": "term", "index": ALL}, "value"),
    Input({"type": "fixed-rate", "index": ALL}, "value"),
    Input({"type": "var-store", "index": ALL}, "data"),
    # Tranche check
    Input({"type": "tranche-row", "index": ALL}, "style"),
    Input({"type": "tranche-notional", "index": ALL}, "value"),
    Input({"type": "tranche-rate", "index": ALL}, "value"),
    prevent_initial_call=False
)
def _toggle_run_button(
        loan_styles, asset_types, products, faces, terms, fixed_rates, var_stores,
        tranche_styles, tranche_notionals, tranche_rates
):
    # Handle None lists (user hasn't added yet)
    loan_styles = loan_styles or []
    asset_types = asset_types or []
    products = products or []
    faces = faces or []
    terms = terms or []
    fixed_rates = fixed_rates or []
    var_stores = var_stores or []

    tranche_styles = tranche_styles or []
    tranche_notionals = tranche_notionals or []
    tranche_rates = tranche_rates or []


    # Compute visible loans
    loan_visible_idxs = [i for i, st in enumerate(loan_styles) if _is_visible(st)]
    tranche_visible_idxs = [i for i, st in enumerate(tranche_styles) if _is_visible(st)]

    # If we don't have 1 of each...
    if len(loan_visible_idxs) == 0 or len(tranche_visible_idxs) == 0:
        return True, "Add at least one loan and one tranche"


    # Loan validity
    any_valid_loan = False
    for i in loan_visible_idxs:
        at = (asset_types[i] if i < len(asset_types) else None)
        pr = (products[i] if i < len(products) else None)
        fc = (faces[i] if i < len(faces) else None)
        tm = (terms[i] if i < len(terms) else None)
        fr = (fixed_rates[i] if i < len(fixed_rates) else None)
        vs = (var_stores[i] if i < len(var_stores) else None)
        try:
            face_ok = (fc is not None) and (float(fc) > 0)
            term_ok = (tm is not None) and (float(tm) > 0)
        except Exception:
            face_ok = term_ok = False


        has_rate = False
        if pr and "variable" in str(pr).lower():
            has_rate = bool(vs) and (len(vs) > 0)
        else:
            try:
                has_rate = (fr is not None) and (float(fr) >= 0)
            except Exception:
                has_rate = False


        # Check all good
        if at and pr and face_ok and term_ok and has_rate:
            any_valid_loan = True
            break

    if not any_valid_loan:
        return True, "Complete at least one visible loan (face, term, rate). "



    # Tranche validity
    any_valid_tranche = False
    for j in tranche_visible_idxs:
        nt = (tranche_notionals[j] if j < len(tranche_notionals) else None)
        rt = (tranche_rates[j] if j < len(tranche_rates) else None)
        try:
            notional_ok = (nt is not None) and (float(nt) > 0)
            rate_ok = (rt is not None)
        except Exception:
            notional_ok = rate_ok = False


        if notional_ok and rate_ok:
            any_valid_tranche = True
            break

    if not any_valid_tranche:
        return True, "Enter at least one visible tranche (notional, rate). "


    # ALL GOOD?
    return False, ""



@callback(
    Output("waterfall-results", "data"),
    Output("app-input-snapshot", "data"),
    Input("run-waterfall", "n_clicks"),
    # Loans (States)
    State({"type": "loan-row", "index": ALL}, "style"),
    State({"type": "asset-type", "index": ALL}, "value"),
    State({"type": "asset-subtype", "index": ALL}, "value"),
    State({"type": "loan-product", "index": ALL}, "value"),
    State({"type": "face", "index": ALL}, "value"),
    State({"type": "term", "index": ALL}, "value"),
    State({"type": "fixed-rate", "index": ALL}, "value"),
    State({"type": "var-store", "index": ALL}, "data"),
    # Tranches (States)
    State({"type": "tranche-row", "index": ALL}, "style"),
    State({"type": "tranche-notional", "index": ALL}, "value"),
    State({"type": "tranche-rate", "index": ALL}, "value"),
    State({"type": "tranche-label", "index": ALL}, "value"),
    State("global-mode", "value"),
    prevent_initial_call=True
)
def _build_and_run(
        n_clicks,
        loan_styles, asset_types, asset_subtypes, products, faces, terms, fixed_rates, var_stores,
        tranche_styles, tranche_notionals, tranche_rates, tranche_labels,
        global_mode_value
):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    # Normalize ararys
    loan_styles = loan_styles or []
    asset_types = asset_types or []
    asset_subtypes = asset_subtypes or []
    products = products or []
    faces = faces or []
    terms = terms or []
    fixed_rates = fixed_rates or []
    var_stores = var_stores or []

    tranche_styles = tranche_styles or []
    tranche_notionals = tranche_notionals or []
    tranche_rates = tranche_rates or []
    tranche_labels = tranche_labels or []


    # --- Builds Loans ---
    loan_visible_idxs = [i for i, st in enumerate(loan_styles) if _is_visible(st)]
    loans = []
    loan_snapshot = []

    for i in loan_visible_idxs:
        at = (asset_types[i] if i < len(asset_types) else None)
        sub = (asset_subtypes[i] if i < len(asset_subtypes) else None)
        pr = (products[i] if i < len(products) else None)
        fc = (faces[i] if i < len(faces) else None)
        tm = (terms[i] if i < len(terms) else None)
        fr = (fixed_rates[i] if i < len(fixed_rates) else None)
        vs = (var_stores[i] if i < len(var_stores) else None)

        # Skip incomplete
        if not (at and pr and fc is not None and tm is not None):
            continue

        asset_obj = _build_asset(at, sub, fc)
        try:
            loan_obj = _build_loan(at, pr, asset_obj, fc, tm, fr, vs)
        except Exception as e:
            # Incomplete row w
            continue

        loans.append(loan_obj)
        loan_snapshot.append({
            "asset-type": at, "asset-subtype": sub, "product": pr,
            "face": fc, "term": tm,
            "fixed-rate": fr,
            "var-ranges": vs or []
        })


    if not loans:
        return dash.no_update, dash.no_update


    lp = LoanPool(loans)



    # --- Build Structured Securities ---
    tranche_visible_idxs = [j for j, st in enumerate(tranche_styles) if _is_visible(st)]

    # Get visible ones
    t_rows = []
    for j in tranche_visible_idxs:
        label = (tranche_labels[j] if j < len(tranche_labels) else None)
        nt = (tranche_notionals[j] if j < len(tranche_notionals) else None)
        rt = (tranche_rates[j] if j < len(tranche_rates) else None)
        if label is None:
            label = f"T{j+1}"

        # Skip incomplete
        try:
            nt_val = float(nt)
            rt_val = float(rt)
        except Exception:
            continue

        # Skip neg notional
        if nt_val <= 0:
            continue
        # Add it
        t_rows.append({"label": str(label), "notional": nt_val, "rate": rt_val, "row_index": j})

    if not t_rows:
        return dash.no_update, dash.no_update


    # Handle notionals --> required rate formats (see structured_securities_class.py: addTranche)
    total_notional_sum = sum(t["notional"] for t in t_rows)

    # Sub by label
    labels = [t["label"] for t in t_rows]
    label_to_rank = _compute_subordination_order(labels)

    # Sort final
    t_rows_sorted = sorted(
        t_rows,
        key=lambda t: (label_to_rank.get(t["label"], 9999), t["row_index"])
    )

    ss = StructuredSecurities(total_notional_sum)
    # Forcing... will revisit the whole mode setting later
    # Involves updating layout too lmaoo... got ahead of myself with "Details" wanting to make it symmetric with Loan half
    ## Updated!!
    # Check sequential input
    chosen_mode = str(global_mode_value).lower()
    ss.setMode("Sequential")
    if chosen_mode == "pro_rata":
        ss.setMode("Pro Rata")
    # Check pro rata from user input
    elif chosen_mode == "sequential":
        ss.setMode("Sequential")
    # Default to sequential (when other modes potentially added)
    else:
        ss.setMode("Sequential")



    # Add tranches
    ordered_labels = []
    for t in t_rows_sorted:
        pct = t["notional"] / total_notional_sum if total_notional_sum > 0 else 0.0
        subordination = label_to_rank.get(t["label"], 9999)
        ss.addTranche(percent_notional=pct, rate=t["rate"], subordination=subordination)
        ordered_labels.append(t["label"])


    # --- Run Waterfall ---
    liability_rows = doWaterfall(lp, ss)


    # Chatted... some JSON voodoo
    rows_serializable = []
    for per in liability_rows:
        rows_serializable.append([list(x) for x in per])


    # Snapshot for reproducibility
    snap = {
        "loans": loan_snapshot,
        "tranches": t_rows_sorted,
        "total_notional": total_notional_sum,
        "ordered_labels": ordered_labels,
        "mode": chosen_mode
    }


    return {"labels": ordered_labels, "rows": rows_serializable}, snap


# ===== RENDER RESULTS TABLE =====
@callback(
    Output("waterfall-output", "children"),
    Input("waterfall-results", "data")
)
def _render_results_table(data):
    if not data:
        return []

    labels = data.get("labels") or []
    rows = data.get("rows") or []


    if not labels or not rows:
        return []


    # Build header rows: Period --> Tranche Titles
    header_row1 = [html.Th("Period", style={"textAlign": "left", "padding": "6px"})]
    for lbl_idx, lbl in enumerate(labels):
        header_row1.append(
            html.Th(
                f"Tranche {lbl}",
                colSpan=5,
                style={
                    "textAlign": "center",
                    "padding": "6px",
                    "borderLeft": "3px solid #444" if lbl_idx > 0 else "1px solid #ccc",
                    "borderBottom": "1px solid #999"
                },
            )
        )


    # Subheader: repeated 5-list per tranche
    subcols = ["Interest Due", "Interest Paid", "Interest Shortfall", "Principal Paid", "Balance"]
    header_row2 = [html.Th("", style={"padding": "6px"})]
    for lbl_idx, _ in enumerate(labels):
        for k, sc in enumerate(subcols):
            header_row2.append(
                html.Th(
                    sc,
                    style={
                        "textAlign": "right" if sc != "Interest Due" else "left",
                        "padding": "6px", # Thick at tranche boundary, thin inside
                        "borderLeft": (
                            "3px solid #444" if k == 0 and lbl_idx > 0 else "1px solid #eee"
                        ),
                    }
                )
            )

    thead = html.Thead([
        html.Tr(header_row1, style={"background": "#f7f7f7"}),
        html.Tr(header_row2, style={"background": "#fafafa"})
    ])


    # Body rows per period
    body_rows = []
    for period_idx, period_data in enumerate(rows, start=1):
        row_cells = [html.Td(period_idx, style={"padding": "6px"})]

        for t_idx, t_values in enumerate(period_data):
            # Force 5 if some random splicing
            vals = list(t_values)[:5] + [None] * max(0, 5 - len(list(t_values)))
            for k, v in enumerate(vals):
                style={
                    "padding": "6px",
                    "textAlign": "right",
                    "borderLeft": ("3px solid #444" if k == 0 and t_idx > 0 else "1px solid #eee"),
                }
                # Align first metric left in tranche block
                if k == 0:
                    style["textAlign"] = "left"
                row_cells.append(html.Td(v, style=style))
        body_rows.append(html.Tr(row_cells))


    table = html.Table(
        [thead, html.Tbody(body_rows)],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "border": "1px solid #ccc"
        }
    )


    return [
        html.H3("Waterfall Results", style={"marginTop": "0"}),
        table
    ]





# yeet


# def add_loan_row(n_clicks, children):
#     # Index trio by id
#     next_idx = (len(children) if children else 0) + 1
#     # # Append new one
#     # children.append(make_loan_row(next_idx))
#     # Instead of appending, return new (maintain session)
#     return (children or []) + [make_loan_row(next_idx)]







if __name__ == "__main__":
    app.run(debug=True)
