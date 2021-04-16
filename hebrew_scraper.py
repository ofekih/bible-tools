from src.data_manager import VerseIdentifier
from src.paths import MM_CSV_PATH


import csv
import requests
from bs4 import BeautifulSoup

BASE_MECHON_URL = 'https://www.mechon-mamre.org/p/pt/pt'

BOOK_LIST = [(f'0{num}', num) for num in range(1, 8)] + [('29', 8)]
SPLIT_BOOK_LIST = [('08', 9), ('09', 11), ('25', 13), ('35', 15)]
BOOK_LIST += [('33', 17), ('27', 18), ('26', 19), ('28', 20), ('31', 21), ('30', 22), ('10', 23), ('11', 24), ('32', 25), ('12', 26), ('34', 27)]
BOOK_LIST += [(str(num), num + 15) for num in range(13, 25)]

def load_soup(url: str) -> str:
	response = requests.get(url)
	return BeautifulSoup(response.content, 'html5lib')


def add_book(url: str, book: int, bible_verses: {VerseIdentifier: str}, split: bool = False):
	soup = load_soup(url)

	for (heading, table) in zip(soup.find_all('h2'), soup.find_all('table')):
		chapter = int(heading.get_text()[heading.get_text().rindex(' '):])

		book_offset = 0
		if split:
			book_symbol = heading.get_text()[0]
			if book_symbol == 'E': # Ezra
				book_offset = 0
			elif book_symbol == 'N': # Nehemiah
				book_offset = 1
			else:
				book_offset = int(book_symbol) - 1

		for row in table.find_all('tr'):
			hebrew, english = row.find_all('td')
			verse = int(english.find('b').get_text())

			hebrew.find('b').decompose()

			bible_verses[VerseIdentifier(book = book + book_offset, chapter = chapter, verse = verse)] = hebrew.get_text().strip().replace(u'\xa0', u' ')

def _write_csv(bible_verses: {VerseIdentifier: str}):
	with open(MM_CSV_PATH, 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter = ',')
		writer.writerow(['id', 'b', 'c', 'v', 't'])

		for (identifier, verse) in sorted(bible_verses.items()):
			writer.writerow(['-', identifier.book, identifier.chapter, identifier.verse, verse])

def _run():
	bible_verses = dict()

	for (book_url_end, book_number) in BOOK_LIST:
		add_book(BASE_MECHON_URL + book_url_end + '.htm', book_number, bible_verses)

	for (book_url_end, book_number) in SPLIT_BOOK_LIST:
		add_book(BASE_MECHON_URL + book_url_end + '.htm', book_number, bible_verses, split = True)

	_write_csv(bible_verses)


if __name__ == '__main__':
	_run()
