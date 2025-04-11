#!/bin/sh
# 在 import 语句后添加 debounceSearch 的定义
sed -i '/import { debounce } from/a\
// 搜索防抖\
const debounceSearch = debounce(() => {\
  refreshShots();\
}, 500);' /app/src/components/ShotList.vue

# 删除原位置的 debounceSearch 定义
sed -i '/^\/\/ 搜索防抖$/,/^}, 500);$/d' /app/src/components/ShotList.vue

# 显示修改结果
echo "修复已完成。" 