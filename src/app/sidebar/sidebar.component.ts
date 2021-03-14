import { Component, OnInit, Output } from '@angular/core';
import { Protocol, StreamLocation } from '../stream-location';
import { CookieService } from 'ngx-cookie-service';
import { StreamLocationService } from '../service/stream-location.service';

/**
 * The sidebar that holds the settings and options.
 */
@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.styl'],
})
export class SidebarComponent implements OnInit {
  /**
   * Enum reference for looping.
   */
  eProtocol = Protocol;

  get streamLocation(): StreamLocation {
    return this.streamLocationService.streamLocation;
  }

  set streamLocation(value: StreamLocation) {
    this.streamLocationService.streamLocation = value;
  }

  /**
   * @param cookieService Injection to access browser cookies.
   * @param streamLocationService Injection to access the global stream location.
   */
  constructor(
    private cookieService: CookieService,
    private streamLocationService: StreamLocationService
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
  }

  clearCookies(): void {
    this.cookieService.delete('protocol');
    this.cookieService.delete('location');
    this.cookieService.delete('port');
    this.cookieService.delete('path');
  }
}
