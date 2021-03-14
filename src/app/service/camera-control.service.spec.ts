import { TestBed } from '@angular/core/testing';

import { CameraControlService } from './camera-control.service';

describe('CameraControlService', () => {
  let service: CameraControlService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CameraControlService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
