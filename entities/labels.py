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

class HoloformLabel(Enum):
    """
    Enumeration of Holoform labels used for email classification.
    Each label includes a definition to guide the LLM in categorizing emails accurately.
    """
    HOLOFORM = "Holoform"  # General label for all emails processed by Holoform.
    HIGH_PRIORITY = "HighPriority"  # Emails that require immediate attention or action.
    MEDIUM_PRIORITY = "MediumPriority"  # Important emails that should be addressed promptly.
    LOW_PRIORITY = "LowPriority"  # Emails that can be addressed at a later time.
    SPAM = "Spam"  # Unsolicited and irrelevant emails, typically for advertising.
    PROMOTIONAL = "Promotional"  # Emails aimed at promoting products, services, or events.
    ACTION_REQUIRED = "ActionRequired"  # Emails that need a response or specific action from the recipient.
    FYI = "FYI"  # Informational emails that provide information without requiring any action.
    RELATIONSHIPS = "Relationships"  # Communications intended to build or maintain professional or personal relationships.
    NEWSLETTER = "Newsletter"  # Regular updates or information broadcasts sent to subscribers.

    @property
    def definition(self) -> str:
        """
        Returns the definition for a specific label.

        Args:
            label_name: Name of the label to get definition for (without 'Holoform/' prefix)

        Returns:
            str: The definition of the label, or empty string if label not found

        Example:
            >>> HoloformLabel.ACTION_REQUIRED.definition
            "Emails that need a response or specific action from the recipient."
        """
        # Combine both definition dictionaries
        all_definitions = {
            **HoloformLabel.get_classification_definitions(),
            **HoloformLabel.get_priority_definitions()
        }
        
        # Return definition if found, empty string if not
        return all_definitions.get(self.value, "")
    
    @staticmethod
    def get_classification_definitions() -> dict:
        """
        Returns a dictionary mapping each label to its definition.
        Useful for providing context to the LLM during email classification.
        """
        return {
            "Spam": "Unsolicited and irrelevant emails, typically for advertising.",
            "Promotional": "Emails aimed at promoting products, services, or events to this user.",
            "ActionRequired": "Emails that need a response or specific action from the recipient.",
            "FYI": "Informational emails that provide information without requiring any action.",
            "Relationships": "Communications intended to build or maintain professional or personal relationships.",
            "Newsletter": "Regular updates or information broadcasts sent to subscribers.",
        }
    @staticmethod
    def get_priority_definitions() -> dict:
        """
        Returns a dictionary mapping each label to its definition.
        Useful for providing context to the LLM during email classification.
        """
        return {
            "HighPriority": "Emails that require immediate attention or action.",
            "MediumPriority": "Important emails that should be addressed promptly.",
            "LowPriority": "Emails that can be addressed at a later time.",
        }
    
    @staticmethod
    def get_full_label(label_name: str) -> str:
        """
        Returns the full Gmail label name including the Holoform prefix.
        """
        label_map = {
            "Holoform": "Holoform",
            "HighPriority": "Holoform/HighPriority", 
            "MediumPriority": "Holoform/MediumPriority",
            "LowPriority": "Holoform/LowPriority",
            "Spam": "Holoform/Spam",
            "Promotional": "Holoform/Promotional", 
            "ActionRequired": "Holoform/ActionRequired",
            "FYI": "Holoform/FYI",
            "Relationships": "Holoform/Relationships",
            "Newsletter": "Holoform/Newsletter"
        }
        return label_map.get(label_name, "")

    @property
    def full_label(self) -> str:
        """
        Returns the full Gmail label name including the Holoform prefix.

        Args:
            label_name: The short label name (e.g. "HighPriority", "Spam")

        Returns:
            str: The full label name with prefix (e.g. "Holoform/HighPriority")
        """
        label_map = {
            "Holoform": "Holoform",
            "HighPriority": "Holoform/HighPriority", 
            "MediumPriority": "Holoform/MediumPriority",
            "LowPriority": "Holoform/LowPriority",
            "Spam": "Holoform/Spam",
            "Promotional": "Holoform/Promotional", 
            "ActionRequired": "Holoform/ActionRequired",
            "FYI": "Holoform/FYI",
            "Relationships": "Holoform/Relationships",
            "Newsletter": "Holoform/Newsletter"
        }
        return label_map.get(self.value, "")

    @property
    def is_gmail_managed(self) -> bool:
        """
        Indicates if the label is automatically managed by Gmail.
        """
        return self in {
            GmailSystemLabel.SENT,
            GmailSystemLabel.DRAFT,
        }