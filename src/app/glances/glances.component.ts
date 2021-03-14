import { Component, OnInit } from '@angular/core';
import { CameraUrlService } from '../service/camera-url.service';
import { join } from '../camera-url';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-glances',
  templateUrl: './glances.component.html',
  styleUrls: ['./glances.component.styl'],
})
export class GlancesComponent implements OnInit {
  glancesUrl: SafeUrl;

  constructor(
    private cameraUrlService: CameraUrlService,
    private sanitizer: DomSanitizer
  ) {
    this.glancesUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
      join(this.cameraUrlService.streamLocation, 'glances')
    );
  }

  ngOnInit(): void {}
}
