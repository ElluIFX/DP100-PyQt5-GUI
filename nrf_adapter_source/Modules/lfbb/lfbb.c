/**************************************************************
 * @file lfbb.c
 * @brief A bipartite buffer implementation written in standard
 * c11 suitable for both low-end microcontrollers all the way
 * to HPC machines. Lock-free for single consumer single
 * producer scenarios.
 **************************************************************/

/**************************************************************
 * Copyright (c) 2022 Djordje Nedic
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software
 * without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to
 * whom the Software is furnished to do so, subject to the
 * following conditions:
 *
 * The above copyright notice and this permission notice shall
 * be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
 * KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 * PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
 * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * This file is part of LFBB - Lock Free Bipartite Buffer
 *
 * Author:          Djordje Nedic <nedic.djordje2@gmail.com>
 * Version:         1.3.5
 **************************************************************/

/************************** INCLUDE ***************************/

#include "lfbb.h"

// #include <assert.h>
#define assert(x) ((void)0)

/*************************** MACRO ****************************/

#ifndef MIN
#define MIN(x, y) (((x) < (y)) ? (x) : (y))
#endif

/******************** FUNCTION PROTOTYPES *********************/

static size_t CalcFree(size_t w, size_t r, size_t size);

/******************** EXPORTED FUNCTIONS **********************/

void LFBB_Init(LFBB_Inst_Type* inst, uint8_t* data_array, const size_t size) {
    assert(inst != NULL);
    assert(data_array != NULL);
    assert(size != 0U);

    inst->data = data_array;
    inst->size = size;
    MOD_ATOMIC_INIT(inst->r, 0U);
    MOD_ATOMIC_INIT(inst->w, 0U);
    MOD_ATOMIC_INIT(inst->i, 0U);
    inst->write_wrapped = false;
    inst->read_wrapped = false;
}

uint8_t* LFBB_WriteAcquire(LFBB_Inst_Type* inst, const size_t free_required) {
    assert(inst != NULL);
    assert(inst->data != NULL);

    /* Preload variables with adequate memory ordering */
    const mod_atomic_size_t w =
        MOD_ATOMIC_LOAD(inst->w, MOD_ATOMIC_ORDER_RELAXED);
    const mod_atomic_size_t r =
        MOD_ATOMIC_LOAD(inst->r, MOD_ATOMIC_ORDER_ACQUIRE);
    const size_t size = inst->size;

    const size_t free = CalcFree(w, r, size);
    const size_t linear_space = size - w;
    const size_t linear_free = MIN(free, linear_space);

    /* Try to find enough linear space until the end of the buffer */
    if (free_required <= linear_free) {
        return &inst->data[w];
    }

    /* If that doesn't work try from the beginning of the buffer */
    if (free_required <= free - linear_free) {
        inst->write_wrapped = true;
        return &inst->data[0];
    }

    /* Could not find free linear space with required size */
    return NULL;
}

uint8_t* LFBB_WriteAcquireAlt(LFBB_Inst_Type* inst, size_t* available) {
    assert(inst != NULL);
    assert(inst->data != NULL);

    /* Preload variables with adequate memory ordering */
    const mod_atomic_size_t w =
        MOD_ATOMIC_LOAD(inst->w, MOD_ATOMIC_ORDER_RELAXED);
    const mod_atomic_size_t r =
        MOD_ATOMIC_LOAD(inst->r, MOD_ATOMIC_ORDER_ACQUIRE);
    const size_t size = inst->size;

    const size_t free = CalcFree(w, r, size);
    const size_t linear_space = size - w;
    const size_t linear_free = MIN(free, linear_space);

    /* Try to find enough linear space until the end of the buffer */

    if (free - linear_free <= linear_free) {
        *available = linear_free;
        return &inst->data[w];
    } else {
        inst->write_wrapped = true;
        *available = free - linear_free;
        return &inst->data[0];
    }

    /* Could not find free linear space with required size */
    *available = 0;
    return NULL;
}

void LFBB_WriteRelease(LFBB_Inst_Type* inst, const size_t written) {
    assert(inst != NULL);
    assert(inst->data != NULL);

    /* Preload variables with adequate memory ordering */
    mod_atomic_size_t w = MOD_ATOMIC_LOAD(inst->w, MOD_ATOMIC_ORDER_RELAXED);
    mod_atomic_size_t i;

    /* If the write wrapped set the invalidate index and reset write index*/
    if (inst->write_wrapped) {
        inst->write_wrapped = false;
        i = w;
        w = 0U;
    } else {
        i = MOD_ATOMIC_LOAD(inst->i, MOD_ATOMIC_ORDER_RELAXED);
    }

    /* Increment the write index */
    assert(w + written <= inst->size);
    w += written;

    /* If we wrote over invalidated parts of the buffer move the invalidate
   * index
   */
    if (w > i) {
        i = w;
    }

    /* Wrap the write index if we reached the end of the buffer */
    if (w == inst->size) {
        w = 0U;
    }

    /* Store the indexes with adequate memory ordering */
    MOD_ATOMIC_STORE(inst->i, i, MOD_ATOMIC_ORDER_RELAXED);
    MOD_ATOMIC_STORE(inst->w, w, MOD_ATOMIC_ORDER_RELEASE);
}

uint8_t* LFBB_ReadAcquire(LFBB_Inst_Type* inst, size_t* available) {
    assert(inst != NULL);
    assert(inst->data != NULL);
    assert(available != NULL);

    /* Preload variables with adequate memory ordering */
    const mod_atomic_size_t r =
        MOD_ATOMIC_LOAD(inst->r, MOD_ATOMIC_ORDER_RELAXED);
    const mod_atomic_size_t w =
        MOD_ATOMIC_LOAD(inst->w, MOD_ATOMIC_ORDER_ACQUIRE);

    /* When read and write indexes are equal, the buffer is empty */
    if (r == w) {
        *available = 0;
        return NULL;
    }

    /* Simplest case, read index is behind the write index */
    if (r < w) {
        *available = w - r;
        return &inst->data[r];
    }

    /* Read index reached the invalidate index, make the read wrap */
    const mod_atomic_size_t i =
        MOD_ATOMIC_LOAD(inst->i, MOD_ATOMIC_ORDER_RELAXED);
    if (r == i) {
        inst->read_wrapped = true;
        *available = w;
        return &inst->data[0];
    }

    /* There is some data until the invalidate index */
    *available = i - r;
    return &inst->data[r];
}

void LFBB_ReadRelease(LFBB_Inst_Type* inst, const size_t read) {
    assert(inst != NULL);
    assert(inst->data != NULL);

    /* If the read wrapped, overflow the read index */
    size_t r;
    if (inst->read_wrapped) {
        inst->read_wrapped = false;
        r = 0U;
    } else {
        r = MOD_ATOMIC_LOAD(inst->r, MOD_ATOMIC_ORDER_RELAXED);
    }

    /* Increment the read index and wrap to 0 if needed */
    r += read;
    if (r == inst->size) {
        r = 0U;
    }

    /* Store the indexes with adequate memory ordering */
    MOD_ATOMIC_STORE(inst->r, r, MOD_ATOMIC_ORDER_RELEASE);
}

/********************* PRIVATE FUNCTIONS **********************/

static size_t CalcFree(const size_t w, const size_t r, const size_t size) {
    if (r > w) {
        return (r - w) - 1U;
    } else {
        return (size - (w - r)) - 1U;
    }
}

bool LFBB_IsEmpty(LFBB_Inst_Type* inst) {
    assert(inst != NULL);
    assert(inst->data != NULL);
    /* When read and write indexes are equal, the buffer is empty */
    if (inst->r == inst->w) {
        return true;
    }
    return false;
}
