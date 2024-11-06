# ---------------------------------------
#   程序：import_export.py
#   版本：0.11
#   作者：lds
#   日期：2023-09-22
#   语言：Python 3.X
#   说明：django 导入和导出
# ---------------------------------------

import csv
import time
from pathlib import Path

from django.db import transaction
# 获取模型实例的字典
from django.forms.models import model_to_dict
from ilds.excel_xlrd import ReadXlsx as ReadXls
from ilds.excel_xlsx import ReadXlsx

from djlds.model import ModelFields, get_field_file_path, ModelData, TableData


class BaseImportExcel:
    """
    导入 Excel 的基础类

    我们没有使用已经写好的导入库，是为了速度和方便定制。
    """

    def __init__(self, model, exclude=None, revised=None, debug=False):
        self.file = None
        self.model = model
        self.read = None  # 正在读取的数据，有时候我们会用到数据列表以外的数据
        self.debug = debug
        if exclude is None:
            self.exclude = self.get_exclude()
        else:
            self.exclude = exclude
        if revised is None:
            self.revised = self.get_revised()
        else:
            self.revised = revised
        self.table = TableData(model)
        self.field_data = []
        self.init_parsing_field()

        self.titles = None
        self.is_multiple_sheet = False

        self.count = 0
        self.count_all = 0
        self.load_list = []
        self.adding_data = {}  # 需要附加数据的时候使用
        self.model_kwargs = {}  # 创建数据的时候添加公用数据
        # 导入数据用的时间
        self.time_cost = 0
        self.info = []

    def init_parsing_field(self):
        """
        初始化处理字段内容
        """
        # super().init_parsing_field()
        parsing_field = {
            'IntegerField': self.parsing_integer,
            'FloatField': self.parsing_float,
            'DateField': self.parsing_date,
            'DateTimeField': self.parsing_date_time,
            'BooleanField': self.parsing_boolean,
        }
        for data in self.table.iter('field', 'type'):
            _field, _type = data
            # print(data)
            if _type in parsing_field:
                self.field_data.append((_field, parsing_field[_type]))
        # pp(self.field_data)

    def parsing_integer(self, field, data):
        """
        解析数字字段
        """
        if field in data:
            try:
                data[field] = int(data[field])
            except Exception as e:
                if self.debug:
                    info = f'parsing_integer: {field} {e}'
                    print(info)
                    self.info.append(info)
                del data[field]

    def parsing_float(self, field, data):
        """
        解析浮点数字段
        """
        if field in data:
            try:
                data[field] = float(data[field])
            except Exception as e:
                if self.debug:
                    print(f'parsing_float: {field} {e}')
                del data[field]

    def parsing_date(self, field, data):
        """
        解析日期字段
        """
        if field in data:
            v = data[field]
            if not v:
                del data[field]
            elif '/' in v:
                data[field] = v.replace('/', '-')

    def parsing_date_time(self, field, data):
        """
        解析时间字段
        """
        if field in data:
            v = data[field]
            if not v:
                del data[field]
            elif '/' in v:
                data[field] = v.replace('/', '-')

    def parsing_boolean(self, field, data):
        """
        解析布尔字段
        """
        if field in data:
            v = str(data[field]).lower()
            if v in ['true', '有', '是', ]:
                data[field] = True
            elif v in ['false', '无', '否', ] or not v:
                data[field] = False
            elif v in ['none', '未知', ]:
                data[field] = None

    def get_revised(self):
        """
        需要修正的标题
        """
        return {}

    def get_exclude(self):
        """
        排除的标题
        """
        return []

    def init_title(self, datasets):
        """
        初始化标题
        """
        # # 第一行不是标题的例子
        # max_row = 20
        # for i, row in enumerate(datasets):
        #     # print(i, row)
        #     # 检查是否包含指定内容
        #     if "账号昵称（必填）" in row and "发布链接（必填）" in row:
        #         self.titles = row
        #         break
        #     if i >= max_row:
        #         break
        #
        # if not self.titles:
        #     return None

        self.titles = next(datasets)
        ret = self.table.set_title(self.titles, exclude=self.exclude, **self.revised)
        # print('set_title', self.titles, self.exclude, self.revised)
        if any([data['Name'] for data in ret]):
            print([data['Name'] for data in ret])
            raise ValueError(f'没有匹配的字段：{ret}')
        if self.table.duplicate_info:
            raise ValueError(f'重复的字段：{self.table.duplicate_info}')
        if self.debug:
            print(self.table.table_fields)
            print(self.table.index_list)

    def init(self):
        """
        多表导入的时候，初始化数据
        """
        self.count = 0
        self.titles = None
        self.load_list = []

    def init_handle(self):
        """
        初始化处理数据需要的前置内容
        """
        ...

    def handle_data(self, data):
        """
        处理数据
        """
        for field, fun in self.field_data:
            fun(field, data)
        return data

    def ignore_import(self, kwargs):
        """
        根据条件来判断是否忽略导入
        """
        # print(kwargs)
        if not any(kwargs.values()):
            return True

    def import_data(self, datasets):
        """
        导入数据
        """

        self.init_handle()

        for i, data in enumerate(datasets):
            # print(data)
            kwargs = self.table.get_model_data(data)
            if self.ignore_import(kwargs):
                if self.debug:
                    print(f'跳过行 {i}：{data}')
                continue

            kwargs.update(self.model_kwargs)

            kwargs = self.handle_data(kwargs)

            try:
                self.append(kwargs, data)
            except Exception as e:
                raise ValueError(f"i:{i} 错误: {e}\ntitles: {self.titles}\ndata: {data}\nkwargs: {kwargs}")

        if not self.debug:
            self.count += len(self.model.objects.bulk_create(self.load_list))

        self.info.append(f'{self.read.title} 导入 {self.count} 行')
        self.count_all += self.count

        return self.info

    def append(self, data, original_data):
        # super().append(data, original_data)
        if self.debug:
            self.model.objects.create(**data)
            self.count += 1
        else:
            self.load_list.append(self.model(**data))

    def read_file(self, file, *args, **kwargs):
        """
        读取文件
        """
        self.file = Path(file)
        suffix = self.file.suffix.lower()
        if suffix == '.xlsx':
            self.read = ReadXlsx(file, *args, **kwargs)
            datasets = None
        elif suffix == '.xls':
            self.read = ReadXls(file, *args, **kwargs)
            datasets = None
        elif suffix == '.csv':
            if 'encoding' in kwargs:
                encoding = kwargs.pop('encoding')
            else:
                encoding = 'utf-8-sig'
            # 读取csv文件
            f = open(file, newline='', encoding=encoding)
            self.read = csv.reader(f, *args, **kwargs)  # delimiter=':', quoting=csv.QUOTE_NONE
            datasets = iter(self.read)
            if self.is_multiple_sheet:
                print('cvs 文件没有多个表')
                self.is_multiple_sheet = False
        else:
            raise ValueError(f'导入 {file} 失败， 不支持导入 {suffix[1:]} 格式')

        return datasets

    @transaction.atomic
    def start(self, file, exclude_sheet=None, *args, **kwargs):
        """
        开始导入数据
        @param file:
        @param exclude_sheet: 忽略导入的表
        @return:
        """

        start_time = time.time()

        if exclude_sheet is None:
            exclude_sheet = []

        datasets = self.read_file(file, *args, **kwargs)

        for sheet_name in self.read.sheet_names:
            print('sheet_name', sheet_name)
            self.read.set_sheet(sheet_name)

            if datasets is None:
                datasets = self.read.values()

            # 跳过结算数据导入
            if self.read.title in exclude_sheet:
                info = f'排除导入 {self.read.title}'
                if self.debug:
                    print(info)
                self.info.append(info)
            else:
                self.init_title(datasets)
                if self.titles:
                    self.import_data(datasets)
                else:
                    info = f'跳过导入“{self.read.title}”，没有找到标题'
                    if self.debug:
                        print(info)
                    self.info.append(info)

            if not self.is_multiple_sheet:
                break

            self.init()

        self.time_cost = time.time() - start_time

        info = f'总共导入 {self.count_all} 条数据'
        print(info)
        self.info.append(info)

        self.end_import()

        return self.info

    def end_import(self, *args, **kwargs):
        """
        结束导入数据的时候调用
        """
        ...


def import_csv(model, csv_file, encoding='utf-8', conversion_type=None, max_batch=10000, import_names=None,
               exclude=None):
    """
    导入 csv 文件到数据库

    注意：需要处理日期和文件名的不要用她导入，她只用于备份和恢复。

    :param model: 要导出的数据库模型
    :param csv_file: 保存文件
    :param encoding: 保存文件编码
    :param conversion_type: 转换字段数据内容
    :param max_batch: 一次最大导入数量，超过以后分批导入
    :param import_names: 重命名标题名，比如 厂牌名称 改名为 版权公司名
    :param exclude: 排除导入的内容
    :return:
    """

    print('导入开始 ---------------------------------------------------------\n', csv_file)

    # 读取csv文件
    with open(csv_file, newline='', encoding=encoding) as f:
        reader = csv.reader(f)
        import_count = 0
        batch_count = 0
        load_list = []

        try:
            iter_reader = iter(reader)
            export = ModelData(model, next(iter_reader), import_names, exclude)
            export.clean_fields.add('shouquan_kaishi_date')
            export.clean_fields.add('shouquan_jieshu_date')
            export.clean_fields.add('external_settlement_float')
            # 如果需要转换类型
            if isinstance(conversion_type, dict):
                for k, v in conversion_type.items():
                    # print(k, v, export.import_fields)
                    if k in export.import_fields:
                        export.conversion_type[k] = v
            for row in iter_reader:
                # print(ku_field, xls_row, row)
                kwargs = export.get_import_data(row)
                # print(kwargs)
                load_list.append(model(**kwargs))
                batch_count += 1
                if batch_count == max_batch:
                    import_count += len(model.objects.bulk_create(load_list))
                    batch_count = 0
                    load_list = []
        except csv.Error as e:
            return f'file {csv_file}, line {reader.line_num}: {e}'
        else:
            import_count += len(model.objects.bulk_create(load_list))
            info = '成功导入 %s 行' % import_count
            print(info)
            print('---------------------------------------------------------')
            return info


class LdsExportCsv:
    """
    写入数据到 csv 文件
    支持自定义写入的表头和要导出的字段

    这个主要是自用，等抽时间我们改成通用的

    例子

    # model = 要导出的模型
    objs = model.objects.all()
    # 找到的歌曲列表
    if objs.exists():
        xlsxfile = r'导出：测试.csv'
        ex_csv = LdsExportCsv(model, xlsxfile)  # 歌曲库的中文名
        ex_csv.set_title()
        # 或者元组列表
        # ex_csv.set_title(['歌曲名称', '表演者', '专辑名称',] ) # , row=3, col=3
        for obj in objs:
            ex_csv.append(obj)
        info = ex_csv.print_count_info()
        ex_csv.close()
    else:
        print('没有找到歌曲')
    """

    def __init__(self, model, work_file, exclude=None, encoding='utf-8'):
        """初始化"""
        self.title = []
        self.export = None

        # 要处理的库
        self.model = model

        # 写入csv文件
        self.csv_file = open(work_file, 'w', newline='', encoding=encoding)  # 有软件打开乱码
        self.writer_csv = csv.writer(self.csv_file)

        self.gequ_dict = {}

        # 设置排除内容
        if exclude is None or not isinstance(exclude, list):
            self.exclude = []  # 'id',
        else:
            self.exclude = exclude

        self.f = ModelFields(model, self.exclude)

        # 初始化统计
        self.count_all = 0
        self.info = {}
        self.count_merge = 0

        self.field_list = []

    def set_title(self, fields=None):
        """
        设置标题和写入的内容
        export 是要导出列的名字列表
        """

        # 需要获取数据的字段列表
        self.field_list = []
        if fields is None:
            self.export = self.f.verbose_list
        else:
            self.export = fields

        # 获取模型的字段
        model_field = self.f.verbose_dict()
        # pprint(model_field)

        # 写表头
        csv_row = []
        for i_export in self.export:
            i_export = i_export.strip()
            if i_export:
                try:
                    self.field_list.append(model_field[i_export])
                except:
                    self.field_list.append('None')
                # print(self.field_list)
                csv_row.append(i_export)
        self.writer_csv.writerow(csv_row)

        self.init_count()

        return

    def append(self, date, row=0, col=0):
        """
        写入 csv 文件
        date 要写入的数据
        """

        model_dict = model_to_dict(date, exclude=self.exclude)

        # 写入文件
        # print(model_dict)
        # print(self.field_list)
        csv_row = []
        for i_field_list in self.field_list:
            try:
                # 统计信息
                if i_field_list in self.info:
                    value = model_dict[i_field_list]
                    if i_field_list.endswith('_float'):
                        self.info[i_field_list] += float(value)
                    else:
                        self.info[i_field_list] += int(value)
                    # print(self.info)
                # 处理日期
                # if i_field_list == 'shujuriqi_date':
                #     value = model_dict[i_field_list].strftime("%Y-%m")
                if i_field_list.endswith('_date'):
                    value = model_dict[i_field_list].strftime("%Y-%m-%d")
                # 处理文件
                elif i_field_list.endswith('_file'):
                    value = get_field_file_path(model_dict[i_field_list])
                else:
                    value = model_dict[i_field_list]
            except:
                value = ''
            csv_row.append(value)
        self.writer_csv.writerow(csv_row)

        # print(model_dict)
        self.count_all += 1
        return

    def get_count_list(self):
        """获取统计信息的列表 列表内容是字典 键为 count_name count_field count"""
        count_list = []
        model_fields = self.f.verbose_dict()
        # print(model_fields)
        if self.info:
            for k, v in model_fields.items():
                _dict = {}
                _field = self.info.get(v)
                # print(k,v,_field)
                if not _field is None:
                    _dict['count_name'] = k
                    _dict['count_field'] = v
                    _dict['count'] = self.info[v]
                    count_list.append(_dict)
        return count_list

    def print_count_info(self):
        """打印统计信息"""
        print_info = '导出：%s    总共：%s' % (self.count_all - self.count_merge, self.count_all)
        for _count in self.get_count_list():
            print_info += '%s：%s    ' % (_count['count_name'], _count['count'])  # _count['count_field']
        print(print_info)
        return print_info

    def init_count(self):
        """ 初始化需要统计的内容"""

        self.info = {}
        # print(field_list)
        for i in self.field_list:
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
                    self.info[i] = 0

        # print(self.info)

    def close(self):
        """
        写入结束，关闭文件
        """
        self.csv_file.close()

    def __repr__(self):
        return str(self.export)


def export_csv(model, sep='', max_export=1000000, exclude=None):
    """
    导出数据为csv文件
    """

    name_str = '导出 %s' % model.__name__
    # name_str = '导出 %s(%s)' % (ku_str, ku.__name__)

    if exclude is None:
        exclude = []

    data_list = model.objects.all()
    # 自定义了到处方式
    # # 按日期导出
    # kwargs = {}
    # kwargs['shujuriqi_date__range'] = ['2018-01-01', '2100-01-01']
    # data_list = ku.objects.filter(**kwargs)
    try:
        data_count = data_list.count()
    except Exception as e:
        return f'{model.__name__} 没有歌曲导出 {e}'

    # 找到的歌曲列表
    if data_count:
        print('---------------------------------------------------------')
        print('开始 %s' % name_str)
        print()

        print('搜索结果：', data_count)
        if data_count > max_export:
            export_start = 0
            export_stop = max_export
            info = '已分多个文件导出：'
            # print(info)
            while True:
                if export_start > data_count:
                    break
                data_list = model.objects.all()[export_start:export_stop]
                if export_stop == max_export:
                    name = name_str + '.csv'
                else:
                    # print(type(export_start),type(max_export),type(export_start/max_export))
                    name = name_str + '_%03d.csv' % int(export_start / max_export)
                mycsv = LdsExportCsv(model, name, exclude=exclude)  # 歌曲库的中文名
                mycsv.set_title()  # , row=3, col=3
                for i_data_list in data_list:
                    # print(i_data_list)
                    mycsv.append(i_data_list)
                info += sep + mycsv.print_count_info()
                mycsv.close()
                export_start += max_export
                export_stop += max_export
        else:
            print('没有超过 %s' % max_export)
            mycsv = LdsExportCsv(model, name_str + '.csv', exclude=exclude)  # 歌曲库的中文名
            mycsv.set_title()  # , row=3, col=3
            for i_data_list in data_list:
                # print(i_data_list)
                mycsv.append(i_data_list)
            mycsv.close()
            info = mycsv.print_count_info()
            # print(mycsv.tongji_info)
            # mycsv.print_count_info()
            print()
            print('导出结束')
            print('---------------------------------------------------------')
    else:
        info = (model.__name__, '库没有歌曲')

    # print(info)
    return info
