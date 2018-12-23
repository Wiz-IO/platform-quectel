/****************************************************************************  
 *  WizIO 2018 Georgi Angelov
 *      http://www.wizio.eu/
 *      https://github.com/Wiz-IO
 ****************************************************************************/
 
/****************************************************************************
 * Included Files
 ****************************************************************************/
 
#include "custom_feature_def.h"
#include "ql_type.h"
#include "ql_stdlib.h"
#include "ql_trace.h"
#include "ql_uart.h"
#include "ql_error.h"

/****************************************************************************
 * Defines
 ****************************************************************************/

#ifdef CORE_BC66
#   define DPORT UART_PORT0 
#else
#   define DPORT UART_PORT1
#endif

static Enum_SerialPort m_myUartPort = DPORT; 
#define DEBUG_ENABLE 1
#if DEBUG_ENABLE > 0
#define DEBUG_PORT  DPORT
#define DBG_BUF_LEN   512
static char DBG_BUFFER[DBG_BUF_LEN];
#define APP_DEBUG(FORMAT,...) {\
    Ql_memset(DBG_BUFFER, 0, DBG_BUF_LEN);\
    Ql_sprintf(DBG_BUFFER,FORMAT,##__VA_ARGS__); \
    if (UART_PORT2 == (DEBUG_PORT)) {\
        Ql_Debug_Trace(DBG_BUFFER);\
    } else {\
        Ql_UART_Write((Enum_SerialPort)(DEBUG_PORT), (u8*)(DBG_BUFFER), Ql_strlen((const char *)(DBG_BUFFER)));\
    }\
}
#else
#define APP_DEBUG(FORMAT,...) 
#endif

static void CallBack_UART_Hdlr(Enum_SerialPort port, Enum_UARTEventType msg, bool level, void* customizedPara){}

/****************************************************************************
 * Source
 ****************************************************************************/

void proc_main_task(void) {
    s32 ret;
    ST_MSG msg;
    Ql_UART_Register(m_myUartPort, CallBack_UART_Hdlr, NULL);
    Ql_UART_Open(m_myUartPort, 115200, FC_NONE);
    APP_DEBUG("PlatformIO - Quectel OpenCPU 2018 Georgi Angelov\n");  
    while (1) {
         Ql_OS_GetMessage(&msg);
        switch(msg.message) {
            case MSG_ID_RIL_READY:                
                Ql_RIL_Initialize();
                APP_DEBUG("RIL is ready\n");
                break;  
            case MSG_ID_URC_INDICATION: 
                APP_DEBUG("MSG_ID_URC_INDICATION: %d, %d\n", msg.param1, msg.param2);  
                if (msg.param1 == 5 && msg.param2 == 1) { 
                    APP_DEBUG("Network Connected\n");  
                }                           
            default: 
                break;
        }       
    } 
}