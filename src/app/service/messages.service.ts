import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root',
})
export class MessagesService {
  constructor(private snackBar: MatSnackBar) {}

  add(message: string, value?: any): void {
    let finalMessage = message;
    if (value !== undefined && value !== null) {
      finalMessage += ': ' + value;
    }
    this.snackBar.open(finalMessage, 'OK', {
      duration: 2000,
    });
  }
}
