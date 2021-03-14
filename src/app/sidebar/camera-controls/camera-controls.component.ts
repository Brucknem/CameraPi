import { Component, OnInit } from '@angular/core';
import { CameraControlService } from '../../service/camera-control.service';
import { interval } from 'rxjs';

@Component({
  selector: 'app-camera-controls',
  templateUrl: './camera-controls.component.html',
  styleUrls: ['./camera-controls.component.styl'],
})
export class CameraControlsComponent implements OnInit {
  record = false;
  password = '';
  isRecording = false;

  constructor(private cameraControlService: CameraControlService) {
    interval(1000).subscribe((_) => {
      this.cameraControlService.isRecording().subscribe((result) => {
        this.isRecording = result.success;
      });
    });
  }

  ngOnInit(): void {}

  onStartRecording(): void {
    this.cameraControlService.startRecording(this.password).subscribe();
  }

  onStopRecording(): void {
    this.cameraControlService.stopRecording(this.password).subscribe();
  }
}
