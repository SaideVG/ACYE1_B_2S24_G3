import { Component, ElementRef, inject, ViewChild, OnDestroy } from '@angular/core';

import moment from 'moment';
//import 'moment/locale/es';
import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexTitleSubtitle,
  ApexDataLabels,
  ApexStroke,
  ApexLegend,
  ApexMarkers,
  ApexTooltip,
  ApexGrid,
  ApexPlotOptions,
  ApexFill,
  ApexYAxis,
  ApexNonAxisChartSeries
} from "ng-apexcharts";
import { data_acciones, data_temp, dataService } from '../../services/data.service';
import { NgbCalendar, NgbDate, NgbDateStruct } from '@ng-bootstrap/ng-bootstrap';

export type ChartOptions = {
  series: ApexAxisChartSeries;
  series_2: ApexNonAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  yaxis: ApexYAxis;
  title: ApexTitleSubtitle;
  dataLabels: ApexDataLabels;
  stroke: ApexStroke;
  legend: ApexLegend;
  markers: ApexMarkers;
  tooltip: ApexTooltip;
  grid:  ApexGrid;
  plotOptions:  ApexPlotOptions;
  fill: ApexFill;
  labels?: string[];
};


@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnDestroy {
  
  public Line_chartOptions!: ChartOptions;
  public ingresos_chartOptions!: ChartOptions;
  public bar_chartOptions!: ChartOptions;
  public range_bar_chartOptions!: ChartOptions;

  data_completa:data_acciones[] = [];

  model!: NgbDateStruct;
  model2!: NgbDateStruct;
	date!: { year: number; month: number };
  
  id_interval!: any;
  ngOnDestroy(): void {
    console.log("se limpio el intervalo");
    clearInterval(this.id_interval);
  }
 
  ngOnInit(): void {
    this.getDataTemp();
    this.getAllData();
    console.log("object");
  }

  constructor(private dataService: dataService) {
   
    this.bar_Chart();
    this.pie_Chart();
    this.ingresos_casa();
    this.getDataSwitchAction("garage");
    
    this.id_interval = setInterval(() => {

      this.recargarQuerys();
      
    }, 15000);
  }

  recargarQuerys(){
    let query = {};
    if (this.fromDateQuery) {
      query = {
        Fecha_registro: { $gte: this.fromDateQuery, $lte: this.toDateQuery }
      };
    }

    this.getAllData().then((data) => {
      const data_agrupada = this.agruparPorAccion(data);
      this.range_bar_chartOptions.series_2 = data_agrupada.map((element:any) => element.total + 10);
    })

    this.getDataTemp();
    //console.log("");
    this.getDataSwitchAction("garage").then((data) => {
      this.bar_chartOptions.series = [{data:data}];
    })

    this.getDataSwitchAction("Patron").then((data) => {
      console.log(this.ingresos_chartOptions.series[0].data);
      this.ingresos_chartOptions.series = [{data:data}];
      console.log(this.ingresos_chartOptions.series[0].data);
    })
  }

  getDataTemp(){
    let query = {};
    if (this.fromDateQuery) {
      query = {
        Fecha_registro: { $gte: this.fromDateQuery, $lte: this.toDateQuery }
      };
    }
    this.dataService.get_data("registros_temp", query, {Fecha_registro: 1} ).subscribe({
      next : res => {
        // this.data_completa = res.documents;
        const data_temp:data_temp[] = res.documents;
        const data_chart_format = [];
        for (const element of data_temp) {
          
          data_chart_format.push({
            x: moment(element.Fecha_registro),
            y: element.temp,
            type: 'Temperatura'
          });
          data_chart_format.push({
            x: moment(element.Fecha_registro),
            y: element.humedad,
            type: 'Humedad'
          });
        }
        if (!this.Line_chartOptions) {
          this.Line_Chart(data_chart_format);  
        }else{
          const series = [{
            name: "Temperatura",
            data: data_chart_format.filter((element, index) => element.type == 'Temperatura')
          },
          {
            name: "Humedad",
            data: data_chart_format.filter((element, index) => element.type == 'Humedad')
          }
        ]

          this.Line_chartOptions.series = series;
        }
        
      }
    });
  }

  getAllData():Promise<any>{
    return new Promise<any>((resolve, reject) => {
      let query = {};
      if (this.fromDateQuery) {
        query = {
          Fecha_registro: { $gte: this.fromDateQuery, $lte: this.toDateQuery }
        };
      }
      this.dataService.get_data("registros", query, { Fecha_registro: 1 } ).subscribe({
        next : res => {
          this.data_completa = res.documents;
          for (const element of this.data_completa) {
            element.fecha_texto = moment(element.Fecha_registro).add(6, 'hours').format('DD MMMM YYYY, hh:mm:ss a');
          }
          //console.log(this.data_completa);
          resolve(this.data_completa);
          
        },
        error: (err) => {
          reject(err)
        }
      })  
    });
  }

  getDataSwitchAction(accion:string): Promise<any>{
    return new Promise<any>((resolve, reject) => {
      let query:any = {};
      if (this.fromDateQuery) {
        query = {
          Fecha_registro: { $gte: this.fromDateQuery, $lte: this.toDateQuery }
        };
      }
      query.accion = accion;
      console.log(query);
      this.dataService.get_data("registros", query ).subscribe({
        next : res => {
          const data_regs:data_acciones[] = res.documents;
          for (const element of data_regs) {
            element.fecha_texto = moment(element.Fecha_registro).add(6, 'hours').format('DD MMMM YYYY, hh:mm:ss a');
          }
          //console.log(data_regs);
          resolve(this.agruparPorHora(data_regs));
        },
        error: (err) => {
          reject(err);
        }
      });
    });
  }

  Line_Chart(data_chart_format:any[]) {
    this.Line_chartOptions =  {
      series: [{
        name: "Temperatura",
        data: data_chart_format.filter((element, index) => element.type == 'Temperatura')
      },
      {
        name: "Humedad",
        data: data_chart_format.filter((element, index) => element.type == 'Humedad')
      }
    ],
    chart: {
      height: 350,
      type: 'line',
      zoom: {
        enabled: false
      },
      toolbar: {
        show: false
      }, 
      foreColor: '#ffffff'
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      width: [5, 7, 5],
      curve: 'straight'
    },
    title: {
      text: 'Estadisticas de Temperatura & Humedad',
      align: 'left'
    },
    legend: {
      tooltipHoverFormatter: function(val:any, opts:any) {
        if (val == "Temperatura") {
          return val + ' - <strong>' + opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] + 'º </strong>'  
        }
        return val + ' - <strong>' + opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] + '% </strong>'
      },
      position: 'top',
    },
    markers: {
      size: 0,
      hover: {
        sizeOffset: 6
      }
    },
    xaxis: {
      type: 'datetime',
      tooltip: { enabled: false }
    },
    tooltip: {
      y: [
        {
          title: {
            formatter: function (val:any) {
              return val + " (ºC)"
            }
          }
        },
        {
          title: {
            formatter: function (val:any) {
              return val + " (%)"
            }
          }
        }
      ],
      theme: 'dark',
    },
    grid: {
      borderColor: '#f1f1f1',
    },
    plotOptions: {},
    fill: {},
    yaxis: {},
    series_2: []
    };
    
  }

  bar_Chart() {
    this.getDataSwitchAction("garage").then((data) => {
      this.bar_chartOptions =  {
        series: [
          {
            data: data
          }
      ],
      chart: {
        height: 350,
        type: 'bar',
        zoom: {
          enabled: false
        },
        toolbar: {
          show: false
        }, 
        foreColor: '#ffffff'
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        width: [5, 7, 5],
        curve: 'straight'
      },
      title: {
        text: 'Funcionamiento del garage por hora',
        align: 'left'
      },
      legend: {
        tooltipHoverFormatter: function(val:any, opts:any) {
          
          return '<strong>' + opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] + '</strong>'
        },
        position: 'top',
      },
      markers: {
        size: 0,
        hover: {
          sizeOffset: 6
        }
      },
      xaxis: {
      },
      tooltip: {
        y: [
          {
            title: {
              formatter: function (val:any) {
                return ""
              }
            }
          }
        ],
        theme: 'dark',
      },
      grid: {
        borderColor: '#f1f1f1',
      },
      plotOptions: {},
      fill: {},
      yaxis: {},
      series_2: []
      };
    })
  }

  pie_Chart() {
    this.getAllData().then((data) => {
      const data_agrupada = this.agruparPorAccion(data);
      this.range_bar_chartOptions = {
        title: {
        text: 'Uso de elementos en la casa',
        },
        dataLabels: {
          
        },
        grid: {},
        markers: {},
        tooltip: {
          theme: 'dark',
        },
        series: [],
        chart: {
          // height: 600,
          type: 'donut',
          zoom: {
            enabled: false
          },
          toolbar: {
            show: false
          }, 
          foreColor: '#ffffff'
        },
        plotOptions: {},
        xaxis: {},
        yaxis: {},
        stroke: {
          width: 1
        },
        fill: {
          type: 'solid',
          opacity: 1
        },
        legend: {
          position: 'top',
          horizontalAlign: 'left'
        },
        series_2: data_agrupada.map((element:any) => element.total),
        labels: data_agrupada.map((element:any) => element.accion),
      };

      

      
    })

    
  }

  ingresos_casa() {
    this.getDataSwitchAction("Patron").then((data) => {
      this.ingresos_chartOptions =  {
        series: [
          {
            data: data
          }
      ],
      chart: {
        height: 350,
        type: 'bar',
        zoom: {
          enabled: false
        },
        toolbar: {
          show: false
        }, 
        foreColor: '#ffffff'
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        width: [5, 7, 5],
        curve: 'straight'
      },
      title: {
        text: 'Ingresos a la casa por hora',
        align: 'left'
      },
      legend: {
        tooltipHoverFormatter: function(val:any, opts:any) {
          
          return '<strong>' + opts.w.globals.series[opts.seriesIndex][opts.dataPointIndex] + '</strong>'
        },
        position: 'top',
      },
      markers: {
        size: 0,
        hover: {
          sizeOffset: 6
        }
      },
      xaxis: {},
      tooltip: {
        y: [
          {
            title: {
              formatter: function (val:any) {
                return ""
              }
            }
          }
        ],
        theme: 'dark',
      },
      grid: {
        borderColor: '#f1f1f1',
      },
      plotOptions: {},
      fill: {},
      yaxis: {},
      series_2: []
      };
    });
  }

  agruparPorHora(data:data_acciones[]){

    //console.log(data);
    const data_agrupada = Array.from({ length: 24 }, (_, index) => {
      return {
        x: index, 
        y:0
      }
    });

    
    for (const element of data) {
      const hora = moment(element.Fecha_registro).hour()+6
      data_agrupada[hora].y++;
    }
      
    //console.log(data_agrupada);
    return data_agrupada;
  }

  agruparPorAccion(data:data_acciones[]){
    const data_agrupada:any = [];
    for (const element of data) {
      const encontrado = data_agrupada.find((element_agrupado:any) => element_agrupado.accion == element.accion); 
      if (encontrado) {
        encontrado.total++;
      }else{
        data_agrupada.push({
          accion: element.accion,
          total: 1
        });
      }
    }
    //console.log(data_agrupada.map((element:any) => element.accion));
    //console.log(data_agrupada.map((element:any) => element.total));
    return data_agrupada
  
  }
  calendar = inject(NgbCalendar);
  
	fromDate: NgbDate = this.calendar.getToday();
	toDate: NgbDate = this.calendar.getNext(this.fromDate, 'd', 10);
  fromDateQuery!: string;
  toDateQuery!: string;

  onDateSelection(type:string, date: NgbDate) {
    if (type == 'from') {
      this.fromDate = date;  
    }
    if (type == 'to') {
      this.toDate = date;  
    }

    if (this.fromDate.day > this.toDate.day) {
      this.toDate = this.fromDate;
    }

    this.fromDateQuery = this.formatFecha(this.fromDate, false);
    this.toDateQuery = this.formatFecha(this.toDate, true);
    
    console.log(this.fromDateQuery);
    console.log(this.toDateQuery);
    this.recargarQuerys();
	}

  formatFecha(objFecha:any, final:boolean) {
    const { day, month, year } = objFecha;

    // Crear el objeto de fecha ajustando mes (JavaScript maneja los meses en base 0)
    const fecha = new Date(year, month - 1, day);

    // Establecer la hora al inicio del día
    if (final) {
      fecha.setHours(23, 59, 59, 999);
      return moment(fecha).add(-6, 'hours').toDate().toISOString();
    }else{
      fecha.setHours(0, 0, 0, 0);
      return moment(fecha).add(-6, 'hours').toDate().toISOString();
    }
    

  }
}
