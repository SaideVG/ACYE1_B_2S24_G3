import { Injectable } from '@angular/core';
import {  HttpClient} from "@angular/common/http";
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ControlService {

  constructor(private http: HttpClient) { }

  get_state_control(): Observable<any>{
    return this.http.get('http://172.20.10.10:5000/get_state_control');
  }
  control(body:any): Observable<any>{
    return this.http.post('http://172.20.10.10:5000/control', body );
  }

  msg_lcd(msg:string): Observable<any>{
    const data = { msg}
    return this.http.post('http://172.20.10.10:5000/msg_lcd', data );
  }
}

