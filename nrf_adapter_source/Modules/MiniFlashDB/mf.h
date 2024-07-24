#ifndef __MF_H__
#define __MF_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <ctype.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char* name;
    const void* data;
    uint32_t data_size;
    void* _iter_key;  // for mf_iter()
} mf_keyinfo_t;

typedef enum {
    MF_OK = 0,          // 操作成功
    MF_ERR = -1,        // 未知错误
    MF_ERR_FULL = -2,   // 数据库已满
    MF_ERR_NULL = -3,   // 键值不存在
    MF_ERR_EXIST = -4,  // 键值已存在
    MF_ERR_SIZE = -5,   // 数据大小不匹配
    MF_ERR_IO = -6,     // IO错误(FALSH读写错误)
    MF_ERR_BLOCK = -7,  // FLASH块错误(数据区域被破坏)
} mf_status_t;

/**
 * @brief 初始化MiniFlashDB
 * @retval 操作结果 (MF_OK/MF_ERR_IO)
 * @note   如果数据库损坏会自动尝试修复
 */
mf_status_t mf_init(void);

/**
 * @brief 尝试初始化MiniFlashDB, 检测到数据库损坏时返回错误
 * @retval 操作结果 (MF_OK/MF_ERR_IO/MF_ERR_BLOCK)
 */
mf_status_t mf_try_init(void);

/**
 * @brief  执行数据库保存
 * @retval 操作结果 (MF_OK/MF_ERR_IO)
 */
mf_status_t mf_save(void);

/**
 * @brief  重载数据库, 丢弃所有未保存的更改
 * @retval 操作结果 (MF_OK/MF_ERR_BLOCK)
 */
mf_status_t mf_load(void);

/**
 * @brief   执行数据库清空
 * @warning 会同时清空备份区，危险操作
 * @retval  操作结果 (MF_OK/MF_ERR_IO)
 */
mf_status_t mf_purge(void);

/**
 * @brief   尝试修复数据库
 * @retval  操作结果 (MF_OK/MF_ERR_IO)
 * @note    错误时, 如存在有效BACKUP区则恢复, 否则清空数据库
 * @warning 会丢弃所有未保存的更改
 */
mf_status_t mf_fix(void);

/**
 * @brief 获取数据库键值数量
 * @retval 数据库键值数量
 */
size_t mf_len(void);

/**
 * @brief 添加新的键值
 * @param  name 键值名称
 * @param  data 键值数据指针
 * @param  size 数据大小
 * @retval 操作结果
 * @note   如果键值已存在，则抛出MF_ERR_EXIST错误
 * @note   如果数据库已满，则抛出MF_ERR_FULL错误
 */
mf_status_t mf_add_key(const char* name, const void* data, size_t size);

/**
 * @brief 删除已有键值
 * @param  name 键值名称
 * @retval 操作结果
 * @note   如果键值不存在，则抛出MF_ERR_NULL错误
 */
mf_status_t mf_del_key(const char* name);

/**
 * @brief 修改已有键值的数据
 * @param  name 键值名称
 * @param  data 键值数据指针
 * @param  size 数据大小
 * @retval 操作结果
 * @note   如果键值不存在，则抛出MF_ERR_NULL错误
 * @note   如果数据大小与当前键值不匹配，则抛出MF_ERR_SIZE错误
 */
mf_status_t mf_mod_key(const char* name, const void* data, size_t size);

/**
 * @brief 获取键值数据
 * @param  name 键值名称
 * @param  data 缓冲区指针
 * @param  size 缓冲区大小
 * @retval 操作结果
 */
mf_status_t mf_get_key(const char* name, void* data, size_t size);

/**
 * @brief 自动设置键值数据
 * @note  如果键值不存在则添加, 否则修改, 数据大小不匹配则重新分配
 * @param  name 键值名称
 * @param  data 键值数据指针
 * @param  size 数据大小
 * @retval 操作结果
 */
mf_status_t mf_set_key(const char* name, const void* data, size_t size);

/**
 * @brief 从数据库同步键值数据
 * @note  如果键值不存在或大小不匹配则设置当前值, 存在则同步数据到当前值
 * @param  name 键值名称
 * @param  data 键值数据指针
 * @param  size 数据大小
 * @retval 操作结果
 */
mf_status_t mf_sync_key(const char* name, void* data, size_t size);

/**
 * @brief 检查键值是否存在
 * @param  name 键值名称
 * @retval 是否存在
 */
bool mf_has_key(const char* name);

/**
 * @brief 搜索键值信息
 * @param  name 键值名称
 * @retval 键值信息
 * @note   如果键值不存在, 返回name字段为NULL
 */
mf_keyinfo_t mf_search_key(const char* name);

/**
 * @brief 获取键值对应的数据指针
 * @param  name 键值名称
 * @retval 键值数据指针 (NULL: 未找到)
 */
const void* mf_get_key_ptr(const char* name);

/**
 * @brief 获取键值数据大小
 * @param  name 键值名称
 * @retval 数据大小 (0: 未找到)
 */
size_t mf_get_key_size(const char* name);

/**
 * @brief 循环遍历数据库
 * @param[out]  key 键值信息指针(必须初始化为{0})
 * @retval 是否可以继续遍历
 */
bool mf_iter(mf_keyinfo_t* key);

#if 1  // Helper functions

#define __MF_HELPER_DECLARE(name, type)                                      \
    static inline bool mf_hset_##name(const char* key, type value) {         \
        return mf_set_key(key, &value, sizeof(type)) == MF_OK;               \
    }                                                                        \
    static inline type mf_hget_##name(const char* key, type def) {           \
        type value;                                                          \
        return mf_get_key(key, &value, sizeof(type)) == MF_OK ? value : def; \
    }
__MF_HELPER_DECLARE(u8, uint8_t)
__MF_HELPER_DECLARE(u16, uint16_t)
__MF_HELPER_DECLARE(u32, uint32_t)
__MF_HELPER_DECLARE(u64, uint64_t)
__MF_HELPER_DECLARE(i8, int8_t)
__MF_HELPER_DECLARE(i16, int16_t)
__MF_HELPER_DECLARE(i32, int32_t)
__MF_HELPER_DECLARE(i64, int64_t)
__MF_HELPER_DECLARE(f32, float)
__MF_HELPER_DECLARE(f64, double)
#undef __MF_HELPER_DECLARE

#endif  // Helper functions

#ifdef __cplusplus
}
#endif

#endif /* __MF_H__ */
