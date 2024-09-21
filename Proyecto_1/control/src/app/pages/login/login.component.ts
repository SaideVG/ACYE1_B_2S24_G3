import { Component, EventEmitter, Output} from '@angular/core';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {

  constructor(private toast: ToastrService) {
    
  }
  @Output() loged = new EventEmitter<boolean>();
  txt_usuario:string = "";
  txt_password:string = "";
  logear(){
    //! CONSUMIR API DE LOGIN
    console.log(this.txt_usuario);
    console.log(this.txt_password);
    if (this.txt_usuario == "3_B_proy1" && this.txt_password == "Grupo123*") {
      this.loged.emit(true);
      this.toast.success('Bienvenido :D', 'Exito');
      return;
    }else{
      this.toast.error('Usuario o contraseña incorrecta', 'Error');
    }
    this.loged.emit(false);
  }

}
