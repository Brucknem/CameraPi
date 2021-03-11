import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImageStreamComponent } from './image-stream.component';

describe('ImageStreamComponent', () => {
  let component: ImageStreamComponent;
  let fixture: ComponentFixture<ImageStreamComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ImageStreamComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ImageStreamComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
