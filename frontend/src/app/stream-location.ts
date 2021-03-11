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
