/*
 * // C++ Module: xxxx
 * //
 * // Description:
 * //
 * // Author:  2am, (C) 2014
 * //
 * // $Id: pin.h 1118 2017-12-08 02:05:24Z andres $
 * //
 * // Copyright: See COPYING file that comes with this distribution
 * //
 * //
 */

#ifndef GPIO_H3_H
#define GPIO_H3_H

#ifdef __cplusplus
extern "C" {
#endif

int gpio_name2num ( const char * gpio_txt );
char * gpio_num2name ( long n, char * name );
int gpio_test(unsigned int pin);
int gpio_confInput(unsigned int pin);
int gpio_confInputPull(unsigned int pin);
int gpio_confOutput(unsigned int pin) ;
int gpio_confPwmInv(unsigned int pin, int period);
int gpio_confPwm(unsigned int pin, int period) ;
int gpio_confI2C(unsigned int pin);
int gpio_confEint(unsigned int pin) ;
int gpio_confEintPull(unsigned int pin);
int gpio_set ( unsigned int pin, long value );
int gpio_setPWM ( unsigned int pin, unsigned int period ) ;
int gpio_get(unsigned int pin, unsigned long int * value) ;

#ifdef __cplusplus
}
#endif

  //////////////////////////////
 // INICIO CODIGO GENERADO I //
//////////////////////////////

#define PA0 0
#define PA1 1
#define PA2 2
#define PA3 3
#define PA4 4
#define PA5 5
#define PA6 6
#define PA7 7
#define PA8 8
#define PA9 9
#define PA10 10
#define PA11 11
#define PA12 12
#define PA13 13
#define PA14 14
#define PA15 15
#define PA16 16
#define PA17 17
#define PA18 18
#define PA19 19
#define PA20 20
#define PA21 21
#define PC0 22
#define PC1 23
#define PC2 24
#define PC3 25
#define PC4 26
#define PC5 27
#define PC6 28
#define PC7 29
#define PC8 30
#define PC9 31
#define PC10 32
#define PC11 33
#define PC12 34
#define PC13 35
#define PC14 36
#define PC15 37
#define PC16 38
#define PC17 39
#define PC18 40
#define PD0 41
#define PD1 42
#define PD2 43
#define PD3 44
#define PD4 45
#define PD5 46
#define PD6 47
#define PD7 48
#define PD8 49
#define PD9 50
#define PD10 51
#define PD11 52
#define PD12 53
#define PD13 54
#define PD14 55
#define PD15 56
#define PD16 57
#define PD17 58
#define PE0 59
#define PE1 60
#define PE2 61
#define PE3 62
#define PE4 63
#define PE5 64
#define PE6 65
#define PE7 66
#define PE8 67
#define PE9 68
#define PE10 69
#define PE11 70
#define PE12 71
#define PE13 72
#define PE14 73
#define PE15 74
#define PF0 75
#define PF1 76
#define PF2 77
#define PF3 78
#define PF4 79
#define PF5 80
#define PF6 81
#define PG0 82
#define PG1 83
#define PG2 84
#define PG3 85
#define PG4 86
#define PG5 87
#define PG6 88
#define PG7 89
#define PG8 90
#define PG9 91
#define PG10 92
#define PG11 93
#define PG12 94
#define PG13 95
#define PL0 96
#define PL1 97
#define PL2 98
#define PL3 99
#define PL4 100
#define PL5 101
#define PL6 102
#define PL7 103
#define PL8 104
#define PL9 105
#define PL10 106
#define PL11 107
#define PIN_COUNT 108
#define PIN_INVALID -1

  ////////////////////////
 // FIN CODIGO GENERADO//
////////////////////////

#endif



/** I M P O R T A N T E ***
 * 
 * El codigo que esta comentado genera el codigo del final del archivo pata la OrangePi Zero
 * , se podra usar para otros placas en forma similar
 * 
 *     <<<<<<NO BORRAR >>>>>>


//                                                   avance              pins         pins      avance
//                               Primero             xPuerto            reset         xgrupo    xgrupo 
#define PIN_FUNC_OFF(p, i) (       0        +(p%11*       0x24  )+(i%  0x100  )/     8     *    4     )
#define PIN_FUNC_BIT(p, i) (       2        +(p%11*         0   )+(i%   8     )/     1     *    4     )

#define PIN_PULL_OFF(p, i) (      0x1C      +(p%11*       0x24  )+(i%  0x100  )/     16    *    4     )
#define PIN_PULL_BIT(p, i) (       1        +(p%11*         0   )+(i%  16     )/     1     *    2     )

#define PIN_DATA_OFF(p, i) (      0x10      +(p%11*       0x24  )+(i%  0x100  )/     1     *    0     )
#define PIN_DATA_BIT(p, i) (       0        +(p%11*         0   )+(i%  255    )/     1     *    1     )

#define PIN_EINT_OFF(p, i) (       0         +PORT[p][3]         +(i%  0x100  )/     8     *    4     )
#define PIN_EINT_BIT(p, i) (       3        +(p%11*         0   )+(i%  8      )/     1     *    4     )

const int PORT[][4] = { 
//                 PORT  GPIOs, BASE ADDR, IRQOFF
                 { 'A' , 22, 0x01C20800,   0x200 },
                 { 'B' , 0,  0x01C20800,   0 },
                 { 'C' , 19, 0x01C20800,   0 },
                 { 'D' , 18, 0x01C20800,   0 },
                 { 'E' , 16, 0x01C20800,   0 },
                 { 'F' , 7,  0x01C20800,   0 },
                 { 'G' , 14, 0x01C20800,   0x220 },
                 { 'H' , 0,  0,            0 },
                 { 'I' , 0,  0,            0 },
                 { 'J' , 0,  0,            0 },                 
                 { 'K' , 0,  0,            0 },
                 { 'L' , 12, 0x01F02C00,   0 }
};
const int PORTN=12;

int main()
{
 
// Generamos los numeros de PIN
int n= 0;
for (int p = 0 ; p < PORTN; p++) 
   for (int i = 0 ; i < PORT[p][1]; i++) 
     cout << "#define P" <<  (char) PORT[p][0] << i << " " << n++ <<  endl;
cout << "#define PIN_COUNT " <<n<< endl;
cout << endl; 



// Datos de la matriz de PORT
cout << "enum {GPIO_PORT_BANK = 0, GPIO_PORT_N = 1, GPIO_PORT_ACUM = 2, GPIO_PORT_IRQ = 3 }; "        << endl  << endl;

//
// Generamos los datos de los PORTS o bancos
n=0;
cout << "const int PORTS[][4] = { " << endl;
for (int p = 0 ; p < PORTN; p++) {
       cout <<"  { '" << (char ) PORT[p][0] << "', " << PORT[p][1] << ", " << n << ", " << PORT[p][3] << " }" ;
       if (p != PORTN-1 )
         cout << ",";
       cout << endl;
       n+=PORT[p][1];
}
cout << "};"<< endl;
cout << "#define PORTN " << PORTN << endl<< endl;


// Datos de la matriz de dados de PINS
cout << "enum {GPIO_ADDRESS = 0, GPIO_REGISTER = 1, GPIO_REGISTER_BIT = 2, "        << endl <<
        "      GPIO_PULL_REGISTER = 3, GPIO_PULL_REGISTER_BIT = 4,"                  << endl <<
        "      GPIO_DATA_REGISTER = 5, GPIO_DATA_REGISTER_BIT = 6, GPIO_BANK = 7,"  << endl <<
        "      GPIO_IRQ = 8, GPIO_EINT_REGISTER = 9, GPIO_EINT_BIT = 10, GPIO_NUM = 11" << endl <<
        "    };" << endl << endl;

// Generamos la matriz de pins
cout << "unsigned int PINS[][12] = {" << endl;
for (int p = 0 ; p < PORTN; p++) {
   for (int i = 0 ; i < PORT[p][1]; i++) {
     cout << "  { ";
     cout << "0x" << std::hex <<  PORT[p][2] << ", ";
     cout << "0x" << std::hex <<  std::setfill('0') << std::setw(2) << PIN_FUNC_OFF(p, i) 
          << ", " << std::dec <<  std::setfill(' ') << std::setw(2) << PIN_FUNC_BIT(p, i) << ", ";
     cout << "0x" << std::hex <<  std::setfill('0') << std::setw(2) << PIN_PULL_OFF(p, i)
          << ", " << std::dec <<  std::setfill(' ') << std::setw(2) << PIN_PULL_BIT(p, i) << ", ";
     cout << "0x" << std::hex <<  std::setfill('0') << std::setw(2) << PIN_DATA_OFF(p, i) 
          << ", " << std::dec <<  std::setfill(' ') << std::setw(2) << PIN_DATA_BIT(p, i) << ", ";
     cout << "'"  << (char) PORT[p][0] << "' , 0 ,";
     cout << "0x"  <<std::hex <<  std::setfill('0') << std::setw(3) << PIN_EINT_OFF(p, i) << ", " 
                  << std::dec <<  std::setfill(' ') << std::setw(2) << PIN_EINT_BIT(p, i) << ", ";
     cout << std::setfill(' ') << std::setw(2) << i;
     cout << "  } ";
     if ( i !=  PORT[p][1] -1 || p != PORTN-1 )
         cout << ",";
     cout << " // P" << (char) PORT[p][0] << i ;
     cout << endl;
   }
 }
cout << "};" << endl; 

    
}

*/
