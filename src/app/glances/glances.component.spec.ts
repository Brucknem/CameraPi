import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GlancesComponent } from './glances.component';

describe('GlancesComponent', () => {
  let component: GlancesComponent;
  let fixture: ComponentFixture<GlancesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GlancesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GlancesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
