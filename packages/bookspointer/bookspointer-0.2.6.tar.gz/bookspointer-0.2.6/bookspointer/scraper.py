# External imports
from selectolax.parser import HTMLParser
import importlib.resources
from rich import print
import requests

# Standard imports
import json
import re


class BookScraper:
    """
    A comprehensive web scraper for extracting book data from ebanglalibrary.com.

    This class provides methods to scrape book information including titles, authors,
    categories, content, and metadata. It handles both single-page and multi-page books,
    with support for different category types and content extraction.

    The scraper is designed to work with the ebanglalibrary.com website structure and
    includes authentication handling, pagination support, and content aggregation
    capabilities for multi-page books.

    Attributes:
        headers (dict): HTTP headers for making requests to the website, configured
                       to mimic a real browser session
        cookies (dict): Session cookies for maintaining authentication and bypassing
                       certain access restrictions
        multi_page_links (list): List of book URLs that are known to have multiple
                                content pages that should be processed separately
    """

    def __init__(self, multi_page_links: list):
        """
        Initialize the BookScraper with default headers and cookies.

        Sets up the necessary HTTP headers and cookies to mimic a real browser
        session for web scraping. This includes user agent, accept headers, and
        session cookies for authentication.

        Args:
            multi_page_links (list): A list of book URLs that should be processed
                                   as multi-page books, where each page becomes
                                   a separate book entry
        """
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-BD,en-US;q=0.9,en;q=0.8",
            "priority": "u=1, i",
            "referer": "https://www.ebanglalibrary.com/",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        self.cookies = {
            "__gsas": "ID=eeb6a89775d353fc:T=1749577672:RT=1749577672:S=ALNI_MaIBex_3dHulhrGnFupNiyLCvPZsA",
            "cf_clearance": "UDM6zG5aQdnupSDm_pIrI0ahH3Qhf0C4OlzwVW3v9lc-1749711078-1.2.1.1-d6Cn4han6cxVdvXh8d2rCs94t44Ld6FDxpbHkRtKHfqp7kvMLSiNwJkjP_Y__l3tMmK4DA04X6WQG8hAav42mW6h3knRv6Tn_2XUgVAGngGmpizLslySbsm0riaopY33XFSRQ8nafhbavhdijYjzSI3JIbbsj1yywKSkFfloHhS0gPloasy7HFH8CNOlxF.lH7O7AsRJ7X5UMqJrmtk4LrAK4jskS5pp9vcOOIuo.hRqQ5NhlzFZklFpti22RVcmn1t463Z6DM8sAQbrlPObjp9qJYlaZo22uSHjLECc9uXeMy4cf_Xj8qjxPUTbOqpXmDM3qLHnC0563ZpCQHxLZBl2stE1Dr.gOaouTSAC_sw",
            "advanced_ads_visitor": '{"browser_width":1905}'
        }
        self.multi_page_links = multi_page_links
    
    def remove_bangla_number_prefix(self, title):
        # Remove Bangla number + optional dot + optional whitespace from start
        return re.sub(r"^[\u09E6-\u09EF]+[\.\-\s]*", "", title)

    def get_pages(self, book_id: int) -> list:
        """
        Retrieve all page URLs for a given book by its ID using AJAX pagination.

        This method makes an AJAX request to fetch paginated content for a book.
        It's used for books that have multiple pages of content that are loaded
        dynamically through JavaScript.

        Args:
            book_id (int): The unique identifier of the book on the website.

        Returns:
            list: A list of page URLs for the book's content pages.

        Raises:
            requests.RequestException: If the HTTP request fails.
            KeyError: If the response JSON doesn't contain expected data structure.
        """
        url = "https://www.ebanglalibrary.com/wp-admin/admin-ajax.php"

        page_number = 1
        querystring = {"action": ["ld30_ajax_pager", "ld30_ajax_pager"], "pager_nonce": "26c3c2da05", "context": "course_content_shortcode",
                       "course_id": book_id, "shortcode_instance[course_id]": book_id, "shortcode_instance[num]": "100"}

        response = requests.get(url, headers=self.headers,
                                cookies=self.cookies, params=querystring)

        data = response.json()['data']['markup']
        html = HTMLParser(data)
        book_urls = [a.attributes.get('href', '')
                     for a in html.css('a.ld-item-name')]
        return book_urls

    def get_html_pages(self, book_url: str) -> list:
        """
        Retrieve all HTML page URLs for a given book URL by parsing the main book page.

        This method extracts all content page links from a book's main page.
        It parses the HTML to find all chapter or section links within the book.
        It also checks for login requirements and logs URLs that require authentication.

        Args:
            book_url (str): The main URL of the book's landing page.

        Returns:
            list: A list of URLs for all content pages within the book.
                 Returns empty list if login is required or if an error occurs.

        Raises:
            requests.RequestException: If the HTTP request fails or returns an error status.

        Note:
            The method checks for login requirements by looking for specific HTML elements.
            If login is required, the URL is logged to 'login_required.txt' and an empty
            list is returned to prevent further processing of protected content.
        """
        response = requests.get(book_url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad responses
        html = HTMLParser(response.text)

        login_required = html.css_first('div.ld-course-status-action a')
        if login_required:
            with open('login_required.txt', 'a') as f:
                f.write(f"{book_url}\n")
            return []

        book_urls = [a.attributes.get('href', '')
                     for a in html.css('a.ld-item-name')]
        print(len(book_urls), "page urls found")
        return book_urls

    def get_cate_id(self, category_name: list) -> int:
        """
        Get the category ID for a given category name by matching against predefined categories.

        This method loads the categories.json file from the package and matches
        the provided category name against the predefined list. It includes fallback
        logic for various category name variations and partial matches.

        Args:
            category_name (list): A list of category name strings to match.

        Returns:
            int: The category ID that matches the provided category name(s).
                 Returns 20 as default if no match is found.

        Note:
            The method includes hardcoded fallbacks for common category variations
            and partial matches to handle cases where exact matches aren't found.
        """
        with importlib.resources.files('bookspointer').joinpath('categories.json').open('r', encoding='utf-8') as file:
            categories = json.load(file)
            category_name = ' '.join(category_name)
        for category in categories:
            if category['label'] == category_name:
                return category['id']
            elif 'ইতিহাস' in category_name:
                return 1
            elif 'কৌতুক' in category_name:
                return 2
            elif 'উপন্যাস' in category_name:
                return 3
            elif "থ্রিলার রহস্য রোমাঞ্চ অ্যাডভেঞ্চার" in category_name:
                return 4
            elif 'গল্পগ্রন্থ' in category_name:
                return 5
            elif 'গল্পের বই' in category_name:
                return 5
            elif "ভ্রমণ কাহিনী" in category_name:
                return 6
            elif "বৈজ্ঞানিক কল্পকাহিনী" in category_name:
                return 9
            elif "ধর্ম ও দর্শন" in category_name:
                return 10
            elif "ইসলামিক বই" in category_name:
                return 10
            elif "ধর্মীয় বই" in category_name:
                return 10
            elif "সংস্কৃত" in category_name:
                return 10
            elif "কাব্যগ্রন্থ / কবিতা" in category_name:
                return 12
            elif "প্রবন্ধ ও গবেষণা" in category_name:
                return 13
            elif "রচনা" in category_name:
                return 13
            elif "কিশোর সাহিত্য" in category_name:
                return 14
            elif "আত্মজীবনী ও স্মৃতিকথা" in category_name:
                return 15
            elif "আত্মউন্নয়নমূলক বই" in category_name:
                return 15
            elif "নাটক" in category_name:
                return 16
            elif "গোয়েন্দা" in category_name:
                return 18
            elif "ভৌতিক" in category_name:
                return 19
            elif "হরর" in category_name:
                return 19
            elif "ভূতের বই" in category_name:
                return 19
            elif "Editor's Choice" in category_name:
                return 5
            else:
                return 20
        return 20

    def get_book_list(self, author_url: str) -> list:
        """
        Scrape the list of books for a given author URL.

        This method extracts all books written by a specific author from their
        author page. It parses the HTML to find book titles, authors, and links.

        Args:
            author_url (str): The URL of the author's page containing their books.

        Returns:
            list: A list of dictionaries, each containing:
                - 'title': The book title
                - 'author': The author name
                - 'link': The URL to the book's page

        Note:
            If the title contains a dash (–), it splits the title and author.
            If no author is found in the title, it defaults to 'Unknown Author'.
        """
        books = []
        try:
            response = requests.get(author_url, headers=self.headers)
            html = HTMLParser(response.text)
            book_elements = html.css('article.entry-archive')
            print(f'{len(book_elements)} books found for the author.')
            for book in book_elements:
                title_ele = book.css_first(
                    'a.entry-title-link').text(strip=True)
                title = title_ele.split('–')[0].strip(
                ) if '–' in title_ele else title_ele
                author = title_ele.split('–')[1].strip(
                ) if '–' in title_ele else 'Unknown Author'
                book_link = book.css_first(
                    'a.entry-title-link').attributes.get('href', '')
                books.append({
                    'title': title,
                    'author': author,
                    'link': book_link
                })
            return books
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return []

    def get_book_details(self, book_info: dict, author_id: int) -> list:
        """
        Scrape detailed information for a given book including content and metadata.

        This method extracts comprehensive book information including title, author,
        category, series, content, and other metadata. It handles both single-page
        and multi-page books, aggregating content from all pages.

        The method processes books differently based on whether they are in the
        multi_page_links list:
        - Multi-page books: Creates separate book entries for each content page
        - Single-page books: Aggregates all content into a single book entry

        Args:
            book_info (dict): Dictionary containing basic book info:
                - 'title': Book title
                - 'author': Author name  
                - 'link': Book URL
            author_id (int): The ID of the author for database association

        Returns:
            list: A list of dictionaries containing detailed book information:
                - 'book_id': Unique book identifier extracted from the page
                - 'title': Book title (may be updated for multi-page books)
                - 'author': Author name
                - 'author_id': Author ID for database association
                - 'category': List of category names
                - 'category_id': Numeric category ID for database storage
                - 'series': Series information or category as fallback
                - 'content': Book content (aggregated for single-page, individual for multi-page)
                - 'url': Book URL (original for single-page, page-specific for multi-page)

        Note:
            - For multi-page books: Creates separate entries for each content page
            - For single-page books: Aggregates all content with HTML line breaks as separators
            - Books with empty content are skipped to avoid creating empty entries
            - Login-required books are logged and skipped
            - Content is cleaned by removing interactive elements like buttons
        """
        books = []
        try:
            response = requests.get(book_info['link'], headers=self.headers)
            response.raise_for_status()  # Raise an error for bad responses
            html = HTMLParser(response.text)
            book_ele = html.css_first('h1.page-header-title').text(strip=True)
            title = book_ele.split('–')[0].strip(
            ) if '–' in book_ele else 'Unknown Title'
            if title == 'Unknown Title':
                title = html.css_first('h1.page-header-title').text(strip=True)
            category = [cat.text(strip=True) for cat in html.css(
                'span.entry-terms-ld_course_category a')]
            cate_id = self.get_cate_id(category_name=category)
            try:
                series = html.css_first(
                    'span.entry-terms-series a').text(strip=True)
            except:
                series = category
            paragraphs = html.css_first('div.ld-tabs-content div')
            button = paragraphs.css_first('button')
            if button:
                button.decompose()
            content_str = ''  # str(paragraphs.html) if paragraphs else ''
            contents = [content_str]
            book_id = html.css_first(
                'div.ld-tab-content').attributes.get('id').split('-')[-1]
            book = {
                'book_id': book_id,
                'title': self.remove_bangla_number_prefix(title),
                'author': book_info['author'],
                'author_id': author_id,
                'category': category,
                'category_id': cate_id,
                'series': series,
                'content': '',
                'url': book_info['link']
            }
            all_books_url = self.get_html_pages(book_info['link'])
            for idx, book_url in enumerate(all_books_url, start=1):
                new_content = self.get_book_content(book_url)
                if new_content:
                    if book_info['link'] in self.multi_page_links:
                        book_copy = book.copy()
                        book_copy['title'] = self.remove_bangla_number_prefix(new_content['title'])
                        book_copy['content'] = new_content['content']
                        book_copy['url'] = book_url
                        # print(book_copy)
                        books.append(book_copy)
                    else:
                        contents.append(new_content.get('content', ''))

                print(
                    f"Page Processed {idx}/{len(all_books_url)}: Author ID: {author_id}")

            book['content'] = '<br/>'.join(contents)

            if book['content'] == '':
                print('This book may have login required')
                return books

            books.append(book)

            return books
        except requests.RequestException as e:
            print(f"An error occurred while fetching book details: {e}")
            return []

    def get_book_content(self, url: str) -> dict:
        """
        Scrape the content and title from a specific book page URL.

        This method extracts the actual content and title from a book's content page.
        It removes any interactive elements (like buttons) and cleans up the HTML
        for better content extraction.

        Args:
            url (str): The URL of the specific book content page.

        Returns:
            dict: A dictionary containing:
                - 'content': The HTML content of the book page
                - 'title': The title of the content page
            None: If the request fails or content cannot be extracted.

        Note:
            The method replaces closing paragraph tags with line breaks for better
            formatting and removes any button elements from the content.
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            html = HTMLParser(response.text.replace('</p>', '</p><br/>'))
            content_div = html.css_first('div.ld-tabs-content > div')
            title = html.css_first('div.ld-focus-content h1').text(strip=True)
            for button in content_div.css('button'):
                button.decompose()
            
            for heading in content_div.css('div#ftwp-container'):
                heading.decompose()
            
            if content_div:
                content_str = str(content_div.html)
                return {'content': content_str, 'title': title}
        except requests.RequestException as e:
            print(f"An error occurred while fetching book content: {e}")
            return None
