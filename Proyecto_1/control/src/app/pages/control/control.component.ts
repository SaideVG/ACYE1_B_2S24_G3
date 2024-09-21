import { Component, OnDestroy } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { ControlService } from '../../services/control.service';
import moment from 'moment';

@Component({
  selector: 'app-control',
  templateUrl: './control.component.html',
  styleUrl: './control.component.scss'
})
export class ControlComponent implements OnDestroy {
  is_loged:boolean = true;

  //=========== VARIABLES PARA LC ===========
  tiempo_msj:number = 15;
  texto_msj:string = "";

  //=========== MENSAJES DEL SISTEMA ===========
  mensajes: any[] = [];
  state_compontens:any = {
    light: false, 
    alarm : false,
    air: false,
    garage: false,
    temp: 20
  };

  fecha = new Date();
  fecha_act!:Date;
  interval_id: any = 0;
  constructor(
    private toastr: ToastrService,
    private contro_service: ControlService
  ) {
    this.actualizarComponentes();
    this.interval_id = setInterval(() => {
      this.actualizarComponentes();
      
    }, 5000);
    
  }

  actualizarComponentes(){
    this.contro_service.get_state_control().subscribe({
      next: (res) => {
        this.state_compontens = res;
        this.fecha_act = moment().toDate();
        console.log(this.state_compontens);
        if (this.state_compontens.alarm) {
          this.mensajes.push({
            text: "Alarma activada",
            fec: moment().toDate(),
          })
        }
      },
    });
    
    if (this.state_compontens.alarm) {
      this.mensajes.push({
        text: "Alarma activada",
        fec: moment().toDate(),
      })
    }
    this.fecha_act = moment().toDate();   
  }

  loged(event:boolean){
    this.is_loged = event;
  }

  enviar_msg(){
    if (this.texto_msj == "") {
      this.toastr.error('Debe mandar un mensaje!', 'Error!');
      return;
    }

    this.contro_service.msg_lcd(this.texto_msj).subscribe({
      next: res => {}
    });

    const intervalo_activo = setInterval(() => {
      this.tiempo_msj = Number((this.tiempo_msj - 0.1).toFixed(2));
      if (this.tiempo_msj == 0) {
        clearInterval(intervalo_activo);
        this.tiempo_msj = 15;
        this.texto_msj = "";
      }
      
    }, 100);

    

    
  }

  control( type:string, value:any){
    let value_to_send:any = {};
    
    console.log(this.state_compontens);
    
    
    value_to_send[type] = this.state_compontens[type];
    
    this.contro_service.control(value_to_send).subscribe({
      next: res=> console.log(res)
    });

  }

  ngOnDestroy(): void {
    console.log("se limpia el intervalo");
    clearInterval(this.interval_id);
  }

  
}
