#ifndef _EE_H_
#define _EE_H_

/***********************************************************************************************************

  Author:     Nima Askari
  Github:     https://www.github.com/NimaLTD
  LinkedIn:   https://www.linkedin.com/in/nimaltd
  Youtube:    https://www.youtube.com/@nimaltd
  Instagram:  https://instagram.com/github.NimaLTD

  Version:    3.0.0

  History:

              3.0.0
              - Rewrite again
              - Support STM32CubeMx Packet installer

***********************************************************************************************************/

#ifdef __cplusplus
extern "C" {
#endif

/************************************************************************************************************
**************    Include Headers
************************************************************************************************************/

#include <stdbool.h>

#include "main.h"

/**
 * @brief Get the size of one page
 */
uint32_t EE_PageSize(void);

/**
 * @brief Get the number of pages
 */
uint8_t EE_PageCount(void);

/**
 * @brief Get the address of a page
 * @param PageOffset Page offset (reverse order, 0 is Last page)
 * @return NULL if failed
 */
uint8_t* EE_PageAddress(uint8_t PageOffset);

/**
 * @brief Erase a page
 * @param PageOffset Page offset (reverse order, 0 is Last page)
 * @return true if successful
 * @note In STM32, the data after formatting is 0xFF, not 0x00
 */
bool EE_Erase(uint8_t PageOffset);

/**
 * @brief Read data from a page
 * @param PageOffset Page offset (reverse order, 0 is Last page)
 * @param Data Data buffer
 * @param Size Data size
 * @return true if successful
 */
bool EE_Read(uint8_t PageOffset, uint8_t* Data, uint32_t Size);

/**
 * @brief Write data to a page
 * @param PageOffset Page offset (reverse order, 0 is Last page)
 * @param Data Data buffer
 * @param Size Data size (should be multiple of 4 (32bit word))
 * @param Erase Erase page before writing (can be false if EE_Erase is called
 * manually)
 * @return true if successful
 */
bool EE_Write(uint8_t PageOffset, uint8_t* Data, uint32_t Size, bool Erase);

#ifdef __cplusplus
}
#endif
#endif
