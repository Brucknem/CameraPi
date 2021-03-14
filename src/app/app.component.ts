import { Component, OnInit } from '@angular/core';
import { MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.styl'],
})
export class AppComponent implements OnInit {
  title = 'frontend';
  sidebarOpened = false;

  constructor(
    private matIconRegistry: MatIconRegistry,
    private domSanitizer: DomSanitizer
  ) {
    this.matIconRegistry.addSvgIcon(
      `github-circle-white-transparent`,
      this.domSanitizer.bypassSecurityTrustResourceUrl(
        'assets/github-circle-white-transparent.svg'
      )
    );
    this.matIconRegistry.addSvgIcon(
      `camerapi-icon`,
      this.domSanitizer.bypassSecurityTrustResourceUrl(
        'assets/camerapi_icon.svg'
      )
    );
  }

  ngOnInit(): void {}
}
