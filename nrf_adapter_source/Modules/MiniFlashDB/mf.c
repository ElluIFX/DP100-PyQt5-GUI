#include "mf.h"

#if __has_include("mf_hal.h")
#include "mf_hal.h"
#else
#include "mf_hal_ee.h"
#endif

#include <stdint.h>

typedef struct {
    uint32_t name_size : 8;
    uint32_t data_size : 23;
    uint32_t next_key : 1;
} mf_key_t;

typedef struct {
    uint32_t header : 24;
    uint32_t sumcheck : 8;
    mf_key_t key;
} mf_flash_t;

static uint8_t mf_temp[MF_FLASH_BLOCK_SIZE];
static mf_flash_t* mf_data = (mf_flash_t*)mf_temp;
static mf_flash_t* info_main = NULL;
#ifdef MF_FLASH_BACKUP_ADDR
static mf_flash_t* info_backup = NULL;
#endif

static void block_calc_sumcheck(mf_flash_t* block) {
    uint8_t sumcheck = 0;
    block->sumcheck = 0;
    for (int i = 0; i < MF_FLASH_BLOCK_SIZE; i++) {
        sumcheck += ((uint8_t*)block)[i];
    }
    block->sumcheck = 0xFF - sumcheck;
}

static void init_temp(void) {
    mf_flash_t info = {.header = MF_FLASH_HEADER, .key = {0}};
    memset(mf_temp, MF_FLASH_FILL, MF_FLASH_BLOCK_SIZE);
    memcpy(mf_temp, &info, sizeof(info));
    mf_temp[MF_FLASH_BLOCK_SIZE - 1] = MF_FLASH_TAIL;
    block_calc_sumcheck(mf_data);
}

static bool init_block(mf_flash_t* block) {
    return mf_erase((uint32_t)block) && mf_write((uint32_t)block, mf_temp);
}

static bool block_empty(mf_flash_t* block) {
    return block->key.name_size == 0;
}

static bool block_err(mf_flash_t* block) {
    uint8_t sumcheck = 0;
    for (int i = 0; i < MF_FLASH_BLOCK_SIZE; i++) {
        sumcheck += ((uint8_t*)block)[i];
    }
    return block->header != MF_FLASH_HEADER ||
           ((uint8_t*)block)[MF_FLASH_BLOCK_SIZE - 1] != MF_FLASH_TAIL ||
           block->key.name_size > MF_FLASH_BLOCK_SIZE ||
           block->key.data_size > MF_FLASH_BLOCK_SIZE || sumcheck != 0xFF;
}

mf_status_t mf_fix(void) {
#ifdef MF_FLASH_BACKUP_ADDR
    bool main_to_backup = false;  // try to rewrite from main block
    if (block_err(info_backup)) {
        main_to_backup = true;
        if (!init_block(info_backup)) {
            return MF_ERR_IO;
        }
    }
#endif
    if (block_err(info_main)) {
        do {
#ifdef MF_FLASH_BACKUP_ADDR
            if (!block_empty(info_backup) &&
                !main_to_backup) {  // restore backup
                if (mf_erase((uint32_t)info_main) &&
                    mf_write((uint32_t)info_main, info_backup)) {
                    break;  // skip init
                } else {
                }
            }
            main_to_backup = false;  // main block has no data
#endif
            if (!init_block(info_main)) {
                return MF_ERR_IO;
            }
        } while (0);
    } else {
#ifdef MF_FLASH_BACKUP_ADDR
        if (main_to_backup) {
            if (!mf_erase((uint32_t)info_backup) ||
                !mf_write((uint32_t)info_backup, info_main)) {
            }
        }
#endif
    }
    memcpy(mf_temp, info_main, MF_FLASH_BLOCK_SIZE);
    return MF_OK;
}

mf_status_t mf_try_init(void) {
    info_main = (mf_flash_t*)MF_FLASH_MAIN_ADDR;
#ifdef MF_FLASH_BACKUP_ADDR
    info_backup = (mf_flash_t*)MF_FLASH_BACKUP_ADDR;
#endif

    init_temp();

    if (block_err(info_main))
        return MF_ERR_BLOCK;

    memcpy(mf_temp, info_main, MF_FLASH_BLOCK_SIZE);
    return MF_OK;
}

mf_status_t mf_init(void) {
    mf_status_t status = mf_try_init();
    if (status == MF_ERR_BLOCK) {
        return mf_fix();
    }
    return status;
}

mf_status_t mf_save(void) {
#ifdef MF_FLASH_BACKUP_ADDR
    if (!mf_erase((uint32_t)(info_backup)))
        return MF_ERR_IO;
    if (!mf_write((uint32_t)info_backup, info_main))
        return MF_ERR_IO;
#endif
    block_calc_sumcheck(mf_data);
    if (!mf_erase((uint32_t)info_main))
        return MF_ERR_IO;
    if (!mf_write((uint32_t)info_main, mf_temp))
        return MF_ERR_IO;
    return MF_OK;
}

mf_status_t mf_load(void) {
    if (block_err(info_main))
        return MF_ERR_BLOCK;
    memcpy(mf_temp, info_main, MF_FLASH_BLOCK_SIZE);
    return MF_OK;
}

mf_status_t mf_purge(void) {
    init_temp();
    if (!init_block(info_main))
        return MF_ERR_IO;
#ifdef MF_FLASH_BACKUP_ADDR
    if (!init_block(info_backup))
        return MF_ERR_IO;
#endif
    return MF_OK;
}

static const char* get_key_name(mf_key_t* key) {
    return (char*)((uint8_t*)key + sizeof(mf_key_t));
}

static void* get_key_ptr(mf_key_t* key) {
    return (void*)((uint8_t*)key + sizeof(mf_key_t) + key->name_size);
}

static size_t get_key_size(mf_key_t* key) {
    return sizeof(mf_key_t) + key->name_size + key->data_size;
}

static mf_key_t* get_next_key(mf_key_t* key) {
    if (!key->next_key)
        return NULL;
    return (mf_key_t*)(((uint8_t*)key) + get_key_size(key));
}

static mf_key_t* get_prev_key(mf_key_t* key) {
    if (key == &mf_data->key)
        return NULL;
    mf_key_t* prev_key = &mf_data->key;
    while (get_next_key(prev_key) != key) {
        prev_key = get_next_key(prev_key);
    }
    return prev_key;
}

static mf_key_t* find_last_key(void) {
    if (block_empty(mf_data)) {
        return NULL;
    }
    mf_key_t* ans = &mf_data->key;
    while (ans->next_key) {
        ans = get_next_key(ans);
    }
    return ans;
}

static mf_key_t* find_key(const char* name) {
    if (block_empty(mf_data)) {
        return NULL;
    }
    mf_key_t* ans = &mf_data->key;
    while (ans->next_key) {
        if (strcmp(name, get_key_name(ans)) == 0) {
            return ans;
        }
        ans = get_next_key(ans);
    }
    if (strcmp(name, get_key_name(ans)) == 0) {
        return ans;
    } else {
        return NULL;
    }
}

size_t mf_len(void) {
    if (block_empty(mf_data)) {
        return 0;
    }
    size_t len = 1;
    mf_key_t* ans = &mf_data->key;
    while ((ans = get_next_key(ans)) != NULL) {
        len++;
    }
    return len;
}

mf_status_t mf_add_key(const char* name, const void* data, size_t size) {
    if (find_key(name) != NULL) {
        return MF_ERR_EXIST;
    }

    mf_key_t* key;
    uint8_t* ptr;
    mf_key_t* last_key = find_last_key();
    size_t name_size = strlen(name) + 1;

    if (last_key == NULL) {
        key = &mf_data->key;
        ptr = (uint8_t*)&mf_data->key + sizeof(mf_key_t);
    } else {
        key = (mf_key_t*)(((uint8_t*)last_key) + get_key_size(last_key));
        ptr = (uint8_t*)key + sizeof(mf_key_t);
    }

    if ((uint8_t*)key + sizeof(mf_key_t) + size + name_size >
        mf_temp + MF_FLASH_BLOCK_SIZE - 1) {
        return MF_ERR_FULL;
    }

    memcpy(ptr, name, name_size - 1);
    ptr[name_size - 1] = 0;
    ptr += name_size;
    memcpy(ptr, data, size);

    key->next_key = false;
    key->name_size = name_size;
    key->data_size = size;

    if (last_key != NULL) {
        last_key->next_key = true;
    }

    return MF_OK;
}

mf_status_t mf_del_key(const char* name) {
    if (block_empty(mf_data)) {
        return MF_ERR_NULL;
    }
    mf_key_t* key = find_key(name);
    if (key == NULL) {
        return MF_ERR_NULL;
    }
    mf_key_t* last_key = find_last_key();
    size_t key_size = get_key_size(key);
    if (last_key == key) {
        mf_key_t* prev_key = get_prev_key(key);
        if (prev_key == NULL) {  // only one key
            memset(((uint8_t*)key) + sizeof(mf_key_t), MF_FLASH_FILL,
                   key_size - sizeof(mf_key_t));
            mf_data->key.name_size = 0;
            mf_data->key.data_size = 0;
            mf_data->key.next_key = false;
        } else {
            prev_key->next_key = false;
            memset(key, MF_FLASH_FILL, key_size);
        }
    } else {
        size_t move_size = (uint8_t*)last_key - (uint8_t*)key +
                           get_key_size(last_key) - key_size;
        uint8_t* move_src = (uint8_t*)key + key_size;
        uint8_t* move_dst = (uint8_t*)key;
        memmove(move_dst, move_src, move_size);
        memset(move_dst + move_size, MF_FLASH_FILL, key_size);
    }
    return MF_OK;
}

mf_status_t mf_mod_key(const char* name, const void* data, size_t size) {
    mf_key_t* key = find_key(name);
    if (key == NULL) {
        return MF_ERR_NULL;
    }
    if (key->data_size != size) {
        return MF_ERR_SIZE;
    }

    memcpy(get_key_ptr(key), data, size);

    return MF_OK;
}

mf_status_t mf_get_key(const char* name, void* data, size_t size) {
    mf_key_t* key = find_key(name);
    if (key == NULL) {
        return MF_ERR_NULL;
    }
    if (key->data_size > size) {
        return MF_ERR_SIZE;
    }

    memcpy(data, get_key_ptr(key), size);
    return MF_OK;
}

mf_status_t mf_set_key(const char* name, const void* data, size_t size) {
    mf_key_t* key = find_key(name);

    if (key == NULL) {
        return mf_add_key(name, data, size);
    }

    if (key->data_size != size) {
        mf_status_t status = mf_del_key(name);
        if (status != MF_OK) {
            return status;
        }
        return mf_add_key(name, data, size);
    }

    memcpy(get_key_ptr(key), data, size);

    return MF_OK;
}

mf_status_t mf_sync_key(const char* name, void* data, size_t size) {
    mf_key_t* key = find_key(name);

    if (key == NULL || key->data_size != size) {
        return mf_set_key(name, data, size);
    }

    memcpy(data, get_key_ptr(key), size);

    return MF_OK;
}

bool mf_has_key(const char* name) {
    return find_key(name) != NULL;
}

mf_keyinfo_t mf_search_key(const char* name) {
    mf_key_t* key = find_key(name);
    if (key == NULL) {
        return (mf_keyinfo_t){.name = NULL, .data = NULL, .data_size = 0};
    }
    return (mf_keyinfo_t){.name = get_key_name(key),
                          .data = get_key_ptr(key),
                          .data_size = key->data_size};
}

const void* mf_get_key_ptr(const char* name) {
    mf_key_t* key = find_key(name);
    if (key == NULL) {
        return NULL;
    }
    return get_key_ptr(key);
}

size_t mf_get_key_size(const char* name) {
    mf_key_t* key = find_key(name);
    if (key == NULL) {
        return 0;
    }
    return key->data_size;
}

bool mf_iter(mf_keyinfo_t* key) {
    mf_key_t* temp;
    if (block_empty(mf_data)) {
        return false;
    }
    if (key->_iter_key == NULL) {
        temp = &mf_data->key;
    } else {
        temp = get_next_key(key->_iter_key);
        if (temp == NULL) {
            key->_iter_key = NULL;
            return false;
        }
    }
    *key = (mf_keyinfo_t){.name = get_key_name(temp),
                          .data = get_key_ptr(temp),
                          .data_size = temp->data_size,
                          ._iter_key = (void*)temp};
    return true;
}
