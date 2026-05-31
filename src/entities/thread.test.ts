import { describe, expect, test } from 'bun:test';

import { Message } from './message.ts';
import { Thread, TreeNode } from './thread.ts';

function makeMessage(id: string, headerId: string, inReplyTo = ''): Message {
  return new Message({
    userId: 'u1',
    gmailMessageId: id,
    headerMessageId: headerId,
    threadId: 't1',
    inReplyTo,
  });
}

describe('Thread', () => {
  test('constructor rejects an empty threadId', () => {
    expect(() => new Thread('u1', '')).toThrow('thread_id cannot be empty.');
  });

  test('buildTree returns flat roots when there are no reply links', () => {
    const roots = Thread.buildTree([makeMessage('g1', 'h1'), makeMessage('g2', 'h2')]);
    expect(roots).toHaveLength(2);
    expect(roots.every(node => node instanceof TreeNode)).toBe(true);
  });

  test('buildTree nests a reply under its parent via in-reply-to', () => {
    const parent = makeMessage('g1', 'h1');
    const child = makeMessage('g2', 'h2', 'h1');
    const roots = Thread.buildTree([parent, child]);
    expect(roots).toHaveLength(1);
    expect(roots[0]?.message.gmailMessageId).toBe('g1');
    expect(roots[0]?.children[0]?.message.gmailMessageId).toBe('g2');
  });

  test('buildTree treats a reply with an unknown parent as a root', () => {
    const orphan = makeMessage('g2', 'h2', 'missing');
    const roots = Thread.buildTree([orphan]);
    expect(roots).toHaveLength(1);
    expect(roots[0]?.message.gmailMessageId).toBe('g2');
  });
});
