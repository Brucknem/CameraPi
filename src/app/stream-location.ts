export enum Protocol {
  HTTP = 'http',
  HTTPS = 'https',
}
export interface StreamLocation {
  protocol: Protocol;
  location: string;
  port: number;
  path: string;
}

export function format(streamLocation: StreamLocation): string {
  return (
    streamLocation.protocol +
    '://' +
    streamLocation.location +
    ':' +
    streamLocation.port +
    '/' +
    streamLocation.path +
    '.mjpg'
  );
}
