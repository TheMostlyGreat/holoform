import { describe, expect, test } from 'bun:test';

import { Message } from './message.ts';

describe('Message', () => {
  test('applies defaults for omitted optional fields', () => {
    const message = new Message({
      userId: 'u1',
      gmailMessageId: 'g1',
      headerMessageId: 'h1',
      threadId: 't1',
    });
    expect(message.snippet).toBe('');
    expect(message.labels).toEqual([]);
    expect(message.references).toEqual([]);
    expect(message.status).toBe('unprocessed');
    expect(message.classification).toBeUndefined();
  });

  test('keeps provided values and does not let undefined clobber defaults', () => {
    const message = new Message({
      userId: 'u1',
      gmailMessageId: 'g1',
      headerMessageId: 'h1',
      threadId: 't1',
      subject: 'Hello',
      snippet: undefined,
    });
    expect(message.subject).toBe('Hello');
    expect(message.snippet).toBe('');
  });

  test('generates a unique uuid per instance', () => {
    const base = { userId: 'u', gmailMessageId: 'g', headerMessageId: 'h', threadId: 't' };
    expect(new Message(base).uuid).not.toBe(new Message(base).uuid);
  });
});
