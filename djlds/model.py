# ---------------------------------------
#   程序：model.py
#   版本：0.13
#   作者：lds
#   日期：2022-05-23
#   语言：Python 3.X
#   说明：django 模型相关的函数
# ---------------------------------------

import operator
import os
from functools import reduce
# from collections import OrderedDict

from colorama import Fore, Back, Style

# from django.forms.models import model_to_dict  # 获取模型实例的字典
from django.db.models.base import ModelBase, Model
from django.conf import settings

from django.apps import apps
from django.db import models
# group_by 这个分组 我喜欢
from django.db.models import Aggregate, Avg, Count, Max, Min, StdDev, Sum, Variance
from django.db.models import QuerySet
# # from django.db.models import FileField
from django.db.models import Sum
from django.forms.models import model_to_dict

from djlds.xlsx_util import xl_col_to_name

"""
20181203 添加 搜索多个字段的函数
20181203 ModelFields 添加 获取模型对象
20181203 添加了获取模型的字段，名字和类型的类
20181130 添加 确认是否修改线上数据库（本地操作，因为如果没有修改会直接退出，防止误操作）
20170814 整理了下模型调用
20170814 把模型操作分离出来，以后调用模型都通过这里
20180807 去掉不通用的模型操作，并改成共享库

批量导入例子
loadList = []
kwargs = 需要添加的字段字典
loadList.append(需要添加的库模型(**kwargs))
print('成功导入 %s 行' % len(models_ku.objects.bulk_create(loadList)))
"""


def get_model(value, model_dict=None, is_exact=True) -> Model:
    """
    通过库的名字或模型的名字获取模型

    例子：
        ku_model = get_model('酷狗', model_dict=None, is_exact=True)
        if not ku_model:
            raise RuntimeError('没有找到模型！')

    :param value: 要获取的模型，如果本身就是模型，直接返回
    :param model_dict: 从模型字典（模型名字：模型）中获取模型
    :param is_exact: 精确模式，控制是否匹配文件名中包含模型名的情况
    :return: Model
    """

    if isinstance(value, ModelBase):
        return value

    _model_dict = {app.__name__: app for app in apps.get_models() if
                   'django.contrib.' not in str(app) and '.models.' in str(app)}
    # print(_model_dict)

    # 检查模型的名称
    if value in _model_dict:
        return _model_dict[value]
    elif model_dict is not None:
        if is_exact:
            # 如果是精确模式，匹配以后就可以返回
            if value in model_dict:
                return model_dict[value]
        else:
            # 不是精确模式，主要是处理文件名中包含模型名字的情况
            for ku_name in model_dict.keys():
                # print(ku_name)
                if ku_name in value:
                    return model_dict[ku_name]


def get_search_results(queryset, search_fields, search_term):
    """
    搜索，返回包含查询集的
    来自：from django.contrib.admin.options import ModelAdmin
    """

    # 应用关键字搜索。
    def construct_search(field_name):
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            return "%s__search" % field_name[1:]
        else:
            return "%s__icontains" % field_name

    if search_fields and search_term:
        orm_lookups = [construct_search(str(search_field))
                       for search_field in search_fields]
        for bit in search_term.split():
            or_queries = [models.Q(**{orm_lookup: bit})
                          for orm_lookup in orm_lookups]
            #
            queryset = queryset.filter(reduce(operator.or_, or_queries))

    return queryset


class ModelFields:
    """
    获取模型的字段，名字和类型。

    例子：
    from djlds.model import ModelFields

    print(ModelFields(mymodel).verbose_to_type('标题'))
    for i in ModelFields(mymodel).iter('type'):
        print(i)
    """

    def __init__(self, model, exclude=None):
        """
        初始化
        """
        self.model = model
        self.field_list = []
        self.verbose_list = []
        self.type_list = []
        self.fields = []

        if exclude is None:
            exclude = []
        for f in model._meta.fields:  # model._meta._get_fields(reverse=False) 包括 ManyToMany 字段
            field_name = f.name
            verbose_name = str(f.verbose_name)
            type_name = type(f).__name__
            if field_name in exclude or verbose_name in exclude or type_name in exclude:
                continue
            self.field_list.append(field_name)
            self.verbose_list.append(verbose_name)
            self.type_list.append(type_name)
            self.fields.append(f)

        self.count = len(self.field_list)
        # print(self.field_list)
        # print(self.verbose_list)
        # print(self.type_list)

    def field_to_verbose(self, field):
        """
        通过 field_name 获取 verbose_name
        """
        if field in self.field_list:
            return self.verbose_list[self.field_list.index(field)]

    def field_to_type(self, field):
        """
        通过 field_name 获取 type_name
        """
        if field in self.field_list:
            return self.type_list[self.field_list.index(field)]

    def field_dict(self):
        """
        获取键为 field，值为 verbose_name 的字典
        :
        """
        return {field: self.field_to_verbose(field) for field in self.field_list}

    def verbose_to_field(self, field):
        """
        通过 verbose_name 获取 field_name
        """
        if field in self.verbose_list:
            return self.field_list[self.verbose_list.index(field)]

    def verbose_to_type(self, field):
        """
        通过 verbose_name 获取 type_name
        """
        if field in self.verbose_list:
            return self.type_list[self.verbose_list.index(field)]

    def verbose_dict(self):
        """
        获取键为 verbose_name，值为 field 的字典
        :
        """
        return {verbose: self.verbose_to_field(verbose) for verbose in self.verbose_list}

    def get_field(self, name):
        """
        通过 名字获取 field 属性
        按 field_name -> verbose_name 的顺序查找，
        已经找到就不在继续查找，没有找到返回空
        """
        if name in self.field_list:
            return self.fields[self.field_list.index(name)]
        elif name in self.verbose_list:
            return self.fields[self.verbose_list.index(name)]

    def iter(self, *args):
        """
        获取指定字段的生成器
        """
        iter_dict = {
            'field': self.field_list,
            'verbose': self.verbose_list,
            'type': self.type_list,
        }
        if not args:
            args = ['field']
        else:
            if [arg for arg in args if arg not in iter_dict]:
                raise ValueError(f"参数错误：{args}，可用参数为：'field', 'verbose', 'type'")

        # print([iter_dict[arg][1] for arg in args])
        # print([i for i in range(self.count)])
        return ([iter_dict[arg][i] for arg in args] for i in range(self.count))


class TableData(ModelFields):
    """
    转换 Eccel 数据为 Django 模型数据

    我们继承自 ModelFields ，所以可以使用它所有的功能

    # 例子
    table = TableData(models)
    xiuzheng = {'替换内容1':'替换为1', '替换内容2':'替换为2'}
    r = table.set_title(self.headers_title, **xiuzheng)
    print(table.exclude_info)
    if r:
        raise ValueError(f'字段没有导入：{r}')
    # print(r, table.table_fields, table.index_list)
    """

    def __init__(self, model, exclude=None):
        super().__init__(model, exclude)
        # 标题
        self.title = None
        # Excel列数据对应数据库字段的索引
        self.index_list = None
        # Excel列数据对应数据库的字段名
        self.table_fields = None
        self.exclude_info = []
        self.duplicate_info = {}

    def set_title(self, row, exclude=None, **kwargs):
        """
        设置标题行内容

        我们通过标题行对应的列索引获取数据

        :param row: 标题行内容
        :param exclude: 排除的内容
        :param kwargs: 用来修正数据，数据库的表述和列表标题不同的时候使用
        :return:
        """
        if not isinstance(row, list):
            raise ValueError('Excel行是列表类型！')
        if exclude is None:
            exclude = []

        index_list = []
        table_fields = []
        cannot_import = []
        self.exclude_info = []
        for i, name in enumerate(row):
            if name in exclude:
                self.exclude_info.append(name)
                continue
            # 优先使用别名
            if name in kwargs:
                name = kwargs[name]
            field = self.verbose_to_field(name)
            if field:
                # print(field)
                if name in exclude:
                    self.exclude_info.append(name)
                else:
                    index_list.append(i)
                    table_fields.append(field)
            else:
                cannot_import.append({'Column': xl_col_to_name(i), 'Name': name})

        self.title = row
        self.index_list = index_list
        self.table_fields = table_fields
        self.count = len(table_fields)

        # 检查是否有重复字段
        if self.count != len(set(self.table_fields)):
            check_duplicates = {}
            for i, field in enumerate(self.table_fields):
                if field in check_duplicates:
                    if field not in self.duplicate_info:
                        self.duplicate_info[field] = [{'Column': xl_col_to_name(check_duplicates[field]),
                                                       'Name': self.title[check_duplicates[field]]}]
                    self.duplicate_info[field].append(
                        {'Column': xl_col_to_name(self.index_list[i]), 'Name': self.title[self.index_list[i]]})
                else:
                    check_duplicates[field] = self.index_list[i]

        return cannot_import

    def row_to_dict(self, row):
        """
        获取 Django 模型使用的字典数据

        :param row: Excel行
        :return: model_dict
        """
        return {field: row[self.index_list[i]] for i, field in enumerate(self.table_fields)}

    def get_model_data(self, row):
        """
        获取 Django 模型使用的字典数据
        """
        return self.row_to_dict(row)


class ModelData:
    """
    根据 django 模型转换导入数据

    例子：
    reader = ['rows', 'rows']
    iter_reader = iter(reader)
    model = '数据模型'
    conversion_type = '需要转换格式的字段名'
    export = ModelData(model, next(iter_reader))
    load_list = []
    # 如果需要转换类型
    if isinstance(conversion_type, dict):
        export.conversion_type = conversion_type
    for row in iter_reader:
        # print(ku_field, xls_row, row)
        kwargs = export.get_import_data(row)
        # print(kwargs)
        load_list.append(model(**kwargs))
    model.objects.bulk_create(load_list)
    """

    # 获取字段类型，处理一部分类型
    WIDGETS_MAP = {
        # 'ManyToManyField': 'get_m2m_widget',
        # 'OneToOneField': 'get_fk_widget',
        # 'ForeignKey': 'get_fk_widget',
        # 'DecimalField': widgets.DecimalWidget,
        # 'DateTimeField': widgets.DateTimeWidget,
        # 'DateField': widgets.DateWidget,
        # 'TimeField': widgets.TimeWidget,
        # 'DurationField': widgets.DurationWidget,
        # 'FloatField': float,
        # 'IntegerField': widgets.IntegerWidget,
        # 'PositiveIntegerField': widgets.IntegerWidget,
        # 'BigIntegerField': widgets.IntegerWidget,
        # 'PositiveSmallIntegerField': widgets.IntegerWidget,
        # 'SmallIntegerField': widgets.IntegerWidget,
        # 'AutoField': widgets.IntegerWidget,
        # 'NullBooleanField': widgets.BooleanWidget,
        # 'BooleanField': widgets.BooleanWidget,
    }

    def __init__(self, model, row, import_names=None, exclude=None):

        # 需要转换的 id 然后批量转换
        # 如果有需要 再添加

        # print(filed)

        if exclude is None:
            exclude = []

        self.model = model
        self.import_fields = []
        self.import_index = []
        self.conversion_type = {}
        # 清理字段，有些字段不能为空字符，我们在这里清理
        self.clean_fields = set()

        names = {}
        verbose_names = {}
        if import_names is None:
            import_names = {}

        for f in model._meta.fields:
            # print('处理不同字段内容', isinstance(f, models.BooleanField))
            # print('获取模型的字段名', f.get_internal_type())
            internal_type = f.get_internal_type() if callable(getattr(f, "get_internal_type", None)) else ""
            # print(internal_type, f.verbose_name, f.name)
            names[f.name] = {'name': f.name, 'internal_type': internal_type}
            verbose_names[str(f.verbose_name)] = {'name': f.name, 'internal_type': internal_type}

        for i, field in enumerate(row):
            field = field.strip()
            # 排除的内容
            if field in exclude:
                continue

            # 重命名的内容
            if field in import_names:
                field = import_names[field]

            # 字段名导入
            if field in names:
                self.import_fields.append(names[field]['name'])
                self.import_index.append(i)
                if names[field]['internal_type'] in self.WIDGETS_MAP:
                    self.conversion_type[names[field]['name']] = self.WIDGETS_MAP[names[field]['internal_type']]
            # 按名字导入
            elif field in verbose_names:
                self.import_fields.append(verbose_names[field]['name'])
                self.import_index.append(i)
                if verbose_names[field]['internal_type'] in self.WIDGETS_MAP:
                    self.conversion_type[verbose_names[field]['name']] = self.WIDGETS_MAP[
                        verbose_names[field]['internal_type']]
            # 没有导入的内容
            else:
                # pass
                # print('导入失败：-------------------表头 %s %s 应该为 %s 。-------------------' % (i + 1, field, now_0[i]))
                # print(field, field in names, names, )
                # print(field, field in verbose_names, verbose_names, )
                raise RuntimeError('导入失败：row[%s]："%s" 不能导入数据库。' % (i + 1, field))

    def get_import_data(self, row):
        """
        """
        import_data = {}

        for index, field in zip(self.import_index, self.import_fields):
            if field in self.clean_fields:
                if row[index] == 0:
                    ...
                elif not row[index]:
                    continue
            import_data[field] = row[index]

        for field, func in self.conversion_type.items():
            # print('转换类型', self.conversion_type[field], val)
            import_data[field] = func(import_data[field])

        return import_data


def get_field_file_path(field_file):
    """
    获取 模型 FileField 路径
    """
    # print(_fieldfile.path)
    # print(_fieldfile.upfile.name)
    # print(_fieldfile.read())
    try:
        return field_file.path
    except:
        return None


def get_queryset_sum(queryset, field_list, *args):
    """
    计算 QuerySet 的和 参数 QuerySet 需要求和的字段  需要显示的字段
    """

    kwargs = {}

    try:
        # 获取需要求和的内容
        for i in field_list:
            # print(i)
            if '_quanli_' in i:
                # print('_quanli_')
                continue
            elif i.endswith('_int') or i.endswith('_float'):
                if 'rmb_int' in i:
                    pass
                elif 'fencheng_int' in i:
                    pass
                else:
                    # print(i)
                    kwargs[i] = Sum(i)
        if kwargs:
            return queryset.values(*args).annotate(**kwargs)
        else:
            return None
    except:
        pass
    return None


def calc_sum(query_set, field_list):
    """
    计算 QuerySet 中指定字段的和

    这个和 get_queryset_sum 不同，get_queryset_sum 是按分组求和，calc_sum 是聚合求和

    :param query_set: 数据集
    :param field_list: 需要求和的字段
    :return: 求和字段的字典
    """
    assert isinstance(query_set, QuerySet)
    return query_set.aggregate(**{field: Sum(field) for field in field_list})


def annotate(query_set, fields, func='Count', values_fields=None):
    """
    数据聚合

    :param query_set: 查询集
    :param fields: 字段列表
    :param func: 聚合函数 Aggregate, Avg, Count, Max, Min, StdDev, Sum, Variance
    :param values_fields: 用来分组显示的字段名
    :return: 聚合内容
    """
    assert isinstance(query_set, QuerySet)

    if values_fields is None:
        values_fields = fields

    functions = {
        'Aggregate': Aggregate,
        'Avg': Avg,
        'Count': Count,
        'Max': Max,
        'Min': Min,
        'StdDev': StdDev,
        'Sum': Sum,
        'Variance': Variance,
    }
    return query_set.order_by(*values_fields).values(*values_fields).annotate(
        *[functions[func](field) for field in fields])


def group_by(query_set, group_field):
    """
    util:django 获取分类列表 ( 对某些取到的 QuerySet 分组)

    例如获取厂牌名称
    print(group_by(objs,'shouquan_changpai'))
    》 ['厂牌名称1', '厂牌名称2', ...]

    :param query_set:
    :param group_field: 需要分组的字段
    :return: 分组字段的内容列表
    """

    django_groups = annotate(query_set, [group_field], func='Count')
    # django_groups = query_set.values(group_field).annotate(Count(group_field))
    groups = []
    for dict_ in django_groups:
        # print(dict_)
        groups.append(dict_.get(group_field))
    return groups


def calc_file_size(objs, field='file_size'):
    """
    从 QuerySet 计算文件大小
    """
    return objs.exclude(**{field: None}).aggregate(**{field: Sum(field)})[field]


def get_date_range(queryset, date_field='shujuriqi_date', format_string="%Y-%m-%d"):
    """
    获取 QuerySet 的日期间隔 参数 queryset，日期的字段
    """

    from_date = queryset.order_by(date_field)[:1].values_list(date_field)[0][0].strftime(format_string)
    to_date = queryset.order_by('-' + date_field)[:1].values_list(date_field)[0][0].strftime(format_string)
    return from_date, to_date


def confirm_db(db_name=None, is_sqlite3=True, db_name_list=None, title='确认是否继续修改数据库', message='开始修改数据库'):
    """
    确认是否修改线上数据库
    本地操作，因为如果没有修改会直接退出，防止误操作

    :param db_name: 数据库名字，优先（sqlite3）参数处理
    :param is_sqlite3: 如果是 sqlite3 数据库 直接修改数据
    :param db_name_list: 可以直接修改的数据库名字列表
    :param title: 提示标题
    :param message: 确认后的提示信息
    :return:
    """

    if db_name_list is None:
        db_name_list = []

    name = settings.DATABASES['default']['NAME']
    if db_name is not None and db_name == name:
        return
    elif name in db_name_list:
        return
    elif is_sqlite3 and settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        return

    try:
        import wx
        app = wx.App()
        dlg = wx.MessageDialog(None, f'正在修改数据库({name})，是否继续？', title, wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            print(f'{Fore.MAGENTA}{message}({name}){Style.RESET_ALL}')
            return
    except ModuleNotFoundError:
        from djlds.util import confirm_yes_no
        if confirm_yes_no(title=title, text=f'正在修改数据库({name})，是否继续？\n输入 y 确认，其他任意字符表示取消'):
            print(f'{Fore.MAGENTA}{message}({name}){Style.RESET_ALL}')
            return
    exit(f'退出程序，不修改数据库({name})！')


def sync_model(model, src, dst, fields=None, exclude=None, is_clear=False):
    """
    同步模型数据
    :param model:
    :param src:
    :param dst:
    :param fields:
    :param exclude:
    :param is_clear:
    :return:
    """

    load_list = []

    for obj in model.objects.using(src).all():
        kwargs = model_to_dict(obj, fields=fields, exclude=exclude)
        load_list.append(model(**kwargs))

    if load_list:
        if is_clear:
            print('删除数据', model.objects.using(dst).all().delete())
        print('成功导入 %s 行' % len(model.objects.using(dst).bulk_create(load_list)))
    else:
        print('没有数据导入！')
