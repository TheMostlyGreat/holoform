# Holoform - Intelligent Email Management

A Python-based email management system that uses AI to classify, prioritize, and streamline Gmail communications.

## Features

- **Smart Email Classification**: Automatically categorizes emails into actionable categories
- **Priority Management**: Assigns priority levels to help focus on what matters
- **Gmail Integration**: Seamless integration with Gmail's label system
- **AI-Powered Processing**: Uses LLMs for intelligent email analysis
- **Automated Response Drafting**: Generates contextual email response drafts

## Project Structure

```
holoform/
├── config/           # Configuration settings
├── entities/         # Data models and types
├── processors/       # Core processing logic
├── services/        # External service integrations
└── utils/           # Helper functions
```

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv hf-env
source hf-env/bin/activate  # Unix
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with:
```
ARC_BASE_URL=http://localhost:9099
USER_ID=your-email@example.com
ARCADE_API_KEY=your-api-key
```

## Core Components

### Email Classification
See implementation in:

```82:116:processors/message_processor.py
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
```


### Label Management
See implementation in:

```1:19:entities/labels.py
from enum import Enum

class GmailSystemLabel(Enum):
    """
    Enumeration of Gmail system labels.
    """
    INBOX = "INBOX"
    SPAM = "SPAM"
    TRASH = "TRASH"
    UNREAD = "UNREAD"
    STARRED = "STARRED"
    IMPORTANT = "IMPORTANT"
    SENT = "SENT"  # Automatically applied to sent messages
    DRAFT = "DRAFT"  # Automatically applied to draft messages
    CATEGORY_PERSONAL = "CATEGORY_PERSONAL"
    CATEGORY_SOCIAL = "CATEGORY_SOCIAL"
    CATEGORY_PROMOTIONS = "CATEGORY_PROMOTIONS"
    CATEGORY_UPDATES = "CATEGORY_UPDATES"
    CATEGORY_FORUMS = "CATEGORY_FORUMS"
```


### Message Processing
See implementation in:

```25:65:processors/message_processor.py
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

```


## Usage

Run the main script to process emails:

```bash
python main.py
```

The system will:
1. Authenticate with Gmail
2. Fetch recent emails
3. Classify and prioritize messages
4. Apply appropriate labels
5. Generate response drafts when needed

## Dependencies

Key dependencies from requirements.txt:
- arcade_google
- fastapi
- openai
- python-dotenv
- google-auth
- google-auth-oauthlib

## Project Status

This is an active project. Current development focuses on:
- Batch processing optimization
- Multi-part email support
- Forward email with attachments support
- Permanent BCC functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request


