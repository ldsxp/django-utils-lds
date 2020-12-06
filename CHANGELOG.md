# 更改日志

此项目的所有显着更改都将记录在此文件中。

此项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。

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

