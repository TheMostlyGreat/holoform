import 'dotenv/config';

// Loads environment variables from a .env file (via dotenv/config side effect).

export const ARC_BASE_URL = process.env.ARC_BASE_URL ?? 'http://localhost:9099';
export const LM_BASE_URL = process.env.LM_BASE_URL ?? `${ARC_BASE_URL}/v1`;
export const DEFAULT_USER_ID = process.env.USER_ID ?? '0';
export const LOG_LEVEL = process.env.LOG_LEVEL ?? 'DEBUG';
