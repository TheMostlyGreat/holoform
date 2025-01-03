# main.py
import logging
from config.settings import DEFAULT_USER_ID
from services.arcade_services import auth_user, fetch_emails, get_labels, create_label
from processors.message_processor import process_messages, create_message_objects
from entities.labels import HoloformLabel, GmailSystemLabel
from arcade_google.tools.utils import DateRange

# Initialize logger for the current module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

# Create a formatter with the desired log message format
formatter = logging.Formatter(
    '\n%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
)

# Create a stream handler to output logs to the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)  # Assign the formatter to the handler

# Add the configured handler to the logger
logger.addHandler(stream_handler)

def main():
    logger.info("Starting Gmail processing script...")

    # Authorize user and get Gmail token
    token = auth_user(user_id=DEFAULT_USER_ID)
    logger.debug("User authorized successfully.")

        # Check and create necessary labels
    check_and_create_labels(user_id=DEFAULT_USER_ID)
    
    date_range = DateRange.LAST_7_DAYS.value
    date_range = ""
    label = GmailSystemLabel.INBOX.value

    # Fetch recent Gmail messages
    gmail_messages = fetch_emails(user_id=DEFAULT_USER_ID, date_range=date_range, label=label, max_results=100)
    
    # Create Message objects
    messages = create_message_objects(gmail_messages=gmail_messages, user_id=DEFAULT_USER_ID)
    
    # Process Messages
    processed_messages = process_messages(messages=messages)
    
   # Further actions (e.g., storing to DB) can be added here

def check_and_create_labels(user_id: str) -> None:
    """
    Ensures that the 'Holoform' parent label and its child labels exist in the user's Gmail account.
    If any labels are missing, they are created.

    Args:
        user_id: The ID of the user whose labels are to be checked/created.
    """
    # Define parent and child labels
    parent_label = HoloformLabel.HOLOFORM.value
    child_labels = [label.value for label in HoloformLabel if label.value != HoloformLabel.HOLOFORM.value]

    # Retrieve existing labels
    existing_labels = get_labels(user_id=user_id)
    
    # Debug: Print existing_labels to understand their structure
    logger.debug(f"Existing labels: {existing_labels}")

    existing_label_names = [label['name'] for label in existing_labels]

    # Check and create parent label if it doesn't exist
    if parent_label not in existing_label_names:
        logger.info(f"Parent label '{parent_label}' not found. Creating it.")
        create_label(label_name=parent_label, user_id=user_id)
    else:
        logger.debug(f"Parent label '{parent_label}' already exists.")

    # Check and create each child label if it doesn't exist
    for label in child_labels:
        full_label_name = HoloformLabel.get_full_label(label)
        if full_label_name not in existing_label_names:
            logger.info(f"Child label '{full_label_name}' not found. Creating it.")
            create_label(label_name=full_label_name, user_id=user_id)
        else:
            logger.debug(f"Child label '{full_label_name}' already exists.")

if __name__ == "__main__":
    main()