import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

goodreads_key = os.getenv('GOODREADS_API_KEY')

def fetch_data():
	# goodreads fetch request
	http_response = requests.get('https://www.goodreads.com/review/list?v=2', data = {'v': '2','id': '94096085','shelf': 'to-read','per_page': '200','key': goodreads_key})

	return http_response

def create_soup(response):
	# creating soup from response
	soup = BeautifulSoup(response.content, "xml")

	# re-assinging soup with only book info
	return soup.find_all('book')

def process_soup(soup):
	books = []
	for item in soup:
		goodreads_fulltitle = item.title.string
		
		# removing any quote marks from titles
		if '"' in goodreads_fulltitle:
			goodreads_fulltitle = goodreads_fulltitle.replace('"', '')
		
		# splitting title and tagline if present
		if ":" in goodreads_fulltitle:
			goodreads_fulltitle_list = goodreads_fulltitle.split(':', 1)
			goodreads_title = goodreads_fulltitle_list[0].strip()
			goodreads_tagline = goodreads_fulltitle_list[1].strip()
		else:
			goodreads_title = goodreads_fulltitle.strip()
			goodreads_tagline = ""
		
		goodreads_author = item.find("name").string

		book = {
			"title": goodreads_title,
			"tagline": goodreads_tagline,
			"author": goodreads_author
		}

		books.append(book)
	
	return books

def main():
	print("Grabbing Good Reads list")
	goodreads_data = fetch_data()
	goodreads_soup = create_soup(goodreads_data)
	goodreads_books = process_soup(goodreads_soup)
	return goodreads_books

if __name__ == "__main__":
	main()