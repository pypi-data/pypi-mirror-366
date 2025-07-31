# Custom imports
from bookspointer.server import BookAPI, TokenAPI

# External imports
from rich import print
import requests

# Standard imports
import json

book_api = BookAPI()
token_api = TokenAPI()


class BookspointerAPI:
    """
    A client for posting books to the external Bookspointer API.

    This class provides functionality to post book data to the external Bookspointer
    platform using authentication tokens. It handles data transformation, file uploads,
    and response processing for book creation operations.

    The class integrates with the internal BookAPI for updating posting status
    and provides comprehensive error handling for API interactions.

    Attributes:
        token (str): Authentication token for the Bookspointer API
        url (str): The API endpoint for creating books
        headers (dict): HTTP headers including authentication and content type
    """

    def __init__(self, token):
        """
        Initialize the BookspointerAPI client with authentication token.

        This method sets up the API client with the necessary headers and
        authentication for posting books to the external platform.

        Args:
            token (str): The Bearer token for API authentication

        Note:
            The token is used in the Authorization header as 'Bearer {token}'.
            The headers are configured to mimic a real browser session for
            compatibility with the external API.
        """
        self.token = token
        self.url = 'https://api.bookspointer.com/admin/create-book'
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-BD,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://bookspointer.com',
            'Referer': 'https://bookspointer.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'authorization': f'Bearer {self.token}',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def post_book(self, book):
        """
        Post a book to the external Bookspointer API.

        This method transforms book data into the format expected by the external
        API and posts it using multipart form data. It handles series information,
        category mapping, and updates the internal posting status.

        Args:
            book (dict): Dictionary containing book information with keys:
                - 'title': Book title
                - 'category': Category name
                - 'category_id': Category ID
                - 'author_id': Author ID
                - 'content': Book content
                - 'book_id': Internal book ID for status updates

        Note:
            The method includes comprehensive error handling and user feedback.
            It automatically determines series information based on category.
            The content is removed from the book dict after posting to save memory.
            The internal book record is updated with posting status regardless of
            the external API response to maintain consistency.

        Returns:
            None: The method prints the response message but doesn't return a value.
        """
        if book['category'] == 'অসম্পূর্ণ বই':
            series = 'অসম্পূর্ণ বই'
        else:
            series = ''

        data_dict = {
            "title": book['title'],
            "category": {
                "id": book['category_id'],
            },
            "author": {
                "id": book['author_id'],
            },
            "content": book['content'],
            "tags": [],
            "seriesName": series,
        }

        files = {
            'data': (None, json.dumps(data_dict), 'application/json')
        }

        response = requests.post(self.url, headers=self.headers, files=files)
        book.pop('content')
        print(book)
        try:
            book_id = response.json()['last_book']['id']
            message = f"Book created with ID: {book_id}"
            update_book = book_api.update(book['book_id'], {'is_posted': True})
        except KeyError:
            message = response.json()['message']
            update_book = book_api.update(book['book_id'], {'is_posted': True})
        except Exception as e:
            message = f"Failed to post book {book['title']} : {e}"

        print("Bookspointer Response:", message)
