import { Injectable } from '@angular/core';
import {  HttpClient} from "@angular/common/http";
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class dataService {

  constructor(private http: HttpClient) { }

  //IinewZxUa5pYAZeC
  URL_API:string = "https://us-east-1.aws.data.mongodb-api.com/app/data-uvdudur/endpoint/data/v1/action" 

  get_data(collection:string, query:any, sort_query:any = {} ): Observable<any>{
    return this.http.post(
      this.URL_API + "/find",
      {
        "collection": collection,
        "database": "smarthome",
        "dataSource": "proyectoArqui",
        "filter": query,
        "sort": sort_query	
      },
      {
        headers: {
          "Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYWFzX2RldmljZV9pZCI6IjAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMCIsImJhYXNfZG9tYWluX2lkIjoiNjZjNDBhNDAwOWVhMDExNGIwYjg3NzhiIiwiZXhwIjoxNzI2OTQxMzk4LCJpYXQiOjE3MjY5Mzk1OTgsImlzcyI6IjY2ZWYwMWNlOTk2ZjI2OTNhNzVmN2YyZCIsImp0aSI6IjY2ZWYwMWNlOTk2ZjI2OTNhNzVmN2YzMyIsInN1YiI6IjY2ZTBmMTI0ZDc4ODcyMjVkZjRkMmQzYiIsInR5cCI6ImFjY2VzcyJ9.aoSl_YX1PQu1ICNjeTvNYdQZkrNziz7YxYhz3rmzo-s",
          "content-type" : "application/json"
        },
        withCredentials: true
      }
    ) as any;
  }
  
}


export interface data_acciones {
  _id: string;
  accion: string;
  Fecha_registro: string;
  fecha_texto: string;
  on_off: string;
}

export interface data_temp {
  _id: string;
  Fecha_registro: string;
  temp: number;
  humedad: number;
}