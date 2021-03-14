import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CameraUrlChooserComponent } from './camera-url-chooser.component';

describe('StreamLocationChooserComponent', () => {
  let component: CameraUrlChooserComponent;
  let fixture: ComponentFixture<CameraUrlChooserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CameraUrlChooserComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CameraUrlChooserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
