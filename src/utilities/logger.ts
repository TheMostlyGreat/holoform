type LogValues = readonly unknown[];

/** Minimal console-backed logger, mirroring the Python module-level loggers. */
export const logger = {
  debug: (...messages: LogValues): void => {
    console.debug(...messages);
  },
  info: (...messages: LogValues): void => {
    console.info(...messages);
  },
  warn: (...messages: LogValues): void => {
    console.warn(...messages);
  },
  error: (...messages: LogValues): void => {
    console.error(...messages);
  },
};
