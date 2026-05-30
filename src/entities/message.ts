import { randomUUID } from 'node:crypto';

/** Result of classifying a message (labels are full, prefixed Gmail labels). */
export interface Classification {
  classification: string;
  priority: string;
  explanation: string;
}

/** Fields accepted when constructing a {@link Message}. */
export interface MessageOptions {
  userId: string;
  gmailMessageId: string;
  headerMessageId: string;
  threadId: string;
  labels?: string[];
  snippet?: string;
  historyId?: string;
  sender?: string;
  to?: string[];
  cc?: string[];
  replyToAddress?: string[];
  date?: string;
  subject?: string;
  body?: string;
  inReplyTo?: string;
  references?: string[];
}

/** A single email message tracked through the processing pipeline. */
export class Message {
  userId = '';
  gmailMessageId = '';
  headerMessageId = '';
  threadId = '';
  labels: string[] = [];
  snippet = '';
  historyId = '';
  sender = '';
  to: string[] = [];
  cc: string[] = [];
  replyToAddress: string[] = [];
  date = '';
  subject = '';
  body = '';
  inReplyTo = '';
  references: string[] = [];

  summary = '';
  classification: Classification | undefined = undefined;
  response = '';
  threadMessages: unknown[] = [];
  readonly uuid: string = randomUUID();
  status = 'unprocessed';

  constructor(options: MessageOptions) {
    // Copy only defined values so omitted optionals keep their class defaults.
    const defined = Object.fromEntries(
      Object.entries(options).filter(([, value]) => value !== undefined),
    );
    Object.assign(this, defined);
  }
}
