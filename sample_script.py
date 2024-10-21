import requests
import json
import datetime
import random
import logging
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# URL of the login page and API endpoint
LOGIN_URL = 'http://localhost:8000/accounts/login/'
TICKETS_API_URL = 'http://localhost:8000/tickets/api/v1/list/?api_key=123456'

TICKET_EDIT_URL = 'http://localhost:8000/tickets/api/v1/edit/{ticket_id}/?api_key=123456'




from dateutil import parser
import datetime

def is_due_date_in_past(due_date_str):
    """
    Check if the due date is in the past.
    Supports ISO 8601 date strings with time component.
    """
    if due_date_str:
        try:
            due_date = parser.isoparse(due_date_str)  # Parse ISO format date
            today = datetime.datetime.now(due_date.tzinfo)  # Use the same timezone if available
            return due_date < today
        except ValueError as e:
            logger.error(f"Error parsing due date: {e}")
            return False
    return True  # If no due date, assume it's past due

class TicketClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf_token = None
        
    def login(self):
        # Get the CSRF token from the login page (if needed)
        login_page = self.session.get(LOGIN_URL)
        self.csrf_token = self.session.cookies.get('csrftoken', None)  # Get the csrf token safely

        # Your login credentials
        payload = {
            'username': self.username,
            'password': self.password,
            'csrfmiddlewaretoken': self.csrf_token  # Add CSRF token to the payload
        }

        # Send a POST request to login
        response = self.session.post(LOGIN_URL, data=payload, headers={'Referer': LOGIN_URL, "Accept": "application/json"})

        if response.status_code == 200:
            logger.info("Login successful!")
            return True
        else:
            logger.error(f"Login failed, status code: {response.status_code}")
            return False
        
    def get_tickets(self):
        # Get the CSRF token from the login page (if needed)
        # Now, access the protected API
        tickets_response = self.session.get(TICKETS_API_URL, headers={'Accept': 'application/json'})
        tickets = None
        if tickets_response.status_code == 200:
            # Print the JSON response with the tickets
            try:
                tickets = tickets_response.json()
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return None
        else:
            logger.error(f"Failed to retrieve tickets, status code: {tickets_response.status_code}")
            return None
        return tickets["tickets"]



    def set_random_future_due_date(self, ticket_id):
        """
        Set a random future due date for the given ticket.
        """
        # Generate a random future due date within the next 1 to 30 days
        random_days = random.randint(1, 30)
        future_due_date = (datetime.datetime.now() + datetime.timedelta(days=random_days)).strftime('%Y-%m-%d')
        # Prepare the data to update the ticket
        edit_url = TICKET_EDIT_URL.format(ticket_id=ticket_id)
        update_payload = {
            'due_date': future_due_date,
            'csrfmiddlewaretoken': self.csrf_token
        }

        # Send the POST request to update the ticket
        response = self.session.post(edit_url, data=update_payload, headers={'Referer': edit_url})

        if response.status_code == 200:
            logger.info(f"Ticket {ticket_id} updated with due date: {future_due_date}")
        else:
            logger.error(f"Failed to update ticket {ticket_id}, status code: {response.status_code}")
        
if __name__ == '__main__':
    clerk = TicketClient(os.getenv('USERNAME'), os.getenv('PASSWORD'))
    if 1 == 0:
        if clerk.login():
            tickets = clerk.get_tickets()
            if tickets:
                for ticket in tickets:
                    print(ticket)
                    # ticket = json.loads(ticket)
                    # if is_due_date_in_past(ticket.get('due_date')):
                    #     clerk.set_random_future_due_date(ticket.get('id'))
            else:
                logger.error("No tickets found.")
        
        else:
            logger.error("Login failed.")
    else:
        tickets = clerk.get_tickets()
        if tickets:
            for ticket in tickets:
                if is_due_date_in_past(ticket.get('due_date')):
                    print(f"Ticket {ticket.get('id')} is past due.")
                    clerk.set_random_future_due_date(ticket.get('id'))
        else:
            logger.error("No tickets found.")