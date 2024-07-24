#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ee_internal.h"

#include "main.h"

/* 一块FLASH空间的大小 */
#define MF_FLASH_BLOCK_SIZE (EE_SIZE)

/* 主FLASH地址 */
#define MF_FLASH_MAIN_ADDR EE_ADDRESS(0)  // 倒数第一个page

/* 备份FLASH地址，注释则不使用 */
#define MF_FLASH_BACKUP_ADDR EE_ADDRESS(1)  // 倒数第二个page

/* FLASH空数据填充值 */
#define MF_FLASH_FILL 0xFF

/* FLASH标志位 */
#define MF_FLASH_HEADER 0xCAFEBA  // 数据库头(24-bit)
#define MF_FLASH_TAIL 0xBE        // 数据库尾(8-bit)

/* Flash读写函数 */

/**
 * @brief 从addr开始，擦除长度为MF_FLASH_BLOCK_SIZE的flash
 * @param addr 起始地址
 * @retval 操作结果 true: 成功, false: 失败
 * @note   实际入参只可能是MF_FLASH_MAIN_ADDR或MF_FLASH_BACKUP_ADDR，可以考虑简化
 */
__attribute__((unused)) static bool mf_erase(uint32_t addr) {
    uint8_t offset;
    for (offset = 0;; offset++) {
        if (offset >= EE_PAGE_NUMBER) {
            return false;
        }
        if (addr == (uint32_t)EE_PageAddress(offset)) {
            break;
        }
    }
    if (!EE_Erase(offset)) {
        return false;
    }
    return true;
}

/**
 * @brief 从addr开始，写入MF_FLASH_BLOCK_SIZE大小的数据
 * @param addr 起始地址
 * @param buf 数据指针
 * @retval 操作结果 true: 成功, false: 失败
 * @note   实际入参只可能是MF_FLASH_MAIN_ADDR或MF_FLASH_BACKUP_ADDR，可以考虑简化
 */
__attribute__((unused)) static bool mf_write(uint32_t addr, void* buf) {
    uint8_t offset;
    for (offset = 0;; offset++) {
        if (offset >= EE_PAGE_NUMBER) {
            return false;
        }
        if (addr == (uint32_t)EE_PageAddress(offset)) {
            break;
        }
    }
    if (!EE_Write(offset, buf, EE_SIZE, false)) {
        return false;
    }
    return true;
}
