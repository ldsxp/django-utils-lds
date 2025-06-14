# 更改日志

此项目的所有显着更改都将记录在此文件中。

此项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [1.3.10]
### Fixed
- 修复confirm_yes_no错误

## [1.3.9]
### Fixed
- 修复导入的时候变量修改发生的错误
### Changed
- 以后修改记录不再添加日期

## [1.3.8] - 2024-11-06
### Fixed
- 修复打开文件错误

## [1.3.7] - 2024-11-06
### Fixed
- 修复多表导入错误

## [1.3.6] - 2024-10-24
### Fixed
- TableData 不要修改 fields ，会影响我们获取 Django 的字段

## [1.3.5] - 2024-10-24
### Changed
- 取消django版本限制
- 清理ilds中存在的代码
- 删除重复代码

## [1.3.4] - 2024-10-24
### Changed
- 添加 djt.py 示例

## [1.3.3] - 2024-10-23
### Changed
- TableData 添加 fields 保存导入的标题名

## [1.3.2] - 2024-10-23
### Changed
- TableData 排除的字段也添加到附加内容

## [1.3.1] - 2024-10-23
### Changed
- 优化 TableData 的导入标题信息

## [1.3.0] - 2024-10-23
### Added
- TableData 支持保存附加字段

## [1.2.0] - 2024-10-22
### Changed
- 修复 DjangoTool 使用变量没有正确设置的错误

## [1.1.0] - 2024-10-17
### Added
- 添加 DjangoTool，以为我们经常每个网站放一个，但是这样不方便维护，统一调用一个就会很方便

## [1.0.0] - 2024-07-18
### Changed
- 重命名版本号为 X.X.X

## [2024.1.15] - 2024-01-15
### Changed
- model.TableData 导入文件的时候，跳过空白标题

## [2023.12.28-2] - 2023-12-28
### Changed
- import_export.BaseImportExcel 导入文件的时候支持解析DateTimeField

## [2023.12.28] - 2023-12-28
### Changed
- import_export.BaseImportExcel 导入文件的时候优先使用别名

## [2023.9.22-2] - 2023-09-22
### Changed
- import_export.BaseImportExcel 把读取文件单独做成一个方法

## [2023.9.22] - 2023-09-22
### Changed
- import_export.BaseImportExcel 添加导入总数

## [2023.9.21-2] - 2023-09-21
### Fixed
- import_export.BaseImportExcel 修复导入错误

## [2023.9.21] - 2023-09-21
### Changed
- import_export.BaseImportExcel 处理日期格式、添加标题不在第一行的例子

## [2023.6.28] - 2023-06-28
### Changed
- import_export.BaseImportExcel 支持 exclude_sheet 跳过表格

## [2023.6.20] - 2023-06-20
### Changed
- 版本改为日期模式
- import_export.BaseImportExcel 支持 csv 格式

## [2023.5.31] - 2023-05-31
### Added
- admin.QuickDeleteQuerysetAction 直接删除选择的内容（不需要确认，谨慎操作）

## [2023.5.11] - 2023-05-11
### Fixed
- import_export.BaseImportExcel 支持更多的布尔导入类型

## [2022.11.22] - 2022-11-22
### Fixed
- 替换 DJango 不支持的 urlquote

## [2022.10.14] - 2022-10-14
### Added
- model.sync_model 同步模型数据

## [2022.5.23] - 2022-05-23
### Fixed
- model.annotate 修复集合数据产生多条重复数据问题

## [2022.5.18] - 2022-05-18
### Added
- timezone.get_local_now 获取本地的当前时间

## [2022.4.22] - 2022-04-22
### Fixed
- 处理模型 verbose_name 的时候转为str，因为有时候他的值是惰性的翻译

## [2022.4.15.2] - 2022-04-15
### Fixed
- import_export.BaseImportExcel 修复多表导入的时候重复导入内容

## [2022.4.15.1] - 2022-04-15
### Added
- import_export.BaseImportExcel 添加 read 保存正在读取的数据类

## [2022.4.15] - 2022-04-15
### Changed
- import_export.BaseImportExcel 取消导入的时候添加附加数据 adding_data，因为这个是我们自定义的数据，导入的时候使用 model_kwargs

## [2022.4.6] - 2022-04-06
### Added
- import_export.BaseImportExcel 导入的时候添加附加数据 adding_data

## [2022.3.26] - 2022-03-26
### Added
- admin.FileSizeQuerysetAction 计算选择内容的文件大小

## [2022.3.3] - 2022-03-03
### Changed
- import_export.BaseImportExcel 添加实例属性：model_kwargs

## [2022.3.2] - 2022-03-02
### Changed
- 版本改为日期模式
- import_export.BaseImportExcel 支持 csv 格式

## [0.0.30] - 2022-02-15
### Changed
- import_export.BaseImportExcel 添加实例属性：time_cost

## [0.0.29] - 2022-02-15
### Changed
- import_export.BaseImportExcel 添加 end_import 结束导入数据的时候调用

## [0.0.28] - 2022-02-15
### Changed
- import_export.BaseImportExcel 添加实例属性：file、adding_data

## [0.0.27] - 2022-01-21
### Added
- user.create_user 添加创建用户的函数
### Changed
- - user.add_superuser 使用 create_user 创建超级管理员

## [0.0.26] - 2021-12-16
### Changed
- import_export import_csv 在导入的时候支持重命名标题名和排除标题

## [0.0.25] - 2021-12-16
### Changed
- import_export LdsExportCsv 设置默认排除字段为空，数据日期改为 YYYY-MM-DD，方便导入数据库

## [0.0.24] - 2021-12-07
### Added
- model.confirm_db 添加 db_name_list 参数，支持可以直接修改的数据库名字列表

## [0.0.23] - 2021-11-05
### Added
- admin.CopyQuerysetAction 复制选中的内容(只支持复制单个内容)

## [0.0.22] - 2021-07-27
### Added
- model.confirm_db 支持数据库名字

## [0.0.21] - 2021-07-05
### Added
- import_export.BaseImportExcel 导入 Excel 的基础类

## [0.0.20] - 2021-04-03
### Added
- model.calc_file_size 从 QuerySet 计算文件大小

## [0.0.19] - 2020-12-13
### Added
- admin.UpdateQuerysetAction 自定义更新类型的动作

## [0.0.18] - 2020-12-06
### Added
- admin.BaseUserAdmin 普通用户只能看自己（owner 字段）的内容，保存修改的时候添加用户信息（write_uid、create_uid）
- admin.SeparateActions 添加动作的分隔符（separate_1、separate_2、separate_3、separate_4、separate_5、separate_actions）
- admin.FavoriteActions 添加收藏动作（收藏、取消收藏）

## [0.0.17] - 2020-11-26
### Added
- model.annotate 添加 values_fields 参数，用来分组显示的字段名

## [0.0.16] - 2020-08-30
### Added
- admin.MultiDBModelAdmin 添加在 Django 管理界面中使用多数据库

## [0.0.15] - 2020-08-25
### Changed
- admin.ExportCsvMixin 支持自定义导出文件名

## [0.0.14] - 2020-07-04
### Added
- model.annotate 添加聚合函数
### Changed
- model.group_by 使用新添加的 annotate

## [0.0.13] - 2020-07-01
### Changed
- util.django_setup 导入模块错误的时候，我们也传递错误

## [0.0.12] - 2020-06-22
### Fixed
- model.TableData 清理字段的时候保留数值 0

## [0.0.11] - 2020-06-06
### Changed
- model.TableData 支持清理字段
### Fixed
- import_export.import_csv 修复字段转换问题

## [0.0.10] - 2020-04-03
### Changed
- model.TableData 设置自定义转换的时候检查是否包含此字段

## [0.0.9] - 2020-03-24
### Changed
- model.TableData 添加更多重复字段相关信息

## [0.0.8] - 2020-03-23
### Changed
- model.TableData 添加检查是否有重复字段

## [0.0.7] - 2020-03-20
### Changed
- model.TableData 不能导入的时候提示更详细信息

## [0.0.6] - 2020-03-18
### Changed
- import_export.ModelData 移动到 model.ModelData

## [0.0.5] - 2020-03-17
### Changed
- 优化导入函数 ModelData
- 导入 csv 支持分批和转换内容

## [0.0.4] - 2020-03-06
### Changed
- TableData 设置标题的时候排除字段和字段名字

## [0.0.3] - 2020-03-06
### Changed
- 修改TableData中的属性名字

## [0.0.2] - 2020-02-27
### Added
- 拷贝 ilds.django 中的函数到本库（注意：我们只是拷贝了过来，还没有测试）

## [0.0.1] - 2019-12-09
**初始版本**
### Added
- 无
### Changed
- 无
### Fixed
- 无

