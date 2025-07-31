# bookspointer

A package for scraping and serving book data.

## Installation

```bash
pip install bookspointer
```

## Usage

Import and use the modules in your Python code:

```python
from bookspointer.scraper import BookScraper
from bookspointer.server import BookAPI, AuthorAPI, TokenAPI
from bookspointer.sheet import AuthorSheetManager
from bookspointer.api import BookspointerAPI

from rich import print
import random

def multipage_links():
    with open('multi_page.txt', 'r') as f:
        links = f.readlines()
    
    return links
    
# Initialize the main classes
scraper = BookScraper(multi_page_links=multipage_links())  # Categories to scrape by single page
book_api = BookAPI()
author_api = AuthorAPI()

    
    
def update_authors_from_bookspointer():
    """
    Fetches authors from a Google Sheet using AuthorSheetManager and updates them on the server.
    """
    # Fetch and update authors from Google Sheet to your server
    author_sheet = AuthorSheetManager().run()


def update_books_from_authors():
    """
    Fetches unscraped authors from the server, scrapes their books, adds the books to the server, and marks authors as scraped.
    """
    # Fetch unscraped authors and update their books
    authors = author_api.get_unscraped_authors()
    for author in authors:
        author_url = author.get('author_link')
        author_name = author.get('author_name', 'Unknown')
        author_id = author.get('author_id')
        if not author_url:
            continue
        books = scraper.get_book_list(author_url)
        for book in books:
            book_list = scraper.get_book_details(book, author_id)
            for book in book_list:
                add_book = book_api.create(book)
                print(
                    f"Added book: {book['title']} by {author_name} with ID: {add_book}")

            author_api.update(author.get('id'), {"is_scraped": "yes"})

        print(f"Finished scraping books for author: {author_name}")

def post_books_on_bookspointer():
    """
    Posts all books that have not yet been posted to Bookspointer using random tokens for authentication.
    """
    books = book_api.get_all_books(is_posted=False)
    tokens = TokenAPI().get_all_tokens()
    for book in books:
        token = random.choice(tokens)
        bookspointer_api = BookspointerAPI(token)
        try:
            bookspointer_api.post_book(book)
        except Exception as e:
            print(f"Error posting book {book['title']}: {e}")
            continue


def main():
    """
    Orchestrates the process of updating authors, updating books, and posting books by calling the respective functions in sequence.
    """
    print("Starting to update authors from Bookspointer...")
    update_authors_from_bookspointer()
    print("Authors updated successfully.")
    print("Starting to update books from authors...")
    update_books_from_authors()
    print("Books updated successfully.")
    print("Starting to post books on Bookspointer...")
    post_books_on_bookspointer()
    print("All books posted successfully.")


if __name__ == "__main__":
    main()

```

## Features

- Scrape book data
- Serve book data via API
- Sync authors and books with Google Sheets

## Project Links

- [Homepage](https://github.com/samircd4)
- [Repository](https://github.com/samircd4/bookspointer)

## License

MIT
