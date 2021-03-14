import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { CameraUrlService } from './camera-url.service';
import { MessagesService } from './messages.service';

@Injectable({
  providedIn: 'root',
})
export class CameraControlService {
  constructor(
    private httpService: HttpClient,
    private cameraUrlService: CameraUrlService,
    private messagesService: MessagesService
  ) {}

  startRecording(): Observable<any> {
    this.messagesService.add('Start recording hit.');
    return this.httpService.get(
      new URL(
        'start_recording',
        this.cameraUrlService.getCameraUrl()
      ).toString()
    );
  }

  stopRecording(): Observable<any> {
    this.messagesService.add('Stop recording hit.');
    return this.httpService.get(
      new URL('stop_recording', this.cameraUrlService.getCameraUrl()).toString()
    );
  }
}
