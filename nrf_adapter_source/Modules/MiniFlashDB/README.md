# Mini Flash

嵌入式Flash数据库，无磨损平衡等功能，但是有极低的Flash占用（stm32 -Og编译仅占用1.7k）和对不支持逆序写入的Flash（STM32L4/G4）的支持。

## 使用方法

### CMakelists.txt

```
add_subdirectory(${MiniFlashDB_PATH} mf.out)

target_include_directories(
    MiniFlash
    PUBLIC ${MiniFlashDB_CONFIG_FILE_PATH}
)
```

### mf_config.h

示例配置文件在 `./config`文件夹下。请将 `mf_config.h`放在`${MiniFlashDB_CONFIG_FILE_PATH}`目录下，由cmake加入头文件列表

```c
// mf_config.h

/* 一块FLASH空间的大小 */
#define MF_FLASH_BLOCK_SIZE (2048)

/* 主FLASH地址 */
#define MF_FLASH_MAIN_ADDR (flash_1)

/* 备份FLASH地址 */
#define MF_FLASH_BACKUP_ADDR (flash_2)

/* Flash读写函数 */
#define MF_ERASE mf_erase
#define MF_WRITE mf_write

static void mf_erase(void *addr) {
  /* 从addr开始，擦除长度为MF_FLASH_BLOCK_SIZE的flash */
  ...
}

static void mf_write(void *addr, void *buf) {
  /* 从addr开始，把buf写入长度为MF_FLASH_BLOCK_SIZE的flash */
  ...
}

```

## API

```c
/* 初始化 */
void mf_init();

/* 添加键值 */
mf_status_t mf_add_key(const char *name, void *data, size_t size);

/* 设置键值数据 */
mf_status_t mf_set_key(const char *name, const void *data, size_t size);

/* 查找键值 */
mf_key_info_t *mf_search_key(const char *name);

/* 获取键值数据 */
uint8_t *mf_get_key_data(mf_key_info_t *key);

/* 获取键值名称 */
const char *mf_get_key_name(mf_key_info_t *key);
```
