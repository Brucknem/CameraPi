import { Component, OnInit } from '@angular/core';
import { CameraControlService } from '../../service/camera-control.service';
import { MessagesService } from '../../service/messages.service';

@Component({
  selector: 'app-camera-controls',
  templateUrl: './camera-controls.component.html',
  styleUrls: ['./camera-controls.component.styl'],
})
export class CameraControlsComponent implements OnInit {
  record = false;

  constructor(
    private cameraControlService: CameraControlService,
    private messagesService: MessagesService
  ) {}

  ngOnInit(): void {}

  onStartRecording(): void {
    this.cameraControlService.startRecording().subscribe((result) => {
      this.messagesService.add(result);
    });
  }
}
