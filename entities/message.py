from dataclasses import dataclass, field
import uuid

@dataclass
class Message:
    """
    A data structure representing a single email message.
    
    Fields:
    - message_id: Unique ID from email service
    - thread_id: ID of parent thread
    - sender: Email address of sender
    - recipients: List of recipient email addresses
    - subject: Email subject line
    - body: Main message content
    - date: When message was sent
    - labels: Any labels/categories applied to message
    """
    user_id: str 
    gmail_message_id: str
    header_message_id: str
    thread_id: str 
    labels: list = field(default_factory=list)
    snippet: str = ""
    history_id: str = ""
    sender: str = ""
    to: list = ""
    cc: list = ""
    reply_to_address: list = ""
    date: str = ""
    subject: str = ""
    body: str = ""
    summary: str = ""
    classification: str = ""
    in_reply_to: str = ""
    references: list = field(default_factory=list)
    response: str = ""
    thread_messages: list = field(default_factory=list)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    # We use a lambda to generate a unique UUID if none is provided
    status: str = "unprocessed"