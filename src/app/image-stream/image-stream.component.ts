import { Component, OnInit } from '@angular/core';
import { format, Protocol, StreamLocation } from '../stream-location';
import { StreamLocationService } from '../service/stream-location.service';

/**
 * The component to display the image stream.
 */
@Component({
  selector: 'app-image-stream',
  templateUrl: './image-stream.component.html',
  styleUrls: ['./image-stream.component.styl'],
})
export class ImageStreamComponent implements OnInit {
  format = format;

  get streamLocation(): string {
    return this.streamLocationService.getStreamLink();
  }

  constructor(private streamLocationService: StreamLocationService) {}

  ngOnInit(): void {}
}
