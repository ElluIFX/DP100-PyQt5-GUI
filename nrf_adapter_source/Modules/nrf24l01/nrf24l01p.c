/*
 *  nrf24l01_plus.c
 *
 *  Created on: 2021. 7. 20.
 *      Author: mokhwasomssi
 *
 */

#include "nrf24l01p.h"

#define NRF_MODE_IDLE 0
#define NRF_MODE_RX 1
#define NRF_MODE_TX 2

static uint8_t nrf_mode = NRF_MODE_IDLE;
static uint8_t nrf_auto = 0;
static uint8_t nrf_auto_tx_cnt = 0;
static uint8_t* nrf_rx_payload = NULL;
static void (*nrf_tx_callback)(uint8_t) = NULL;
static void (*nrf_rx_callback)(uint8_t) = NULL;
static uint8_t payload_length = 32;

static void cs_high() {
    HAL_GPIO_WritePin(NRF24L01P_SPI_CS_PIN_PORT, NRF24L01P_SPI_CS_PIN_NUMBER,
                      GPIO_PIN_SET);
}

static void cs_low() {
    HAL_GPIO_WritePin(NRF24L01P_SPI_CS_PIN_PORT, NRF24L01P_SPI_CS_PIN_NUMBER,
                      GPIO_PIN_RESET);
}

static void ce_high() {
    HAL_GPIO_WritePin(NRF24L01P_CE_PIN_PORT, NRF24L01P_CE_PIN_NUMBER,
                      GPIO_PIN_SET);
}

static void ce_low() {
    HAL_GPIO_WritePin(NRF24L01P_CE_PIN_PORT, NRF24L01P_CE_PIN_NUMBER,
                      GPIO_PIN_RESET);
}

static void led_on() {
    HAL_GPIO_WritePin(NRF24L01P_STA_LED_PIN_PORT, NRF24L01P_STA_LED_PIN_NUMBER,
                      GPIO_PIN_RESET);
}

static void led_off() {
    HAL_GPIO_WritePin(NRF24L01P_STA_LED_PIN_PORT, NRF24L01P_STA_LED_PIN_NUMBER,
                      GPIO_PIN_SET);
}

static void read_register_multi(uint8_t reg, uint8_t* buffer, uint8_t len) {
    uint8_t command = NRF24L01P_CMD_R_REGISTER | reg;
    uint8_t status;

    cs_low();
    HAL_SPI_TransmitReceive(NRF24L01P_SPI, &command, &status, 1, 2000);
    HAL_SPI_Receive(NRF24L01P_SPI, buffer, len, 2000);
    cs_high();
}

static uint8_t read_register(uint8_t reg) {
    uint8_t read_val;
    read_register_multi(reg, &read_val, 1);
    return read_val;
}

static void write_register_multi(uint8_t reg, uint8_t* value, uint8_t len) {
    uint8_t command = NRF24L01P_CMD_W_REGISTER | reg;
    uint8_t status;

    cs_low();
    HAL_SPI_TransmitReceive(NRF24L01P_SPI, &command, &status, 1, 2000);
    HAL_SPI_Transmit(NRF24L01P_SPI, value, len, 2000);
    cs_high();
}

static void write_register(uint8_t reg, uint8_t value) {
    return write_register_multi(reg, &value, 1);
}

/* nRF24L01+ Main Functions */
void nrf24l01p_receive(uint8_t* rx_payload, void (*rx_callback)(uint8_t)) {
    nrf_rx_payload = rx_payload;
    nrf_rx_callback = rx_callback;
    nrf_auto = 0;
    if (nrf_mode != NRF_MODE_RX) {
        nrf24l01p_rx_mode();
    }
}

void nrf24l01p_transmit(uint8_t* tx_payload, void (*tx_callback)(uint8_t)) {
    nrf_tx_callback = tx_callback;
    nrf_auto = 0;
    if (nrf_mode != NRF_MODE_TX) {
        nrf24l01p_tx_mode();
    }
    nrf24l01p_write_tx_fifo(tx_payload);
    led_on();
}

uint8_t nrf24l01p_transmit_then_receive(uint8_t* tx_payload,
                                        void (*tx_callback)(uint8_t)) {
    uint8_t ret = 1;
    nrf_tx_callback = tx_callback;
    nrf_auto = 1;
    if ((nrf_auto_tx_cnt >= 3 && (nrf24l01p_get_fifo_status() & 0x20) ||
         nrf_auto_tx_cnt >= 6)) {
        nrf24l01p_idle_mode();
        nrf24l01p_flush_tx_fifo();
        nrf24l01p_clear_max_rt();
        nrf24l01p_clear_tx_ds();
        ret = 0;
        nrf_auto_tx_cnt = 0;
    }
    if (nrf_mode != NRF_MODE_TX) {
        nrf24l01p_tx_mode();
    }
    nrf24l01p_write_tx_fifo(tx_payload);
    led_on();
    nrf_auto_tx_cnt++;
    return ret;
}

static void nrf24l01p_tx_irq() {
    uint8_t tx_ds = nrf24l01p_get_status();

    if (tx_ds & 0x20) {
        // TX_DS
        nrf24l01p_clear_tx_ds();
        led_off();
        nrf_tx_callback(1);
        if (nrf_auto_tx_cnt)
            nrf_auto_tx_cnt--;
    }

    else if (tx_ds & 0x10) {
        // MAX_RT
        nrf24l01p_flush_tx_fifo();
        nrf24l01p_clear_max_rt();
        led_off();
        nrf_tx_callback(0);
        nrf_auto_tx_cnt = 0;
    }

    if (nrf_auto) {
        if (!nrf_auto_tx_cnt)
            nrf24l01p_rx_mode();
    }
}

static void nrf24l01p_rx_irq() {
    while (!(nrf24l01p_get_fifo_status() & 0x01)) {
        led_on();
        nrf24l01p_read_rx_fifo(nrf_rx_payload);
        nrf24l01p_clear_rx_dr();
        nrf_rx_callback(1);
        led_off();
    }
}

/* nRF24L01+ Sub Functions */
void nrf24l01p_reset() {
    // Reset pins
    cs_high();
    for (int i = 0; i < 0xffff; i++) {
        __NOP();
    }
    ce_low();
    nrf_mode = NRF_MODE_IDLE;
    // Reset registers
    write_register(NRF24L01P_REG_CONFIG, 0x08);
    write_register(NRF24L01P_REG_EN_AA, 0x01);
    write_register(NRF24L01P_REG_EN_RXADDR, 0x01);
    write_register(NRF24L01P_REG_SETUP_AW, 0x03);
    write_register(NRF24L01P_REG_SETUP_RETR, 0x03);
    write_register(NRF24L01P_REG_RF_CH, 0x02);
    write_register(NRF24L01P_REG_RF_SETUP, 0x07);
    write_register(NRF24L01P_REG_STATUS, 0x7E);
    write_register(NRF24L01P_REG_RX_PW_P0, 0x00);
    write_register(NRF24L01P_REG_RX_PW_P0, 0x00);
    write_register(NRF24L01P_REG_RX_PW_P1, 0x00);
    write_register(NRF24L01P_REG_RX_PW_P2, 0x00);
    write_register(NRF24L01P_REG_RX_PW_P3, 0x00);
    write_register(NRF24L01P_REG_RX_PW_P4, 0x00);
    write_register(NRF24L01P_REG_RX_PW_P5, 0x00);
    write_register(NRF24L01P_REG_FIFO_STATUS, 0x11);
    write_register(NRF24L01P_REG_DYNPD, 0x00);
    write_register(NRF24L01P_REG_FEATURE, 0x00);

    // Reset FIFO
    nrf24l01p_flush_rx_fifo();
    nrf24l01p_flush_tx_fifo();
}

void nrf24l01p_rx_mode() {
    ce_low();
    uint8_t new_config = read_register(NRF24L01P_REG_CONFIG);
    new_config |= 1 << 0;

    write_register(NRF24L01P_REG_CONFIG, new_config);

    nrf_mode = NRF_MODE_RX;
    ce_high();
}

void nrf24l01p_tx_mode() {
    ce_low();
    uint8_t new_config = read_register(NRF24L01P_REG_CONFIG);
    new_config &= 0xFE;

    write_register(NRF24L01P_REG_CONFIG, new_config);

    nrf_mode = NRF_MODE_TX;
    ce_high();
}

void nrf24l01p_idle_mode() {
    ce_low();
    nrf_mode = NRF_MODE_IDLE;
}

uint8_t nrf24l01p_read_rx_fifo(uint8_t* rx_payload) {
    uint8_t command = NRF24L01P_CMD_R_RX_PAYLOAD;
    uint8_t status;

    cs_low();
    HAL_SPI_TransmitReceive(NRF24L01P_SPI, &command, &status, 1, 2000);
    HAL_SPI_Receive(NRF24L01P_SPI, rx_payload, payload_length, 2000);
    cs_high();

    return status;
}

uint8_t nrf24l01p_write_tx_fifo(uint8_t* tx_payload) {
    uint8_t command = NRF24L01P_CMD_W_TX_PAYLOAD;
    uint8_t status;

    cs_low();
    HAL_SPI_TransmitReceive(NRF24L01P_SPI, &command, &status, 1, 2000);
    HAL_SPI_Transmit(NRF24L01P_SPI, tx_payload, payload_length, 2000);
    cs_high();

    return status;
}

void nrf24l01p_flush_rx_fifo() {
    uint8_t command = NRF24L01P_CMD_FLUSH_RX;
    uint8_t status;

    cs_low();
    HAL_SPI_TransmitReceive(NRF24L01P_SPI, &command, &status, 1, 2000);
    cs_high();
}

void nrf24l01p_flush_tx_fifo() {
    uint8_t command = NRF24L01P_CMD_FLUSH_TX;
    uint8_t status;

    cs_low();
    HAL_SPI_TransmitReceive(NRF24L01P_SPI, &command, &status, 1, 2000);
    cs_high();
}

uint8_t nrf24l01p_get_status() {
    uint8_t command = NRF24L01P_CMD_NOP;
    uint8_t status;

    cs_low();
    HAL_SPI_TransmitReceive(NRF24L01P_SPI, &command, &status, 1, 2000);
    cs_high();

    return status;
}

uint8_t nrf24l01p_get_fifo_status() {
    return read_register(NRF24L01P_REG_FIFO_STATUS);
}

uint8_t nrf24l01p_get_payload_width() {
    return payload_length;
}

void nrf24l01p_rx_set_payload_widths(widths bytes) {
    write_register(NRF24L01P_REG_RX_PW_P0, bytes);
    payload_length = bytes;
}

void nrf24l01p_clear_rx_dr() {
    uint8_t new_status = nrf24l01p_get_status();
    new_status |= 0x40;

    write_register(NRF24L01P_REG_STATUS, new_status);
}

void nrf24l01p_clear_tx_ds() {
    uint8_t new_status = nrf24l01p_get_status();
    new_status |= 0x20;

    write_register(NRF24L01P_REG_STATUS, new_status);
}

void nrf24l01p_clear_max_rt() {
    uint8_t new_status = nrf24l01p_get_status();
    new_status |= 0x10;

    write_register(NRF24L01P_REG_STATUS, new_status);
}

void nrf24l01p_power_up() {
    uint8_t new_config = read_register(NRF24L01P_REG_CONFIG);
    new_config |= 1 << 1;

    write_register(NRF24L01P_REG_CONFIG, new_config);
}

void nrf24l01p_power_down() {
    uint8_t new_config = read_register(NRF24L01P_REG_CONFIG);
    new_config &= 0xFD;

    write_register(NRF24L01P_REG_CONFIG, new_config);
}

void nrf24l01p_set_crc_length(length bytes) {
    uint8_t new_config = read_register(NRF24L01P_REG_CONFIG);

    switch (bytes) {
        // CRCO bit in CONFIG resiger set 0
        case 1:
            new_config &= 0xFB;
            break;
        // CRCO bit in CONFIG resiger set 1
        case 2:
            new_config |= 1 << 2;
            break;
    }

    write_register(NRF24L01P_REG_CONFIG, new_config);
}

void nrf24l01p_set_address_widths(widths bytes) {
    write_register(NRF24L01P_REG_SETUP_AW, bytes - 2);
}

void nrf24l01p_set_rx_address(uint8_t* address, size_t width) {
    uint8_t addr[5] = {0};
    for (int i = 0; i < width; i++) {
        addr[i] = address[width - 1 - i];  // LSB first
    }
    write_register_multi(NRF24L01P_REG_RX_ADDR_P0, addr, 5);
}

void nrf24l01p_set_tx_address(uint8_t* address, size_t width) {
    uint8_t addr[5] = {0};
    for (int i = 0; i < width; i++) {
        addr[i] = address[width - 1 - i];  // LSB first
    }
    write_register_multi(NRF24L01P_REG_TX_ADDR, addr, 5);
}

void nrf24l01p_auto_retransmit_count(count cnt) {
    uint8_t new_setup_retr = read_register(NRF24L01P_REG_SETUP_RETR);

    // Reset ARC register 0
    new_setup_retr |= 0xF0;
    new_setup_retr |= cnt;
    write_register(NRF24L01P_REG_SETUP_RETR, new_setup_retr);
}

void nrf24l01p_auto_retransmit_delay(delay us) {
    uint8_t new_setup_retr = read_register(NRF24L01P_REG_SETUP_RETR);
    if (us < 250) {
        us = 250;
    }
    // Reset ARD register 0
    new_setup_retr |= 0x0F;
    new_setup_retr |= ((us / 250) - 1) << 4;
    write_register(NRF24L01P_REG_SETUP_RETR, new_setup_retr);
}

void nrf24l01p_set_rf_channel(channel MHz) {
    uint16_t new_rf_ch = MHz - 2400;
    write_register(NRF24L01P_REG_RF_CH, new_rf_ch);
}

void nrf24l01p_set_rf_tx_output_power(output_power dBm) {
    uint8_t new_rf_setup = read_register(NRF24L01P_REG_RF_SETUP) & 8;
    new_rf_setup |= dBm & 0x07;

    write_register(NRF24L01P_REG_RF_SETUP, new_rf_setup);
}

void nrf24l01p_set_rf_air_data_rate(air_data_rate bps) {
    // Set value to 0
    uint8_t new_rf_setup = read_register(NRF24L01P_REG_RF_SETUP) & 0xD7;

    switch (bps) {
        case ADR_1Mbps:
            break;
        case ADR_2Mbps:
            new_rf_setup |= 1 << 3;
            break;
        case ADR_250kbps:
            new_rf_setup |= 1 << 5;
            break;
    }
    write_register(NRF24L01P_REG_RF_SETUP, new_rf_setup);
}

void nrf24l01p_irq(void) {
    if (nrf_mode == NRF_MODE_RX) {
        nrf24l01p_rx_irq();
    } else if (nrf_mode == NRF_MODE_TX) {
        nrf24l01p_tx_irq();
    }
}

uint8_t __nrf24l01p_debug_read_register(uint8_t reg) {
    return read_register(reg);
}
