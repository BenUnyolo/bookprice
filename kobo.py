# the urllib.request module defines functions and classes which help in opening URLs
# urlopen is a function that will open a specified URL
from urllib.request import urlopen, Request
# parse string into search query format
from urllib.parse import quote_plus
# library for pulling data out of HTML and XML files
from bs4 import BeautifulSoup
# function from a module for comparing sequences
from difflib import SequenceMatcher

import json

import good_reads
# demo lists for testing
from demo_lists import *

# colours for terminal output
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# initialise array for final output
books_final = []

def create_search_dict(book):
    search_dict = {
        "title": quote_plus(book['title']),
        "author": quote_plus(book['author'])
    }
    return(search_dict)

def fetch_page(search_dict):
    # creates request for urlopen
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    reg_url = "https://www.kobo.com/ca/en/search?query=" + \
        search_dict['title'] + "&nd=true&ac=1&ac.author=" + search_dict['author'] + \
        "&ac.title=" + search_dict['title'] + "&fcmedia=Book"
    req = Request(url=reg_url, headers=headers)

    # opens URL
    page = urlopen(req).read()

    return page


def create_soup(book):
    search_dict = create_search_dict(book)
    page = fetch_page(search_dict)
    # parses html into a soup data structure to traverse html
    soup = BeautifulSoup(page, "lxml")

    # selects each book's info from page
    soup = soup.find("div", {"class": "item-info"})

    # TODO DRY
    if (soup == None):
        # split string into list
        name_list = book['author'].split()
        # get last word in string
        last_name = name_list[-1]
        book['author'] = last_name
        search_dict = create_search_dict(book)
        page = fetch_page(search_dict)
        soup = BeautifulSoup(page, "lxml")
        soup = soup.find("div", {"class": "item-info"})

    return soup


def process_soup(soup, goodreads_book):
    if (soup == None):
        current_book = {
            "title": "N/A",
            "tagline": "N/A",
            "author": "N/A",
            "price": -1,
            "price_currency": "N/A",
            "source": goodreads_book["title"],
            "source_author": goodreads_book["author"]
        }
        return current_book

    book_title = soup.find("p", class_="title").text.strip()

    if ":" in book_title:
        book_fulltitle_list = book_title.split(':', 1)
        book_title = book_fulltitle_list[0].strip()
        book_tagline = book_fulltitle_list[1].strip()
    else:
        # TODO fix this code?
        book_tagline = soup.find("p", class_="subtitle") or ""

        if book_tagline != '':
            book_tagline = book_tagline.text.strip()

    book_author = soup.find(
        "a", class_="contributor-name").text.strip()

    book_free = (soup.select('p.price.free'))

    if book_free == []:
        book_price = soup.find("p", class_="price").select(
            "span span")[0].text.strip()
        book_price_currency = soup.find(
            "p", class_="price").select("span span")[1].text.strip()
    else:
        book_price = "0"
        book_price_currency = ""

    current_book = {
        "title": book_title,
        "tagline": book_tagline,
        "author": book_author,
        "price": float(book_price.replace('$', '')),
        "price_currency": book_price_currency,
        "source": goodreads_book["title"],
        "source_author": goodreads_book["author"]
    }

    return current_book


def iterate_goodreads_books(source_list):
    for index, book in enumerate(source_list, start=1):
        print(book)
        # page = fetch_page(create_search_strings(book))
        # soup = create_soup(page)
        soup = create_soup(book)
        # instead of page we can return the selected book
        book_selection = process_soup(soup, book)

        books_final.append(book_selection)


def main(demo_list):
    # books_search_list = demo_list
    books_search_list = good_reads.main()

    iterate_goodreads_books(books_search_list)

    books_final.sort(key=lambda i: i['price'], reverse=True)

    counting = 1
    
    for book in books_final:
        print("\n")
        print(str(counting) + ". " + book["source"] + "|" + book["source_author"] + " -> " + book["title"] + "|" + book["author"] + "|" + bcolors.OKCYAN +
              str(book["price"]) + bcolors.ENDC)
        counting += 1


if __name__ == "__main__":
    main(demo_list)
