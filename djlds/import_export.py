# ---------------------------------------
#   程序：import_export.py
#   版本：0.3
#   作者：lds
#   日期：2020-03-18
#   语言：Python 3.X
#   说明：django 导入和导出
# ---------------------------------------

import csv

# 获取模型实例的字典
from django.forms.models import model_to_dict

from djlds.model import ModelFields, get_field_file_path, ModelData


def import_csv(model, csv_file, encoding='utf-8', conversion_type=None, max_batch=10000):
    """
    导入 csv 文件到数据库

    注意：需要处理日期和文件名的不要用她导入，她只用于备份和恢复。

    :param model: 要导出的数据库模型
    :param csv_file: 保存文件
    :param encoding: 保存文件编码
    :param conversion_type: 转换字段数据内容
    :param max_batch: 一次最大导入数量，超过以后分批导入
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
            export = ModelData(model, next(iter_reader))
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
            self.exclude = ['denglushijian_date']  # 'id',
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
                if i_field_list == 'shujuriqi_date':
                    value = model_dict[i_field_list].strftime("%Y-%m")
                elif i_field_list.endswith('_date'):
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
