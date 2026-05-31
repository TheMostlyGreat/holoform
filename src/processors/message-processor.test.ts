import { describe, expect, test } from 'bun:test';

import { GmailSystemLabel } from '../entities/labels.ts';
import type { Classification } from '../entities/message.ts';
import type { FetchedEmail } from '../services/arcade-service.ts';
import { computeLabelChanges, createMessageObjects } from './message-processor.ts';

describe('createMessageObjects', () => {
  test('returns an empty list when given no emails', () => {
    expect(createMessageObjects([], 'u1')).toEqual([]);
  });

  test('maps fetched-email fields onto Message instances', () => {
    const email: FetchedEmail = {
      id: 'g1',
      headerMessageId: 'h1',
      threadId: 't1',
      from: 'alice@example.com',
      subject: 'Hi',
      labelIds: ['INBOX'],
    };
    const [message] = createMessageObjects([email], 'u1');
    expect(message?.gmailMessageId).toBe('g1');
    expect(message?.sender).toBe('alice@example.com');
    expect(message?.labels).toEqual(['INBOX']);
    expect(message?.userId).toBe('u1');
  });
});

const fullLabel = (priority: string, category: string): Classification => ({
  classification: category,
  priority,
  explanation: '',
});

describe('computeLabelChanges', () => {
  test('always adds Holoform, classification, and priority labels', () => {
    const { labelsToAdd } = computeLabelChanges(
      fullLabel('Holoform/LowPriority', 'Holoform/Newsletter'),
    );
    expect(labelsToAdd).toEqual(['Holoform', 'Holoform/Newsletter', 'Holoform/LowPriority']);
  });

  test('archives (removes Inbox) for low-priority, non-actionable mail', () => {
    const { labelsToRemove } = computeLabelChanges(
      fullLabel('Holoform/LowPriority', 'Holoform/Newsletter'),
    );
    expect(labelsToRemove).toEqual([GmailSystemLabel.Inbox]);
  });

  test('keeps high-priority mail in the inbox', () => {
    const { labelsToRemove } = computeLabelChanges(
      fullLabel('Holoform/HighPriority', 'Holoform/Newsletter'),
    );
    expect(labelsToRemove).toEqual([]);
  });
});
