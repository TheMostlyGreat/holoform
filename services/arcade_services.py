# services/arcade_service.py
import json
import logging
from arcadepy import Arcade
from config.settings import ARC_BASE_URL
from arcade_google.tools.utils import DateRange
# Initialize Arcade client for authentication and API access
arcade_client = Arcade(base_url=ARC_BASE_URL)

# Initialize logger for the current module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

# Create a formatter with the desired log message format
formatter = logging.Formatter(
    '\n\n%(asctime)s - %(name)s - %(levelname)s - %(message)s\n\n'
)

# Create a stream handler to output logs to the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)  # Assign the formatter to the handler

# Add the configured handler to the logger
logger.addHandler(stream_handler)

def fetch_emails(user_id: str, date_range: DateRange = DateRange.TODAY, label: str = None, max_results: int = 10) -> list:
    TOOL_NAME = "Google.ListEmailsByHeader"
    auth_response = arcade_client.tools.authorize(
        tool_name=TOOL_NAME,
        user_id=user_id,
    )
    arcade_client.auth.wait_for_completion(auth_response)
    
    inputs = {
        "date_range": date_range,
        "max_results": max_results,
        "label": label
    }
    response = arcade_client.tools.execute(
        tool_name=TOOL_NAME,
        inputs=inputs,
        user_id=user_id,
    )
    response_json = json.loads(response.to_json())
    logging.debug(f"Response MessagesJSON: {json.dumps(response_json, indent=2)}")

    output_data = response_json.get("output", {})
    values_data = output_data.get("value", {})
    messages = values_data.get("emails", [])

    logging.debug(f"messages: {messages}")

 
    return messages

def fetch_threads(user_id, max_results=10):
    """
    Gets the most recent email threads from Gmail.
    """
    TOOL_NAME = "Google.ListThreads"
    auth_response = arcade_client.tools.authorize(
        tool_name=TOOL_NAME,
        user_id=user_id,
    )
    arcade_client.auth.wait_for_completion(auth_response)

    # Prepare inputs for tool execution
    inputs = {
        "max_results": max_results,
        "include_spam_trash": False,
    }

    # Execute the tool and parse the JSON response
    response = arcade_client.tools.execute(
        tool_name=TOOL_NAME,
        inputs=inputs,
        user_id=user_id,
    )

    response_json = json.loads(response.to_json())
    logging.debug(f"Response ThreadsJSON: {json.dumps(response_json, indent=2)}")

    output_data = response_json.get("output", {})
    values_data = output_data.get("value", {})
    threads = values_data.get("threads", [])

    return threads

def get_thread_message_list(thread_id, user_id):
    """
    Extracts the text content from a Gmail thread.
    """
    TOOL_NAME = "Google.GetThread"

    auth_response = arcade_client.tools.authorize(
        tool_name=TOOL_NAME,
        user_id=user_id,
    )
    arcade_client.auth.wait_for_completion(auth_response)

    # Prepare inputs for tool execution
    inputs = {"thread_id": thread_id}

    response = arcade_client.tools.execute(
        tool_name=TOOL_NAME,
        inputs=inputs,
        user_id=user_id,
    )
    
    response_json = json.loads(response.to_json())

    output_data = response_json.get("output", {})
    values_data = output_data.get("value", {})
    messages = values_data.get("messages", [])

    return messages

def change_email_labels(email_id: str, labels_to_add: list, labels_to_remove: list, user_id: str) -> None:
    TOOL_NAME = "Google.ChangeEmailLabels"
    response = arcade_client.tools.execute(
        tool_name=TOOL_NAME,
        inputs={"email_id": email_id, 
                "labels_to_add": labels_to_add, 
                "labels_to_remove": labels_to_remove},
        user_id=user_id,
    )
    logging.debug(f"Finished changing labels for email: {email_id}")
    logging.debug(f"Response: {response}")
    return response

def get_labels(user_id: str) -> list:
    TOOL_NAME = "Google.ListLabels"
    response = arcade_client.tools.execute(
        tool_name=TOOL_NAME,
        user_id=user_id,
    )
    response_json = json.loads(response.to_json())
    logging.debug(f"Response JSON: {response_json}")
    labels = response_json.get("output", {}).get("value", {}).get("labels", [])
    logging.debug(f"Labels available to user: {labels}")
    return labels


def auth_user(user_id: str) -> str:
    """
    Authorize the user to access their Gmail account.
    """
    # Start the authorization process
    auth_response = arcade_client.auth.start(
        user_id=user_id,
        provider="google",
        scopes=["https://www.googleapis.com/auth/gmail.modify"],
    )

    if auth_response.status != "completed":
        print("Please complete the authorization challenge in your browser:")
        print(auth_response.authorization_url)
    
    # Wait for the authorization to complete
    auth_response = arcade_client.auth.wait_for_completion(auth_response)
    
    token = auth_response.context.token
    
    return token

def create_label(label_name: str, user_id: str) -> None:
    """
    Creates a new label in the user's Gmail account.

    Args:
        label_name: The name of the label to create.
        user_id: The ID of the user where the label will be created.
    """
    TOOL_NAME = "Google.CreateLabel"
    inputs = {"label_name": label_name}

    response = arcade_client.tools.execute(
        tool_name=TOOL_NAME,
        inputs=inputs,
        user_id=user_id,
    )

    response_json = json.loads(response.to_json())
    if response_json.get("success"):
        logging.info(f"Label '{label_name}' created successfully.")
    else:
        logging.error(f"Failed to create label '{label_name}'. Response: {response_json}")