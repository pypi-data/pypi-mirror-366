#include "gpio_h3.h"
#include <string.h>
#include <stdio.h>
/*
 * En el caso de no compilar para un driver necesitamos mapear a la memoria
 */

///////////////////////////////
// INICIO CODIGO GENERADO II //
///////////////////////////////

enum
{
    GPIO_ADDRESS = 0,
    GPIO_REGISTER = 1,
    GPIO_REGISTER_BIT = 2,
    GPIO_PULL_REGISTER = 3,
    GPIO_PULL_REGISTER_BIT = 4,
    GPIO_DATA_REGISTER = 5,
    GPIO_DATA_REGISTER_BIT = 6,
    GPIO_BANK = 7,
    GPIO_IRQ = 8,
    GPIO_EINT_REGISTER = 9,
    GPIO_EINT_BIT = 10,
    GPIO_NUM = 11
};

// using namespace std;
unsigned int GPIO_PINS[][12] = {
    {0x1c20800, 0x00, 2, 0x1c, 1, 0x10, 0, 'A', 0, 0x200, 3, 0},      // PA0
    {0x1c20800, 0x00, 6, 0x1c, 3, 0x10, 1, 'A', 0, 0x200, 7, 1},      // PA1
    {0x1c20800, 0x00, 10, 0x1c, 5, 0x10, 2, 'A', 0, 0x200, 11, 2},    // PA2
    {0x1c20800, 0x00, 14, 0x1c, 7, 0x10, 3, 'A', 0, 0x200, 15, 3},    // PA3
    {0x1c20800, 0x00, 18, 0x1c, 9, 0x10, 4, 'A', 0, 0x200, 19, 4},    // PA4
    {0x1c20800, 0x00, 22, 0x1c, 11, 0x10, 5, 'A', 0, 0x200, 23, 5},   // PA5
    {0x1c20800, 0x00, 26, 0x1c, 13, 0x10, 6, 'A', 0, 0x200, 27, 6},   // PA6
    {0x1c20800, 0x00, 30, 0x1c, 15, 0x10, 7, 'A', 0, 0x200, 31, 7},   // PA7
    {0x1c20800, 0x04, 2, 0x1c, 17, 0x10, 8, 'A', 0, 0x204, 3, 8},     // PA8
    {0x1c20800, 0x04, 6, 0x1c, 19, 0x10, 9, 'A', 0, 0x204, 7, 9},     // PA9
    {0x1c20800, 0x04, 10, 0x1c, 21, 0x10, 10, 'A', 0, 0x204, 11, 10}, // PA10
    {0x1c20800, 0x04, 14, 0x1c, 23, 0x10, 11, 'A', 0, 0x204, 15, 11}, // PA11
    {0x1c20800, 0x04, 18, 0x1c, 25, 0x10, 12, 'A', 0, 0x204, 19, 12}, // PA12
    {0x1c20800, 0x04, 22, 0x1c, 27, 0x10, 13, 'A', 0, 0x204, 23, 13}, // PA13
    {0x1c20800, 0x04, 26, 0x1c, 29, 0x10, 14, 'A', 0, 0x204, 27, 14}, // PA14
    {0x1c20800, 0x04, 30, 0x1c, 31, 0x10, 15, 'A', 0, 0x204, 31, 15}, // PA15
    {0x1c20800, 0x08, 2, 0x20, 1, 0x10, 16, 'A', 0, 0x208, 3, 16},    // PA16
    {0x1c20800, 0x08, 6, 0x20, 3, 0x10, 17, 'A', 0, 0x208, 7, 17},    // PA17
    {0x1c20800, 0x08, 10, 0x20, 5, 0x10, 18, 'A', 0, 0x208, 11, 18},  // PA18
    {0x1c20800, 0x08, 14, 0x20, 7, 0x10, 19, 'A', 0, 0x208, 15, 19},  // PA19
    {0x1c20800, 0x08, 18, 0x20, 9, 0x10, 20, 'A', 0, 0x208, 19, 20},  // PA20
    {0x1c20800, 0x08, 22, 0x20, 11, 0x10, 21, 'A', 0, 0x208, 23, 21}, // PA21
    {0x1c20800, 0x48, 2, 0x64, 1, 0x58, 0, 'C', 0, 0x000, 3, 0},      // PC0
    {0x1c20800, 0x48, 6, 0x64, 3, 0x58, 1, 'C', 0, 0x000, 7, 1},      // PC1
    {0x1c20800, 0x48, 10, 0x64, 5, 0x58, 2, 'C', 0, 0x000, 11, 2},    // PC2
    {0x1c20800, 0x48, 14, 0x64, 7, 0x58, 3, 'C', 0, 0x000, 15, 3},    // PC3
    {0x1c20800, 0x48, 18, 0x64, 9, 0x58, 4, 'C', 0, 0x000, 19, 4},    // PC4
    {0x1c20800, 0x48, 22, 0x64, 11, 0x58, 5, 'C', 0, 0x000, 23, 5},   // PC5
    {0x1c20800, 0x48, 26, 0x64, 13, 0x58, 6, 'C', 0, 0x000, 27, 6},   // PC6
    {0x1c20800, 0x48, 30, 0x64, 15, 0x58, 7, 'C', 0, 0x000, 31, 7},   // PC7
    {0x1c20800, 0x4c, 2, 0x64, 17, 0x58, 8, 'C', 0, 0x004, 3, 8},     // PC8
    {0x1c20800, 0x4c, 6, 0x64, 19, 0x58, 9, 'C', 0, 0x004, 7, 9},     // PC9
    {0x1c20800, 0x4c, 10, 0x64, 21, 0x58, 10, 'C', 0, 0x004, 11, 10}, // PC10
    {0x1c20800, 0x4c, 14, 0x64, 23, 0x58, 11, 'C', 0, 0x004, 15, 11}, // PC11
    {0x1c20800, 0x4c, 18, 0x64, 25, 0x58, 12, 'C', 0, 0x004, 19, 12}, // PC12
    {0x1c20800, 0x4c, 22, 0x64, 27, 0x58, 13, 'C', 0, 0x004, 23, 13}, // PC13
    {0x1c20800, 0x4c, 26, 0x64, 29, 0x58, 14, 'C', 0, 0x004, 27, 14}, // PC14
    {0x1c20800, 0x4c, 30, 0x64, 31, 0x58, 15, 'C', 0, 0x004, 31, 15}, // PC15
    {0x1c20800, 0x50, 2, 0x68, 1, 0x58, 16, 'C', 0, 0x008, 3, 16},    // PC16
    {0x1c20800, 0x50, 6, 0x68, 3, 0x58, 17, 'C', 0, 0x008, 7, 17},    // PC17
    {0x1c20800, 0x50, 10, 0x68, 5, 0x58, 18, 'C', 0, 0x008, 11, 18},  // PC18
    {0x1c20800, 0x6c, 2, 0x88, 1, 0x7c, 0, 'D', 0, 0x000, 3, 0},      // PD0
    {0x1c20800, 0x6c, 6, 0x88, 3, 0x7c, 1, 'D', 0, 0x000, 7, 1},      // PD1
    {0x1c20800, 0x6c, 10, 0x88, 5, 0x7c, 2, 'D', 0, 0x000, 11, 2},    // PD2
    {0x1c20800, 0x6c, 14, 0x88, 7, 0x7c, 3, 'D', 0, 0x000, 15, 3},    // PD3
    {0x1c20800, 0x6c, 18, 0x88, 9, 0x7c, 4, 'D', 0, 0x000, 19, 4},    // PD4
    {0x1c20800, 0x6c, 22, 0x88, 11, 0x7c, 5, 'D', 0, 0x000, 23, 5},   // PD5
    {0x1c20800, 0x6c, 26, 0x88, 13, 0x7c, 6, 'D', 0, 0x000, 27, 6},   // PD6
    {0x1c20800, 0x6c, 30, 0x88, 15, 0x7c, 7, 'D', 0, 0x000, 31, 7},   // PD7
    {0x1c20800, 0x70, 2, 0x88, 17, 0x7c, 8, 'D', 0, 0x004, 3, 8},     // PD8
    {0x1c20800, 0x70, 6, 0x88, 19, 0x7c, 9, 'D', 0, 0x004, 7, 9},     // PD9
    {0x1c20800, 0x70, 10, 0x88, 21, 0x7c, 10, 'D', 0, 0x004, 11, 10}, // PD10
    {0x1c20800, 0x70, 14, 0x88, 23, 0x7c, 11, 'D', 0, 0x004, 15, 11}, // PD11
    {0x1c20800, 0x70, 18, 0x88, 25, 0x7c, 12, 'D', 0, 0x004, 19, 12}, // PD12
    {0x1c20800, 0x70, 22, 0x88, 27, 0x7c, 13, 'D', 0, 0x004, 23, 13}, // PD13
    {0x1c20800, 0x70, 26, 0x88, 29, 0x7c, 14, 'D', 0, 0x004, 27, 14}, // PD14
    {0x1c20800, 0x70, 30, 0x88, 31, 0x7c, 15, 'D', 0, 0x004, 31, 15}, // PD15
    {0x1c20800, 0x74, 2, 0x8c, 1, 0x7c, 16, 'D', 0, 0x008, 3, 16},    // PD16
    {0x1c20800, 0x74, 6, 0x8c, 3, 0x7c, 17, 'D', 0, 0x008, 7, 17},    // PD17
    {0x1c20800, 0x90, 2, 0xac, 1, 0xa0, 0, 'E', 0, 0x000, 3, 0},      // PE0
    {0x1c20800, 0x90, 6, 0xac, 3, 0xa0, 1, 'E', 0, 0x000, 7, 1},      // PE1
    {0x1c20800, 0x90, 10, 0xac, 5, 0xa0, 2, 'E', 0, 0x000, 11, 2},    // PE2
    {0x1c20800, 0x90, 14, 0xac, 7, 0xa0, 3, 'E', 0, 0x000, 15, 3},    // PE3
    {0x1c20800, 0x90, 18, 0xac, 9, 0xa0, 4, 'E', 0, 0x000, 19, 4},    // PE4
    {0x1c20800, 0x90, 22, 0xac, 11, 0xa0, 5, 'E', 0, 0x000, 23, 5},   // PE5
    {0x1c20800, 0x90, 26, 0xac, 13, 0xa0, 6, 'E', 0, 0x000, 27, 6},   // PE6
    {0x1c20800, 0x90, 30, 0xac, 15, 0xa0, 7, 'E', 0, 0x000, 31, 7},   // PE7
    {0x1c20800, 0x94, 2, 0xac, 17, 0xa0, 8, 'E', 0, 0x004, 3, 8},     // PE8
    {0x1c20800, 0x94, 6, 0xac, 19, 0xa0, 9, 'E', 0, 0x004, 7, 9},     // PE9
    {0x1c20800, 0x94, 10, 0xac, 21, 0xa0, 10, 'E', 0, 0x004, 11, 10}, // PE10
    {0x1c20800, 0x94, 14, 0xac, 23, 0xa0, 11, 'E', 0, 0x004, 15, 11}, // PE11
    {0x1c20800, 0x94, 18, 0xac, 25, 0xa0, 12, 'E', 0, 0x004, 19, 12}, // PE12
    {0x1c20800, 0x94, 22, 0xac, 27, 0xa0, 13, 'E', 0, 0x004, 23, 13}, // PE13
    {0x1c20800, 0x94, 26, 0xac, 29, 0xa0, 14, 'E', 0, 0x004, 27, 14}, // PE14
    {0x1c20800, 0x94, 30, 0xac, 31, 0xa0, 15, 'E', 0, 0x004, 31, 15}, // PE15
    {0x1c20800, 0xb4, 2, 0xd0, 1, 0xc4, 0, 'F', 0, 0x000, 3, 0},      // PF0
    {0x1c20800, 0xb4, 6, 0xd0, 3, 0xc4, 1, 'F', 0, 0x000, 7, 1},      // PF1
    {0x1c20800, 0xb4, 10, 0xd0, 5, 0xc4, 2, 'F', 0, 0x000, 11, 2},    // PF2
    {0x1c20800, 0xb4, 14, 0xd0, 7, 0xc4, 3, 'F', 0, 0x000, 15, 3},    // PF3
    {0x1c20800, 0xb4, 18, 0xd0, 9, 0xc4, 4, 'F', 0, 0x000, 19, 4},    // PF4
    {0x1c20800, 0xb4, 22, 0xd0, 11, 0xc4, 5, 'F', 0, 0x000, 23, 5},   // PF5
    {0x1c20800, 0xb4, 26, 0xd0, 13, 0xc4, 6, 'F', 0, 0x000, 27, 6},   // PF6
    {0x1c20800, 0xd8, 2, 0xf4, 1, 0xe8, 0, 'G', 0, 0x220, 3, 0},      // PG0
    {0x1c20800, 0xd8, 6, 0xf4, 3, 0xe8, 1, 'G', 0, 0x220, 7, 1},      // PG1
    {0x1c20800, 0xd8, 10, 0xf4, 5, 0xe8, 2, 'G', 0, 0x220, 11, 2},    // PG2
    {0x1c20800, 0xd8, 14, 0xf4, 7, 0xe8, 3, 'G', 0, 0x220, 15, 3},    // PG3
    {0x1c20800, 0xd8, 18, 0xf4, 9, 0xe8, 4, 'G', 0, 0x220, 19, 4},    // PG4
    {0x1c20800, 0xd8, 22, 0xf4, 11, 0xe8, 5, 'G', 0, 0x220, 23, 5},   // PG5
    {0x1c20800, 0xd8, 26, 0xf4, 13, 0xe8, 6, 'G', 0, 0x220, 27, 6},   // PG6
    {0x1c20800, 0xd8, 30, 0xf4, 15, 0xe8, 7, 'G', 0, 0x220, 31, 7},   // PG7
    {0x1c20800, 0xdc, 2, 0xf4, 17, 0xe8, 8, 'G', 0, 0x224, 3, 8},     // PG8
    {0x1c20800, 0xdc, 6, 0xf4, 19, 0xe8, 9, 'G', 0, 0x224, 7, 9},     // PG9
    {0x1c20800, 0xdc, 10, 0xf4, 21, 0xe8, 10, 'G', 0, 0x224, 11, 10}, // PG10
    {0x1c20800, 0xdc, 14, 0xf4, 23, 0xe8, 11, 'G', 0, 0x224, 15, 11}, // PG11
    {0x1c20800, 0xdc, 18, 0xf4, 25, 0xe8, 12, 'G', 0, 0x224, 19, 12}, // PG12
    {0x1c20800, 0xdc, 22, 0xf4, 27, 0xe8, 13, 'G', 0, 0x224, 23, 13}, // PG13
    {0x1f02c00, 0x00, 2, 0x1c, 1, 0x10, 0, 'L', 0, 0x000, 3, 0},      // PL0
    {0x1f02c00, 0x00, 6, 0x1c, 3, 0x10, 1, 'L', 0, 0x000, 7, 1},      // PL1
    {0x1f02c00, 0x00, 10, 0x1c, 5, 0x10, 2, 'L', 0, 0x000, 11, 2},    // PL2
    {0x1f02c00, 0x00, 14, 0x1c, 7, 0x10, 3, 'L', 0, 0x000, 15, 3},    // PL3
    {0x1f02c00, 0x00, 18, 0x1c, 9, 0x10, 4, 'L', 0, 0x000, 19, 4},    // PL4
    {0x1f02c00, 0x00, 22, 0x1c, 11, 0x10, 5, 'L', 0, 0x000, 23, 5},   // PL5
    {0x1f02c00, 0x00, 26, 0x1c, 13, 0x10, 6, 'L', 0, 0x000, 27, 6},   // PL6
    {0x1f02c00, 0x00, 30, 0x1c, 15, 0x10, 7, 'L', 0, 0x000, 31, 7},   // PL7
    {0x1f02c00, 0x04, 2, 0x1c, 17, 0x10, 8, 'L', 0, 0x004, 3, 8},     // PL8
    {0x1f02c00, 0x04, 6, 0x1c, 19, 0x10, 9, 'L', 0, 0x004, 7, 9},     // PL9
    {0x1f02c00, 0x04, 10, 0x1c, 21, 0x10, 10, 'L', 0, 0x004, 11, 10}, // PL10
    {0x1f02c00, 0x04, 14, 0x1c, 23, 0x10, 11, 'L', 0, 0x004, 15, 11}  // PL11
};
enum
{
    GPIO_PORT_BANK = 0,
    GPIO_PORT_N = 1,
    GPIO_PORT_ACUM = 2,
    GPIO_PORT_IRQ = 3
};

const int PORTS[][4] = {
    {'A', 22, 0, 512},
    {'B', 0, 22, 0},
    {'C', 19, 22, 0},
    {'D', 18, 41, 0},
    {'E', 16, 59, 0},
    {'F', 7, 75, 0},
    {'G', 14, 82, 544},
    {'H', 0, 96, 0},
    {'I', 0, 96, 0},
    {'J', 0, 96, 0},
    {'K', 0, 96, 0},
    {'L', 12, 96, 0}};
#define PORTN 12

////////////////////////
// FIN CODIGO GENERADO//
////////////////////////

const unsigned int GPIO_LEN = 3;
const unsigned int GPIO_INPUT = 0;
const unsigned int GPIO_I2C = 2;
const unsigned int GPIO_OUTPUT = 1;
const unsigned int GPIO_EINT = 6;

const unsigned int GPIO_EINT_LEN = 4;
const unsigned int GPIO_EINT_POS_EDGE = 0;
const unsigned int GPIO_EINT_NEG_EDGE = 1;
const unsigned int GPIO_EINT_DOBLE_EDGE = 4;
const unsigned int GPIO_EINT_HIGH = 2;
const unsigned int GPIO_EINT_LOW = 3;

const unsigned int GPIO_PULL_LEN = 2;
const unsigned int GPIO_PULL_DISABLE = 0;
const unsigned int GPIO_PULL_PULLUP = 1;
const unsigned int GPIO_PULL_PULLDOWN = 2;

const int PWM_PIN = PA5;
const unsigned int PWM_PIN_CONFIG = 0b011;
const unsigned int PWM_BASE_ADDRESS = 0x01C21400;
const unsigned int PWM_CTRL_REGISTER = 0x00;
const unsigned int PWM_PERI_REGISTER = 0x04;

///////////////////////////////////
#ifndef DRIVER_DESC /////////////  USER MEM  //////////
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>

int gpio_openMem()
{
    return open("/dev/mem", O_RDWR);
}

void gpio_closeMem(int fd)
{
    close(fd);
}

int setBit(int fd, unsigned int base_address, unsigned int register_offset, unsigned int mask_pos, unsigned int mask_len, unsigned long int val)
{
    unsigned int *pc;
    char *ptr;
    unsigned int addr_start, addr_offset, pageSize, pageMask, mask, data;

    pageSize = sysconf(_SC_PAGESIZE);
    pageMask = (~(pageSize - 1));
    addr_start = base_address & pageMask;
    addr_offset = base_address & ~pageMask;

    pc = (unsigned int *)mmap(0, pageSize * 2, PROT_READ | PROT_WRITE, MAP_SHARED, fd, addr_start);

    if (pc == MAP_FAILED)
    {
        return (-1);
    }

    ptr = (char *)pc + addr_offset;
    data = *(unsigned int *)(ptr + register_offset); // Obtenemos el valor actual
    // DBG ( " data " << BITS ( data ) << " bit_pos:" << mask_pos << endl );

    mask = (~((~0x00) << mask_len)) << (mask_pos - mask_len + 1); // mascara de los bits a escribir
    // DBG ( " mask " << BITS ( mask ) << " bit_len:" << mask_len << endl );
    val = (val << (mask_pos - mask_len + 1)) & mask;
    // DBG ( " val  " << BITS ( val ) << " " << val << endl );
    data = (data & ~mask) | val;
    // DBG ( " data " << BITS ( data ) << " final" << endl );

    *(unsigned int *)(ptr + register_offset) = data; // escribimos el nuevo valor
    munmap(pc, pageSize * 2);

    // DBG ( "End" << endl );

    return 0;
}

int getBit(int fd, unsigned int base_address, unsigned int register_offset, unsigned int mask_pos, unsigned int mask_len, unsigned long int *pval)
{
    unsigned int *pc;
    char *ptr;
    unsigned int addr_start, addr_offset, pageSize, pageMask, mask, data;
    // DBG ( "start" << endl );

    pageSize = sysconf(_SC_PAGESIZE);
    pageMask = (~(pageSize - 1));
    addr_start = base_address & pageMask;
    addr_offset = base_address & ~pageMask;

    // DBG ( "mapping" << endl );
    pc = (unsigned int *)mmap(0, pageSize * 2, PROT_READ | PROT_WRITE, MAP_SHARED, fd, addr_start);
    if (pc == MAP_FAILED)
    {
        return (-1);
    }

    // DBG ( "set pointer" << endl );
    ptr = (char *)pc + addr_offset;

    data = *(unsigned int *)(ptr + register_offset); // Obtenemos el valor actual
    // DBG ( "data " << BITS ( data ) << " original" << endl );

    mask = (~((~0x00) << mask_len)) << (mask_pos - mask_len + 1); // mascara de los bits a escribir
    // DBG ( "mask " << BITS ( mask ) << endl );

    data = (data & mask);
    // DBG ( "data " << BITS ( data ) << endl );

    *pval = data >> (mask_pos - mask_len + 1);
    // DBG ( "val  " << BITS ( val ) << endl );

    munmap(pc, pageSize * 2);

    return 0;
}

//////////////////////////////////////
#else /////////////  KERNEL MEM  ///////////
int gpio_openMem(void)
{
    return 0;
}
void gpio_closeMem(int m)
{
    ;
}

int setBit(int fd, unsigned int base_address, unsigned int register_offset, unsigned int mask_pos, unsigned int mask_len, unsigned long int val)
{
    void __iomem *ptr;
    unsigned int data, mask;

    ptr = ioremap(base_address + register_offset, 4);

    data = readl(ptr); // Obtenemos el valor actual

    mask = (~((~0x00) << mask_len)) << (mask_pos - mask_len + 1); // mascara de los bits a escribir
    // DBG ( " mask " << BITS ( mask ) << " bit_len:" << mask_len << endl );
    val = (val << (mask_pos - mask_len + 1)) & mask;
    // DBG ( " val  " << BITS ( val ) << " " << val << endl );
    data = (data & ~mask) | val;
    // DBG ( " data " << BITS ( data ) << " final" << endl );

    writel(data, ptr); // escribimos el nuevo valor
    iounmap(ptr);

    // DBG ( "End" << endl );

    return 0;
}

int getBit(int fd, unsigned int base_address, unsigned int register_offset, unsigned int mask_pos, unsigned int mask_len, unsigned long int *pval)
{

    void __iomem *ptr;
    unsigned int data, mask;

    ptr = ioremap(base_address + register_offset, 4);

    data = readl(ptr); // Obtenemos el valor actual

    mask = (~((~0x00) << mask_len)) << (mask_pos - mask_len + 1); // mascara de los bits a escribir
    // DBG ( "mask " << BITS ( mask ) << endl );

    data = (data & mask);
    // DBG ( "data " << BITS ( data ) << endl );

    *pval = data >> (mask_pos - mask_len + 1);
    // DBG ( "val  " << BITS ( val ) << endl );

    iounmap(ptr);
    return 0;
}

#endif

// gpio_txt form PA22, PC6, etc
int gpio_name2num(const char *gpio_txt)
{
    unsigned int len = strlen(gpio_txt);
    if (len < 3) 
        return PIN_INVALID;

    unsigned int ch = gpio_txt[1] - 'A';
    if (ch >= 12)
        return PIN_INVALID;
    
    unsigned int offset;
    if(sscanf( &(gpio_txt[2]), "%u", &offset) != 1)
        return PIN_INVALID;

    if ( offset >= PORTS[ch][GPIO_PORT_N] )
        return PIN_INVALID;

    unsigned int pin = PORTS[ch][GPIO_PORT_ACUM] + offset;
    if (pin >= PIN_COUNT)
        return PIN_INVALID;
    
    return pin;
};

char *gpio_num2name(long n, char *name)
{
    int pn;
    name[0] = 'P';
    name[1] = GPIO_PINS[n][GPIO_BANK];
    pn = GPIO_PINS[n][GPIO_DATA_REGISTER_BIT];
    if (pn > 9)
    {
        name[2] = pn / 10 + '0';
        name[3] = pn % 10 + '0';
        name[4] = 0;
    }
    else
    {
        name[2] = pn + '0';
        name[3] = 0;
    };
    return name;
};

int gpio_confInput(unsigned int pin)
{
    int fd;
    fd = gpio_openMem();
    if (fd < 0)
        return -1;
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_REGISTER], GPIO_PINS[pin][GPIO_REGISTER_BIT], GPIO_LEN, GPIO_INPUT);
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_PULL_REGISTER], GPIO_PINS[pin][GPIO_PULL_REGISTER_BIT], GPIO_PULL_LEN, GPIO_PULL_DISABLE);
    gpio_closeMem(fd);
    return 0;
}

int gpio_test(unsigned int pin)
{
    int fd = gpio_openMem();
    gpio_closeMem(fd);
	return pin;
}

int gpio_confInputPull(unsigned int pin)
{
    int fd = gpio_openMem();
    if (fd < 0)
        return -1;
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_REGISTER], GPIO_PINS[pin][GPIO_REGISTER_BIT], GPIO_LEN, GPIO_INPUT);
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_PULL_REGISTER], GPIO_PINS[pin][GPIO_PULL_REGISTER_BIT], GPIO_PULL_LEN, GPIO_PULL_PULLUP);
    gpio_closeMem(fd);
    return 0;
}

int gpio_confI2C(unsigned int pin)
{
    int fd = gpio_openMem();
    if (fd < 0)
        return -1;
    if (pin != PA11 && pin != PA12)
        return -1;
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_REGISTER], GPIO_PINS[pin][GPIO_REGISTER_BIT], GPIO_LEN, GPIO_I2C);
    gpio_closeMem(fd);
    return 0;
}

int gpio_confOutput(unsigned int pin)
{
    int fd = gpio_openMem();
    if (fd < 0)
        return -1;
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_REGISTER], GPIO_PINS[pin][GPIO_REGISTER_BIT], GPIO_LEN, GPIO_OUTPUT);
    gpio_closeMem(fd);
    return 0;
}

int gpio_confPwmInv(unsigned int pin, int period)
{
    int fd = gpio_openMem();
    if (fd < 0)
        return -1;
    if (pin != PA5)
    {
        return -1;
    }
    setBit(fd, PWM_BASE_ADDRESS, PWM_CTRL_REGISTER, 8, 9, 0b101011111);                                                                   // Configuramoe el PWM como indica pagina 188 de H3
    setBit(fd, PWM_BASE_ADDRESS, PWM_PERI_REGISTER, 31, 16, period);                                                                      // Configuramoe el periodo como indica pagina 189 de H3
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_REGISTER], GPIO_PINS[pin][GPIO_REGISTER_BIT], GPIO_LEN, PWM_PIN_CONFIG); // 011 es PWM0 page 317
    setBit(fd, PWM_BASE_ADDRESS, PWM_PERI_REGISTER, 15, 16, 0);                                                                           // Lo ponemos encero
    gpio_closeMem(fd);
    return 0;
}

int gpio_confPwm(unsigned int pin, int period)
{
    int fd;
    if (pin != PA5)
    {
        return -1;
    }
    fd = gpio_openMem();
    if (fd < 0)
        return -1;
    setBit(fd, PWM_BASE_ADDRESS, PWM_CTRL_REGISTER, 8, 9, 0b101111111);                                                                   // Configuramoe el PWM como indica pagina 188 de H3
    setBit(fd, PWM_BASE_ADDRESS, PWM_PERI_REGISTER, 31, 16, period);                                                                      // Configuramoe el periodo como indica pagina 189 de H3
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_REGISTER], GPIO_PINS[pin][GPIO_REGISTER_BIT], GPIO_LEN, PWM_PIN_CONFIG); // 011 es PWM0 page 317
    setBit(fd, PWM_BASE_ADDRESS, PWM_PERI_REGISTER, 15, 16, 0);                                                                           // Lo ponemos encero
    gpio_closeMem(fd);
    return 0;
}

int gpio_confEint(unsigned int pin)
{
    int fd;

    if (GPIO_PINS[pin][GPIO_PORT_IRQ] == 0)
    {
        return -1;
    }
    fd = gpio_openMem();
    if (fd < 0)
        return -1;
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_REGISTER], GPIO_PINS[pin][GPIO_REGISTER_BIT], GPIO_LEN, GPIO_EINT);
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_EINT_REGISTER], GPIO_PINS[pin][GPIO_EINT_BIT], GPIO_EINT_LEN, GPIO_EINT_DOBLE_EDGE);
    // DBG ( "configuramos PULL Disable start" << endl );
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_PULL_REGISTER], GPIO_PINS[pin][GPIO_PULL_REGISTER_BIT], GPIO_PULL_LEN, GPIO_PULL_DISABLE);
    // DBG ( "configuramos PULL Disable end" << endl );
    gpio_closeMem(fd);
    return 0;
}

int gpio_confEintPull(unsigned int pin)
{
    int fd = gpio_openMem();
    if (fd < 0)
        return -1;
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_REGISTER], GPIO_PINS[pin][GPIO_REGISTER_BIT], GPIO_LEN, GPIO_EINT);
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_EINT_REGISTER], GPIO_PINS[pin][GPIO_EINT_BIT], GPIO_EINT_LEN, GPIO_EINT_DOBLE_EDGE);
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_PULL_REGISTER], GPIO_PINS[pin][GPIO_PULL_REGISTER_BIT], GPIO_PULL_LEN, GPIO_PULL_PULLUP);
    gpio_closeMem(fd);
    return 0;
}

int gpio_set(unsigned int pin, long state)
{
    int fd = gpio_openMem();
    if (fd < 0)
        return -1;
    setBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_DATA_REGISTER], GPIO_PINS[pin][GPIO_DATA_REGISTER_BIT], 1, (state == 0 ? 0 : 1));
    gpio_closeMem(fd);
    return 0;
}

int gpio_setPWM(unsigned int pin, unsigned int period)
{
    int fd = gpio_openMem();
    if (fd < 0)
        return -1;
    setBit(fd, PWM_BASE_ADDRESS, PWM_PERI_REGISTER, 15, 16, period); // Configuramoe el periodo como indica pagina 189
    gpio_closeMem(fd);
    return 0;
}

int gpio_get(unsigned int pin, unsigned long int *value)
{
    int fd = gpio_openMem();
    if (fd < 0)
        return -1;
    getBit(fd, GPIO_PINS[pin][GPIO_ADDRESS], GPIO_PINS[pin][GPIO_DATA_REGISTER], GPIO_PINS[pin][GPIO_DATA_REGISTER_BIT], 1, value);
    gpio_closeMem(fd);
    return 0;
}
