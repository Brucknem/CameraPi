import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { ImageStreamComponent } from './image-stream/image-stream.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatSidenavModule } from '@angular/material/sidenav';

import { CookieService } from 'ngx-cookie-service';
import { SidebarComponent } from './sidebar/sidebar.component';
import { HttpClientModule } from '@angular/common/http';
import { MatIconModule, MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';
import { MatButtonModule } from '@angular/material/button';
import { StreamLocationChooserComponent } from './sidebar/stream-location-chooser/stream-location-chooser.component';
import { CameraControlsComponent } from './sidebar/camera-controls/camera-controls.component';
import { MessagesComponent } from './messages/messages.component';

@NgModule({
  declarations: [AppComponent, ImageStreamComponent, SidebarComponent, StreamLocationChooserComponent, CameraControlsComponent, MessagesComponent],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    MatOptionModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    MatSidenavModule,
    HttpClientModule,
    MatIconModule,
    MatButtonModule,
  ],
  providers: [CookieService],
  bootstrap: [AppComponent],
})
export class AppModule {
  constructor(iconRegistry: MatIconRegistry, domSanitizer: DomSanitizer) {
    iconRegistry.addSvgIconSet(
      domSanitizer.bypassSecurityTrustResourceUrl('./assets/mdi.svg')
    );
  }
}
