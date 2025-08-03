"""Parse and extract useful info from salary pdf files"""
# -*- coding: utf-8 -*-
# @author Ratnadip Adhikari

from __future__ import absolute_import

import re
from calendar import month_abbr
from copy import deepcopy
from datetime import datetime
from functools import reduce
from itertools import product

import pandas as pd
import pdfplumber
from devs import PAYSLIP_COMPONENTS
from utils.dtypesutils import DtypesOpsHandler
from utils.textclean import PreprocessText


class PayslipParser(object):
    """The salary parser class"""

    def __init__(self):
        self.parsed_payslips = {}  # the parsed payslip obj
        self.payslips_df = pd.DataFrame()  # the combined payslips df
        self.monthyrs_dict = {}  # all available month and yers in the parsed payslips
        self.agg_paycomps = {}  # the aggregated payslip components

    @staticmethod
    def _validate_paystr(pay_str: str):
        """Validates if a pay str contains at least one alphabet, one digit and decimal (optional).
        >>> ['Basic 3000', 'Provident Fund 1800', '   Provident Fund 1800'] --> returns True
        >>> ['Basic', '   235 ', '7987'] --> returns False
        """
        check_str = re.sub(r'\s+', ' ', pay_str).strip()
        if not check_str:
            return False
        return not bool(re.fullmatch(r'(^[^\d]*$)|(^[^a-zA-Z]*$)', check_str))

    @staticmethod
    def _eval_str(text_str: str):
        """Evals a str. In case of error, returns `None`"""
        try:
            check_str = PreprocessText().spaces_clean(text_str)
            return eval(check_str)
        except Exception:
            return

    @staticmethod
    def _concat_payslip_dfs(payslips: dict, set_index=''):
        """Row-wise concat 'pay_elements' dfs from parsed payslips

        Parameters
        ----------
        payslips (dict):
            Parsed payslips dict
        set_index (str):
            The column to set index for the concatenated df. Can be empty if not required.

        Returns
        ----------
        The concatenated payslip df
        """
        payslip_df = reduce(lambda x, y: pd.concat([x, y]), [v['pay_elements'] for k, v in payslips.items()])
        payslip_df.reset_index(drop=True, inplace=True)
        if set_index and set_index in payslip_df.columns:
            payslip_df.set_index(set_index, inplace=True)
        return payslip_df

    def _extract_monthyear(self, input_str):
        """Extracts month year in MMM-YYYY format from the `input_str`."""
        patterns = [
            r'(?i)\b(\w+)[^\w|s]*(\d{4})\b',    # matches 'Feb-2016', 'FEBRUARY 2016', 'Nov 2021' etc.
            r'(?i)\b(\w+)[^\w|s]*(\d{2})\b',    # matches 'April-24', 'Mar-16' etc.
        ]
        for pattern in patterns:
            match = re.search(pattern, input_str)
            if match:
                month, year = match.groups()
                if len(year) == 2:
                    year = '20' + year
                try:
                    # Parse and format the date correctly
                    date = datetime.strptime(f'{month} {year}', '%B %Y')
                    return date.strftime('%b-%Y')
                except ValueError:
                    try:
                        # Attempt to parse abbreviated month names
                        date = datetime.strptime(f'{month} {year}', '%b %Y')
                        return date.strftime('%b-%Y')
                    except ValueError:
                        continue
        return None

    def _clean_payslip(self, payslip: str):
        # """Parse a single payslips and extract useful components, e.g. -- 'Net Salary', 'Deductions' etc."""
        """Clean a payslip to get rid of non-ascii chars, extra spaces etc."""
        clean_payslip = PreprocessText().ascii_filter(payslip).split('\n')  # clean the payslip text
        clean_payslip = [re.sub(r'(\b\w)\s+(\w)', r'\1\2', s) for s in clean_payslip]  # corrects odd spaces
        clean_payslip = [_ctxt for _txt in clean_payslip if (_ctxt := PreprocessText().spaces_clean(_txt))]
        return clean_payslip

    def _match_key(self, strs, keys, pos=None):
        """Given single/multiple strings: `'strs'` and `'keys' (str or tuple of strs)`, the func returns the
        index where at least one of the  `'keys'` str matches at the `'pos' ('start', 'end', 'any', `None`)`.
        If no match is found, it returns `None`.
        """
        if not keys:
            return None
        keys_lower = tuple([k.lower() for k in keys]) if isinstance(keys, tuple) else tuple([keys.lower()])
        str_list = strs if isinstance(strs, list) else [strs]
        for idx, s in enumerate(str_list):
            s_lower = s.lower()
            if pos in ('start', 'end', 'any'):
                check_match = s_lower.startswith(keys_lower) if pos == 'start' else s_lower.endswith(
                    keys_lower) if pos == 'end' else any(k in s_lower for k in keys_lower) if pos == 'any' else None
            else:
                check_match = s_lower.startswith(keys_lower) | any(k in s_lower for k in keys_lower) | \
                    s_lower.endswith(keys_lower)
            if check_match:
                return idx
        return None

    def _parse_paycomps(self, paycomps: list, monthyr=''):
        """Parse pay components and convert to useable items"""
        paycomps_ = [s for s in paycomps if self._validate_paystr(s)]
        paycomps_ = re.sub(',', '', ' '.join(paycomps_))
        paycomps_ = re.split(r'(?<=\d)\s+(?=[A-Za-z])|(?<=\d)\s+(?=\d+[A-Za-z])', paycomps_)
        paycomps_ = [cs for s in paycomps_ if (cs := PreprocessText().spaces_clean(s))]
        parsed_paycomps, col_names = [], []
        for paycomp in paycomps_:
            found_matches = re.compile(r'(\d+\D+|[^\d]+)([\d.]+)').findall(paycomp)
            gather_comps = [(m[0].strip(), m1) for m in found_matches if (m1 := self._eval_str(m[1])) is not None]
            gather_comps = DtypesOpsHandler().flatten_iterable(gather_comps)
            gather_comps = [s for s in gather_comps if s not in ['', None]]
            if gather_comps:
                gather_comps = [monthyr] + gather_comps
                parsed_paycomps.append(gather_comps)
        # Convert parsed component list to df
        tot_len = max(map(len, parsed_paycomps))
        col_names += (['month_year'] if monthyr else []) + (['pay_item'] if parsed_paycomps else []) +\
            [f'paycol_{c}' for c in range(tot_len - 2)]
        parsed_paycomps = pd.DataFrame(parsed_paycomps, columns=col_names)
        return parsed_paycomps

    def _extract_components(self, payslip: list, extract_dict: dict):
        """Extracts useful info from a cleaned payslip, e.g. -- company & employee info, salary components etc.

        Parameters
        ----------
            payslip (list):
                A cleaned list of payslip strs
            extract_dict:
                A dict of the below depicted form to extract specific components\n
                    extract_dict = {
                        'component_1': ['start_str'],
                        'component_2': ['start_str', 'end_str'],
                        'component_3': [['start_str_1', 'start_str_2'], 'end_str']
                    }
                It must have keys from `PAYSLIP_COMPONENTS`.
            month_key (str):
                The optional month key; must be present in the `extract_dict`
            salary_key (str):
                The optional salary key; must be present in the `extract_dict`

        Example
        ----------
        >>> payslip = [
            'ABC company',
            'Address, Line 1',
            'Address, Line 2',
            'Payslip for the month of FEBRUARY 2016',
            'Employee Number: XXXXX',
            'Employee Name: XXXXX XXXXX',
            'Location :XXXXX, XXX, XXX',
            'Joining Date :21-DEC-2015',
            'Designation: XXXX XXXX XXXX',
            'EARNINGS MASTER RATE PAID',
            'BASIC 11111 11111',
            'House Rent Allowance 11111 11111',
            'Income Tax 11111',
            'Total Earnings Rs. 11111 Total Deductions Rs. 11111 Net Salary Rs. 11111',
            'Additional text'
        ]
        >>> extract_dict = {
            'company_name': ['ABC company'],
            'company_address': ['Address, Line 1', 'Address, Line 2'],
            'month_info': [('Payslip for', 'Salary Slip for')],
            'employee_info': ['Employee', 'Designation'],
            'pay_elements': ['BASIC', 'Total Earnings']
            'additional_info': ['Additional text']
        }

        Returns
        ----------
        The extracted components as per the `extract_dict`
        """
        payslip_info = {}
        extract_dict = {k: v for k, v in extract_dict.items() if k in PAYSLIP_COMPONENTS}
        for info_key, info_item in extract_dict.items():
            start_str = info_item[0] if len(info_item) else ''
            end_str = info_item[1] if len(info_item) == 2 else ''
            start_idx, end_idx = self._match_key(payslip, start_str), self._match_key(payslip, end_str)
            if (not start_idx) and ('__' in start_str):
                start_idx = 0
            if (not end_idx) and ('__' in end_str):
                end_idx = len(payslip) - 1
            if (start_idx is not None) and (end_idx is not None):
                payslip_info[info_key] = [payslip[i] for i in range(start_idx, end_idx+1)]
            elif start_idx is not None:
                payslip_info[info_key] = [payslip[start_idx]]
            elif end_idx is not None:
                payslip_info[info_key] = [payslip[end_idx]]
        payslip_info = {_key: _info if _key == 'pay_elements' else self._extract_monthyear('\n'.join(_info)) if
                        _key == 'month_info' else '\n'.join(_info) for _key, _info in payslip_info.items()}
        payslip_info = {_key: self._parse_paycomps(_info, payslip_info.get('month_info')) if
                        _key == 'pay_elements' else _info for _key, _info in payslip_info.items()}
        return payslip_info

    def _filter_payslips(self, payslips: dict, filter_dict: dict):
        """Filter parsed payslips, based on `filter_dict`

        Parameters
        ----------
        payslips (dict):
            Parsed payslips dict
        filter_dict (dict):
            The dict to be used for filtering. If present (non-null), it should be of the following form.
            The keys of the `filter_dict` must be one of the keys as shown below.\n
            >>> filter_dict = {
                'company_name': 'Fractal Analytics',
                'designation_info': 'Data Scientist',
                'month_info': ['Jan-2022', 'Feb-2022', 'Jan-2023', 'Feb-2023'],
                'pay_elements': {
                    'Basic': 0,
                    'TDS': 0,
                    'Net Salary': 1
                }  # should contain {paycomp_key: paycol_index}
            }
        """
        filtered_payslips = deepcopy(payslips)
        myears = set(filter_dict.get('month_info', []))
        payels = list(filter_dict.get('pay_elements', {}).keys())
        all_keys = set(DtypesOpsHandler().flatten_iterable([list(v.keys()) for v in payslips.values()]))
        for fkey, fitem in filter_dict.items():
            if not fitem or (fkey not in all_keys):
                continue
            elif fkey not in ['month_info', 'pay_elements']:
                _fitem = tuple([PreprocessText().spaces_clean(k) for k in fitem.split(',')])
                filtered_payslips = {k: v for k, v in filtered_payslips.items() if self._match_key(
                    v.get(fkey, []), _fitem) is not None}
            elif fkey == 'month_info':
                filtered_payslips = {k: v for k, v in filtered_payslips.items() if v.get('month_info') in myears}
            elif fkey == 'pay_elements':
                for k, v in filtered_payslips.items():
                    orig_payels = v.get('pay_elements', pd.DataFrame())
                    if not orig_payels.empty:
                        pay_items = list(orig_payels['pay_item'])
                        filtered_payels = pd.DataFrame()
                        for payel in payels:
                            match_idx = self._match_key(pay_items, payel)
                            if match_idx is not None:
                                match_row = orig_payels.iloc[[match_idx]]
                                match_row['pay_item'] = payel
                                filtered_payels = pd.concat([filtered_payels, match_row], ignore_index=True)
                                filtered_payslips[k]['pay_elements'] = filtered_payels
        # if not filtered_payslips:
        #     filtered_payslips = deepcopy(payslips)
        return filtered_payslips

    def _agg_payslips(self, payslips: dict, agg_dict: dict):
        """Compute aggregation of payslip components

        Parameters
        ----------
        payslips (dict):
            Parsed (and filtered) payslips dict
        agg_dict (dict):
            A dict of agg components of the form\n
            >>> agg_dict = {
            'Basic': 0,
            'TDS': 0,
            'Net Salary': 1
        }  # should contain {paycomp_key: paycol_index}
        """
        if not (payslips and agg_dict):
            return
        payslip_df, agg_paycomps = self._concat_payslip_dfs(payslips, 'month_year'), {}
        for payel, idx in agg_dict.items():
            if pd.isna(idx):
                paycol_name = 'paycol_x'
                filter_df = payslip_df.loc[payslip_df['pay_item'] == payel]
                filter_df[paycol_name] = filter_df.iloc[:, 1:].where(filter_df.iloc[:, 1:].gt(0)).min(axis=1)
                filter_df = filter_df[['pay_item', paycol_name]]
            else:
                paycol_name = f'paycol_{int(idx)}'
                filter_df = payslip_df.loc[payslip_df['pay_item'] == payel, ['pay_item', paycol_name]]
            if not filter_df.empty:
                min_df = filter_df.iloc[[filter_df[paycol_name].argmin()]]
                max_df = filter_df.iloc[[filter_df[paycol_name].argmax()]]
                # +++++++++++++++++
                # Update res dict with various aggs
                agg_paycomps.update(
                    {
                        payel: {
                            'Sum': filter_df[paycol_name].sum().round(2),
                            'Min': filter_df[paycol_name].min().round(2),
                            'Max': filter_df[paycol_name].max().round(2),
                            'Mean': filter_df[paycol_name].mean().round(2),
                            'Median': filter_df[paycol_name].median().round(2),
                            'min_in': min_df.index[0],
                            'max_in': max_df.index[0]
                        }
                    }
                )
        return agg_paycomps

    def parse(self, file_stream, extract_dict=PAYSLIP_COMPONENTS, **kwargs):
        """Parse payslips and extract components

        Parameters
        ----------
        file_stream:
            The pdf file object or path.
        extract_dict:
            A dict of the below depicted form to extract specific components\n
                extract_dict = {
                    'component_1': ['start_str'],
                    'component_2': ['start_str', 'end_str'],
                    'component_3': [['start_str_1', 'start_str_2'], 'end_str']
                }
            It muct have keys from `PAYSLIP_COMPONENTS`.
        kwargs:
            Additional args for `PdfReader()` [e.g. 'password'].
        """
        # First read texts
        # reader_attrs = {k: v for k, v in kwargs.items() if k in get_func_attrs({}, PdfReader, False, False)}
        pdf_reader = pdfplumber.open(file_stream)
        total_pages = len(pdf_reader.pages)
        all_payslips = {k: pdf_reader.pages[k].extract_text() for k in range(total_pages)}
        clean_payslips = {k: self._clean_payslip(all_payslips[k]) for k in range(total_pages)}
        parsed_payslips = {k: self._extract_components(clean_payslips[k], extract_dict) for k in range(total_pages)}
        payslips_df = self._concat_payslip_dfs(parsed_payslips)  # Get combined payslips df
        # +++++++++++++++++
        # Get all available month and years
        all_mnthyrs = [minfo for _, paycomp in parsed_payslips.items() if (minfo := paycomp.get('month_info'))]
        all_years = sorted(list(set([myr.split('-')[1] for myr in all_mnthyrs])))
        all_months = list(month_abbr)[1:]
        # +++++++++++++++++
        # Assign parsed elements to the class obj
        self.parsed_payslips = parsed_payslips
        self.payslips_df = payslips_df
        self.monthyrs_dict = {'years': all_years, 'months': all_months, 'month_years': all_mnthyrs}

    def aggregate(self, parsed_payslips={}, monthyrs_dict={}, agg_dict={}):
        """Aggregate payslip components, based on 'filter_dict'

        Parameters
        ----------
        parsed_payslips (dict):
            The dict containing parsed payslips
        monthyrs_dict (dict):
            A dict containing months and years info, extracted from the payslips. It is of the below form.\n
            >>> monthyrs_dict = {
                'years': ['2022', '2023'],
                'months': ['Jan', 'Feb', 'Mar'],
                'month_years': ['Jan-2022', 'Feb-2022', 'Mar-2022', 'Jan-2023', 'Feb-2023', 'Mar-2023']
            }
        agg_dict (dict):
            A dict with the filtering components of the form below.\n
            >>> agg_dict = {
                'agg_type': 'Sum',  # one of: ['Sum', 'Min', 'Max', 'Mean', 'Median'] (it is optional)
                'filter_years': ['All'],  # or like ['2022', '2023', '2024']
                'filter_months':  ['All'],  # or like ['Jan', 'Feb', 'Mar']
                'exclude_months': ['Feb-2022', 'Aug-2022', 'Mar-2023']
                'company_name': 'Fractal Analytics',  # or ''
                'designation': 'Data Scientist',  # or ''
                'filter_comps': {
                    'Basic': 0,
                    'TDS': 0,
                    'Net Salary': 1
                }  # should contain {paycomp_key: paycol_index}
            }
        """
        # Extract all relevant components from passed params
        all_years, all_months = [monthyrs_dict.get(k, []) for k in ('years', 'months')]
        comp_name, desig = [agg_dict.get(k, '') for k in ('company_name', 'designation')]
        filter_years, filter_months, exclude_months, filter_comps = agg_dict.get('filter_years', []), \
            agg_dict.get('filter_months', []), agg_dict.get('exclude_months', []), agg_dict.get('filter_comps', {})
        # +++++++++++++++++
        # Basic formatting of the components
        filter_years = all_years if (not filter_years) or ('All' in filter_years) else filter_years
        filter_months = all_months if (not filter_months) or ('All' in filter_months) else filter_months
        filter_myears = [my for (m, y) in product(filter_months, filter_years) if (my := f'{m}-{y}') not in exclude_months]
        filter_comps = {PreprocessText().preprocess_text(
            k, [], False, False, print_el_time=False): v for k, v in filter_comps.items()}
        # +++++++++++++++++
        # Perform various filterings as per `agg_dict`
        filter_dict = {
            'company_name': comp_name,
            'designation_info': desig,
            'month_info': filter_myears,
            'pay_elements': filter_comps
        }
        filt_payslips = self._filter_payslips(parsed_payslips, filter_dict)
        self.agg_paycomps = self._agg_payslips(filt_payslips, filter_comps)
