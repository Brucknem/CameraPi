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

  it('camera path correct formatted', () => {
    expect(service.getCameraUrl()).toBe(
      new URL('https://marcelbruckner.webhop.me:443/camerapi')
    );
  });
});
