import { describe, expect, test } from 'bun:test';

import {
  getClassificationDefinitions,
  getDefinition,
  getFullLabel,
  getPriorityDefinitions,
  HoloformLabel,
} from './labels.ts';

describe('getFullLabel', () => {
  test('prefixes a known short label', () => {
    expect(getFullLabel('HighPriority')).toBe('Holoform/HighPriority');
    expect(getFullLabel('Holoform')).toBe('Holoform');
  });

  test('returns empty string for an unknown label', () => {
    expect(getFullLabel('Nope')).toBe('');
  });

  test('maps every HoloformLabel value', () => {
    for (const value of Object.values(HoloformLabel)) {
      expect(getFullLabel(value)).not.toBe('');
    }
  });
});

describe('definitions', () => {
  test('classification definitions include the expected keys', () => {
    expect(getClassificationDefinitions()).toHaveProperty('ActionRequired');
    expect(getPriorityDefinitions()).toHaveProperty('HighPriority');
  });

  test('getDefinition resolves classification and priority labels', () => {
    expect(getDefinition(HoloformLabel.ActionRequired)).toContain('response');
    expect(getDefinition(HoloformLabel.HighPriority)).toContain('immediate');
  });

  test('getDefinition returns empty string for labels without a definition', () => {
    expect(getDefinition(HoloformLabel.Holoform)).toBe('');
  });
});
