import { Component, OnInit } from '@angular/core';
import { Protocol, CameraUrl } from '../../camera-url';
import { CookieService } from 'ngx-cookie-service';
import { CameraUrlService } from '../../service/camera-url.service';

@Component({
  selector: 'app-stream-location-chooser',
  templateUrl: './stream-location-chooser.component.html',
  styleUrls: ['./stream-location-chooser.component.styl'],
})
export class StreamLocationChooserComponent implements OnInit {
  /**
   * Enum reference for looping.
   */
  eProtocol = Protocol;

  get streamLocation(): CameraUrl {
    return this.streamLocationService.streamLocation;
  }

  set streamLocation(value: CameraUrl) {
    this.streamLocationService.streamLocation = value;
  }

  /**
   * @param cookieService Injection to access browser cookies.
   * @param streamLocationService Injection to access the global stream location.
   */
  constructor(
    private cookieService: CookieService,
    private streamLocationService: CameraUrlService
  ) {}

  /**
   * Initializes the component.
   */
  ngOnInit(): void {
    this.retrieveCookies();
  }

  /**
   * Checks the cookies for the stream location.
   * @private
   */
  private retrieveCookies(): void {
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

  /**
   * @callback Called when the stream location is changed in the UI. Saves the values as cookies.
   */
  onChangeStreamLocation(): void {
    this.cookieService.set('protocol', this.streamLocation.protocol);
    this.cookieService.set('location', this.streamLocation.location);
    this.cookieService.set('port', this.streamLocation.port.toString());
    this.cookieService.set('path', this.streamLocation.path);
    this.cookieService.set('streamSubPath', this.streamLocation.path);
  }

  /**
   * Clears the cookies from the server, as frequent changes in location does not update.
   */
  clearCookies(): void {
    this.cookieService.delete('protocol');
    this.cookieService.delete('location');
    this.cookieService.delete('port');
    this.cookieService.delete('path');
    this.cookieService.delete('streamSubPath');
  }
}
