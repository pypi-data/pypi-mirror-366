"""Movies fetcher page"""

import hashlib
import io
import json
import webbrowser
from copy import deepcopy
from datetime import datetime

import pandas as pd
import pycountry
import streamlit as st
from devs.moviemanager import MovieFetcher
from pages import CSS, auto_size_js, moviefetcher_col_config
from pages.initilizer import initialize_file_manager
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from st_pages import add_page_title

initialize_file_manager()


class MovieFetcherAssist(object):
    """streamlit assist class for fetching movies for a given year and language"""
    def __init__(self):
        self.clear_logs()  # browser logs clearance button at top right corner
        add_page_title(layout='wide')
        # st.set_page_config(page_title='Movies Fetcher', page_icon=':label:')
        st.markdown(CSS, unsafe_allow_html=True)
        movie_cols = [
            'title', 'id', 'release_date', 'runtime', 'type', 'rating', 'vote_count',
            'cast', 'overview', 'genres'
        ]
        cols_str = f'''
            <li><strong>
                <span style='color:gray;'>{
                    " | ".join([col for col in movie_cols])}
                </span>
            </strong></li>'''
        st.markdown(
            '''
            <style>
                div[class*="stTextInput"] div[data-testid="stMarkdownContainer"] > p {
                    font-family: sans-serif;
                    font-weight: bold;
                    font-size: 16px;
                    color: darkslategray;
                }
                div[class*="stNumberInput"] div[data-testid="stMarkdownContainer"] > p {
                    font-family: sans-serif;
                    font-weight: bold;
                    font-size: 16px;
                    color: darkslategray;
                }
                div[class*="stSelect"]>label>div[data-testid="stMarkdownContainer"]>p {
                    font-family: sans-serif;
                    font-weight: bold;
                    font-size: 16px;
                    color: darkslategray;
                }
                div[data-testid="stCheckbox"] label {
                    font-family: sans-serif; !important;
                    font-weight: bold; !important;
                    font-size: 16px; !important;
                    color: darkslategray; !important;
                }
                .stSubmitButton, div.stButton {
                    text-align:right;
                }
            </style>
            ''', unsafe_allow_html=True
        )
        st.markdown('<h2 class="head-h2">Extract movies metadata</h2>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="para-p1">
                Fetch and enrich movies metadata using <strong>TMDb</strong> and <strong>IMDb</strong> for a selected year and language.
                <ul>
                    <li><strong>Discover movies</strong> released in a specific year & language via TMDb API</li>
                    <li><strong>Enrich metadata</strong> using IMDb rating and cast info via web scraping</li>
                    <li><strong>Get structured insights</strong> for each movie, including:
                        <ul>
                            {cols_str}
                        </ul>
                    </li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)

        # ---------------------------------
        # Define global variables
        self.lang_options = {
            f'{lang.name} ({lang.alpha_2})': lang.alpha_2
            for lang in pycountry.languages
            if hasattr(lang, 'alpha_2')
        }
        self.lang_options["Other"] = 'Other'
        self.year_options = list(range(datetime.now().year + 3, 1900, -1))
        self.page_options = list(range(1, 21))

    def clear_logs(self):
        """Utility func for logs and cache clearance"""
        cols = st.columns([8, 2])
        with cols[1]:
            if st.button('🗑️ Clear logs', key='clear_button', type='primary'):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.session_state.clear()
                st.rerun()  # rerun entire script

    def display_params_header(self, label, help='', **kwargs):
        """Title to display for params input section"""
        st.markdown(
            f'''
                <p style="
                    margin-top: {kwargs.get("top", '0em')};
                    margin-bottom: {kwargs.get("bottom", '0em')};
                    font-family: {kwargs.get("family", 'sans-serif')};
                    font-weight: {kwargs.get("weight", 'normal')};
                    font-size: {kwargs.get("size", '20px')};
                    color: {kwargs.get("color", 'DodgerBlue')};
                ">
                    {label}
                </p>
            ''',
            help=help,
            unsafe_allow_html=True
        )

    def get_params(self):
        """Get params for movies extraction"""
        # ---------------------------------
        # Take input params
        cols = st.columns([0.3, 0.3, 0.4])
        with cols[0]:
            year = st.selectbox("Release year", self.year_options, index=3)
            lang_list = list(self.lang_options.keys())
            lang_label = st.selectbox("Language", lang_list, index=lang_list.index('English (en)'))
            language = (
                st.text_input("Enter ISO 639-1 language code (e.g. ja, de, ru)").strip()
                if self.lang_options[lang_label] == 'Other'
                else self.lang_options[lang_label]
            )
        with cols[1]:
            max_pages = st.selectbox("Total pages to search for", self.page_options, index=0)
            sort_by = st.selectbox(
                "Sort movies list by",
                options=('rating', 'release_date', 'runtime'),
                index=0
            )

        with cols[2]:
            self.display_params_header("Fetch metadata in en", size='16px', weight='bold', color='darkslategray')
            en_info = st.radio(
                "Fetch metadata in en",
                [True, False],
                index=1,
                horizontal=True,
                label_visibility='collapsed'
            )
            self.display_params_header("Save as", size='16px', weight='bold', top='-0.5em', color='darkslategray')
            save_option = st.radio(
                "Save option",
                ['json', 'excel', 'none'],
                index=1,
                horizontal=True,
                label_visibility='collapsed'
            )

        # ---------------------------------
        # Get the hash fingerprint of param state
        param_state = {
            "year": year,
            "language": language,
            "en_info": en_info,
            "sort_by": sort_by,
            "max_pages": max_pages,
            "save_option": save_option
        }
        param_hash = hashlib.md5(json.dumps(param_state, sort_keys=True).encode()).hexdigest()

        return param_state, param_hash

    def execute_on_submit(self, **kwargs):
        """Run movie fetcher fom `MovieFetcher` class on clicking 'Submit' button"""
        if st.button('Submit'):
            st.session_state.submit_button = True
            st.session_state.just_finished = False

            fetcher = MovieFetcher(
                api_key=st.secrets["tmdb_api_key"],
                year=kwargs.get("year", datetime.now().year),
                language=kwargs.get("language", 'en'),
                en_info=kwargs.get("en_info", True),
                sort_by=kwargs.get("sort_by", 'rating'),
                max_pages=kwargs.get("max_pages", 2)
            )
            fetcher.fetch()
            st.session_state.update({
                "fetched_movies": fetcher.all_movies,
                "movies_data": pd.DataFrame([
                    {k: v for k, v in meta.items() if k in moviefetcher_col_config}
                    for meta in fetcher.all_movies
                ]),
                "elapsed_tstr": fetcher.run_time
            })

            st.session_state.just_finished = True  # reset session state here

    def display_data(self, input_data, **kwargs):
        """Display fetched movies data with option of opening few movies (IMDb link)

        Parameters:
            input_data (pd.DataFrame): Data to display.
            col_config (dict, optional): Column configuration. Defaults to empty dict.
            ```
            Format:
                {
                    'col_name_1': {'editable': True/False, 'cellStyle': {...}, 'maxWidth': int, ...},
                    'col_name_2': {'editable': True/False, 'cellStyle': {...}, 'maxWidth': int, ...},
                    ...
                }
            ```
            show_title (bool, optional): Whether to show title for table display. Defaults ton `True`.
            page_size (int, optional): Number of rows per page in pagination. Defaults to 10.
            height (int, optional): Height of the grid in pixels. Defaults to 350.

        Returns:
            pd.DataFrame: Edited data.
        """
        edited_data = pd.DataFrame()
        if input_data is not None:
            if kwargs.get("show_title", True):
                title_text = f'''🎯 {input_data.shape[0]} {kwargs.get("language", '')} movies fetched for the year {kwargs.get("year")}👇'''
                self.display_params_header(title_text, top='1em', bottom='0.5em', size='16px', weight='bold', color='darkslategray')

            # ---------------------------------
            # Form the AgGrid obj through col configs
            gb = GridOptionsBuilder.from_dataframe(input_data)
            for col, config in kwargs.get("col_config", {}).items():
                gb.configure_column(
                    field=col,
                    editable=config.get("editable", False),
                    cellStyle=config.get("cellStyle", {}),
                    maxWidth=config.get("maxWidth"),
                    width=config.get("width"),
                    cellEditor=config.get("cellEditor"),
                    cellRenderer=config.get("cellRenderer", None),
                    cellEditorParams=config.get("cellEditorParams", None),
                    filter=config.get("filter", None),
                    suppressMenu=config.get("suppressMenu", False),
                    suppressMovable=config.get("suppressMovable", False),
                    checkboxSelection=config.get("checkboxSelection", False),
                    headerCheckboxSelection=config.get("headerCheckboxSelection", False),
                )
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=kwargs.get("page_size", 10))
            gb.configure_selection(selection_mode="multiple", use_checkbox=False)
            grid_options = gb.build()

            # ---------------------------------
            # Render AgGrid
            grid_response = AgGrid(
                input_data,
                gridOptions=grid_options,
                custom_js={"onGridReady": eval(auto_size_js)},
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                allow_unsafe_jscode=True,
                fit_columns_on_grid_load=False,
                enable_enterprise_modules=False,
                theme="streamlit",
                height=kwargs.get("height", 350)
            )

            # ---------------------------------
            # Get edited data
            selected_rows = grid_response.get("selected_rows")
            selected_rows = (
                selected_rows
                .to_dict(orient='records') if isinstance(selected_rows, pd.DataFrame)
                else (selected_rows or [])
            )
            edited_data = pd.DataFrame(selected_rows)

        return edited_data

    def open_movie_link(self, name: str, imdb_id: str = '', tmdb_id: str = '', new: int = 2):
        """
        Open the IMDb (preferred) or TMDb (fallback) movie URL in the system's default web browser.

        Parameters
        ----------
        name (str) : The name of the movie to open (used for message only).
        imdb_id (str, optional) : IMDb ID (e.g., 'tt1375666'). Used first if available.
        tmdb_id (str, optional) : TMDb ID (e.g., '12345'). Used only if IMDb is missing.
        new (int) : 0 -> same window, 1 -> new window, 2 -> new tab (default)

        Yields
        ------
        str
            Success or failure message.
        """
        if isinstance(imdb_id, str) and imdb_id.startswith("tt"):
            url = f"https://www.imdb.com/title/{imdb_id}/"
            msg = f"✅ Successfully opened IMDb page for: '{name}'"
        elif isinstance(tmdb_id, int):
            url = f"https://www.themoviedb.org/movie/{tmdb_id}"
            msg = f"⚠️ IMDb ID missing — opened TMDb page for: '{name}'"
        else:
            yield f"❌ No valid IMDb or TMDb ID found for the movie: '{name}'"
            return

        try:
            if webbrowser.open(url, new=new):
                yield msg
            else:
                yield f"❌ Failed to open URL for: '{name}'"
        except Exception:
            yield f"❌ Error occurred while trying to open URL for: '{name}'"

    def save_output(self, save_type='excel'):
        """Saves generated summary as json|excel|both (for mover utility)"""
        if st.session_state.just_finished and save_type:
            fetched_movies = st.session_state.get("fetched_movies", [])
            json_bytes = json.dumps(fetched_movies, indent=4).encode("utf-8")
            df_fetched = pd.DataFrame(fetched_movies)
            excel_buffer = io.BytesIO()
            df_fetched.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            cols = st.columns([0.75, 0.25])

            # ---------------------------------
            # Save summary output based on intended save type
            if save_type == 'json':
                with cols[1]:
                    st.download_button(
                        "Download movies JSON",
                        json_bytes,
                        'movie_summary.json',
                        'application/json',
                        type='primary'
                    )
            elif save_type == 'excel':
                with cols[1]:
                    st.download_button(
                        "Download movies Excel",
                        excel_buffer,
                        'movie_summary.xlsx',
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        type='primary'
                    )

    def fetch(self):
        """Fetch movies by year & language with enriched metadata info"""
        self.display_params_header('Provide required params here👇', bottom='0.5em')
        param_state, param_hash = self.get_params()
        # ---------------------------------
        # Fresh execute movies fetcher thriugh user input params
        if st.session_state.get("last_param_hash") != param_hash:
            st.session_state.update({
                "just_finished": False,
                "fetched_movies": [],
                "movies_data": pd.DataFrame(),
                "elapsed_tstr": '',
                "log_lines": [],
                "last_param_hash": param_hash  # update hash
            })
        self.execute_on_submit(**param_state)

        # ---------------------------------
        # Display elapsed time
        if st.session_state.get("elapsed_tstr"):
            elapsed_tstr = f'''--------Movies fetching completed in: {st.session_state.get("elapsed_tstr")}'''
            st.markdown(
                f'''<div class='output-card-3'>
                    {elapsed_tstr}
                </div>''', unsafe_allow_html=True
            )

        # ---------------------------------
        # Display (and optionally open few) movies list
        edited_data = pd.DataFrame()
        language = next((lang.name for lang in pycountry.languages if
                         getattr(lang, 'alpha_2', '') == param_state["language"]), '')
        if not st.session_state.get("movies_data", pd.DataFrame()).empty:
            col_config = deepcopy(moviefetcher_col_config)
            col_config["title"].update({"checkboxSelection": True, "headerCheckboxSelection": True})
            edited_data = self.display_data(
                st.session_state.get("movies_data", pd.DataFrame()),
                col_config=col_config,
                show_title=True,
                page_size=10,
                height=350,
                year=param_state["year"],
                language=language
            )

        # ---------------------------------
        # Open movie url (IMDb|TMDb) and display success/failure logs
        if (edited_data is not None) and (not edited_data.empty) and st.button('Open'):
            st.session_state.log_lines = []
            for row in edited_data.itertuples(index=False):
                log_line = next(self.open_movie_link(row.title, row.imdb_id, row.tmdb_id)).rstrip('\n')
                st.session_state.log_lines.append(log_line)
        if st.session_state.get("log_lines"):
            st.markdown("```\n" + "\n".join(st.session_state.log_lines) + "\n```")

        # ---------------------------------
        # Save fetched movies JSON/excel
        self.save_output(param_state["save_option"])

    def main_executor(self):
        """The main module that performs all tasks and displays to page"""
        if st.checkbox(r'$\textsf{\textbf{\large \color{DodgerBlue}Proceed to fetch movies}}$'):
            self.fetch()


# +++++++++++++++++
# The main streamlit operations for this page
if __name__ == "__main__":
    MovieFetcherAssist().main_executor()
