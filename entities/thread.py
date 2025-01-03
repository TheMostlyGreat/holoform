from dataclasses import dataclass, field
import uuid
from entities.message import Message
from services.arcade_services import get_thread_message_list
from typing import List, Dict, Optional

@dataclass
class TreeNode:
    """
    Represents a node in the message tree.
    
    Fields:
    - message: The Message instance.
    - children: List of child TreeNodes (replies).
    """
    message: Message
    children: List['TreeNode'] = field(default_factory=list)

@dataclass
class Thread:
    """
    Stores and tracks email thread data through the processing pipeline.
    
    Fields:
    - user_id: ID of the user owning the thread
    - thread_id: Unique ID of the thread from the email service
    - summary: AI-generated summary of the content
    - history_id: ID tracking history
    - snippet: Short preview of the thread
    - uuid: Internal unique ID
    - status: Processing status
    - messages: List of all messages in the thread
    - tree_roots: Root nodes of the message tree
    """
    user_id: str
    thread_id: str
    summary: str = ""    
    history_id: str = ""
    snippet: str = ""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "unprocessed"
    messages: List[Message] = field(default_factory=list)
    tree_roots: List[TreeNode] = field(default_factory=list)  # Root nodes of the tree

    def __post_init__(self):
        """
        Initializes the thread by fetching messages and building the tree structure.
        """
        if not self.thread_id:
            raise ValueError("thread_id cannot be empty.")
        
        # Get the message list from the email service
        messagelist = get_thread_message_list(thread_id=self.thread_id, user_id=self.user_id)
        message_dict: Dict[str, Message] = {}

        # Create Message instances and store them in a dictionary
        for msg_data in messagelist:
            message = Message(
                user_id=self.user_id,
                gmail_message_id=msg_data["id"],
                header_message_id=msg_data.get("header_message_id", ""),
                thread_id=self.thread_id,
                in_reply_to=msg_data.get("in_reply_to", ""),
                body=msg_data.get("body", ""),
                date=msg_data.get("date", ""),
                sender=msg_data.get("from", ""),
                subject=msg_data.get("subject", "")
            )
            message_dict[message.gmail_message_id] = message
            self.messages.append(message)

        # Build the tree by creating TreeNodes and establishing parent-child relationships
        node_dict: Dict[str, TreeNode] = {}
        header_to_gmail_id: Dict[str, str] = {}

        # First, map header_message_id to gmail_message_id
        for message in self.messages:
            node = TreeNode(message=message)
            node_dict[message.gmail_message_id] = node
            if message.header_message_id:
                header_to_gmail_id[message.header_message_id] = message.gmail_message_id

        # Now, establish parent-child relationships using the mapped IDs
        for message in self.messages:
            in_reply_to = message.in_reply_to if message.in_reply_to else None  # Single message ID string or empty string
            if in_reply_to:
                # Map header_message_id to gmail_message_id
                parent_gmail_id = header_to_gmail_id.get(in_reply_to)
                if parent_gmail_id and parent_gmail_id in node_dict:
                    parent_node = node_dict[parent_gmail_id]
                    parent_node.children.append(node_dict[message.gmail_message_id])
                else:
                    # No valid parent found; this is a root node
                    self.tree_roots.append(node_dict[message.gmail_message_id])
            else:
                # No in_reply_to; this is a root node
                self.tree_roots.append(node_dict[message.gmail_message_id])