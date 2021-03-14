import { Component, OnInit } from '@angular/core';
import { CameraControlService } from '../../service/camera-control.service';

@Component({
  selector: 'app-camera-controls',
  templateUrl: './camera-controls.component.html',
  styleUrls: ['./camera-controls.component.styl'],
})
export class CameraControlsComponent implements OnInit {
  record = false;
  password = '';

  constructor(private cameraControlService: CameraControlService) {}

  ngOnInit(): void {}

  onStartRecording(): void {
    this.cameraControlService.startRecording(this.password).subscribe();
  }

  onStopRecording(): void {
    this.cameraControlService.stopRecording(this.password).subscribe();
  }
}
