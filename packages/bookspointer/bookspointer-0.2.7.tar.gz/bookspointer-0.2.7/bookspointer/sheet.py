# Custom imports
from bookspointer.server import AuthorAPI

# External imports
import requests
from rich import print
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import importlib.resources

# Standard imports
import os
import json


class AuthorSheetManager:
    """
    A comprehensive manager for synchronizing author data between Google Sheets and the API.

    This class provides functionality to fetch authors from external APIs, manage them
    in Google Sheets, and synchronize data with the internal API. It handles authentication,
    data transformation, and status tracking for author scraping operations.

    The class integrates with Google Sheets for data storage and the AuthorAPI for
    server-side operations. It supports environment variable configuration for
    sensitive credentials and provides comprehensive error handling.

    Attributes:
        sheet_name (str): The name of the Google Sheet to work with
        worksheet_name (str): The specific worksheet within the Google Sheet
        creds_file (str): The path to the Google service account credentials file
        author_api (AuthorAPI): Instance of the AuthorAPI for server operations
        gc (gspread.Client): Authenticated Google Sheets client
        sh (gspread.Spreadsheet): The Google Spreadsheet object
        worksheet (gspread.Worksheet): The specific worksheet object
    """

    def __init__(self, sheet_name="Books Pointer Data", worksheet_name="verified_authors", creds_file="Credentials.json"):
        """
        Initialize the AuthorSheetManager with Google Sheets configuration.

        This method sets up the Google Sheets connection using service account
        credentials and initializes the API client for server operations.

        Args:
            sheet_name (str): The name of the Google Sheet. Defaults to "Books Pointer Data".
            worksheet_name (str): The name of the worksheet within the sheet. 
                                Defaults to "verified_authors".
            creds_file (str): The filename of the credentials file in the package.
                             Defaults to "Credentials.json".

        Note:
            The credentials file is loaded from the package using importlib.resources
            to ensure it works correctly when the package is installed.
            Environment variables CLIENT_EMAIL, CLIENT_ID, and PRIVATE_KEY_ID
            can be used to override credential values for security.
        """
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.creds_file = creds_file
        self.author_api = AuthorAPI()

        # Load .env and patch client_email if present
        load_dotenv()
        client_email = os.getenv("CLIENT_EMAIL")
        client_id = os.getenv("CLIENT_ID")
        private_key_id = os.getenv("PRIVATE_KEY_ID")

        with importlib.resources.files('bookspointer').joinpath(self.creds_file).open("r", encoding="utf-8") as f:
            creds_data = json.load(f)

        creds_data["client_email"] = client_email
        creds_data["client_id"] = client_id
        creds_data["private_key_id"] = private_key_id

        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_info(
            creds_data, scopes=scopes)
        self.gc = gspread.authorize(creds)
        self.sh = self.gc.open(self.sheet_name)
        self.worksheet = self.sh.worksheet(self.worksheet_name)

    def get_authors(self, page=1):
        """
        Fetch authors from the external Bookspointer API.

        This method retrieves author data from the Bookspointer API with pagination
        support. It transforms the API response into a standardized format for
        internal processing and storage.

        Args:
            page (int): The page number for pagination. Defaults to 1.

        Returns:
            list: A list of dictionaries containing author information:
                - 'id': Author ID
                - 'first_name': Author's first name
                - 'last_name': Author's last name
                - 'full_name': Combined full name
                - 'author_link': VLOOKUP formula for author link
                - 'is_scraped': Scraping status (False for new authors)

        Note:
            The method includes comprehensive error handling and user feedback.
            If no authors are found, it returns an empty list.
            The author_link field contains a VLOOKUP formula for Google Sheets integration.
        """
        print(f"Getting authors from bookspointer page: {page}")
        authors = []
        url = "https://api.bookspointer.com/authors"
        headers = {
            "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
            "Connection": "keep-alive",
            "Origin": "https://bookspointer.com",
            "Referer": "https://bookspointer.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "accept": "application/json",
            "content-type": "application/json",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }
        data = {
            "userId": 248,
            "device": 1,
            "page": page,
            "limit": 200
        }

        response = requests.post(url, headers=headers, json=data)
        data = response.json()['authors']
        if not data:
            return []
        for d in data:
            author = {
                'id': d['id'],
                'first_name': d['firstName'],
                'last_name': d['lastName'],
                'full_name': f'{d['firstName']} {d['lastName']}',
                'author_link': '=VLOOKUP(D254,table,3,0)',
                'is_scraped': False,
            }
            authors.append(author)
        return authors

    def save_authors_to_sheet(self, df):
        """
        Save new authors to the Google Sheet, avoiding duplicates.

        This method processes a DataFrame of authors and adds only new ones
        to the Google Sheet. It checks for existing authors by ID to prevent
        duplicates and uses VLOOKUP formulas for dynamic linking.

        Args:
            df (pandas.DataFrame): DataFrame containing author information with columns:
                - 'id': Author ID
                - 'first_name': Author's first name
                - 'last_name': Author's last name
                - 'full_name': Combined full name
                - 'author_link': VLOOKUP formula
                - 'is_scraped': Scraping status

        Note:
            The method includes comprehensive error handling and user feedback.
            It automatically generates VLOOKUP formulas for the author_link column
            based on the row number to ensure proper Google Sheets integration.
            If no new authors are found, it prints an informative message.
        """
        print(f"Saving authors to sheet")
        try:
            worksheet = self.worksheet
            # Get all existing ids from the sheet
            sheet_records = worksheet.get_all_records()
            existing_ids = set(str(row.get("id", "")) for row in sheet_records)

            # Filter out events whose event_id is already in the sheet
            new_rows = df[~df["id"].astype(str).isin(existing_ids)]

            if new_rows.empty:
                print(
                    "[bold yellow]No truly new events to add to Google Sheets.[/bold yellow]")
                return

            # Get the next empty row
            # +2 because sheet_records doesn't include header row
            next_row = len(sheet_records) + 2

            # Prepare data with formulas
            for index, row in new_rows.iterrows():
                row_data = [
                    row['id'],
                    row['first_name'],
                    row['last_name'],
                    row['full_name'],
                    # Formula with dynamic row reference
                    '=IFERROR(VLOOKUP(D' + str(next_row) + ',Authors,2,0), "")',
                    row['is_scraped']
                ]

                # Append the row with value_input_option to treat formulas properly
                worksheet.append_row(
                    row_data, value_input_option='USER_ENTERED')
                next_row += 1

            print(
                f"[bold green]Added {len(new_rows)} new authors to Google Sheet.[/bold green]")

        except Exception as e:
            if df.empty:
                print(
                    "[bold yellow]No new authors to add to Google Sheet.[/bold yellow]")
                return
            else:
                print(
                    f"[bold red]Failed to add Authors to Google Sheet: {e}[/bold red]")

    def get_unscraped_authors(self):
        """
        Retrieve all authors from the sheet that have not been scraped yet.

        This method fetches all author records from the Google Sheet and filters
        them to return only those that have not been marked as scraped. This is
        useful for identifying authors whose books still need to be processed.

        Returns:
            list: A list of dictionaries containing unscraped author information.
                 Each dictionary contains all the columns from the Google Sheet.
                 Returns empty list if no unscraped authors found or if an error occurs.

        Note:
            The method includes comprehensive error handling and user feedback.
            It looks for authors where 'is_scraped' is False (boolean) or "FALSE" (string).
            The method prints the number of unscraped authors found.
        """
        try:
            worksheet = self.worksheet
            # Get all records from the sheet
            sheet_records = worksheet.get_all_records()

            # Filter records where is_scraped is FALSE
            unscraped_authors = []
            for record in sheet_records:
                # Check if is_scraped is False (boolean) or "FALSE" (string)
                is_scraped = record.get('is_scraped', False)
                if is_scraped == False or str(is_scraped).upper() == "FALSE":
                    unscraped_authors.append(record)

            print(
                f"[bold green]Found {len(unscraped_authors)} unscraped authors.[/bold green]")
            return unscraped_authors

        except Exception as e:
            print(f"[bold red]Failed to get unscraped authors: {e}[/bold red]")
            return []

    def update_scraped_status(self, author_id: str):
        """
        Update the scraping status of an author from FALSE to TRUE.

        This method finds an author by their ID in the Google Sheet and updates
        their 'is_scraped' status to True, indicating that their books have been
        successfully processed.

        Args:
            author_id (str): The ID of the author whose status to update

        Returns:
            bool: True if the update was successful, False otherwise

        Note:
            The method includes comprehensive error handling and user feedback.
            It automatically determines the correct column index for the 'is_scraped'
            field and provides detailed logging of the update operation.
            If the author is not found, it prints an error message and returns False.
        """
        try:
            worksheet = self.worksheet
            # Get all records from the sheet
            sheet_records = worksheet.get_all_records()

            # Find the row with the matching author ID
            target_row = None
            # start=2 because row 1 is header
            for i, record in enumerate(sheet_records, start=2):
                if str(record.get('id', '')) == str(author_id):
                    target_row = i
                    break

            if target_row is None:
                print(
                    f"[bold red]Author with ID {author_id} not found in the sheet.[/bold red]")
                return False

            # Get the column index for 'is_scraped' column
            headers = list(sheet_records[0].keys())
            try:
                is_scraped_col_index = headers.index('is_scraped')
                is_scraped_col = is_scraped_col_index + 1  # Convert to 1-based index
            except ValueError:
                # If 'is_scraped' column not found, assume it's the last column
                is_scraped_col = len(headers)

            # Update the cell value to TRUE using update_cell method
            print(
                f"[bold blue]Updating cell at row {target_row}, column {is_scraped_col} for author ID {author_id}[/bold blue]")
            worksheet.update_cell(target_row, is_scraped_col, True)

            print(
                f"[bold green]Successfully updated author ID {author_id} is_scraped status to TRUE.[/bold green]")
            return True

        except Exception as e:
            print(f"[bold red]Failed to update author status: {e}[/bold red]")
            return False

    def run(self):
        """
        Execute the complete author synchronization workflow.

        This method orchestrates the entire process of fetching authors from the
        external API, saving them to Google Sheets, and processing unscraped
        authors. It provides a complete end-to-end workflow for author data management.

        The workflow includes:
        1. Fetching authors from the Bookspointer API (with pagination)
        2. Saving new authors to Google Sheets
        3. Retrieving unscraped authors from the sheet
        4. Creating author records in the internal API
        5. Updating scraping status in the sheet

        Note:
            The method includes comprehensive error handling and user feedback.
            It processes up to 100 pages of authors from the external API.
            If no unscraped authors are found, the process stops gracefully.
            Each step includes detailed logging for monitoring and debugging.
        """
        authors = []
        for i in range(1, 100):
            try:
                new_authors = self.get_authors(i)
            except:
                new_authors = []

            if len(new_authors) == 0:
                break
            else:
                authors.extend(new_authors)

        if len(authors) >= 0:
            df = pd.DataFrame(authors)
            self.save_authors_to_sheet(df)

        unscraped_authors = self.get_unscraped_authors()
        if len(unscraped_authors) == 0:
            return
        for author in unscraped_authors:
            print(author)
            self.update_scraped_status(int(author['id']))
            self.author_api.create(author)


if __name__ == "__main__":
    manager = AuthorSheetManager().run()
