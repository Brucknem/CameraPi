import { TestBed } from '@angular/core/testing';

import { StreamLocationService } from './stream-location.service';

describe('StreamLocationService', () => {
  let service: StreamLocationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StreamLocationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
