"""Movies summarizer page"""

import json
import os

import streamlit as st
from devs.moviemanager import MovieLibraryManager
from pages import CSS
from pages.initilizer import initialize_file_manager
from st_pages import add_page_title

initialize_file_manager()


class MovieSummarizerAssist(object):
    """streamlit assist class for summarizing total movies in a given base dir"""
    def __init__(self):
        self.clear_logs()  # browser logs clearance button at top right corner
        add_page_title(layout='wide')
        # st.set_page_config(page_title='Movies Summarizer', page_icon=':label:')
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
                div[class*="stNumberInput"] div[data-testid="stMarkdownContainer"] > p {
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
        st.markdown('<h2 class="head-h2">Summarize movie collection</h2>', unsafe_allow_html=True)
        st.markdown('''
            <div class="para-p1">
                This app analyzes movies in a chosen base folder and provides a quick overview of &ndash;
                <ul>
                    <li><strong>Total movies in the folder</strong></li>
                    <li><strong>Total movie folders with external subtitles</strong></li>
                    <li><strong>Folders vs. standalone video files</strong></li>
                    <li><strong>Movies organized by year ranges, genres and file types</strong></li>
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

    def execute_on_submit(self, **kwargs):
        """Run summarizer from `MovieLibraryManager` class on clicking 'Submit' button"""
        if st.button('Submit'):
            st.session_state.submit_button = True
            st.session_state.just_finished = False
            st.session_state.log_lines = []
            st.session_state.summary_text = ''

            place_holder = st.empty()
            movie_manager = MovieLibraryManager(
                base_path=kwargs.get("base_path", ''),
                exclude_subdirs=kwargs.get("exclude_subdirs", []),
                year_interval=kwargs.get("year_interval", 10),
                save_summary=kwargs.get("save_summary", False),
                write_logs=False
            )
            for line in movie_manager.summarize():
                st.session_state.log_lines.append(line.rstrip('\n'))
                place_holder.markdown("```\n" + "\n".join(st.session_state.log_lines) + "\n```")
            # ---------------------------------
            # Fetch summary from summarizer
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
        if st.session_state.summary_text:
            st.markdown(f"```json\n{st.session_state.summary_text}\n```")

    def summarize_movies(self):
        """Main summarizer module"""
        # ---------------------------------
        # Take input params
        st.write(
            '''
            <p style="
                font-family: sans-serif;
                font-weight: normal;
                font-size: 20px;
                color: DodgerBlue;
            ">
                Provide params for movie summarization👇
            </p>
            ''',
            unsafe_allow_html=True
        )
        save_summary = st.checkbox("Save JSON summary and movies info excel", value=False)
        year_interval = st.number_input("Provide years group interval (1–50)", 1, 50, 10, format='%d')
        base_path, exclude_subdirs = self.get_scan_path('Provide the base folder path :file_folder:')

        # ---------------------------------
        # Run summarizer utility
        params_dict = {
            "base_path": base_path,
            "exclude_subdirs": exclude_subdirs,
            "year_interval": year_interval,
            "save_summary": save_summary
        }
        self.execute_on_submit(**params_dict)

    def main_executor(self):
        """The main module that performs all tasks and displays to page"""
        st.session_state.submit_button = False
        st.session_state.log_lines = []
        st.session_state.summary_text = ''
        self.summarize_movies()


# +++++++++++++++++
# The main streamlit operations for this page
if __name__ == "__main__":
    MovieSummarizerAssist().main_executor()
