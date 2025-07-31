# External imports
from dotenv import load_dotenv
from rich import print
import requests

# Standard imports
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


class BaseAPI:
    """
    A base class providing common HTTP methods for interacting with RESTful APIs.

    This class serves as the foundation for all API client classes in the package.
    It provides standardized methods for GET, POST, PATCH, and DELETE operations
    with proper error handling and response processing.

    Attributes:
        base_url (str): The base URL for all API endpoints
    """

    def __init__(self, base_url=BASE_URL):
        """
        Initialize the API client with a base URL.

        Args:
            base_url (str): The root URL for the API endpoints. 
                           Defaults to the BASE_URL environment variable.
        """
        self.base_url = base_url

    def _get(self, endpoint):
        """
        Send a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint path (e.g., "books/", "authors/")

        Returns:
            requests.Response: The HTTP response object from the API

        Note:
            This is a protected method intended for use by subclasses.
        """
        return requests.get(f"{self.base_url}{endpoint}")

    def _post(self, endpoint, data):
        """
        Send a POST request to the specified endpoint with JSON data.

        Args:
            endpoint (str): The API endpoint path
            data (dict): The JSON data to send in the request body

        Returns:
            requests.Response: The HTTP response object from the API

        Note:
            This is a protected method intended for use by subclasses.
        """
        return requests.post(f"{self.base_url}{endpoint}", json=data)

    def _patch(self, endpoint, data):
        """
        Send a PATCH request to the specified endpoint with JSON data.

        Args:
            endpoint (str): The API endpoint path
            data (dict): The JSON data to update in the request body

        Returns:
            requests.Response: The HTTP response object from the API

        Note:
            This is a protected method intended for use by subclasses.
        """
        return requests.patch(f"{self.base_url}{endpoint}", json=data)

    def _delete(self, endpoint, headers=None):
        """
        Send a DELETE request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint path
            headers (dict, optional): Additional headers to include in the request

        Returns:
            dict: A dictionary containing the response status and message.
                  On success: {"status": "success", "message": "Deleted", "status_code": code}
                  On error: {"status": "error", "message": error_description}

        Note:
            This is a protected method intended for use by subclasses.
            It includes comprehensive error handling and logging.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return {"status": "success", "message": "Deleted", "status_code": response.status_code}
        except requests.RequestException as e:
            print(f"[red]DELETE request failed for {url}: {e}[/red]")
            return {"status": "error", "message": str(e)}


class BookAPI(BaseAPI):
    """
    A client for managing book data through the REST API.

    This class provides comprehensive methods for creating, reading, updating,
    and deleting book records. It handles all book-related operations including
    content management, categorization, and posting status.

    Inherits from BaseAPI to use the common HTTP methods.
    """

    def create(self, book_data: dict):
        """
        Create a new book entry in the API.

        This method takes book data and creates a new book record in the system.
        It transforms the input data to match the API's expected format and
        handles the response appropriately.

        Args:
            book_data (dict): Dictionary containing book details with keys:
                - 'book_id': Unique book identifier
                - 'title': Book title
                - 'author': Author name
                - 'author_id': Author ID
                - 'category': List of categories
                - 'category_id': Category ID
                - 'url': Book URL
                - 'content': Book content

        Returns:
            str or dict: Book ID if successful, or error message dictionary

        Note:
            Categories are joined with commas for API storage.
            The method includes comprehensive error handling and logging.
        """
        data = {
            "book_id": book_data['book_id'],
            "title": book_data['title'],
            "author": book_data['author'],
            "author_id": book_data['author_id'],
            "category": ','.join(book_data['category']),
            "category_id": book_data['category_id'],
            "book_link": book_data['url'],
            "content": book_data['content'],
        }
        
        response = self._post("books/", data)
        try:
            resp_json = response.json()
        except Exception:
            resp_json = {}
        if hasattr(response, 'status_code') and response.status_code == 201 and resp_json.get('book_id'):
            print(
                f"Book created successfully. Title: {data.get('title')}, ID: {resp_json.get('book_id')}")
            return resp_json.get('book_id', '')
        else:
            error_msg = resp_json.get('message', response.text if hasattr(
                response, 'text') else 'Unknown error')
            print(f"Failed to create book: {error_msg}")
            return {"success": False, "message": error_msg}

    def update(self, book_id: int, updated_data: dict):
        """
        Update an existing book entry with new data.

        This method allows partial or complete updates to existing book records.
        Only the fields provided in updated_data will be modified.

        Args:
            book_id (int): The ID of the book to update
            updated_data (dict): Dictionary containing the fields to update

        Returns:
            dict: A dictionary indicating success or failure:
                - On success: {"success": True, "message": "Book updated"}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._patch(f"books/{book_id}/", updated_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to update book {book_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Book {book_id} updated successfully.")
        return {"success": True, "message": f"Book {book_id} updated."}

    def delete(self, book_id):
        """
        Delete a book entry by its ID.

        This method permanently removes a book record from the system.
        Use with caution as this action cannot be undone.

        Args:
            book_id (int): The ID of the book to delete

        Returns:
            dict: A dictionary indicating success or failure:
                - On success: {"success": True, "message": "Book deleted"}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._delete(f"books/{book_id}/")
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to delete book {book_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Book {book_id} deleted successfully.")
        return {"success": True, "message": f"Book {book_id} deleted."}

    def get(self, book_id=None):
        """
        Retrieve book data from the API.

        This method can fetch either a specific book by ID or all books
        depending on whether book_id is provided.

        Args:
            book_id (int, optional): The ID of a specific book to retrieve.
                                    If None, returns all books.

        Returns:
            dict or list: Book data for a specific book, or list of all books.
                         Content is automatically removed for performance.

        Note:
            For performance reasons, the 'content' field is automatically
            removed from book records when retrieving multiple books.
        """
        if book_id:
            data = self._get(f"books/{book_id}/").json()
            if isinstance(data, dict) and "content" in data:
                data.pop("content")
            return data
        data = self._get("books/").json()
        if isinstance(data, list):
            for book in data:
                if "content" in book:
                    book.pop("content")
        return data

    def get_all_books(self, is_posted=False):
        """
        Retrieve all books with optional filtering by posting status.

        This method fetches all books and optionally filters them based on
        whether they have been posted to external platforms.

        Args:
            is_posted (bool): If True, returns only books that have been posted.
                             If False, returns only books that have not been posted.
                             Defaults to False.

        Returns:
            list: A list of book dictionaries matching the posting criteria.
                 Returns empty list if no books match or if an error occurs.

        Note:
            The method includes comprehensive error handling and user feedback.
            If no books match the criteria, it prints an informative message.
        """
        response = self._get("books/")
        if response.status_code == 200:
            books = [book for book in response.json(
            ) if book.get('is_posted') == is_posted]
            if len(books) == 0:
                print('All books are up to date')
                return []
            print("📚 All Books:")
            for book in books:
                print(
                    f"ID: {book.get('book_id')}, Title: {book.get('title')}, Author: {book.get('author')}")
        else:
            print(f"❌ Failed to retrieve books: {response.status_code}")
            print("Response:", response.text)
            return []
        return books


class AuthorAPI(BaseAPI):
    """
    A client for managing author data through the REST API.

    This class provides comprehensive methods for creating, reading, updating,
    and deleting author records. It handles author-related operations including
    scraping status management and data synchronization.

    Inherits from BaseAPI to use the common HTTP methods.
    """

    def create(self, author_data):
        """
        Create a new author entry in the API.

        This method takes author data and creates a new author record in the system.
        It handles the response and provides user feedback on success or failure.

        Args:
            author_data (dict): Dictionary containing author details with keys:
                - 'name' or 'author': Author name
                - Additional fields as required by the API

        Returns:
            dict: A dictionary containing success status and author information:
                - On success: {"success": True, "message": "Author created", "id": author_id}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes comprehensive error handling and user feedback.
        """
        
        author = {
            "author_id": author_data['id'],
            "author_name": author_data['full_name'],
            "author_link": author_data['author_link']
        }
        response = self._post("authors/", author)
        if isinstance(response, dict) and response.get("status") == "error":
            print(f"Failed to create author: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        obj_id = None
        try:
            obj_id = response.json().get("id", "")
        except Exception:
            pass
        print(
            f"Author created successfully. Name: {author.get('author_name')}")
        return {"success": True, "message": f"Author '{author.get('author_name')}' created.", "id": obj_id}

    def update(self, author_id, updated_data):
        """
        Update an existing author entry with new data.

        This method allows partial or complete updates to existing author records.
        Only the fields provided in updated_data will be modified.

        Args:
            author_id (int): The ID of the author to update
            updated_data (dict): Dictionary containing the fields to update

        Returns:
            dict: A dictionary indicating success or failure:
                - On success: {"success": True, "message": "Author updated"}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._patch(f"authors/{author_id}/", updated_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to update author {author_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Author {author_id} updated successfully.")
        return {"success": True, "message": f"Author {author_id} updated."}

    def delete(self, author_id):
        """
        Delete an author entry by its ID.

        This method permanently removes an author record from the system.
        Use with caution as this action cannot be undone.

        Args:
            author_id (int): The ID of the author to delete

        Returns:
            dict: A dictionary indicating success or failure:
                - On success: {"success": True, "message": "Author deleted"}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._delete(f"authors/{author_id}/")
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to delete author {author_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Author {author_id} deleted successfully.")
        return {"success": True, "message": f"Author {author_id} deleted."}

    def get(self, author_id=None):
        """
        Retrieve author data from the API.

        This method can fetch either a specific author by ID or all authors
        depending on whether author_id is provided.

        Args:
            author_id (int, optional): The ID of a specific author to retrieve.
                                      If None, returns all authors.

        Returns:
            dict or list: Author data for a specific author, or list of all authors.
        """
        if author_id:
            return self._get(f"authors/{author_id}/").json()
        return self._get("authors/").json()

    def get_all_authors(self):
        """
        Retrieve all authors from the API.

        This method fetches all author records and provides user feedback
        on the number of authors found.

        Returns:
            list: A list of all author dictionaries.
                 Returns empty list if an error occurs.

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._get("authors/")
        if response.status_code == 200:
            authors = response.json()
            print(f"Authors found: {len(authors)}")
            return authors
        else:
            print(f"❌ Failed to retrieve authors: {response.status_code}")
            print("Response:", response.text)
            return []

    def get_unscraped_authors(self):
        """
        Retrieve all authors that have not been scraped yet.

        This method fetches all author records and filters them to return
        only those that have not been marked as scraped. This is useful
        for identifying authors whose books still need to be processed.

        Returns:
            list: A list of unscraped author dictionaries.
                 Returns empty list if no unscraped authors found or if an error occurs.

        Note:
            The method includes error handling and user feedback through logging.
            It looks for authors where 'is_scraped' equals "no".
        """
        response = self._get("authors/")
        if response.status_code == 200:
            authors = response.json()
            unscraped = [a for a in authors if a.get('is_scraped') == "no"]
            print(f"Unscraped authors found: {len(unscraped)}")
            return unscraped
        else:
            print(f"❌ Failed to retrieve authors: {response.status_code}")
            print("Response:", response.text)
            return []


class TokenAPI(BaseAPI):
    """
    A client for managing user tokens through the REST API.

    This class provides comprehensive methods for creating, reading, updating,
    and deleting user token records. It handles authentication token management
    for external API integrations.

    Inherits from BaseAPI to use the common HTTP methods.
    """

    def create(self, token_data):
        """
        Create a new user token entry in the API.

        This method takes token data and creates a new user token record in the system.
        It handles the response and provides user feedback on success or failure.

        Args:
            token_data (dict): Dictionary containing token details with keys:
                - 'username' or 'user_id': User identifier
                - Additional fields as required by the API

        Returns:
            dict: A dictionary containing success status and token information:
                - On success: {"success": True, "message": "Token created", "id": token_id}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes comprehensive error handling and user feedback.
        """
        response = self._post("users/", token_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(f"Failed to create token: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        obj_id = None
        try:
            obj_id = response.json().get("id", "")
        except Exception:
            pass
        print(
            f"Token created successfully for user: {token_data.get('username', token_data.get('user_id'))}")
        return {"success": True, "message": f"Token for user '{token_data.get('username', token_data.get('user_id'))}' created.", "id": obj_id}

    def update(self, user_id, updated_data):
        """
        Update an existing user token entry with new data.

        This method allows partial or complete updates to existing user token records.
        Only the fields provided in updated_data will be modified.

        Args:
            user_id (int): The ID of the user whose token to update
            updated_data (dict): Dictionary containing the fields to update

        Returns:
            dict: A dictionary indicating success or failure:
                - On success: {"success": True, "message": "Token updated"}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._patch(f"users/{user_id}/", updated_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to update token for user {user_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Token for user {user_id} updated successfully.")
        return {"success": True, "message": f"Token for user {user_id} updated."}

    def get_all_tokens(self):
        """
        Retrieve all user tokens from the API.

        This method fetches all user token records and randomly shuffles them
        for load balancing purposes when using tokens for external API calls.

        Returns:
            list: A randomly shuffled list of all user token dictionaries.
                 Returns empty list if an error occurs.

        Note:
            The method includes error handling and shuffles the results for
            better distribution when using tokens for external API calls.
        """
        import random
        response = self._get("users/")
        if response.status_code == 200:
            tokens = response.json()
            if isinstance(tokens, list):
                random.shuffle(tokens)
            tokens = [token['token'] for token in tokens if token.get('is_verified') == True]
            return tokens
        else:
            print(f"❌ Failed to retrieve tokens: {response.status_code}")
            print("Response:", response.text)
            return []

    def delete(self, user_id):
        """
        Delete a user token entry by its ID.

        This method permanently removes a user token record from the system.
        Use with caution as this action cannot be undone.

        Args:
            user_id (int): The ID of the user whose token to delete

        Returns:
            dict: A dictionary indicating success or failure:
                - On success: {"success": True, "message": "Token deleted"}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._delete(f"users/{user_id}/")
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to delete token for user {user_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Token for user {user_id} deleted successfully.")
        return {"success": True, "message": f"Token for user {user_id} deleted."}

    def get(self, user_id=None):
        """
        Retrieve user token data from the API.

        This method can fetch either a specific user token by ID or all user tokens
        depending on whether user_id is provided.

        Args:
            user_id (int, optional): The ID of a specific user to retrieve.
                                     If None, returns all users.

        Returns:
            dict or list: User token data for a specific user, or list of all users.
        """
        if user_id:
            return self._get(f"users/{user_id}/").json()
        data = self._get("users/").json()
        if isinstance(data, list):
            import random
            random.shuffle(data)
        return data


class CategoryAPI(BaseAPI):
    """
    A client for managing category data through the REST API.

    This class provides comprehensive methods for creating, reading, updating,
    and deleting category records. It handles category-related operations for
    book classification and organization.

    Inherits from BaseAPI to use the common HTTP methods.
    """

    def create(self, category_data):
        """
        Create a new category entry in the API.

        This method takes category data and creates a new category record in the system.
        It handles the response and provides user feedback on success or failure.

        Args:
            category_data (dict): Dictionary containing category details with keys:
                - 'name' or 'category': Category name
                - Additional fields as required by the API

        Returns:
            dict: A dictionary containing success status and category information:
                - On success: {"success": True, "message": "Category created", "id": category_id}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes comprehensive error handling and user feedback.
        """
        response = self._post("categories/", category_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(f"Failed to create category: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        obj_id = None
        try:
            obj_id = response.json().get("id", "")
        except Exception:
            pass
        print(
            f"Category created successfully. Name: {category_data.get('name', category_data.get('category'))}")
        return {"success": True, "message": f"Category '{category_data.get('name', category_data.get('category'))}' created.", "id": obj_id}

    def update(self, category_id, updated_data):
        """
        Update an existing category entry with new data.

        This method allows partial or complete updates to existing category records.
        Only the fields provided in updated_data will be modified.

        Args:
            category_id (int): The ID of the category to update
            updated_data (dict): Dictionary containing the fields to update

        Returns:
            dict: A dictionary indicating success or failure:
                - On success: {"success": True, "message": "Category updated"}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._patch(f"categories/{category_id}/", updated_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to update category {category_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Category {category_id} updated successfully.")
        return {"success": True, "message": f"Category {category_id} updated."}

    def delete(self, category_id):
        """
        Delete a category entry by its ID.

        This method permanently removes a category record from the system.
        Use with caution as this action cannot be undone.

        Args:
            category_id (int): The ID of the category to delete

        Returns:
            dict: A dictionary indicating success or failure:
                - On success: {"success": True, "message": "Category deleted"}
                - On failure: {"success": False, "message": error_description}

        Note:
            The method includes error handling and user feedback through logging.
        """
        response = self._delete(f"categories/{category_id}/")
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to delete category {category_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Category {category_id} deleted successfully.")
        return {"success": True, "message": f"Category {category_id} deleted."}

    def get(self, category_id=None):
        """
        Retrieve category data from the API.

        This method can fetch either a specific category by ID or all categories
        depending on whether category_id is provided.

        Args:
            category_id (int, optional): The ID of a specific category to retrieve.
                                        If None, returns all categories.

        Returns:
            dict or list: Category data for a specific category, or list of all categories.
        """
        if category_id:
            return self._get(f"categories/{category_id}/").json()
        return self._get("categories/").json()
