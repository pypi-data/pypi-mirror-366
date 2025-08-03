"""Elapsed time page"""

import calendar
import re
from datetime import date, datetime
from functools import reduce

import pandas as pd
import streamlit as st
from apiroutes.calctimeapis import CalcTimeAssist
from pages import CSS, static_table_style
from st_pages import add_page_title
from utils.timeutils import CalculateTime


class CalcTimeStAssist(object):
    """streamlit assist class for time operations"""
    def __init__(self):
        add_page_title(layout='wide')
        # st.set_page_config(page_title='Elapsed Time', page_icon=':alarm_clock:')
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown('<h2 class="head-h2">Perform various time-related computations</h2>', unsafe_allow_html=True)
        st.markdown('<p class="para-p1">Finds elapsed/lapsed times, new date, age as well as converts time from one format to another.</p>', unsafe_allow_html=True)
        self.todays_date = datetime.today().strftime('%d-%b-%Y')
        self.today = datetime.strptime(self.todays_date, '%d-%b-%Y')

    @staticmethod
    def display_static_table(table_df, table_style={}, descr_str='', ):
        """Display a static table data with specified style"""
        output_df = table_df.style.set_properties(**{'text-align': 'left'}).set_table_styles(table_style)
        st.write(descr_str, output_df.to_html(), unsafe_allow_html=True)
        # st.table(output_df)

    def convert_time_st(self):
        """Time converter st module"""
        st.write("**Provide inputs for time conversion👇**")
        input_data = pd.DataFrame(
            [
                {
                    "param": 'time_str',
                    "description": 'The time string to convert',
                    "value": '12d 210h 500m 50s'
                },
                {
                    "param": 'units',
                    "description": 'Conversion units as a combination of `YQMWDhms`',
                    "value": 'YMD'
                },
                {
                    "param": 'format',
                    "description": "The display format",
                    "value": '1'
                }
            ]
        )
        input_data = input_data.style.set_properties(**{'background-color': 'LightCyan'}, subset=['param'])
        edited_data = st.data_editor(input_data, hide_index=True, disabled=('param', 'description'))
        if st.button('Submit'):
            time_str, to_units, format_type = edited_data['value']
            time_dict = CalculateTime().extract_timeunits(time_str)
            convert_dict = CalculateTime().convert_timeunits(time_dict, to_units)
            convert_str = CalculateTime().stringify_timeunits(convert_dict, int(format_type))
            given_str = CalculateTime().stringify_timeunits(time_dict, int(format_type))
            response = pd.DataFrame([
                {'time': '<strong>given time</strong>', 'value': given_str},
                {'time': '<strong>converted time<strong>', 'value': convert_str}
            ])
            self.display_static_table(response, static_table_style, "**The converted time below👇**")

    def compute_age_st(self):
        """Age computer st module"""
        st.write("**Provide inputs for age computation👇**")
        input_data = pd.DataFrame(
            [
                {
                    "param": "DOB",
                    "description": f"DOB in 'DD-MMM-YYYY' format (e.g. '{self.todays_date}')",
                    "value": "08-Apr-2019"
                },
                {
                    "param": "target_date",
                    "description": f"Target date (e.g. '{self.todays_date}', 'after 2yrs 3mnths', 'present')",
                    "value": self.todays_date
                },
                {
                    "param": "units",
                    "description": "Conversion units (either 'single' or 'multi')",
                    "value": "multi"
                },
                {
                    "param": 'include_enddate',
                    "description": 'Whether to include end date in the computation',
                    "value": 'True'
                },
                {
                    "param": 'format',
                    "description": "The display format",
                    "value": '1'
                }
            ]
        )
        input_data = input_data.style.set_properties(**{'background-color': 'LightCyan'}, subset=['param'])
        edited_data = st.data_editor(input_data, hide_index=True, disabled=('param', 'description'))
        if st.button('Submit'):
            dob_date, target_date, multi_units, include_enddate, format_type = edited_data['value']
            multi_units = True if multi_units == 'multi' else False
            include_enddate, format_type = eval(include_enddate), eval(format_type)
            get_age = CalcTimeAssist().compute_age(dob_date, target_date, include_enddate, multi_units, format_type)
            get_age = pd.DataFrame(
                reduce(lambda x, y: x+y, [[{
                    'param': f'<strong><em>{v[0].strip()}</strong></em>',
                    'value': v[1].strip()}] for s in get_age if (v := s.split(':'))])
                )
            target_date = self.todays_date if target_date == 'present' else target_date
            response = pd.DataFrame([
                {'param': '<strong>DOB</strong>', 'value': dob_date},
                {'param': '<strong>target_date</strong>', 'value': target_date},
                {'param': '<strong>include_enddate</strong>', 'value': include_enddate}
            ])
            response = pd.concat([response, get_age]).reset_index(drop=True)
            self.display_static_table(response, static_table_style, "**The computed age below👇**")

    def compute_newdate_st(self):
        """New date computation st module"""
        st.write("**Provide inputs for new date computation👇**")
        input_data = pd.DataFrame(
            [
                {
                    "param": "current_date",
                    "description": "Current date in 'DD-MMM-YYYY' format",
                    "value": self.todays_date
                },
                {
                    "param": "change_str",
                    "description": "The desired date expression",
                    "value": "after 2yrs 3mnths 10days"
                }
            ]
        )
        input_data = input_data.style.set_properties(**{'background-color': 'LightCyan'}, subset=['param'])
        edited_data = st.data_editor(input_data, hide_index=True, disabled=('param', 'description'))
        if st.button('Submit'):
            curr_date, new_date_str = edited_data['value']
            match_str = re.compile(r'^(before|after)\s+(.*)$', re.IGNORECASE).match(new_date_str)
            date_direction, target_date = match_str.groups() if match_str else ('after', '')
            date_direction, target_date = date_direction.lower(), re.sub(r'\s+', ' ', target_date).strip()
            new_date = CalculateTime().derive_new_date(curr_date, target_date, date_direction)
            response = f"<strong>The new date is: <span style='color: DodgerBlue'>{new_date}</span></stong>"
            st.write(response, unsafe_allow_html=True)

    def compute_rel_date(self):
        """Relative date computation st module"""
        note_txt = '''
        <div class="profile-card">
            &#9432; Derives the date that satisfies the desired time as per the given time and reference date. Examples below:
            <ul>
                <li>if today it is <em>'8yrs 2mnths 12days'</em>, then when will it be <em>'10yrs 5mnths 22days'</em> ?</li>
                <li>if on <em>'30-Jul-2024'</em> it is <em>'8yrs 2mnths 12days'</em>, then when was it <em>'5yrs 8mnths 20days'</em> ?</li>
            </ul>
        </div>
        '''
        st.markdown(note_txt, unsafe_allow_html=True)
        st.write("**Provide inputs for relative date computation👇**")
        input_data = pd.DataFrame(
            [
                {
                    "param": "current_time",
                    "description": "Current time expression",
                    "value": '8yrs 2mnths 12days'
                },
                {
                    "param": "desired_time",
                    "description": "Desired time expression",
                    "value": '10yrs 5mnths 22days'
                },
                {
                    "param": "reference_date",
                    "description": "The reference in 'DD-MMM-YYYY' format",
                    "value": self.todays_date
                }
            ]
        )
        input_data = input_data.style.set_properties(**{'background-color': 'LightCyan'}, subset=['param'])
        edited_data = st.data_editor(input_data, hide_index=True, disabled=('param', 'description'))
        if st.button('Submit'):
            curr_time_str, reqd_time_str, ref_date = edited_data['value']
            rel_date = CalculateTime().derive_relative_date(curr_time_str, reqd_time_str, ref_date)
            refd_parsed = datetime.strptime(ref_date, '%d-%b-%Y')
            reld_parsed = datetime.strptime(rel_date, '%d-%b-%Y')
            comp_str_1 = 'was' if refd_parsed < self.today else 'is' if refd_parsed == self.today else 'would be'
            comp_str_2 = 'would be' if reld_parsed < self.today else 'is' if reld_parsed == refd_parsed else 'will be'
            response = f'''
            <div class='output-card-1'>
                <strong>
                    On {ref_date}, it {comp_str_1}: <span style='color: DodgerBlue'>{curr_time_str}</span><br>
                    On {rel_date}, it {comp_str_2}: <span style='color: DodgerBlue'>{reqd_time_str}</span>
                </stong>
            </div>
            '''
            st.write(response, unsafe_allow_html=True)

    def compute_totaltime_st(self):
        """Total time computation st module"""
        note_txt = '''
        <div class="profile-card">
            &#9432; Computes total elapsed and lapsed times from given times list. The individual time components can be provided as:
            <ul>
                <li>time strings, e.g. [<em>'3 Months 9 Days'</em>, <em>'2 Years 5 Months 11 Days'</em>, '5 yrs 8 mnths 600 hrs']</li>
                <li>from_dates and to_dates, e.g. [<em>('19-Aug-2013', '09-Nov-2015')</em>, <em>('21-Dec-2015', '17-Sep-2021')</em>]</li>
            </ul>
        </div>
        '''
        st.markdown(note_txt, unsafe_allow_html=True)
        time_op = st.selectbox(
            label='How do you wanna provide the time entities ?',
            options=('as time strings', 'as from-to dates'),
            index=None
        )
        if time_op == 'as time strings':
            st.write("**Enter the time strings👇**")
            time_df = st.data_editor(
                pd.DataFrame([{"time_str": '0yr 0mnths 0days'}]),
                use_container_width=True,
                hide_index=True,
                num_rows='dynamic'
            )
        elif time_op == 'as from-to dates':
            st.write("**Enter _'from_date'_ and _'to_date'_ dates👇**")
            ymd = datetime.today().year, datetime.today().month, datetime.today().day
            time_df = st.data_editor(
                pd.DataFrame([{"from_date": date(*ymd), "to_date": date(*ymd)}]),
                column_config={
                    "from_date": st.column_config.DateColumn(format='DD-MMM-YYYY'),
                    "to_date": st.column_config.DateColumn(format='DD-MMM-YYYY')
                },
                hide_index=True,
                num_rows='dynamic'
            )
        if time_op:
            st.write("**Provide values for the following params👇**")
            input_data = pd.DataFrame(
                [
                    {
                        "param": 'units',
                        "description": 'Conversion units as a combination of `YQMWDhms`',
                        "value": 'YMD'
                    },
                    {
                        "param": 'include_enddate',
                        "description": 'Whether to include end date in the computation',
                        "value": 'True'
                    },
                    {
                        "param": 'format',
                        "description": "The display format",
                        "value": '1'
                    }
                ]
            )
            input_data = input_data.style.set_properties(**{'background-color': 'LightCyan'}, subset=['param'])
            params_data = st.data_editor(input_data, hide_index=True, disabled=('param', 'description'))
            if st.button('Compute now !'):
                to_units, include_enddate, format_type = params_data['value']
                include_enddate, format_type = eval(include_enddate), int(format_type)
                time_df.dropna(inplace=True)  # drop unintential `None` entries
                if time_op == 'as time strings':
                    time_list = list(time_df['time_str'])
                else:
                    time_list = reduce(lambda x, y: x+y, [[(
                        r[0].strftime('%d-%b-%Y'), r[1].strftime('%d-%b-%Y'))] for _, r in time_df.iterrows()])
                tot_time = CalcTimeAssist().compute_total_elapsed_time(time_list, to_units, include_enddate, format_type)
                tot_time = reduce(lambda x, y: x+y, [[' '.join((
                    f"{v[0]}: ", f"<span style='color: DodgerBlue'>{v[1].strip()}</span>"))]
                        for s in tot_time if (v := s.split(':'))])
                response = f"<div class='output-card-1'><strong>{'<br>'.join(tot_time)}</strong></div>"
                st.write(response, unsafe_allow_html=True)

    def display_calendar_st(self):
        """Prints Julian calendar for a given year"""
        st.info(f''':balloon: Displays the Julian calendar for any given year
                (e.g. display the calendar for: {self.today.year})''')
        input_data = pd.DataFrame(
            [
                {
                    "param": 'year',
                    "description": 'Provide the 4-digit year for calendar display',
                    "value": datetime.today().year
                }
            ]
        )
        input_data = input_data.style.set_properties(**{'background-color': 'LightCyan'}, subset=['param'])
        params_data = st.data_editor(input_data, hide_index=True, disabled=('param', 'description'))
        if st.button('Get calendar !'):
            cal_year = int(params_data['value'])
            st.text(f".{calendar.calendar(cal_year, 3, 1, 4, 3)}")

    def find_day_st(self):
        """Finds day name for a given date in 'DD-MMM-YYYY' format"""
        st.info(f''':balloon: Finds the day for any given date in 'DD-MMM-YYYY' format
                (e.g. which day is: '{self.todays_date}' ?)''')
        input_data = pd.DataFrame(
            [
                {
                    "param": 'date',
                    "description": "Enter date in the 'DD-MMM-YYYY' format",
                    "value": self.todays_date
                }
            ]
        )
        input_data = input_data.style.set_properties(**{'background-color': 'LightCyan'}, subset=['param'])
        params_data = st.data_editor(input_data, hide_index=True, disabled=('param', 'description'))
        if st.button('Get day name!'):
            date_str = params_data['value'][0]
            parse_date = datetime.strptime(date_str, '%d-%b-%Y')
            comp_str = 'was' if parse_date < self.today else 'is' if parse_date == self.today else 'will be'
            parse_day, parse_month, parse_year = parse_date.strftime('%A'), parse_date.month, parse_date.year
            curr_cal = calendar.HTMLCalendar().formatmonth(parse_year, parse_month)
            response = f'''
                <div class='output-card-2'> <strong>
                    {date_str} {comp_str}:
                    <span style='color: DodgerBlue'>
                        {parse_day}
                    </span></strong>
                </div>
                {curr_cal}
            '''
            st.write(response, unsafe_allow_html=True)

    def main_executor(self):
        """The main module that performs all tasks and displays to page"""
        selected_op = st.radio(
            label='Select the desired time operation to perform',
            options=('Convert time', 'Compute age', 'Compute new date', 'Compute relative date',
                     'Derive total time', 'Display calendar', 'Find day for a date'),
            index=None,
            horizontal=True
        )
        if selected_op == 'Convert time':
            self.convert_time_st()
        elif selected_op == 'Compute age':
            self.compute_age_st()
        elif selected_op == 'Compute new date':
            self.compute_newdate_st()
        elif selected_op == 'Compute relative date':
            self.compute_rel_date()
        elif selected_op == 'Derive total time':
            self.compute_totaltime_st()
        elif selected_op == 'Display calendar':
            self.display_calendar_st()
        elif selected_op == 'Find day for a date':
            self.find_day_st()


# +++++++++++++++++
# The main streamlit operations for this page
if __name__ == "__main__":
    CalcTimeStAssist().main_executor()
