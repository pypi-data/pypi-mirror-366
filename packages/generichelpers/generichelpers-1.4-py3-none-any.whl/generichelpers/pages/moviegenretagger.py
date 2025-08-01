"""Movies genre-tagger page"""

import io
import json
import os
import re
import zipfile

import pandas as pd
import streamlit as st
from configs import CONFIG
from devs.moviemanager import MovieLibraryManager
from pages import CSS
from pages.initilizer import initialize_file_manager
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_pages import add_page_title

initialize_file_manager()


class GenreTaggerAssist(object):
    """streamlit assist class for sorting movie files/folders/listing"""
    def __init__(self):
        self.clear_logs()  # browser logs clearance button at top right corner
        add_page_title(layout='wide')
        # st.set_page_config(page_title='Genre Tagger', page_icon=':label:')
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown(
            '''
            <style>
                div[class*="stTextInput"] div[data-testid="stMarkdownContainer"] > p {
                    font-family: sans-serif;
                    font-weight: bold;
                    font-size: 16px !important;
                    color: darkslategray !important;
                }
                div[class*="stSelect"]>label>div[data-testid="stMarkdownContainer"]>p {
                    font-family: sans-serif;
                    font-weight: bold;
                    font-size: 16px !important;
                    color: darkslategray !important;
                }
                div[class*="stExpander"] > label>div[data-testid="stMarkdownContainer"]>p {
                    font-family: sans-serif;
                    font-weight: bold;
                    font-size: 16px !important;
                    color: darkslategray !important;
                }
                .stSubmitButton, div.stButton {
                    text-align:right;
                }
            </style>
            ''', unsafe_allow_html=True
        )
        st.markdown('<h2 class="head-h2">Tag genres to movies</h2>', unsafe_allow_html=True)
        st.markdown('''
            <div class="para-p1">
                This app tags movie folders or files with genres scraped from <em>Wikipedia</em>:
                <ul>
                    <li><strong>Scans to detect all movie folders and files</strong></li>
                    <li><strong>Cleans movie names and extracts year</strong></li>
                    <li><strong>Builds + searches <em>Wikipedia</em> URLs for genres</strong></li>
                    <li><strong>Updates movie names with cleaned genre info</strong></li>
                    <li><strong>Moves updated movie folders/files if not in <em>dry_run</em> mode.</strong></li>
                </ul>
            </div>''', unsafe_allow_html=True)

    def clear_logs(self):
        """Utility func for logs and cache clearance"""
        cols = st.columns([8, 2])
        with cols[1]:
            if st.button('🗑️ Clear logs', key='clear_button', type='primary'):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.session_state.clear()
                st.rerun()  # rerun entire script

    def display_params_header(self, title, margin_bottom='-1em'):
        """Title to display for params input section"""
        st.markdown(
            f'''
                <p style="
                    margin-top: 0.5em;
                    margin-bottom: {margin_bottom};
                    font-family: sans-serif;
                    font-weight: bold;
                    font-size: 13px !important;
                    color: darkslategray !important;
                ">
                    {title}
                </p>
            ''',
            unsafe_allow_html=True
        )

    def get_params(self, utility='tag'):
        """Get input params for genre tagging/stripping"""
        bracket_type, path_label, path_help, genre_change = 'curly', '', '', ''
        cols = st.columns(
            [0.5, 0.5] if utility == 'untag'
            else [0.3, 0.3, 0.4] if utility == 'tag'
            else [0.25, 0.25, 0.25, 0.25]
        )
        # ---------------------------------
        # Logs & mode
        with cols[0]:
            self.display_params_header("Logs and mode", '0.5em')
            write_logs = st.checkbox("Write logs to file", value=True)
            dry_run = st.checkbox("Dry-run mode", value=True)

        # ---------------------------------
        # Save option
        with cols[1]:
            self.display_params_header("Save option")
            save_summary = st.radio(
                "Save option",
                ['json', 'excel', 'both', "don't save"],
                index=1,
                label_visibility='collapsed'
            )

        # ---------------------------------
        # Get path label & path help strs
        path_label = (
            'Provide the base folder path :file_folder:' if utility == 'untag' else
            'Provide the base path for scanning movies :file_folder:' if utility == 'tag' else ''
        )
        if utility == 'tag':
            path_help = 'Can also give file (.json|.csv|.xlsx) path with movies in `movie_name` key/column'

        # ---------------------------------
        # Bracket style (for tag/move utilities)
        if utility in ('tag', 'move'):
            with cols[2]:
                self.display_params_header("Bracket style")
                bracket_type = st.radio(
                    "Bracket style:",
                    ['(round)', '{curly}', '[square]', '<angle>'],
                    index=1,
                    label_visibility='collapsed'
                )
        # ---------------------------------
        # Genre change checkbox (for move utility)
        if utility == 'move':
            with cols[3]:
                self.display_params_header("Genres map")
                genre_change = st.checkbox("Rename few genres", value=False)

        # ---------------------------------
        # Exxtract 'save_summary' & clean 'bracket_type'
        save_summary = {
            "json": 'json',
            "excel": 'excel',
            "both": True,
            "don't save": False
        }.get(save_summary, False)

        bracket_type = re.sub(r'[()\[\]{}<>]', '', bracket_type)

        return write_logs, dry_run, save_summary, bracket_type, path_label, path_help, genre_change

    def get_scan_path(self, label_str, help_str=''):
        """Get base_path & exclude_subdirs"""
        base_path, exclude_subdirs = '', []
        base_path = st.text_input(label=label_str, help=help_str)
        if os.path.isdir(base_path):
            all_subdirs = [
                d for d in os.listdir(base_path)
                if os.path.isdir(os.path.join(base_path, d))
            ]
            # Show only if subdirectories exist
            if all_subdirs:
                exclude_flag = st.checkbox("Want to exclude some subdirectories ?")
                if exclude_flag:
                    exclude_subdirs = st.multiselect(
                        label=r'$\textsf{\textbf{Select subdirectories to exclude👇}}$',
                        options=all_subdirs,
                        help="Leave empty if you don't want to exclude any subdirectories"
                    )
            else:
                st.info("No subdirectories found under this path.")
        return base_path, exclude_subdirs

    def get_genre_map(self):
        """Get `genre_map` dict for changing some genre names, based on user input"""
        genre_map = {}
        all_genres = sorted(st.session_state.mover_data['genre'].dropna().unique())
        if all_genres:
            self.display_params_header(f"🎯 Detected {len(all_genres)} unique genres. Update any you wish below👇", '0.5em')
            input_data = pd.DataFrame({
                "current_genre": all_genres,
                "changed_genre": all_genres   # pre-fill with current genre values
            })

            gb = GridOptionsBuilder()
            gb.from_dataframe(input_data)
            gb.configure_column("current_genre", editable=False, cellStyle={'background-color': 'LightCyan'})
            gb.configure_column("changed_genre", editable=True)
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
            grid_options = gb.build()

            edited_data = AgGrid(
                input_data,
                gridOptions=grid_options,
                update_mode=GridUpdateMode.VALUE_CHANGED,
                theme="streamlit",
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=False,
                height=350,
            )["data"]
            genre_map = edited_data.set_index("current_genre")["changed_genre"].to_dict()
        return genre_map

    def save_output(self, save_type='excel'):
        """Saves generated summary as json|excel|both (for mover utility)"""
        if save_type:
            json_bytes = json.dumps(self.summary, indent=4).encode("utf-8")
            df_summary = pd.DataFrame(self.summary)
            excel_buffer = io.BytesIO()
            df_summary.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            cols = st.columns([0.75, 0.25])

            # ---------------------------------
            # Save summary output based on intended save type
            if save_type == 'json':
                with cols[1]:
                    st.download_button(
                        "Download JSON Summary",
                        json_bytes,
                        'movie_summary.json',
                        'application/json',
                        type='primary'
                    )
            elif save_type == 'excel':
                with cols[1]:
                    st.download_button(
                        "Download Excel Summary",
                        excel_buffer,
                        'movie_summary.xlsx',
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        type='primary'
                    )
            elif save_type is True:
                # create zip for both json & excel
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    zf.writestr("movie_summary.json", json_bytes)
                    zf.writestr("movie_summary.xlsx", excel_buffer.read())
                zip_buffer.seek(0)

                with cols[1]:
                    st.download_button(
                        "Download .zip Summary (JSON + Excel)",
                        zip_buffer,
                        'movie_summary.zip',
                        'application/zip',
                        type='primary'
                    )

    def execute_on_submit(self, **kwargs):
        """Genre Tagger/stripper/mover utility to perform from base class on clicking 'Submit' button"""
        if st.button('Submit'):
            st.session_state.submit_button = True
            st.session_state.just_finished = False
            st.session_state.log_lines = []
            st.session_state.elapsed_tstr = ''
            st.session_state.summary_text = ''

            place_holder = st.empty()
            func_name = kwargs.get("func", 'tag')
            movie_manager = MovieLibraryManager(
                kwargs.get("base_path", ''),
                to_untag=kwargs.get("to_untag", False),
                genre_brackets=kwargs.get("bracket_type", 'curly'),
                exclude_subdirs=kwargs.get("exclude_subdirs", []),
                genre_map=kwargs.get("genre_map", {}),
                save_summary=kwargs.get("save_summary", False),
                write_logs=kwargs.get("write_logs", True),
                dry_run=kwargs.get("dry_run", False)
            )

            # ---------------------------------
            # Print live logs
            for line in getattr(movie_manager, func_name)():
                if 'time' in line:
                    st.session_state.elapsed_tstr = line
                else:
                    st.session_state.log_lines.append(line.rstrip('\n'))
                if not kwargs.get("invoke_saver", False):
                    place_holder.markdown("```\n" + "\n".join(st.session_state.log_lines) + "\n```")
            # ---------------------------------
            # Show summary download button (for mover utility)
            if kwargs.get("invoke_saver", False):
                st.markdown(
                    f'''<div class='output-card-3'>
                        {st.session_state.elapsed_tstr}
                    </div>''', unsafe_allow_html=True
                )
                self.summary, save_type = movie_manager.summary, kwargs.get("save_type", False)
                self.save_output(save_type)
                st.markdown("```\n" + "\n".join(st.session_state.log_lines) + "\n```")
                st.session_state.elapsed_tstr = ''
            # ---------------------------------
            # Gets summary output
            st.session_state.summary_text = "\n" + "="*120 + "\n"
            st.session_state.summary_text += "SUMMARY = \n"
            st.session_state.summary_text += json.dumps(movie_manager.summary, indent=4)

            # Reset session states here
            st.session_state.just_finished = True
            st.session_state.submit_button = False

        # ---------------------------------
        # - Prints logs, elapsed time, summary -- based on session state vars
        # - Also suppresses duplicate logs on immediate rerun
        if st.session_state.get("just_finished", False):
            st.session_state.just_finished = False
        else:
            if st.session_state.log_lines:
                st.markdown("```\n" + "\n".join(st.session_state.log_lines) + "\n```")
        if st.session_state.elapsed_tstr:
            st.markdown(
                f'''<div class='output-card-3'>
                    {st.session_state.elapsed_tstr}
                </div>''', unsafe_allow_html=True
            )
        if st.session_state.summary_text:
            st.markdown(f"```json\n{st.session_state.summary_text}\n```")

    def tag_movies(self, to_untag=False):
        """Tag movie files/folders and move"""
        params_label = 'Provide params for stripping existing movie genres👇' if to_untag \
            else 'Provide params for movie genre tagging👇'
        # ---------------------------------
        # Take input params
        st.markdown(
            '''
            <style>
                div[class*="stCheckbox"] {
                    margin-bottom: 0.1rem;
                }
            </style>
            ''', unsafe_allow_html=True
        )

        st.markdown(
            f'''
                <p style="
                    margin-top: -1.5em;
                    font-family: sans-serif;
                    font-weight: bold;
                    font-size: 16px !important;
                    color: darkslategray !important;
                ">
                    {params_label}
                </p>
            ''',
            unsafe_allow_html=True
        )
        utility = 'untag' if to_untag else 'tag'
        write_logs, dry_run, save_summary, bracket_type, path_label, path_help, _ = self.get_params(utility)
        base_path, exclude_subdirs = self.get_scan_path(path_label, path_help)

        # ---------------------------------
        # Run tagger utility
        params_dict = {
            "base_path": base_path,
            "to_untag": to_untag,
            "bracket_type": bracket_type,
            "exclude_subdirs": exclude_subdirs,
            "save_summary": save_summary,
            "write_logs": write_logs,
            "dry_run": dry_run
        }
        self.execute_on_submit(**params_dict)

    def move_movies(self):
        """Move renamed movies from old path to new path from an .xlsx|.csv file"""
        # ---------------------------------
        # Read the input csv/excel file for movies movement
        required_columns = CONFIG["mover_data_cols"]
        upload_file = st.file_uploader(
            '**Provide the `.csv`|`.xlsx` file for movies movement :spiral_note_pad:**',
            type=(['.csv', '.xlsx'])
        )
        findTotal = lambda col: len(tot) if (tot := sorted(st.session_state.mover_data[col].dropna().unique())) else 'no'
        st.session_state.mover_data = None
        if upload_file is not None:
            try:
                file_ext = upload_file.name.lower().split('.')[-1]
                st.session_state.mover_data = pd.read_csv(upload_file) if file_ext == 'csv' else pd.read_excel(upload_file)
            except Exception as e:
                st.warning(f"**:red[Error reading the file: {e}]**", icon="⚠️")
            if st.session_state.mover_data is not None and isinstance(st.session_state.mover_data, pd.DataFrame):
                num_movies, num_genres = findTotal('movie_name'), findTotal('genre')
                st.success(f"File loaded successfully: {num_movies} movies • {num_genres} genres. A snapshot below !", icon="✅")
                st.dataframe(st.session_state.mover_data.head())

                # +++++++++++++++++
                # Check for missing cols
                missing_cols = [
                    col for col in required_columns
                    if col not in st.session_state.mover_data.columns
                ]
                if missing_cols:
                    required_cols_str = ", ".join(f"**:blue[`{col}`]**" for col in required_columns)
                    missing_cols_str = ", ".join(f"**:blue[`{col}`]**" for col in missing_cols)
                    st.warning(
                        f'''
                            **:red[Input columns mismatch!]**
                            The data **must** include the following columns: {required_cols_str}.
                            **Missing column(s) detected:** {missing_cols_str}
                        ''',
                        icon="⚠️"
                    )
                else:
                    # ---------------------------------
                    # Get params for mover utility
                    genre_map = {}
                    st.markdown(
                        '''
                            <p style="
                                margin-top: 0.5em;
                                font-family: sans-serif;
                                font-weight: bold;
                                font-size: 16px !important;
                                color: darkslategray !important;
                            ">
                                Provide params for moving movie files/folders👇
                            </p>
                        ''',
                        unsafe_allow_html=True
                    )
                    write_logs, dry_run, save_summary, bracket_type, _, _, genre_change = self.get_params('move')
                    if genre_change and st.session_state.mover_data is not None:
                        genre_map = self.get_genre_map()

                    # ---------------------------------
                    # Run mover utility
                    params_dict = {
                        "func": 'move',
                        "invoke_saver": True,
                        "save_type": save_summary,
                        "prompt_logs": True,
                        "base_path": st.session_state.mover_data,
                        "bracket_type": bracket_type,
                        "genre_map": genre_map,
                        "write_logs": write_logs,
                        "dry_run": dry_run,
                    }
                    self.execute_on_submit(**params_dict)
                    st.session_state.log_lines = []
                    st.session_state.elapsed_tstr = ''
                    st.session_state.summary_text = ''
            else:
                st.warning("**:red[The input file is not valid, check again !]**", icon="⚠️")

    def main_executor(self):
        """The main module that performs all tasks and displays to page"""
        selected_op = st.radio(
            label='Select the desired movie genre-tagging operation to perform',
            options=(
                'Attach genre tags to movie files/folders',
                'Strip genre tags from movie files/folders',
                'Move movie files/folders from csv/excel input'
                ),
            index=None
        )
        # ---------------------------------
        # Detect change in operation
        if selected_op != st.session_state.get("selected_op"):
            # User switched operations → reset everything
            st.session_state.log_lines = []
            st.session_state.elapsed_tstr = ''
            st.session_state.summary_text = ''

        st.session_state.selected_op = selected_op  # store the current choice for next rerun

        # ---------------------------------
        # Route to the appropriate tagging function
        if selected_op == 'Attach genre tags to movie files/folders':
            self.tag_movies()
        elif selected_op == 'Strip genre tags from movie files/folders':
            self.tag_movies(to_untag=True)
        elif selected_op == 'Move movie files/folders from csv/excel input':
            self.move_movies()


# +++++++++++++++++
# The main streamlit operations for this page
if __name__ == "__main__":
    GenreTaggerAssist().main_executor()
