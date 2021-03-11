import { Component, OnInit } from '@angular/core';
import { StreamLocation, Protocol } from '../stream-location';
import { CookieService } from 'ngx-cookie-service';

/**
 * The component to display the image stream.
 */
@Component({
  selector: 'app-image-stream',
  templateUrl: './image-stream.component.html',
  styleUrls: ['./image-stream.component.styl'],
})
export class ImageStreamComponent implements OnInit {
  eProtocol = Protocol;

  streamLocation: StreamLocation = {
    protocol: Protocol.HTTP,
    location: '192.168.0.245',
    port: 8080,
    path: 'stream',
  };

  constructor(private cookieService: CookieService) {}

  ngOnInit(): void {
    if (this.cookieService.check('protocol')) {
      this.streamLocation.protocol = this.cookieService.get(
        'protocol'
      ) as Protocol;
    }

    if (this.cookieService.check('location')) {
      this.streamLocation.location = this.cookieService.get('location');
    }

    if (this.cookieService.check('port')) {
      this.streamLocation.port =
        Number(this.cookieService.get('port')) || this.streamLocation.port;
    }

    if (this.cookieService.check('path')) {
      this.streamLocation.path = this.cookieService.get('path');
    }
  }

  onChangeStreamLocation(): void {
    this.cookieService.set('protocol', this.streamLocation.protocol);
    this.cookieService.set('location', this.streamLocation.location);
    this.cookieService.set('port', this.streamLocation.port.toString());
    this.cookieService.set('path', this.streamLocation.path);
  }
}
