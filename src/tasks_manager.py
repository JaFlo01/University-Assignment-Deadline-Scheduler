from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import datetime

SCOPES = ['https://www.googleapis.com/auth/tasks']

def authenticate_google_tasks():
    """Authenticate and create a Google Tasks service."""
    creds = None

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('tasks', 'v1', credentials=creds)
    return service

def add_task_to_google_tasks(service, task_list_id, title, due_date):
    """Add a task to Google Tasks."""
    task = {
        'title': title,
        'due': due_date
    }
    result = service.tasks().insert(tasklist=task_list_id, body=task).execute()
    print(f"Task created: {result.get('title')} (ID: {result.get('id')})")

def format_due_date_for_google_tasks(due_date):
    """Convert a due date string to RFC3339 format for Google Tasks."""
    try:
        # Check if the due date is in 'MMM DD' format
        due_date_object = None
        try:
            # Try parsing 'MMM DD' format first
            due_date_object = datetime.datetime.strptime(due_date, '%b %d')
        except ValueError:
            # Handle cases where 'Sept' might be spelled out in full
            if 'Sept' in due_date:
                due_date = due_date.replace('Sept', 'Sep')
                due_date_object = datetime.datetime.strptime(due_date, '%b %d')

        # Check if date is still not parsed
        if not due_date_object:
            try:
                # Attempt to parse 'MM/DD' format
                due_date_object = datetime.datetime.strptime(due_date, '%m/%d')
            except ValueError as e:
                raise ValueError(f"Unable to parse date '{due_date}': {e}")

    except ValueError as e:
        raise ValueError(f"Unable to parse date '{due_date}': {e}")

    current_year = datetime.datetime.now().year
    due_date_object = due_date_object.replace(year=current_year)
    
    return due_date_object.isoformat() + 'Z'