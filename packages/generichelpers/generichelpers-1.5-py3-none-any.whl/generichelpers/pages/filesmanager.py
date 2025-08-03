"""Files summarizer page"""

import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path

import pandas as pd
import streamlit as st
from pages import CSS, auto_size_js, checkbox_renderer, filesmanager_col_config
from pages.initilizer import initialize_file_manager
from send2trash import send2trash
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from st_pages import add_page_title
from utils.dtypesutils import DtypesOpsHandler
from utils.fileopsutils import FileopsHandler

initialize_file_manager()


class FileSummarizerAssist(object):
    """streamlit assist class for summarizing files in a given base dir"""
    def __init__(self):
        self.clear_logs()  # browser logs clearance button at top right corner
        add_page_title(layout='wide')
        # st.set_page_config(page_title='Files Summarizer', page_icon=':label:')
        st.markdown(CSS, unsafe_allow_html=True)
        file_cols = ['file_name', 'file_ext', 'file_size', 'created_date', 'modified_date', 'file_path']
        cols_str = f'''
            <li><strong>
                <span style='color:gray;'>{
                    " | ".join([col for col in file_cols])}
                </span>
            </strong></li>'''
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
        st.markdown('<h2 class="head-h2">Manage files</h2>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="para-p1">
                This app analyzes files in a chosen base folder and provides a quick overview of &ndash;
                <ul>
                    <li><strong>Total files of given types in the folder</strong></li>
                    <li><strong>Total Total files of each type</strong></li>
                    <li><strong>Total files of each type inside subdirs</strong></li>
                    <li><strong>A consolidated list of files of each type as:</strong>
                        <ul>
                            {cols_str}
                        </ul>
                    </li>
                Also provides utilities for renaming/deleting files in the base folder.
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

    def display_params_header(self, params_label, top='-1.5em', bottom='-1em'):
        """Title to display for params input section"""
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
                    margin-top: {top};
                    margin-bottom: {bottom};
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

    def get_params(self, task_mode='summarize'):
        """Get params for files summarization"""
        # ---------------------------------
        # Take input params
        to_save = st.checkbox("Save files summary", value=False) if task_mode == 'summarize' else False
        exclude_hidden = st.checkbox("Exclude hidden subdirectories", value=True)
        dry_run = st.checkbox("Dry-run mode", value=True) if task_mode in ('rename', 'delete') else False
        st.text_input('Provide the base folder path :file_folder:', key='base_path')
        base_path = FileopsHandler().normalize_path(st.session_state.get("base_path", ''))

        # -----------------------------
        # Detect if base_path or params changed → update all_exts
        prev_path = st.session_state.get("prev_path", '')
        prev_exclude_flag = st.session_state.get("prev_exclude_flag", True)
        prev_dryrun_flag = st.session_state.get("prev_dryrun_flag", True)
        is_path_changed = base_path and os.path.isdir(base_path) and base_path != prev_path
        is_exclude_changed = exclude_hidden != prev_exclude_flag
        is_dryrun_changed = dry_run != prev_dryrun_flag

        if is_path_changed or is_exclude_changed or is_dryrun_changed:
            all_exts, _ = DtypesOpsHandler().summarize_files(base_path, exclude_hidden=exclude_hidden)
            st.session_state.update({
                "prev_path": base_path,
                "prev_exclude_flag": exclude_hidden,
                "prev_dryrun_flag": dry_run,
                "all_exts": sorted(all_exts)
            })

        # -----------------------------
        # Get file_types as user input
        all_file_exts, file_types = st.session_state.get("all_exts", []), []
        if base_path:
            if os.path.isdir(base_path):
                to_select = st.checkbox(
                    label=f"Select specific files to {task_mode}",
                    help=f"Check to select specific file types to {task_mode}, or leave unchecked for all",
                    value=False
                )
                if to_select:
                    file_types = st.multiselect(
                        label=fr'$\textsf{{\textbf{{Select file types to {task_mode}👇}}}}$',
                        options=all_file_exts,
                        help="Select from the list of all available file types"
                    )
                    file_types = sorted(set(file_types))
                else:
                    file_types = deepcopy(all_file_exts)
            else:
                st.warning("**:red[Non-existent base path, please check !]**", icon="⚠️")

        # ---------------------------------
        # Get the hash fingerprint of param state
        param_state = {
            "to_save": to_save,
            "exclude_hidden": exclude_hidden,
            "dry_run": dry_run,
            "base_path": base_path,
            "all_exts": all_file_exts,
            "file_types": file_types
        }
        param_hash = hashlib.md5(json.dumps(param_state, sort_keys=True).encode()).hexdigest()

        return to_save, exclude_hidden, dry_run, base_path, file_types, param_hash

    def save_summary(self, to_save):
        """Save generated files summary"""
        if (
            to_save and
            st.session_state.just_finished
            and not st.session_state.summary_data.empty
        ):
            excel_buffer = io.BytesIO()
            st.session_state.summary_data.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            cols = st.columns([0.75, 0.25])
            with cols[1]:
                st.download_button(
                    "Download Excel Summary",
                    excel_buffer,
                    'file_summary.xlsx',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    type='primary'
                )

    def execute_on_submit(self, base_path: str, file_types: list, exclude_hidden: bool, task_mode='summarize'):
        """Run file summarizer from `DtypesOpsHandler` class on clicking 'Submit' button"""
        if file_types and st.button('Submit'):
            st.session_state.submit_button = True
            st.session_state.just_finished = False
            st.session_state.summary_data = pd.DataFrame()
            st.session_state.consol_summary = pd.DataFrame()  # consolidated summary

            consol_summary = []
            file_summary, st.session_state.summary_data = DtypesOpsHandler().summarize_files(
                base_path, file_types, exclude_hidden)
            if task_mode == 'summarize':
                for ext in file_types:
                    consol_summary.append({
                        "file_ext": ext,
                        "total_files": file_summary[ext]["total_files"],
                        "hidden_files": file_summary[ext]["total_hidden_files"],
                        "files_inside_subdirs": file_summary[ext]["total_files_in_subdirs"]
                    })
                st.session_state.consol_summary = pd.DataFrame(consol_summary)

            st.session_state.just_finished = True  # reset session state here

    def make_path_relative(self, path: str, base_path: str, reverse=False):
        """Make the path relative to `base_path`, or reverse the process if `reverse=True`.

        Parameters:
            path (str): The path to process.
            base_path (str): The base path to relate to.
            reverse (bool): If True, convert relative path back to absolute using base_path.

        Returns:
            str: The processed path.
        """
        base = Path(base_path).resolve()
        try:
            if reverse:
                return str((base/Path(path)).resolve())
            else:
                return f"./{Path(path).resolve().relative_to(base)}"
        except ValueError:
            return str(Path(path).resolve())  # fallback to full path if not under base_path

    def get_input_table(self, base_path: str, task_mode='rename'):
        """Get user input data for files rename/delete operations"""
        if (st.session_state.summary_data is not None) and (not st.session_state.summary_data.empty):
            input_data = (
                st.session_state.summary_data[['file_name', 'file_ext', 'file_path']]
                .dropna()
                .drop_duplicates()
                .assign(
                    file_path=lambda d: d['file_path'].apply(lambda x: self.make_path_relative(x, base_path)),
                    **({'new_name': lambda d: d['file_name']} if task_mode == 'rename'
                       else {'confirm_delete': False})
                )
                .sort_values(by=['file_ext', 'file_name'])
            )
            order_cols = (
                ['file_name', 'new_name', 'file_ext', 'file_path'] if task_mode == 'rename'
                else ['file_name', 'confirm_delete', 'file_ext', 'file_path']
            )
            input_data = input_data[order_cols]
            return input_data

    def extract_edited_data(self, grid_response, input_data, task_mode):
        """Derive edited data based on user interaction type with the displayed table."""
        edited_data = grid_response.get("data", pd.DataFrame())
        selected_rows = grid_response.get("selected_rows")
        selected_rows = (
            selected_rows
            .to_dict(orient='records') if isinstance(selected_rows, pd.DataFrame)
            else (selected_rows or [])
        )
        if task_mode == 'summarize':
            return pd.DataFrame(selected_rows)
        if task_mode == 'delete' and selected_rows:
            edited_data = input_data.copy()
            selected_paths = {row["file_path"] for row in selected_rows}
            edited_data["confirm_delete"] = edited_data["file_path"].isin(selected_paths)
        return edited_data

    @staticmethod
    def is_wsl():
        """Detect if the current environment is WSL (Windows Subsystem for Linux)."""
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except FileNotFoundError:
            return False

    def open_file(self, path: str, base_path: str = ''):
        """Open file with system default application"""
        platform_name = platform.system()
        rel_path = (
            self.make_path_relative(path, base_path)
            if os.path.exists(path) and os.path.exists(base_path) else path
        )
        try:
            if not os.path.exists(path):
                yield f"❌ File does not exist: {path}"
                return
            if platform_name == 'Windows':
                getattr(os, "startfile")(path)
            elif platform_name == 'Darwin':  # macOS
                subprocess.call(['open', path])
            elif self.is_wsl():  # WSL
                win_path = subprocess.check_output(["wslpath", "-w", path]).decode().strip()
                subprocess.call(["explorer.exe", win_path])
            else:  # Linux/Unix
                subprocess.call(['xdg-open', path])
            yield f"✅ Successfully opened file: '{rel_path}'"
        except Exception:
            yield f"❌ Failed opening file: '{rel_path}'"
            raise

    def display_edit_data(self, input_data, col_config=dict(), show_title=True, task_mode='rename', page_size=10, height=350):
        """
        Display data for user edit (rename/delete/etc.) using AgGrid with dynamic editable configs.

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
            task_mode (str, optional): The task mode (rename/delete). Defaults to 'rename'.
            page_size (int, optional): Number of rows per page in pagination. Defaults to 10.
            height (int, optional): Height of the grid in pixels. Defaults to 350.

        Returns:
            pd.DataFrame: Edited data.
        """
        edited_data = pd.DataFrame()
        if input_data is not None:
            if show_title:
                title_text = f"🎯 Detected {input_data.shape[0]} unique files."
                title_text += (
                    " All are displayed below👇" if task_mode == 'summarize'
                    else f" {task_mode.title()} any you wish below👇"
                )
                self.display_params_header(title_text, '-1em')
            if task_mode == 'summarize':
                col_config["file_name"].update({"checkboxSelection": True, "headerCheckboxSelection": True})
            if 'confirm_delete' in col_config:
                col_config["confirm_delete"].update({"cellRenderer": eval(checkbox_renderer)})

            # ---------------------------------
            # Form the AgGrid obj through col configs
            gb = GridOptionsBuilder.from_dataframe(input_data)
            for col, config in col_config.items():
                gb.configure_column(
                    field=col,
                    editable=config.get("editable", False),
                    cellStyle=config.get("cellStyle", {}),
                    maxWidth=config.get("maxWidth"),
                    width=config.get("width"),
                    cellEditor=config.get("cellEditor"),
                    cellRenderer=config.get("cellRenderer", None),
                    cellEditorParams=config.get("cellEditorParams", None),
                    suppressMenu=config.get("suppressMenu", False),
                    suppressMovable=config.get("suppressMovable", False),
                    checkboxSelection=config.get("checkboxSelection", False),
                    headerCheckboxSelection=config.get("headerCheckboxSelection", False)
                )
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=page_size)
            gb.configure_selection(selection_mode="multiple", use_checkbox=False)
            grid_options = gb.build()

            # ---------------------------------
            # Render AgGrid
            grid_response = AgGrid(
                input_data,
                gridOptions=grid_options,
                custom_js={"onGridReady": eval(auto_size_js)},
                update_mode=(
                    GridUpdateMode.VALUE_CHANGED if task_mode == 'rename'
                    else GridUpdateMode.SELECTION_CHANGED
                ),
                allow_unsafe_jscode=True,
                fit_columns_on_grid_load=False,
                enable_enterprise_modules=False,
                theme="streamlit",
                height=height
            )

            edited_data = self.extract_edited_data(grid_response, input_data, task_mode)

        return edited_data

    def move_files(self, base_path: str, edited_data: pd.DataFrame, dry_run=True, task_mode='rename'):
        """Rename or delete files based on task_mode and edited data."""
        edited_data['file_path'] = edited_data['file_path'].apply(lambda x: self.make_path_relative(x, base_path, True))
        for row in edited_data.itertuples(index=False):
            file_name, src = row.file_name, row.file_path
            if task_mode == 'rename':
                dst = os.path.join(os.path.dirname(src), row.new_name)
                if dry_run:
                    yield f'→ DRY RUN: Would rename: "{file_name}" → "{row.new_name}"'
                elif not os.path.exists(src):
                    yield f'→ Non-existent path, not renamed: "{file_name}" → "{row.new_name}"'
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.move(src, dst)
                    yield f'→ Successfully renamed: "{file_name}" → "{row.new_name}"'
            elif task_mode == 'delete':
                if dry_run:
                    yield f'→ DRY RUN: Would delete: "{src}"'
                elif not os.path.exists(src):
                    yield f'→ Non-existent path: "{src}"'
                else:
                    send2trash(src)
                    yield f'→ Successfully moved to Trash: "{src}"'

    def _handle_proceed_button(self, updated_df, col_config, task_mode='rename'):
        """'Proceed' button tasks for `act()` func"""
        # ---------------------------------
        # Proceed with the task only if all conditions are valid
        if not updated_df.empty and st.button('Proceed'):
            if not updated_df.equals(st.session_state.edited_data):
                st.session_state.edited_data = deepcopy(updated_df)
            required_cols = {'file_name', 'new_name'} if task_mode == 'rename' else {'file_name', 'confirm_delete'}
            edited_df = pd.DataFrame() if (st.session_state.edited_data is None) else st.session_state.edited_data
            if required_cols.issubset(edited_df.columns):
                changed_df = (
                    edited_df[edited_df['file_name'] != edited_df['new_name']]
                    if task_mode == 'rename' else edited_df[edited_df['confirm_delete']]
                )
                if not changed_df.empty:
                    st.success(f"You wish to {task_mode} {changed_df.shape[0]} files. A snapshot below! ✅")
                    if task_mode == 'rename':
                        col_config["new_name"].update({"editable": False})
                    else:
                        col_config["confirm_delete"].update({
                            "headerCheckboxSelection": False,
                            "checkboxSelection": False
                        })
                    self.display_edit_data(changed_df, col_config, False)
                    st.session_state.update({"changed_data": changed_df.copy(), "proceed_button": True})
                else:
                    st.warning(f"**:red[Nothing to {task_mode} !]**", icon="⚠️")

    def _handle_act_button(self, base_path, dry_run, file_types, task_mode='rename'):
        """Act (Rename/Delete) button tasks for `act()` func"""
        # ---------------------------------
        # Execute rename/delete after rerun
        if st.session_state.get("proceed_button") and not st.session_state.get("act_button"):
            if st.button(task_mode.title() + ' !'):
                st.session_state.update({
                    "act_button": True,
                    "dry_run": dry_run,
                    "post_act_refresh": not dry_run  # flag to signal rescan if not in dry_run mode
                })
                st.rerun()
        if st.session_state.get("act_button") and (st.session_state.get("changed_data") is not None):
            edited_data = st.session_state.get("changed_data", pd.DataFrame())
            for line in self.move_files(base_path, edited_data, dry_run, task_mode):
                st.session_state.log_lines.append(line.rstrip('\n'))
            # Only show logs now if NOT post_act_refresh (i.e., DRY RUN)
            if not st.session_state.get("post_act_refresh", False):
                st.markdown("```\n" + "\n".join(st.session_state.log_lines) + "\n```")
            # +++++++++++++++++
            # Cleanup after rename/delete
            st.session_state.update({
                "changed_data": None,
                "proceed_button": False,
                "act_button": False,
                "log_lines": [],
                "dr_run": dry_run,
                "post_act_logs": st.session_state.log_lines.copy()
            })

            # ---------------------------------
            # Re-scan updated folder after actual run
            if not dry_run and st.session_state.get("post_act_refresh"):
                _, st.session_state.summary_data = DtypesOpsHandler().summarize_files(base_path, file_types)
                st.session_state.update({"post_act_refresh": False, "edited_data": pd.DataFrame()})
                st.rerun()

        # ---------------------------------
        # Display logs after actual run
        if not st.session_state.get("dry_run", True) and st.session_state.get("post_act_logs", []):
            st.markdown("```\n" + "\n".join(st.session_state.post_act_logs) + "\n```")
            st.session_state.post_act_logs = []

    def summarize(self):
        """Summarize files in the base folder"""
        self.display_params_header('Provide params for files summarization👇')
        st.info(
            "For movie files (.avi, .mp4, etc.), use the dedicated :red-background[:memo: Movies Summarizer] utility.",
            icon="ℹ️"
        )
        to_save, exclude_hidden, _, base_path, file_types, param_hash = self.get_params()
        if st.session_state.get("last_param_hash") != param_hash:
            st.session_state.just_finished = False  # clear just_finshed flag
            st.session_state.summary_data = pd.DataFrame()  # clear existing summary data
            st.session_state.consol_summary = pd.DataFrame()  # clear consolidated summary
            st.session_state.last_param_hash = param_hash  # update hash
        self.execute_on_submit(base_path, file_types, exclude_hidden)

        # ---------------------------------
        # Open selected files with respective OS application
        edited_data = pd.DataFrame()
        st.session_state.update({"file_open_logs": []})  # prepare log storage
        if not st.session_state.summary_data.empty:
            col_config = deepcopy(filesmanager_col_config)
            _ = [col_config.pop(k, None) for k in ('new_name', 'confirm_delete')]
            edited_data = self.display_edit_data(
                st.session_state.summary_data.sort_values(by=['file_ext', 'file_name']),
                col_config,
                show_title=True,
                task_mode='summarize'
            )

        if (edited_data is not None) and (not edited_data.empty) and st.button('Open'):
            for row in edited_data.itertuples(index=False):
                log_line = next(self.open_file(row.file_path, base_path)).rstrip('\n')
                st.session_state.file_open_logs.append(log_line)

        # ---------------------------------
        # Display logs
        if st.session_state.get("file_open_logs"):
            st.markdown("```\n" + "\n".join(st.session_state.file_open_logs) + "\n```")

        # Display consolidated summary
        if not st.session_state.get("consol_summary").empty:
            self.display_params_header("📊 Summary of selected file types shown below👇", "-1em")
            consol_summary = (
                st.session_state.consol_summary
                .style
                .highlight_max(axis=0, color='gainsboro')  # 'honeydew'
                .set_properties(**{'background-color': 'LightCyan'}, subset=['file_ext'])
            )
            st.dataframe(consol_summary, hide_index=True)

        self.save_summary(to_save)

    def act(self, task_mode='rename'):
        """Act (Rename/Delete) on files, present in the base folder"""
        self.display_params_header(f"Provide params for {task_mode[:-1] + 'ing'} files")
        _, exclude_hidden, dry_run, base_path, file_types, param_hash = self.get_params(task_mode)
        # ---------------------------------
        # Take rename/delete columns info via user input
        if st.session_state.get("last_param_hash") != param_hash:
            st.session_state.summary_data = pd.DataFrame()
            st.session_state.edited_data = pd.DataFrame()  # clear previous edits
            st.session_state.just_finished = False  # clear just_finished flag
            st.session_state.log_lines = []  # clear existing logs
            st.session_state.last_param_hash = param_hash  # update hash
        self.execute_on_submit(base_path, file_types, exclude_hidden, task_mode)

        # ---------------------------------
        # Get user edits -- initialize edited_data only on first load or param change
        base_data = pd.DataFrame()
        col_config = deepcopy(filesmanager_col_config)
        _, _ = col_config.pop("file_size_bytes"), col_config.pop("file_size")
        _ = col_config.pop("confirm_delete") if task_mode == 'rename' else col_config.pop("new_name")
        if (st.session_state.edited_data is None) or (st.session_state.edited_data.empty):
            base_data = self.get_input_table(base_path, task_mode)
            st.session_state.edited_data = deepcopy(base_data)
        updated_df = self.display_edit_data(st.session_state.edited_data, col_config, task_mode=task_mode)

        self._handle_proceed_button(updated_df, col_config, task_mode)  # execute proceed button

        # --------------------------------------------
        # Detect post-Proceed edits and reset act_button
        has_changed_after_proceed = (
            st.session_state.get("proceed_button")
            and not updated_df.equals(st.session_state.get("edited_data", pd.DataFrame()))
        )
        if has_changed_after_proceed:
            st.session_state.update({"proceed_button": False, "act_button": False})

        self._handle_act_button(base_path, dry_run, file_types, task_mode)  # execute act button

    def main_executor(self):
        """The main module that summarizes files and displays to page"""
        selected_op = st.radio(
            label='Select the desired files manager operation to perform',
            options=('Summarize files', 'Rename files', 'Delete files'),
            index=None,
            horizontal=True
        )
        # ---------------------------------
        # Detect change in operation
        if selected_op != st.session_state.get("selected_op"):
            # User switched operations → reset everything
            st.session_state.base_path = ''
            st.session_state.summary_data = pd.DataFrame()
            st.session_state.edited_data = pd.DataFrame()
            st.session_state.log_lines = []

        st.session_state.selected_op = selected_op  # store the current choice for next rerun

        # ---------------------------------
        # Route to the appropriate tagging function
        if selected_op == 'Summarize files':
            self.summarize()
        elif selected_op == 'Rename files':
            self.act()
        elif selected_op == 'Delete files':
            self.act('delete')


# +++++++++++++++++
# The main streamlit operations for this page
if __name__ == "__main__":
    FileSummarizerAssist().main_executor()
