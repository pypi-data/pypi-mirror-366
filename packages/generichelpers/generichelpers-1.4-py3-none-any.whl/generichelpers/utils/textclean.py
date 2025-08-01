"""text preprocessing class"""

# -*- coding: utf-8 -*-
# @author Ratnadip Adhikari

import re
import unicodedata
from collections import Counter
from bs4 import BeautifulSoup
from utils.genericutils import elapsedTime


class PreprocessText:
    """Text preprocessing class"""
    def __init__(self):
        pass  # initialized class with empty constructor

    def spaces_clean(self, text_str):
        """Clean tabs/linebreaks/extra spaces in a string"""
        return re.sub(r"\s+", " ", text_str).strip()

    def ascii_filter(self, text_str):
        """The ascii encoder function for a string"""
        text_str = (
            unicodedata.normalize("NFKD", text_str)
            .encode("ascii", "ignore")
            .decode("utf-8", "ignore")
        )
        return text_str

    def spchars_remove(self, text_str, replace_str="", remove_digits=True):
        """The special characters cleaner function for a string"""
        pattern = r"[^\\\/a-zA-Z\s]+" if remove_digits else r"[^\\\/a-zA-Z0-9\s]+"
        return re.sub(pattern, replace_str, text_str)

    def stopwords_clean(self, text_str: str, stop_words: list):
        """The stopwords removal function"""
        stopw_dict, words_list = Counter(stop_words), text_str.split()
        text_str = " ".join(
            [
                wd
                for wd in words_list
                if self.spchars_remove(wd.lower()).strip() not in stopw_dict
            ]
        )
        return text_str

    def emptyvals_drop(self, text_list: list):
        """Removes null/empty values from a list of text strs"""
        return [s for s in text_list if s and str(s) != "nan"]

    def duplicates_drop(self, text_list: list):
        """Removes duplicates from a list of text strs"""
        return list(dict.fromkeys(text_list))

    def replace_string(self, given_string: str, replacement_dict: dict):
        """Replace the occurences of items in: `replacement_dict` from `given_string`"""
        replaced_string = given_string
        for original_str, replace_str in replacement_dict.items():
            replaced_string = replaced_string.replace(original_str, str(replace_str))
        return replaced_string

    def clean_html_tags(self, html_text):
        """Clean html tags from the given text"""
        soup = BeautifulSoup(html_text, "html.parser")
        return self.spaces_clean(soup.get_text(separator=" "))

    @elapsedTime
    def preprocess_text(
        self,
        text_str,
        stop_words=[],
        remove_spchars=True,
        replace_str='',
        remove_digits=True,
        print_el_time=True,
    ):
        """This function preprocesses a text string"""
        text_str = self.ascii_filter(text_str)
        text_str = self.spchars_remove(text_str, replace_str, remove_digits) if remove_spchars else text_str
        text_str = self.stopwords_clean(text_str, stop_words)
        text_str = self.spaces_clean(text_str)
        return text_str

    @elapsedTime
    def preprocess_textlist(
        self,
        text_list,
        stop_words=[],
        remove_spchars=True,
        replace_str='',
        remove_digits=True,
        remove_nulls=True,
        remove_dupli=True,
        print_el_time=True,
    ):
        """This function preprocesses a list of text strs"""
        clean_list = text_list.copy()
        clean_list = [self.ascii_filter(s) for s in clean_list]
        clean_list = [self.spchars_remove(s, replace_str, remove_digits) for s in clean_list] if remove_spchars else clean_list
        clean_list = [self.stopwords_clean(s, stop_words) for s in clean_list]
        clean_list = [self.spaces_clean(s) for s in clean_list]
        clean_list = self.emptyvals_drop(clean_list) if remove_nulls else clean_list
        clean_list = self.duplicates_drop(clean_list) if remove_dupli else clean_list
        return clean_list
