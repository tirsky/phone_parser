import re
import unicodedata
import urllib.parse
from string import digits

import requests
from bs4 import BeautifulSoup

INVIS_ELEMS = ('style', 'script', 'head', 'title')
EXCLUDE_PATH = 'mc.yandex.ru'


class PhoneParser:
    """This class returns phone number in 8XXXNNNNNNN format for russian formats and NNNNNNN for moscows's format"""

    def __init__(self, url=str()):
        self.url = url

    def get_phone_from(self, path_to_page=str()):
        uri = urllib.parse.urljoin(self.url, path_to_page)
        r = requests.get(uri)
        soup = BeautifulSoup(r.content, 'html5lib')
        text_lines = self._visible_texts(soup).split('  ')
        phones = []
        for line in text_lines:
            if EXCLUDE_PATH in line:  # for yametrics only
                continue
            res = self._find_phone(line)
            phones.extend(res)
        return phones

    def _visible_texts(self, soup):
        re_spaces = re.compile(r'\s{3,}')
        """ get visible text from a document """
        text = ' '.join([
            s for s in soup.strings
            if s.parent.name not in INVIS_ELEMS
        ])
        # collapse multiple spaces to two spaces.
        return re_spaces.sub('  ', text)

    @staticmethod
    def replace_phone_symbols(phone_number):
        is_phone_number = 0
        phone_number = phone_number.strip()
        if ' ' in phone_number:
            is_phone_number += 1
        if '-' in phone_number:
            is_phone_number += 1
        if phone_number.startswith('+7'):
            is_phone_number += 1
        if phone_number.startswith('8 '):
            is_phone_number += 1
        if is_phone_number >= 1:
            is_phone_number = True
        else:
            is_phone_number = False
        phone_number = unicodedata.normalize("NFKD", phone_number)  # from soup we get not decoded data
        phone_number = phone_number.replace(' ', '').replace('(', '').replace(')', '').replace('-', '').replace('+', '')
        return phone_number, is_phone_number

    def _phone_number_format_out(self, phone_number):
        if len(phone_number) == 11 and phone_number.startswith('7'):
            phone_number = phone_number[:0] + '8' + phone_number[1:]
        elif len(phone_number) == 10:
            phone_number = '8{}'.format(phone_number)
        elif len(phone_number) > 11:
            return ''
        elif len(phone_number) < 11 and len(phone_number) > 7:
            return ''
        return phone_number

    def _find_phone(self, text_str):
        regex = r"(\+?[78]?[-\s]?\(?\d{3,5}\)?[\s.\-]?(\d{1,3})[\s.\-]?(\d{1,3})[\s.\-]?(\d{1,3}))"
        matches = re.finditer(regex, text_str)
        tels = []
        for match in matches:
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                phone_number, is_phone_number = self.replace_phone_symbols(match.group(groupNum))
                if len(phone_number) < 7:
                    continue
                if is_phone_number is not True:
                    continue
                tels.append(self._phone_number_format_out(phone_number))
        return tels


# URL = "https://repetitors.info"
pr = PhoneParser('https://hands.ru/')
print(pr.get_phone_from('company/about'))
