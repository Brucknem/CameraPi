import { Component, OnInit } from '@angular/core';
import { Protocol, CameraUrl } from '../camera-url';
import { CameraUrlService } from '../service/camera-url.service';

/**
 * The component to display the image stream.
 */
@Component({
  selector: 'app-image-stream',
  templateUrl: './image-stream.component.html',
  styleUrls: ['./image-stream.component.styl'],
})
export class ImageStreamComponent implements OnInit {
  get streamLocation(): string {
    return this.streamLocationService.getStreamLink();
  }

  constructor(private streamLocationService: CameraUrlService) {}

  ngOnInit(): void {}
}
