import { Injectable } from '@angular/core';
import { Protocol, StreamLocation, format } from '../stream-location';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class StreamLocationService {
  streamLocation: StreamLocation = {
    protocol: Protocol.HTTP,
    location: '192.168.0.245',
    port: 8080,
    path: 'stream',
  };

  getStreamLink(): string {
    return format(this.streamLocation);
  }

  constructor(private http: HttpClient) {}
}
