"""Payslip parser page"""

from __future__ import absolute_import

import re
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st
from devs.payslipparser import PayslipParser
from pages import CSS, static_table_style
from pages.initilizer import initilizer_payslip_parser
from st_pages import add_page_title

initilizer_payslip_parser()


class PayslipParseStAssist(object):
    """streamlit assist class for time operations"""
    def __init__(self):
        self.todays_date = datetime.today().strftime('%d-%b-%Y')
        self.today = datetime.strptime(self.todays_date, '%d-%b-%Y')
        add_page_title(layout='wide')
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown(
            '''
            <style>
                div[class*="stRadio"]>label>div[data-testid="stMarkdownContainer"]>p {
                    font-size: 18px;
                }
                div[class*="stSelect"]>label>div[data-testid="stMarkdownContainer"]>p {
                    font-size: 14px;
                    color: Black;
                }
                .stSubmitButton, div.stButton {
                    text-align:right;
                }
            </style>
            ''', unsafe_allow_html=True
        )
        st.markdown('''<h2 class="head-h2">
                        Parse a payslip pdf and compute various aggregations
                    </h2>''', unsafe_allow_html=True)
        st.markdown(f'''
                    <div class="para-p1">
                        Separates components of a payslip (e.g. <em>employee info</em>,
                        <em>month info</em>, <em>pay components</em> etc.) and computes
                        aggregated salaries based on different filters. Few example features &ndash;
                        <ul>
                            <li><strong>Total TDS for {self.today.year}</strong></li>
                            <li><strong>Total earnings for the period {self.today.year-2}&ndash;{self.today.year}</strong></li>
                            <li><strong>Total earnings for '{self.today.strftime('%B')}' across entire tenure</strong></li>
                        </ul>
                    </div>''', unsafe_allow_html=True)

    @staticmethod
    def _clear_session():
        """clear st session variables"""
        for key in st.session_state.keys():
            del st.session_state[key]

    def _multiselect_years(self, years_options):
        """Set 'max_selections' option for selecting years"""
        if 'selected_years' in st.session_state:
            if 'All' in st.session_state.selected_years:
                st.session_state.selected_years = [years_options[0]]
                st.session_state.max_year_selections = 1
            else:
                st.session_state.max_year_selections = len(years_options)

    def _multiselect_months(self, months_options):
        """Set 'max_selections' option for selecting months"""
        if 'selected_months' in st.session_state:
            if 'All' in st.session_state.selected_months:
                st.session_state.selected_months = [months_options[0]]
                st.session_state.max_month_selections = 1
            else:
                st.session_state.max_month_selections = len(months_options)

    def _display_payslip(self):
        """Displays pay components dataframe, based on month-year, selected by user."""
        payslips = st.session_state.parsed_payslips
        all_years = st.session_state.monthyrs_dict.get('years', [])
        all_months = st.session_state.monthyrs_dict.get('months', [])
        all_mnthyrs = st.session_state.monthyrs_dict.get('month_years', [])
        mnthyr_dict = {minfo: key for key, paycomp in payslips.items() if (minfo := paycomp.get('month_info'))}
        st.markdown(f'''
            <p style="font-family: sans-serif; font-weight: normal; font-size: 18px; color: DimGrey;">
                Payslips parsed successfully for {len(all_mnthyrs)} months:
                [{all_mnthyrs[0]} &ndash; {all_mnthyrs[-1]}]
            </p>''', unsafe_allow_html=True)
        selected_op = st.radio(
            label='Do you want to view the parsed pay elements ?',
            options=('Yes', 'No'),
            index=None
        )
        if selected_op == 'Yes':
            with st.expander(r"$\textsf{\normalsize Select year and month👇}$"):
                year = st.selectbox('Year', all_years, label_visibility='hidden')
                month = st.radio('Month', all_months, index=None, horizontal=True, label_visibility='hidden')
                month_year = f'{month}-{year}'
                if month_year in all_mnthyrs:
                    paydf = payslips[mnthyr_dict[month_year]]['pay_elements']
                    paydf = paydf.style.format(precision=2, thousands=',', na_rep='N/A').set_properties(
                        **{'text-align': 'left'}).set_table_styles(static_table_style)
                    st.write(paydf.to_html(), unsafe_allow_html=True)
                elif month and year:
                    st.warning(f'''**:red[There is no payslip for: '{month_year}' !!]**''', icon="⚠️")

    def _acton_payslips(self):
        """Perform actions on parsed payslips -- _download_ or _aggregation_."""
        payslips = st.session_state.parsed_payslips
        selected_op = st.radio(
            label='What action would you like to perform on the parsed payslips?',
            options=('Download as excel', 'Compute aggregations'),
            index=None
        )
        if selected_op == 'Download as excel':
            in_memory_fp = BytesIO()
            st.session_state.all_payslips.to_excel(in_memory_fp, index=False, header=True)
            in_memory_fp.seek(0, 0)
            download_df = in_memory_fp.read()
            st.download_button(
                label='📥 Download the consolidated payslip',
                data=download_df,
                file_name='combined_payslips.xlsx'
            )
            st.session_state.display_res = False
        elif selected_op == 'Compute aggregations':
            all_years = ['All'] + st.session_state.monthyrs_dict.get('years', [])
            all_months = ['All'] + st.session_state.monthyrs_dict.get('months', [])
            month_years = st.session_state.monthyrs_dict.get('month_years', [])

            # Get agg_type, filter_year, filter_month, company_name and designation info
            if 'max_year_selections' not in st.session_state:
                st.session_state.max_year_selections = len(all_years)
            if 'max_month_selections' not in st.session_state:
                st.session_state.max_month_selections = len(all_months)
            filter_years = st.multiselect(
                label=r'$\textsf{\textbf{\normalsize Select year(s) to filter👇}}$',
                options=all_years,
                key='selected_years',
                max_selections=st.session_state.max_year_selections,
                on_change=self._multiselect_years(all_years)
            )
            filter_months = st.multiselect(
                label=r'$\textsf{\textbf{\normalsize Select month(s) to filter👇}}$',
                options=all_months,
                key='selected_months',
                max_selections=st.session_state.max_month_selections,
                on_change=self._multiselect_months(all_months)
            )
            exclude_months = st.multiselect(
                label=r'$\textsf{\textbf{\normalsize Select exclude periods (if desired)👇}}$',
                options=month_years
            )
            company_name = st.text_input(
                label=r'$\textsf{\textbf{\normalsize Provide company name if desired (optional)👇}}$',
            )
            designation = st.text_input(
                label=r'$\textsf{\textbf{\normalsize Provide designation if desired (optional)👇}}$',
            )

            # Obtain specific pay component keys to compute aggregations for
            pay_cols = st.session_state.all_payslips.filter(like='paycol').columns.tolist()
            paycols_maxidx = max([int(re.sub('paycol_', '', pc)) for pc in pay_cols])
            note_txt = f'''
            <p style="font-family: sans-serif; font-size: 16px">
                <strong>
                    Input payslip aggregation components👇
                </strong><br>
                (<code>paycol_index range: [0-{paycols_maxidx}]</code>)
            </p>
            '''
            st.write(note_txt, unsafe_allow_html=True)
            options_df = pd.DataFrame(
                [
                    {
                        "param": 'Basic',
                        "paycol_index": 0
                    },
                    {
                        "param": 'TDS',
                        "paycol_index": 0
                    },
                    {
                        "param": 'Net Pay',
                        "paycol_index": 0
                    }
                ]
            )
            options_df = st.data_editor(
                options_df,
                column_config={
                    "paycol_index": st.column_config.NumberColumn(
                        min_value=0,
                        max_value=paycols_maxidx,
                        step=1)
                },
                hide_index=True,
                num_rows='dynamic')
            if st.button('**Compute now !**'):
                options_df.dropna(how='all', inplace=True)  # drop unintential `None` entries
                # options_df['paycol_index'] = options_df['paycol_index'].astype(int)
                agg_options = {
                    # 'agg_type': agg_type,
                    'filter_years': filter_years,
                    'filter_months': filter_months,
                    'exclude_months': exclude_months,
                    'company_name': company_name,
                    'designation': designation,
                    'filter_comps': {r[0]: r[1] for _, r in options_df.iterrows()}
                }
                _parser = PayslipParser()
                _parser.aggregate(payslips, st.session_state.monthyrs_dict, agg_options)
                st.session_state.agg_paycomps = _parser.agg_paycomps
                st.session_state.display_res = True

    def _display_results(self):
        """Display final agg results to the screen."""
        agg_paycomps = st.session_state.agg_paycomps
        display_str = '''
            <p style="font-family: sans-serif;
            font-weight: bold;
            font-size: 16px;
            color: DodgerBlue;">
            The aggregated payslip components are shown below👇
            </p>
            '''
        if agg_paycomps:
            agg_paycomps = pd.DataFrame(agg_paycomps).T
            agg_paycomps = agg_paycomps.style.format(precision=2, na_rep='N/A').set_properties(
                **{'text-align': 'left'}).set_table_styles(static_table_style)
            st.write(display_str, agg_paycomps.to_html(), unsafe_allow_html=True)
        else:
            st.warning("**:red[Aggregation couldn't be done. Check inputs again !!]**", icon="⚠️")

    def main_executor(self):
        """Main module that performs all tasks and displays to page"""
        label_txt = r"$\textsf{\color{DodgerBlue}\large Upload the payslip \texttt{.pdf} file}$ :spiral_note_pad:"
        st.session_state.payslip_pdf = st.file_uploader(label_txt, type=['.pdf'])
        session_keys = [
            'parsed_payslips', 'all_payslips', 'monthyrs_dict',
            'action_button', 'display_res', 'agg_paycomps'
        ]

        if not st.session_state.payslip_pdf:
            _ = [st.session_state.update({key: False}) for key in session_keys]

        if st.session_state.payslip_pdf and st.button('Parse', type='primary'):
            _parser = PayslipParser()
            _parser.parse(st.session_state.payslip_pdf)
            st.session_state.parsed_payslips = _parser.parsed_payslips
            st.session_state.all_payslips = _parser.payslips_df
            st.session_state.monthyrs_dict = _parser.monthyrs_dict
            _ = [st.session_state.update({key: False}) for key in session_keys[-3:]]

        if st.session_state.payslip_pdf and st.session_state.parsed_payslips:
            self._display_payslip()
            if st.button('Go to Next Step', type='primary'):
                st.session_state.action_button = True

        if st.session_state.payslip_pdf:
            if st.session_state.action_button:
                self._acton_payslips()
            if st.session_state.display_res:
                self._display_results()


# +++++++++++++++++
# The main streamlit operations for this page
if __name__ == "__main__":
    PayslipParseStAssist().main_executor()
