import { Injectable } from '@angular/core';
import { Protocol, CameraUrl, format_base, join } from '../camera-url';

@Injectable({
  providedIn: 'root',
})
export class CameraUrlService {
  // streamLocation: StreamLocation = {
  //   protocol: Protocol.HTTP,
  //   location: '192.168.0.245',
  //   port: 8080,
  //   path: 'stream.mjpg',
  // };

  streamLocation: CameraUrl = {
    protocol: Protocol.HTTPS,
    location: 'marcelbruckner.webhop.me',
    port: 443,
    path: 'camerapi',
  };

  getCameraUrl(): string {
    return format_base(this.streamLocation);
  }

  getStreamLink(): string {
    return join(this.streamLocation, 'stream');
  }

  constructor() {}
}
