import { TestBed } from '@angular/core/testing';

import { CameraUrlService } from './camera-url.service';

describe('StreamLocationService', () => {
  let service: CameraUrlService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CameraUrlService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
