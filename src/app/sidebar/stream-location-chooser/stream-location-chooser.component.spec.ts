import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StreamLocationChooserComponent } from './stream-location-chooser.component';

describe('StreamLocationChooserComponent', () => {
  let component: StreamLocationChooserComponent;
  let fixture: ComponentFixture<StreamLocationChooserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ StreamLocationChooserComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(StreamLocationChooserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
