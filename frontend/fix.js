// 搜索防抖
const debounceSearch = debounce(() => {
  refreshShots();
}, 500); 