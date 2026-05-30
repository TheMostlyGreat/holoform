/** Gmail system labels. */
export enum GmailSystemLabel {
  Inbox = 'INBOX',
  Spam = 'SPAM',
  Trash = 'TRASH',
  Unread = 'UNREAD',
  Starred = 'STARRED',
  Important = 'IMPORTANT',
  Sent = 'SENT', // Automatically applied to sent messages
  Draft = 'DRAFT', // Automatically applied to draft messages
  CategoryPersonal = 'CATEGORY_PERSONAL',
  CategorySocial = 'CATEGORY_SOCIAL',
  CategoryPromotions = 'CATEGORY_PROMOTIONS',
  CategoryUpdates = 'CATEGORY_UPDATES',
  CategoryForums = 'CATEGORY_FORUMS',
}

/**
 * Holoform labels used for email classification. Each value is the short label
 * name; {@link getFullLabel} maps it to the prefixed Gmail label.
 */
export enum HoloformLabel {
  Holoform = 'Holoform',
  HighPriority = 'HighPriority',
  MediumPriority = 'MediumPriority',
  LowPriority = 'LowPriority',
  Spam = 'Spam',
  Promotional = 'Promotional',
  ActionRequired = 'ActionRequired',
  Fyi = 'FYI',
  Relationships = 'Relationships',
  Newsletter = 'Newsletter',
}

/**
 * Maps each classification label to its definition. Used to give the LLM
 * context during email classification.
 */
export function getClassificationDefinitions(): Record<string, string> {
  return {
    Spam: 'Unsolicited and irrelevant emails, typically for advertising.',
    Promotional: 'Emails aimed at promoting products, services, or events to this user.',
    ActionRequired: 'Emails that need a response or specific action from the recipient.',
    FYI: 'Informational emails that provide information without requiring any action.',
    Relationships:
      'Communications intended to build or maintain professional or personal relationships.',
    Newsletter: 'Regular updates or information broadcasts sent to subscribers.',
  };
}

/** Maps each priority label to its definition. */
export function getPriorityDefinitions(): Record<string, string> {
  return {
    HighPriority: 'Emails that require immediate attention or action.',
    MediumPriority: 'Important emails that should be addressed promptly.',
    LowPriority: 'Emails that can be addressed at a later time.',
  };
}

const FULL_LABEL_MAP = new Map<string, string>([
  ['Holoform', 'Holoform'],
  ['HighPriority', 'Holoform/HighPriority'],
  ['MediumPriority', 'Holoform/MediumPriority'],
  ['LowPriority', 'Holoform/LowPriority'],
  ['Spam', 'Holoform/Spam'],
  ['Promotional', 'Holoform/Promotional'],
  ['ActionRequired', 'Holoform/ActionRequired'],
  ['FYI', 'Holoform/FYI'],
  ['Relationships', 'Holoform/Relationships'],
  ['Newsletter', 'Holoform/Newsletter'],
]);

/**
 * Returns the full Gmail label name including the `Holoform/` prefix, or an
 * empty string if the short name is unknown.
 */
export function getFullLabel(labelName: string): string {
  return FULL_LABEL_MAP.get(labelName) ?? '';
}

/** Returns the combined definition for a label, or an empty string if unknown. */
export function getDefinition(label: HoloformLabel): string {
  const allDefinitions = new Map<string, string>([
    ...Object.entries(getClassificationDefinitions()),
    ...Object.entries(getPriorityDefinitions()),
  ]);
  return allDefinitions.get(label) ?? '';
}
