# ---------------------------------------
#   程序：admin.py
#   版本：0.5
#   作者：lds
#   日期：2021-11-05
#   语言：Python 3.X
#   说明：django 后台管理相关的动作和功能
# ---------------------------------------

import csv

from ilds.file import human_size

from django.contrib import admin
from django.contrib import messages
from urllib.parse import quote as urlquote

from django.http import HttpResponse
from django.db.models import Sum

from djlds.model import ModelFields


# https://docs.djangoproject.com/zh-hans/4.2/ref/contrib/admin/actions/


class ExportCsvMixin:
    """
    导出 CSV 格式文件的动作

    支持自定义的内容：
    # 设置导出 Csv 文件的编码
    csv_charset = 'utf-8-sig'  # gb2312 有些字符不支持
    # 自定义导出 ForeignKey 字段内容
    related_fields = {'ForeignKey字段': {'fields': ['字段1', '字段2'], }}
    # 排除导出字段
    csv_export_exclude = []
    # 导出 csv 文件的名字
    export_csv_name = '后台数据'

    # 添加到动作
    actions = ['export_as_csv', 'export_all_as_csv', ]
    """

    # def get_actions(self, request):
    #     # 这个可以用来直接添加到动作中，但是有两个问题
    #     # 1 这个要在类继承的最前面
    #     # 2 self.export_as_csv 需要三个参数 modeladmin, request, queryset
    #     actions = super().get_actions(request)
    #     # print(actions)
    #     # 添加自定义动作到动作列表
    #     actions['copy_data_to_target_database'] = (
    #         self.export_as_csv,
    #         'copy_data_to_target_database',
    #         '导出所选的 %(verbose_name_plural)s 为csv文件',
    #     )
    #
    #     return actions

    def export_as_csv(self, request, queryset, is_all=False):
        if getattr(self, 'using', None):
            queryset = queryset.using(self.using)

        meta = self.model._meta
        related_fields = getattr(self, 'related_fields', {})
        export_exclude = getattr(self, 'csv_export_exclude', [])

        # 获取需要导出的 ForeignKey 字段
        for related_field, data in related_fields.items():
            if getattr(meta.concrete_model, related_field, None):
                cg_model = getattr(meta.concrete_model, related_field).field.related_model
                # 另外一种获取模型的方法
                # [field for field in meta.fields if field.name == 'cg_hetong_bianhao'][0].remote_field.model
                m = ModelFields(cg_model)
            else:
                raise ValueError(f'没有找到 {related_field} 模型')
            data['names'] = []
            for field in data['fields']:
                verbose = m.field_to_verbose(field)
                if verbose is None:
                    raise ValueError(f'没有找到 {field} 字段')
                # 写入标题
                data['names'].append(verbose)

        field_names = []
        # 写入标题
        field_verbose_name = []

        for field in meta.fields:
            if field.name in export_exclude or field.verbose_name in export_exclude:
                continue
            field_names.append(field.name)
            if field.name in related_fields:
                field_verbose_name.extend(related_fields[field.name]['names'])
            else:
                field_verbose_name.append(field.verbose_name)

        response = HttpResponse(content_type='text/csv', charset=getattr(self, 'csv_charset', 'utf-8-sig'))
        export_csv_name = getattr(self, 'export_csv_name', meta)
        if is_all:
            export_filename = urlquote(f'导出 {export_csv_name} 全部内容')
        else:
            export_filename = urlquote(f'导出 {export_csv_name} 中选择的内容')
        response['Content-Disposition'] = f"attachment; filename={export_filename}.csv"
        writer = csv.writer(response)

        writer.writerow(field_verbose_name)
        for obj in queryset:
            rows = []
            for field in field_names:
                if field in related_fields:
                    related_obj = getattr(obj, field, None)
                    if related_obj:
                        for related_field in related_fields[field]['fields']:
                            val = getattr(related_obj, related_field)
                            rows.append(val)
                    else:
                        rows.extend(['' for _ in related_fields[field]['fields']])
                else:
                    val = getattr(obj, field)
                    rows.append(val)
            writer.writerow(rows)

        return response

    def export_all_as_csv(self, request, queryset):
        return self.export_as_csv(request, self.model.objects.all(), is_all=True)

    # Export Selected
    export_as_csv.short_description = "导出已选中（csv）"
    export_all_as_csv.short_description = "导出全部（csv）"


class MultiDBModelAdmin(admin.ModelAdmin):
    """
    在 Django 管理界面中使用多数据库
    https://docs.djangoproject.com/zh-hans/3.0/topics/db/multi-db/#exposing-multiple-databases-in-django-s-admin-interface
    """
    # 要使用的数据库
    using = None

    def save_model(self, request, obj, form, change):
        """
        告诉 Django 将对象保存到“指定”数据库
        """
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        """
        告诉 Django 从“指定”数据库中删除对象
        """
        obj.delete(using=self.using)

    def get_queryset(self, request):
        """
        告诉 Django 在“指定”数据库中查找对象
        """
        return super(MultiDBModelAdmin, self).get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        告诉 Django 使用“指定”数据库上的查询填充 ForeignKey 小部件
        """
        return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        告诉 Django 使用“指定”数据库上的查询填充 ManyToMany 小部件
        """
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request, using=self.using, **kwargs)


class BaseUserAdmin(admin.ModelAdmin):
    """
    1. 用来处理文件管理、文件分类、这些 model 的 用户字段自动补充
    2. 用来针对 queryset 过滤当前用户的数据
    """
    # 在编辑、新增页面上排除
    exclude = ('write_uid', 'create_uid',)

    def get_queryset(self, request):
        """
        使当前登录的用户只能看到自己内容
        """
        qs = super(BaseUserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        # 过滤当前用户只能看到自己的文章
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if change:
            obj.write_uid = request.user
        else:
            # obj.write_uid = request.user
            obj.create_uid = request.user
        return super(BaseUserAdmin, self).save_model(request, obj, form, change)


class SeparateActions:
    """
    分割动作，方便区分不同功能
    """

    actions = ['separate_1', 'separate_2', 'separate_3', 'separate_4', 'separate_5', 'separate_actions']

    def separate_1(self, request, queryset):
        self.message_user(request, '未选择动作', level=messages.WARNING)

    def separate_2(self, request, queryset):
        self.message_user(request, '未选择动作', level=messages.WARNING)

    def separate_3(self, request, queryset):
        self.message_user(request, '未选择动作', level=messages.WARNING)

    def separate_4(self, request, queryset):
        self.message_user(request, '未选择动作', level=messages.WARNING)

    def separate_5(self, request, queryset):
        self.message_user(request, '未选择动作', level=messages.WARNING)

    def separate_actions(self, request, queryset):
        self.message_user(request, '未选择动作', level=messages.WARNING)

    separate_1.short_description = "---------"
    separate_2.short_description = "---------"
    separate_3.short_description = "---------"
    separate_4.short_description = "---------"
    separate_5.short_description = "---------"
    separate_actions.short_description = "---------"


class FavoriteActions:
    # actions = ['add_favorite', 'del_favorite']

    def add_favorite(self, request, queryset):
        """
        添加到收藏
        """
        if request.user.is_superuser:
            try:
                count = queryset.filter(is_favorite=False).count()
                update = queryset.update(is_favorite=True)
                self.message_user(request, f'收藏: {count}:{update}')
            except Exception as e:
                self.message_user(request, f'修改失败: {e}', level=messages.ERROR)
        else:
            self.message_user(request, '修改失败，没有权限!', level=messages.ERROR)

    def del_favorite(self, request, queryset):
        """
        取消收藏
        """
        if request.user.is_superuser:
            try:
                count = queryset.filter(is_favorite=True).count()
                update = queryset.update(is_favorite=False)
                self.message_user(request, f'取消收藏: {count}:{update}')
            except Exception as e:
                self.message_user(request, f'修改失败: {e}', level=messages.ERROR)
        else:
            self.message_user(request, '修改失败，没有权限!', level=messages.ERROR)

    add_favorite.short_description = "收藏"
    del_favorite.short_description = "取消收藏"


class UpdateQuerysetAction:
    """
    自定义更新类型的动作
    """

    # actions = ['自定义更新类型的动作']

    def _update_queryset_action(self, name, request, queryset, is_superuser=False, **kwargs):
        """
        更新查询集
        """
        if is_superuser and not request.user.is_superuser:
            self.message_user(request, f'管理员才有权限{name}!', level=messages.ERROR)
            return
        try:
            self.message_user(request, f'{name} {queryset.update(**kwargs)}')
        except Exception as e:
            self.message_user(request, f'{name}失败: {e}', level=messages.ERROR)

    # _update_queryset_action.short_description = "自定义更新类型的动作"


class CopyQuerysetAction:
    # actions = ['copy_queryset']

    def copy_queryset(self, request, queryset):
        """
        复制选中的内容(只支持复制单个内容)
        """
        count = queryset.count()
        if count > 1:
            self.message_user(request, f'不能复制 {count} 个内容，我们只支持复制单个内容', level=messages.ERROR)
        else:
            obj = queryset[0]
            obj.id = None
            obj.save()
            self.message_user(request, f'复制 {obj} 成功', level=messages.INFO)

    copy_queryset.short_description = "复制选中的内容(只支持复制单个内容)"


class FileSizeQuerysetAction:
    # actions = ['action_calc_file_size']

    def action_calc_file_size(self, request, queryset):
        """
        计算选择内容的文件大小
        """
        field = getattr(self, 'file_size_field', 'file_size')
        exclude_count = queryset.filter(**{field: None}).count()
        if exclude_count:
            info = f'（跳过 {exclude_count} 个文件大小为空的内容）'
            queryset = queryset.exclude(**{field: None})
        else:
            info = ''
        file_size = queryset.aggregate(**{field: Sum(field)})[field]
        # print(human_size(file_size))
        self.message_user(request, f'选择内容的文件大小：{human_size(file_size)}' + info, level=messages.INFO)

    action_calc_file_size.short_description = "计算选择内容的文件大小"


class QuickDeleteQuerysetAction:
    # actions = ['action_quick_delete']

    def action_quick_delete(self, request, queryset):
        """
        直接删除选择的内容（不需要确认，谨慎操作）
        """

        self.message_user(request, f'{queryset.delete()}', level=messages.INFO)

    action_quick_delete.short_description = "直接删除选择的内容（不需要确认，谨慎操作）"
