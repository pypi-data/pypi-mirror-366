"""Global options for streamlit pages"""

CSS = """
    <style>
    .head-h2 {
        text-align: left;
        margin-top: -2em;
        font-family: sans-serif;
        font-weight: normal;
        font-size: 24px;
    }
    .para-p1 {
        text-align: left;
        margin-top: -1em;
        line-height: 22px;
        font-family: sans-serif;
        font-weight: normal;
        font-size: 16px;
    }
    .para-p1 ul li {
        list-style-type:disc;
        line-height: 20px;
        margin-left: 30px;
        padding-left:20px
        font-family: sans-serif;
        font-weight: 500;
        font-size: 14px;
        color: DimGrey;
    }
    .para-p1 li:before {
        content: "";
        margin-left: -0.5rem;
    }
    .profile-card {
        margin-top: -1em;
        margin-bottom: 1em;
        # margin: 10px;
        background: LightYellow;
        box-shadow: inset 2px 2px 5px 0px #dddddd;
        height: 100px;
        width: 750px;
        overflow: auto;
        padding: 5px 5px;
        font-family: tahoma;
        # font-family: Lucida Console;
        font-weight: 500;
        font-size: 13px;
        color: MediumBlue;
        border: 1px solid #aaa;
    }
    .profile-card ul li {
        list-style-type:disc;
        margin-left: 30px;
        padding-left:20px
        font-family: tahoma;
        font-weight: 500;
        font-size: 13px;
        color: MediumBlue;
    }
    .profile-card li:before {
        content: "";
        margin-left: -0.5rem;
    }
    .output-card-1 {
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        # margin: 10px;
        background: LightYellow;
        box-shadow: inset 2px 2px 5px 0px #dddddd;
        height: 70px;
        width: 500px;
        overflow: auto;
        padding: 10px 10px;
        font-family: tahoma;
        font-weight: 500;
        font-size: 13px;
    }
    .output-card-2 {
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        # margin: 10px;
        background: LightYellow;
        box-shadow: inset 2px 2px 5px 0px #dddddd;
        height: 40px;
        width: 375px;
        # overflow: auto;
        padding: 10px 10px;
        font-family: tahoma;
        font-weight: 500;
        font-size: 13px;
    }
    .output-card-3 {
        background-color: Cornsilk;
        # border-left: 5px solid #f1c40f;
        box-shadow: inset 2px 2px 5px 0px #dddddd;
        padding: 10px 10px;
        margin-top: 10px;
        margin-bottom: 10px;
        font-family: monospace;
        font-size: 14px;
        font-weight: bold;
    }
    div[class*="stRadio"]>label>div[data-testid="stMarkdownContainer"]>p {
        font-family: sans-serif;
        font-weight: normal;
        font-size: 20px;
        color: DodgerBlue;
    }
    [role=radiogroup] {
        margin-top: -1.5em;
        gap: 5px;
        padding: 25px;
    }
    div[class*="stSelect"]>label>div[data-testid="stMarkdownContainer"]>p {
        font-family: sans-serif;
        font-weight: normal;
        font-size: 16px;
        color: DodgerBlue;
    }
    div[class*="stTextArea"] label {
        font-size: 20px !important;
        color: black;
    }
    div[class*="stTextInput"] label {
        font-size: 20px !important;
        color: black;
    }
    </style>
    """

# Static table display style
static_table_style = [
    {
        "selector": "tr",
        "props": [('line-height', '16px'), ('max-height', '16px')]
    },
    {
        "selector": "th",
        "props": [
            ('font-family', 'sans-serif'),
            ('font-weight', 'normal'),
            ('font-size', '14px'),
            ('text-align', 'left'),
            ('font-weight', 'bold'),
            ('color', '#6d6d6d'),
            ('line-height', 'inherit'),
            ('max-height', 'inherit'),
            ('overflow', 'auto'),
            ('background-color', 'LightCyan')
        ]  # table header
    },
    {
        "selector": "td",
        "props": [
            ('font-family', 'sans-serif'),
            ('font-weight', 'normal'),
            ('font-size', '14px'),
            ('line-height', 'inherit'),
            ('max-height', 'inherit'),
            ('white-space', 'nowrap'),
            ('overflow', 'auto')
            # ('font-weight', 'bold')
        ]  # table data
    }
]


# JS codes for setting col_config
auto_size_js = '''
JsCode("""
    function(e) {
        let allColumnIds = [];
        e.columnApi.getAllColumns().forEach(function(column) {
            allColumnIds.push(column.colId);
        });
        e.api.autoSizeColumns(allColumnIds, false);
    }
""")
'''
checkbox_renderer = '''
JsCode("""
    class ColoredCheckboxRenderer {
        init(params) {
            this.eGui = document.createElement('span');
            this.eGui.innerHTML = `
            <input type="checkbox" ${params.value ? "checked" : ""}
                style="accent-color: #32CD32; transform: scale(1.1);" disabled />
            `;
        }
        getGui() {
            return this.eGui;
        }
    }
""")
'''

# Cols config for files manager
filesmanager_col_config = {
    "file_name": {
        "editable": False,
        "cellStyle": {
            "userSelect": "text",
            "cursor": "text",
            "background-color": 'LightCyan'
        }
    },
    "new_name": {"editable": True},
    "file_ext": {"editable": False, "maxWidth": 80},
    "file_size_bytes": {"editable": False, "maxWidth": 80},
    "file_size": {"editable": False, "maxWidth": 80},
    "confirm_delete": {
        "editable": False,
        "cellRenderer": "agCheckboxCellRenderer",
        "headerCheckboxSelection": True,
        "checkboxSelection": True,
        "suppressMenu": True,
        "suppressMovable": True,
        "width": 120
    },
    "file_path": {
        "editable": False,
        "cellStyle": {
            "userSelect": "text",
            "cursor": "text",
            "backgroundColor": "#F9F9F9"
        }
    }
}

# Cols config for movies fetcher
moviefetcher_col_config = {
    "title": {
        "editable": True,
        "cellStyle": {
            "userSelect": 'text',
            "cursor": 'text',
            "background-color": 'LightCyan'
        }
    },
    "imdb_id": {"editable": True, "maxWidth": 100},
    "tmdb_id": {"editable": True, "filter": 'agNumberColumnFilter', "maxWidth": 100},
    "release_date": {"editable": False, "filter": 'agTextColumnFilter'},
    "countries": {"editable": True, "filter": 'agTextColumnFilter', "maxWidth": 80},
    "runtime": {"editable": False, "filter": 'agTextColumnFilter', "maxWidth": 60},
    "rating": {"editable": False, "filter": 'agNumberColumnFilter', "maxWidth": 80},
    "vote_count": {"editable": False, "filter": 'agNumberColumnFilter', "maxWidth": 100},
    "rating_source": {"editable": False, "maxWidth": 100},
    "cast": {"editable": True, "filter": 'agTextColumnFilter'},
    "genres": {"editable": True, "filter": 'agTextColumnFilter', "maxWidth": 160},
}
