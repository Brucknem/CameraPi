import { Injectable } from '@angular/core';
import { Protocol, CameraUrl, format_base, join } from '../camera-url';

@Injectable({
  providedIn: 'root',
})
export class CameraUrlService {
  streamLocation: CameraUrl = {
    protocol: Protocol.HTTP,
    location: '0.0.0.0',
    port: 9090,
    path: 'camerapi',
  };

  // streamLocation: CameraUrl = {
  //   protocol: Protocol.HTTPS,
  //   location: 'marcelbruckner.webhop.me',
  //   port: 443,
  //   path: 'camerapi',
  // };

  getCameraUrl(): string {
    return format_base(this.streamLocation);
  }

  getStreamLink(): string {
    return join(this.streamLocation, 'stream');
  }

  constructor() {}
}
