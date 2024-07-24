#ifndef _EE_INTERNAL_H_
#define _EE_INTERNAL_H_

#include "ee.h"

#define EE_ERASE_PAGE_ADDRESS 0
#define EE_ERASE_PAGE_NUMBER 1
#define EE_ERASE_SECTOR_NUMBER 2

#ifdef STM32F0
#define EE_ERASE EE_ERASE_PAGE_ADDRESS
#define FLASH_SIZE \
    ((((uint32_t)(*((uint16_t*)FLASHSIZE_BASE)) & (0xFFFFU))) * 1024)
#endif

#ifdef STM32F1
#define EE_ERASE EE_ERASE_PAGE_ADDRESS
#define FLASH_SIZE \
    ((((uint32_t)(*((uint16_t*)FLASHSIZE_BASE)) & (0xFFFFU))) * 1024)
#endif

#ifdef STM32F2
#define EE_ERASE EE_ERASE_SECTOR_NUMBER
#define FLASH_SIZE \
    ((((uint32_t)(*((uint16_t*)FLASHSIZE_BASE)) & (0xFFFFU))) * 1024)
#endif

#ifdef STM32F3
#define EE_ERASE EE_ERASE_PAGE_ADDRESS
#define FLASH_SIZE \
    ((((uint32_t)(*((uint16_t*)FLASHSIZE_BASE)) & (0xFFFFU))) * 1024)
#endif

#ifdef STM32F4
#define EE_ERASE EE_ERASE_SECTOR_NUMBER
#define EE_SIZE 0x20000
#define FLASH_SIZE \
    ((((uint32_t)(*((uint16_t*)FLASHSIZE_BASE)) & (0xFFFFU))) * 1024)
#endif

#ifdef STM32F7
#define EE_ERASE EE_ERASE_SECTOR_NUMBER
#define EE_SIZE 0x20000
#endif

#ifdef STM32H5
#define EE_ERASE EE_ERASE_PAGE_ADDRESS
#endif

#ifdef STM32H7
#define EE_ERASE EE_ERASE_SECTOR_NUMBER
#endif

#ifdef STM32G0
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32G4
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32U0
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32U5
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32L0
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32L1
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32L4
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32L5
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32WB
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32W0
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32WBA
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#undef FLASH_BANK_1
#endif

#ifdef STM32WL
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifdef STM32C0
#define EE_ERASE EE_ERASE_PAGE_NUMBER
#endif

#ifndef EE_SIZE
#if (EE_ERASE == EE_ERASE_PAGE_NUMBER) || (EE_ERASE == EE_ERASE_PAGE_ADDRESS)
#define EE_SIZE ((uint32_t)(FLASH_PAGE_SIZE))
#elif (EE_ERASE == EE_ERASE_SECTOR_NUMBER)
#define EE_SIZE ((uint32_t)(FLASH_SECTOR_SIZE))
#endif
#endif

#if defined FLASH_BANK_2
#define EE_BANK_SELECT FLASH_BANK_2
#elif defined FLASH_BANK_1
#define EE_BANK_SELECT FLASH_BANK_1
#endif

#define EE_FLASH_SIZE ((uint32_t)(FLASH_SIZE))

#ifndef EE_PAGE_NUMBER
#if (EE_BANK_SELECT == FLASH_BANK_2)
#define EE_PAGE_NUMBER (EE_FLASH_SIZE / EE_SIZE / 2)
#else
#define EE_PAGE_NUMBER (EE_FLASH_SIZE / EE_SIZE)
#endif
#endif

#ifndef EE_LAST_PAGE_SECTOR
#define EE_LAST_PAGE_SECTOR (EE_PAGE_NUMBER - 1)
#endif

#ifndef EE_ADDRESS
#if (EE_BANK_SELECT == FLASH_BANK_2)
#define EE_ADDRESS(PageOffset) \
    (FLASH_BASE + EE_SIZE * ((EE_FLASH_SIZE / EE_SIZE) - 1 - PageOffset))
#else
#define EE_ADDRESS(PageOffset) \
    (FLASH_BASE + EE_SIZE * (EE_LAST_PAGE_SECTOR - PageOffset))
#endif
#endif

#ifndef EE_ERASE
#error "Not Supported MCU!"
#endif

#endif  // _EE_INTERNAL_H_
