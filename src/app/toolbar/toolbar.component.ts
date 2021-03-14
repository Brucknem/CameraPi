import { Component, OnInit, Output } from '@angular/core';
import { EventEmitter } from '@angular/core';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.styl'],
})
export class ToolbarComponent implements OnInit {
  @Output()
  menuToggled = new EventEmitter<string>();

  constructor() {}

  ngOnInit(): void {}

  toggleMenu(): void {
    this.menuToggled.emit('toggled menu');
  }
}
