import { Component, OnInit, Output } from '@angular/core';
import { Protocol, CameraUrl } from '../camera-url';
import { CookieService } from 'ngx-cookie-service';
import { CameraUrlService } from '../service/camera-url.service';

/**
 * The sidebar that holds the settings and options.
 */
@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.styl'],
})
export class SidebarComponent implements OnInit {
  ngOnInit(): void {
  }
}
