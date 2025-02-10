# 这个文件仅支持修改钢铁雄心4的国策文件，理论上所有版本。

## 该工具由AI使用python语言写的，默认代码功能：
1. 将持续时间大于14天的国策批量改为14天
2. 将添加1个科研槽的国策改为添加2个科研槽
3. 除了常规添加方式外，还支持文件拖入的方式进行添加

## 自编译注意事项：
1. 该工具依赖库：`tkinterdnd2`
2. 编译语句参考：`pyinstaller --onefile --windowed --add-data "path/to/tkinterdnd2;tkinterdnd2" modify_focus_file_drop.py`
3. ``path/to/tkinterdnd2`` 需要自行修改
   - 可通过 `pip show tkinterdnd2` 命令获取位置
