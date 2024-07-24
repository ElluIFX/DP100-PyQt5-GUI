/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "gpio.h"
#include "iwdg.h"
#include "spi.h"
#include "usart.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "lfbb.h"
#include "mf.h"
#include "nrf24l01p.h"
#include "stdarg.h"
#include "stdio.h"
#include "string.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
void handle_uart_command(uint8_t cmd, uint8_t* data, size_t len);
void parse_uart_data(uint8_t* data, size_t len);
void nrf_tx_callback(uint8_t status);
void nrf_rx_callback(uint8_t status);
void USART_BRR_Configuration(UART_HandleTypeDef* huart, uint32_t BaudRate);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

typedef struct {
    uint16_t ch_mhz;
    uint8_t air_data_rate;
    uint8_t tx_output_power;
    uint8_t crc_length;
    uint8_t payload_length;
    uint8_t auto_retransmit_count;
    uint16_t auto_retransmit_delay;
    uint8_t address_widths;
    uint8_t address_buf[5];
} NRF24L01P_Init_Type;

enum RESPONSE {
    REP_UNKNOWN_CMD = 0x00,   // unknown command
    REP_INVALID_CMD = 0x01,   // invalid command length
    REP_CMD_FAILED = 0x02,    // command failed
    REP_RESET_DONE = 0x03,    // setting reset done
    REP_BAUDRATE_SET = 0x04,  // baudrate set

    REP_NRF_SEND_OK = 0x10,        // NRF24L01P send done
    REP_NRF_SEND_FAIL = 0x11,      // NRF24L01P send failed
    REP_NRF_RECV_OK = 0x12,        // NRF24L01P receive done
    REP_NRF_RECV_FAIL = 0x13,      // NRF24L01P receive failed
    REP_NRF_FIFO_OVERFLOW = 0x15,  // NRF24L01P FIFO overflow

    REP_NRF_INIT = 0x20,       // NRF24L01P init done
    REP_NRF_SET_SAVED = 0x21,  // NRF24L01P setting saved
    REP_NRF_SET_QUERY = 0x22,  // NRF24L01P setting query result

    REP_ECHO = 0xff,  // echo
};

enum CMD {
    CMD_REBOOT = 0x00,        // reset system
    CMD_RESET = 0x03,         // reset settings
    CMD_SET_BAUDRATE = 0x04,  // set baudrate

    CMD_NRF_TX = 0x10,  // nrf24l01p tx (variable length of payload)

    CMD_NRF_SET = 0x20,    // nrf24l01p set setting (9 bytes, see nrf24l01_init)
    CMD_NRF_SAVE = 0x21,   // nrf24l01p save setting (no arg)
    CMD_NRF_QUERY = 0x22,  // nrf24l01p query setting (same as nrf24l01_init)

    CMD_ECHO = 0xff,  // echo
};

NRF24L01P_Init_Type nrf_setting = {
    2478, ADR_2Mbps, OP_7dBm, 2, 32, 3, 250, 5, {0xAA, 0xBB, 0xCC, 0xDD, 0xEE}};
uint32_t baudrate = 921600;

uint8_t mf_ok;

volatile uint8_t nrf_irq_flag = 0;

LFBB_Inst_Type tx_lfbb;
LFBB_Inst_Type rx_lfbb;
size_t tx_sending = 0;
uint8_t tx_buf[256];
uint8_t rx_buf[256];
uint8_t rx_emerg_buf[2];
uint8_t nrf_buffer[32] = {0};

uint8_t temp_buf1[64];
uint8_t temp_buf2[64];

void uart_tx_exchange(uint8_t from_irq) {
    if (!from_irq &&
        (huart1.gState != HAL_UART_STATE_READY ||
         (huart1.hdmatx && huart1.hdmatx->State != HAL_DMA_STATE_READY))) {
        return;
    }
    if (tx_sending) {
        LFBB_ReadRelease(&tx_lfbb, tx_sending);
        tx_sending = 0;
    }
    uint8_t* data = LFBB_ReadAcquire(&tx_lfbb, &tx_sending);
    if (data) {
        HAL_UART_Transmit_DMA(&huart1, data, tx_sending);
    } else {
        tx_sending = 0;
    }
}

size_t uart_tx_send(const uint8_t* data, size_t len) {
    if (!len || len > sizeof(tx_buf))
        return 0;
    uint8_t* buf = NULL;
    while (!buf)
        buf = LFBB_WriteAcquire(&tx_lfbb, len);
    memcpy(buf, data, len);
    LFBB_WriteRelease(&tx_lfbb, len);
    uart_tx_exchange(0);
    return len;
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef* huart) {
    uart_tx_exchange(1);
}

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef* huart, uint16_t Size) {
    static uint8_t overflow = 0;
    if (!overflow)
        LFBB_WriteRelease(&rx_lfbb, Size);
    else
        overflow = 0;
    size_t rx_len;
    uint8_t* rx_ptr = LFBB_WriteAcquireAlt(&rx_lfbb, &rx_len);
    if (!rx_ptr || !rx_len) {
        overflow = 1;
        HAL_UARTEx_ReceiveToIdle_DMA(&huart1, rx_emerg_buf, 2);
        return;
    }
    HAL_UARTEx_ReceiveToIdle_DMA(&huart1, rx_ptr, rx_len);
}

void uart_send_packet(uint8_t cmd, uint8_t* data1, size_t len1, uint8_t* data2,
                      size_t len2) {
    temp_buf1[0] = 0xAA;
    temp_buf1[1] = 0x66;
    temp_buf1[2] = cmd;
    temp_buf1[3] = len1 + len2;
    if (len1)
        memcpy(temp_buf1 + 4, data1, len1);
    if (len2)
        memcpy(temp_buf1 + 4 + len1, data2, len2);
    uart_tx_send(temp_buf1, 4 + len1 + len2);
}

void nrf24l01_init(NRF24L01P_Init_Type* setting) {
    nrf24l01p_reset();
    nrf24l01p_power_up();

    nrf24l01p_set_rf_channel(setting->ch_mhz);  // 2.478GHz
    nrf24l01p_set_rf_air_data_rate(setting->air_data_rate);
    nrf24l01p_set_rf_tx_output_power(setting->tx_output_power);

    nrf24l01p_set_crc_length(setting->crc_length);

    nrf24l01p_set_address_widths(setting->address_widths);
    nrf24l01p_set_tx_address(setting->address_buf, setting->address_widths);
    nrf24l01p_set_rx_address(setting->address_buf, setting->address_widths);

    nrf24l01p_rx_set_payload_widths(setting->payload_length);

    nrf24l01p_auto_retransmit_count(setting->auto_retransmit_count);
    nrf24l01p_auto_retransmit_delay(setting->auto_retransmit_delay);

    memset(nrf_buffer, 0, sizeof(nrf_buffer));
    nrf24l01p_receive(nrf_buffer, nrf_rx_callback);

    uart_send_packet(REP_NRF_INIT, NULL, 0, NULL, 0);
}

void parse_uart_data(uint8_t* data, size_t len) {
    static uint8_t buf[128];
    static uint8_t state, cmd, temp;
    static size_t dl, bp;
    while (len--) {
        temp = *data++;
        if (state == 0 && temp == 0xAA) {
            state = 1;
        } else if (state == 1 && temp == 0x55) {
            state = 2;
        } else if (state == 2) {
            cmd = temp;
            state = 3;
        } else if (state == 3) {
            if (!temp) {
                state = 0;
                handle_uart_command(cmd, NULL, 0);
                break;
            }
            dl = temp;
            bp = 0;
            state = 4;
        } else if (state == 4) {
            buf[bp++] = temp;
            if (bp >= dl) {
                state = 0;
                handle_uart_command(cmd, buf, dl);
            }
        } else {
            state = 0;
        }
    }
}

void handle_uart_command(uint8_t cmd, uint8_t* data, size_t len) {
    switch (cmd) {
        case CMD_REBOOT:  // reset
            NVIC_SystemReset();
            break;
        case CMD_RESET:
            if (!mf_ok) {
                uart_send_packet(REP_CMD_FAILED, NULL, 0, NULL, 0);
                break;
            }
            mf_purge();
            uart_send_packet(REP_RESET_DONE, NULL, 0, NULL, 0);
            HAL_Delay(100);
            NVIC_SystemReset();
            break;
        case CMD_SET_BAUDRATE:
            if (len < 3) {
                uart_send_packet(REP_INVALID_CMD, NULL, 0, NULL, 0);
                break;
            }
            baudrate = data[2] + data[1] * 100 + data[0] * 10000;
            uart_send_packet(REP_BAUDRATE_SET, NULL, 0, NULL, 0);
            HAL_Delay(100);
            USART_BRR_Configuration(&huart1, baudrate);
            if (mf_ok) {
                mf_set_key("baudrate", &baudrate, sizeof(baudrate));
                mf_save();
            }
            break;
        case CMD_NRF_TX:  // nrf24l01p tx
            memset(nrf_buffer, 0, sizeof(nrf_buffer));
            memcpy(nrf_buffer, data, len);
            if (!nrf24l01p_transmit_then_receive(nrf_buffer, nrf_tx_callback)) {
                uart_send_packet(REP_NRF_FIFO_OVERFLOW, NULL, 0, NULL, 0);
            }
            break;
        case CMD_NRF_SET:  // nrf24l01p setting
            if (len < 13) {
                uart_send_packet(REP_INVALID_CMD, NULL, 0, NULL, 0);
                break;
            }
            nrf_setting.ch_mhz = data[0] + 2400,
            nrf_setting.air_data_rate = data[1],
            nrf_setting.tx_output_power = data[2],
            nrf_setting.crc_length = data[3],
            nrf_setting.payload_length = data[4],
            nrf_setting.auto_retransmit_count = data[5],
            nrf_setting.auto_retransmit_delay = data[6] * 250,
            nrf_setting.address_widths = data[7],
            nrf_setting.address_buf[0] = data[8];
            nrf_setting.address_buf[1] = data[9];
            nrf_setting.address_buf[2] = data[10];
            nrf_setting.address_buf[3] = data[11];
            nrf_setting.address_buf[4] = data[12];
            nrf24l01_init(&nrf_setting);
            break;
        case CMD_NRF_SAVE:  // nrf24l01p setting save
            if (mf_ok) {
                mf_set_key("nrf_setting", &nrf_setting, sizeof(nrf_setting));
                mf_save();
                uart_send_packet(REP_NRF_SET_SAVED, NULL, 0, NULL, 0);
            } else {
                uart_send_packet(REP_CMD_FAILED, NULL, 0, NULL, 0);
            }
            break;
        case CMD_NRF_QUERY:  // nrf24l01p setting read
            temp_buf2[0] = nrf_setting.ch_mhz - 2400,
            temp_buf2[1] = nrf_setting.air_data_rate,
            temp_buf2[2] = nrf_setting.tx_output_power,
            temp_buf2[3] = nrf_setting.crc_length,
            temp_buf2[4] = nrf_setting.payload_length,
            temp_buf2[5] = nrf_setting.auto_retransmit_count,
            temp_buf2[6] = nrf_setting.auto_retransmit_delay / 250,
            temp_buf2[7] = nrf_setting.address_widths;
            temp_buf2[8] = nrf_setting.address_buf[0];
            temp_buf2[9] = nrf_setting.address_buf[1];
            temp_buf2[10] = nrf_setting.address_buf[2];
            temp_buf2[11] = nrf_setting.address_buf[3];
            temp_buf2[12] = nrf_setting.address_buf[4];
            uart_send_packet(REP_NRF_SET_QUERY, temp_buf2, 13, NULL, 0);
            break;
        case CMD_ECHO:  // echo
            uart_send_packet(REP_ECHO, NULL, 0, NULL, 0);
            break;
        default:
            uart_send_packet(REP_UNKNOWN_CMD, NULL, 0, NULL, 0);
            break;
    }
    return;
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    // nrf_irq_flag = 1;
    nrf24l01p_irq();
}

void nrf_tx_callback(uint8_t status) {
    if (status) {
        uart_send_packet(REP_NRF_SEND_OK, NULL, 0, NULL, 0);
    } else {
        uart_send_packet(REP_NRF_SEND_FAIL, NULL, 0, NULL, 0);
    }
}

void nrf_rx_callback(uint8_t status) {
    if (status) {
        uart_send_packet(REP_NRF_RECV_OK, nrf_buffer,
                         nrf24l01p_get_payload_width(), NULL, 0);
    } else {
        uart_send_packet(REP_NRF_RECV_FAIL, NULL, 0, NULL, 0);
    }
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void) {
    /* USER CODE BEGIN 1 */

    /* USER CODE END 1 */

    /* MCU Configuration--------------------------------------------------------*/

    /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
    HAL_Init();

    /* USER CODE BEGIN Init */

    /* USER CODE END Init */

    /* Configure the system clock */
    SystemClock_Config();

    /* USER CODE BEGIN SysInit */

    /* USER CODE END SysInit */

    /* Initialize all configured peripherals */
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_USART1_UART_Init();
    MX_SPI1_Init();
    MX_IWDG_Init();
    /* USER CODE BEGIN 2 */
    LFBB_Init(&tx_lfbb, tx_buf, sizeof(tx_buf));
    LFBB_Init(&rx_lfbb, rx_buf, sizeof(rx_buf));
    size_t rx_len;
    uint8_t* rx_ptr = LFBB_WriteAcquireAlt(&rx_lfbb, &rx_len);
    HAL_UARTEx_ReceiveToIdle_DMA(&huart1, rx_ptr, rx_len);

    if (mf_init() == MF_OK) {
        mf_ok = 1;
        mf_sync_key("nrf_setting", &nrf_setting, sizeof(nrf_setting));
        mf_sync_key("baudrate", &baudrate, sizeof(baudrate));
        if (baudrate && baudrate != 921600) {
            USART_BRR_Configuration(&huart1, baudrate);
        }
    } else {
        mf_ok = 0;
    }

    nrf24l01_init(&nrf_setting);

    for (uint8_t i = 0; i < 4 + mf_ok * 2; i++) {
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(100);
    }

    /* USER CODE END 2 */

    /* Infinite loop */
    /* USER CODE BEGIN WHILE */
    uint32_t tick100ms = HAL_GetTick();
    while (1) {
        rx_ptr = LFBB_ReadAcquire(&rx_lfbb, &rx_len);
        if (rx_ptr && rx_len) {
            parse_uart_data(rx_ptr, rx_len);
            LFBB_ReadRelease(&rx_lfbb, rx_len);
        }
        if (HAL_GetTick() - tick100ms >= 100) {
            tick100ms = HAL_GetTick();
            HAL_IWDG_Refresh(&hiwdg);
        }
        /* USER CODE END WHILE */

        /* USER CODE BEGIN 3 */
    }
    /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
    RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

    /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
    RCC_OscInitStruct.OscillatorType =
        RCC_OSCILLATORTYPE_HSI | RCC_OSCILLATORTYPE_LSI;
    RCC_OscInitStruct.HSIState = RCC_HSI_ON;
    RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
    RCC_OscInitStruct.LSIState = RCC_LSI_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
    RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL12;
    RCC_OscInitStruct.PLL.PREDIV = RCC_PREDIV_DIV1;
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
        Error_Handler();
    }

    /** Initializes the CPU, AHB and APB buses clocks
  */
    RCC_ClkInitStruct.ClockType =
        RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;

    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK) {
        Error_Handler();
    }
    PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USART1;
    PeriphClkInit.Usart1ClockSelection = RCC_USART1CLKSOURCE_PCLK1;
    if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK) {
        Error_Handler();
    }
}

/* USER CODE BEGIN 4 */

void USART_BRR_Configuration(UART_HandleTypeDef* huart, uint32_t BaudRate) {
#define UART_BRR_MIN 0x10U       /* UART BRR minimum authorized value */
#define UART_BRR_MAX 0x0000FFFFU /* UART BRR maximum authorized value */
    huart->Init.BaudRate = BaudRate;
    uint32_t pclk;
    uint16_t brrtemp;
    uint32_t usartdiv;
    UART_ClockSourceTypeDef clocksource;
    UART_GETCLOCKSOURCE(huart, clocksource);
    if (huart->Init.OverSampling == UART_OVERSAMPLING_8) {
        switch (clocksource) {
            case UART_CLOCKSOURCE_PCLK1:
                pclk = HAL_RCC_GetPCLK1Freq();
                break;
            case UART_CLOCKSOURCE_HSI:
                pclk = (uint32_t)HSI_VALUE;
                break;
            case UART_CLOCKSOURCE_SYSCLK:
                pclk = HAL_RCC_GetSysClockFreq();
                break;
            case UART_CLOCKSOURCE_LSE:
                pclk = (uint32_t)LSE_VALUE;
                break;
            default:
                pclk = 0U;
                break;
        }

        /* USARTDIV must be greater than or equal to 0d16 */
        if (pclk != 0U) {
            usartdiv =
                (uint32_t)(UART_DIV_SAMPLING8(pclk, huart->Init.BaudRate));
            if ((usartdiv >= UART_BRR_MIN) && (usartdiv <= UART_BRR_MAX)) {
                brrtemp = (uint16_t)(usartdiv & 0xFFF0U);
                brrtemp |= (uint16_t)((usartdiv & (uint16_t)0x000FU) >> 1U);
                huart->Instance->BRR = brrtemp;
            }
        }
    } else {
        switch (clocksource) {
            case UART_CLOCKSOURCE_PCLK1:
                pclk = HAL_RCC_GetPCLK1Freq();
                break;
            case UART_CLOCKSOURCE_HSI:
                pclk = (uint32_t)HSI_VALUE;
                break;
            case UART_CLOCKSOURCE_SYSCLK:
                pclk = HAL_RCC_GetSysClockFreq();
                break;
            case UART_CLOCKSOURCE_LSE:
                pclk = (uint32_t)LSE_VALUE;
                break;
            default:
                pclk = 0U;
                break;
        }

        if (pclk != 0U) {
            /* USARTDIV must be greater than or equal to 0d16 */
            usartdiv =
                (uint32_t)(UART_DIV_SAMPLING16(pclk, huart->Init.BaudRate));
            if ((usartdiv >= UART_BRR_MIN) && (usartdiv <= UART_BRR_MAX)) {
                huart->Instance->BRR = (uint16_t)usartdiv;
            }
        }
    }
}

void uart_error_process(UART_HandleTypeDef* huart) {
    if (huart->Instance != USART1) {
        return;
    }
    if ((__HAL_UART_GET_FLAG(huart, UART_FLAG_PE)) != 0) {  // 奇偶校验错误
        __HAL_UNLOCK(huart);
        __HAL_UART_CLEAR_PEFLAG(huart);
    }
    if ((__HAL_UART_GET_FLAG(huart, UART_FLAG_FE)) != 0) {  // 帧错误
        __HAL_UNLOCK(huart);
        __HAL_UART_CLEAR_FEFLAG(huart);
    }
    if ((__HAL_UART_GET_FLAG(huart, UART_FLAG_NE)) != 0) {  // 噪声错误
        __HAL_UNLOCK(huart);
        __HAL_UART_CLEAR_NEFLAG(huart);
    }
    if ((__HAL_UART_GET_FLAG(huart, UART_FLAG_ORE)) != 0) {  // 接收溢出
        __HAL_UNLOCK(huart);
        __HAL_UART_CLEAR_OREFLAG(huart);
    }
    HAL_UART_MspDeInit(huart);
    MX_USART1_UART_Init();
    LFBB_Init(&rx_lfbb, rx_buf, sizeof(rx_buf));
    size_t rx_len;
    uint8_t* rx_ptr = LFBB_WriteAcquireAlt(&rx_lfbb, &rx_len);
    HAL_UARTEx_ReceiveToIdle_DMA(&huart1, rx_ptr, rx_len);
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void) {
    /* USER CODE BEGIN Error_Handler_Debug */
    /* User can add his own implementation to report the HAL error return state */
    __disable_irq();
    while (1) {}
    /* USER CODE END Error_Handler_Debug */
}

#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t* file, uint32_t line) {
    /* USER CODE BEGIN 6 */
    /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
    /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
