export enum Protocol {
  HTTP = 'http',
  HTTPS = 'https',
}
export interface CameraUrl {
  protocol: Protocol;
  location: string;
  port: number;
  path: string;
}

export function format_base(streamLocation: CameraUrl): string {
  return (
    streamLocation.protocol +
    '://' +
    streamLocation.location +
    ':' +
    streamLocation.port +
    '/'
  );
}

export function join(streamLocation: CameraUrl, subpath: string): string {
  let url = format_base(streamLocation);
  url += streamLocation.path;
  if (url.endsWith('/')) {
    url = url.substring(0, url.length - 1);
  }
  if (!subpath.startsWith('/')) {
    url += '/';
  }
  url += subpath;
  return url;
}
