import logging
from services.arcade_services import get_thread_message_list
from services.lm_services import call_lm
from utils.utils import markdown_to_json
from entities.message import Message
from services.arcade_services import change_email_labels
from entities.labels import HoloformLabel, GmailSystemLabel

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

def create_message_objects(gmail_messages: list, user_id: str) -> list[Message]:
    """
    Converts a list of Gmail message dictionaries into Message objects.

    Args:
        gmail_messages: List of Gmail message dictionaries.
        user_id: ID of the user owning the thread
    Returns:
        List of Message objects.
    """
    if not gmail_messages:
        logger.info("No Gmail messages found.")
        return []

    messages = []
    for message in gmail_messages:
        if "id" not in message:
            continue

        logger.debug(f"Creating Message object for Message: {message['id']}")

        message_obj = Message(
            user_id=user_id,
            gmail_message_id=message["id"],
            header_message_id=message["header_message_id"],
            thread_id=message["thread_id"],
            labels=message["label_ids"],
            snippet=message["snippet"],
            history_id=message["history_id"],
            to=message["to"],
            cc=message["cc"],
            sender=message["from"],
            reply_to_address=message["reply_to"],
            date=message["date"],
            subject=message["subject"],
            body=message["body"],
            in_reply_to=message["in_reply_to"],
            references=message["references"],

        )

        logger.debug(f"message_obj created: {message_obj.gmail_message_id}")
        messages.append(message_obj)

    return messages

def summarize_thread(message: Message) -> None:
    prompt = (f"{message} \n"
                f"Summarize the following thread of emails. "
                f"Put it in 2nd person to {message.user_id} and highlight the most important parts to them. "
                f"And if anyone is waiting on them for a response, highlight that prominently. "
                f"Be concise, clear, direct, specific, and correct."
                )
        
    # Summarize the thread
    message.summary = call_lm(prompt=prompt)

def classify_message(message: Message) -> None:
    prompt = f"""
        ## Message: {message}
        ----
        ## Prompt:
        Classify the email into one of the following categories with definitions:
        {HoloformLabel.get_classification_definitions()}

        Then assign a priority level:
        {HoloformLabel.get_priority_definitions()}

        Consider:
        - **Content:** Analyze the main topics and purpose.
        - **Tone:** Determine the formality and sentiment.
        - **Sender:** Identify if the sender is known or reputable.
        - **Time-Sensitivity:** Assess if immediate action is needed.
        - **Calls to Action:** Look for requests or required responses.


        RESPONSE FORMAT:
        Return JSON only: {{"classification": "...", "priority": "...", "explanation": "..."}}
        ----"""
    response = call_lm(prompt=prompt)
    classification = markdown_to_json(response)

    # Add the Holoform prefix to the classification and priority
    classification["classification"] = HoloformLabel.get_full_label(classification["classification"])
    classification["priority"] = HoloformLabel.get_full_label(classification["priority"])
    # Assign the classification to the message
    message.classification = classification

    logger.debug(f"\nMessage Classification: {classification['classification']}\n")
    logger.debug(f"Priority Level: {classification['priority']}\n")
    logger.debug(f"Explanation: {classification['explanation']}\n")

def update_labels(message: Message) -> None:
    logger.debug(f"Updating labels for message: {message.gmail_message_id}")
    labels_to_add = [HoloformLabel.HOLOFORM.full_label, message.classification["classification"], message.classification["priority"]]
    labels_to_remove = []
    if not (message.classification["classification"].lower() == HoloformLabel.ACTION_REQUIRED.full_label or
            message.classification["priority"] == HoloformLabel.HIGH_PRIORITY.full_label):
        labels_to_remove = [GmailSystemLabel.INBOX.value]
    logger.debug(f"\nLabels to add: {labels_to_add}\n")
    logger.debug(f"\nLabels to remove: {labels_to_remove}\n")
    change_email_labels(
        email_id=message.gmail_message_id,
        labels_to_add=labels_to_add,
        labels_to_remove=labels_to_remove,
        user_id=message.user_id,
    )
    logger.debug(f"Finished updating labels for message: {message.gmail_message_id}\n")

def draft_response(message: Message) -> None:
    draft_prompt = (
        f"## Message: {message}\n"
        f"{'-'*8}\n"
        "## Prompt: \n"
        "Draft a response to the message. "
        f"Write in the first person as {message.user_id}. "
        "Be concise, clear, direct, specific, authentic, empathetic, personal, and correct. "
        "Use technical language where appropriate but remain plainspoken. Avoid clichés. "
        "The response should be a reply-all, sent to the sender and all other recipients. Retain CC. "
        "Reponse should be in JSON format: {{'thread_id': '...', 'to': '...', 'cc': '...', 'subject': '...', 'body': '...'}}"
    )
    draft_response_email = (f"response draft: {call_lm(prompt=draft_prompt, tools=['Google.WriteDraftResponseEmail'], tool_choice="Generate")} \n")
    logger.debug(f"draft_response_email: {draft_response_email}\n")

def process_message(message: Message) -> Message:
    """
    Process a single message
    """
    message.thread_messages = get_thread_message_list(message.thread_id, message.user_id)
    classify_message(message)
    logger.debug(f"\n\n Subject: {message.subject} \n Classification: {message.classification} \n {'-'*20}\n")
    update_labels(message)
    logger.debug(f"\n\nFinished processing message: {message.gmail_message_id}\n\n")
    message.status = "processed"
    return message

def process_messages(messages: list[Message]) -> list[Message]:
    return [process_message(message) for message in messages]