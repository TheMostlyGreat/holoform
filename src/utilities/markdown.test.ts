import { describe, expect, test } from 'bun:test';

import { markdownToJson } from './markdown.ts';

describe('markdownToJson', () => {
  test('parses a plain JSON string', () => {
    expect(markdownToJson('{"a": 1}')).toEqual({ a: 1 });
  });

  test('strips ```json fences before parsing', () => {
    expect(markdownToJson('```json\n{"a": 1}\n```')).toEqual({ a: 1 });
  });

  test('strips bare ``` fences before parsing', () => {
    expect(markdownToJson('```\n{"b": "x"}\n```')).toEqual({ b: 'x' });
  });

  test('throws on invalid JSON', () => {
    expect(() => markdownToJson('not json')).toThrow();
  });
});
