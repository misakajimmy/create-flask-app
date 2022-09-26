# coding: utf-8
"""
算法表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from datetime import date, datetime
from typing import List
import ast

from .model import TwinsModel, TwinDomain
from .twins import TwinsAuthor, TwinsTag, TwinsScene, TwinsIndustry, ModelPackage
from .. import db


def ast_str_list(list):
    res = []
    for i in list:
        res.append(i.s)
    return res


def get_value(code: str, val: str):
    expr_ast = ast.parse(code)

    for b in expr_ast.body:
        if type(b).__name__ == 'Assign':
            index = 0
            res = {}
            if b.targets[0].id == val:
                for k in b.value.keys:
                    key = k.s
                    value = ast_str_list(b.value.values[index].elts)
                    res[key] = value
                    index += 1
                return res


class TwinsAlgorithm(db.Document):
    """算法表"""
    __tablename__ = 't_twins_algorithm'

    model = db.ReferenceField(TwinsModel, commnet='数孪')
    code = db.StringField(default='', comment='代码')
    inputField = db.ListField(default=[], comment='输入数据')
    outField = db.ListField(default=[], comment='输出数据')

    def format_domains(self):
        return {
            'input': self.inputField,
            'output': self.outField,
        }

    def rename(self, side, id, name):
        if side == 'input':
            for f in self.inputField:
                if f['field'] == id:
                    f['chinese'] = name
        if side == 'output':
            for f in self.outField:
                if f['field'] == id:
                    f['chinese'] = name
        self.save()

    @staticmethod
    def exist(name):
        twin_algorithm_num = TwinsAlgorithm.objects(name=name).count()
        return twin_algorithm_num > 0

    @staticmethod
    def create(
            model: TwinsModel, code: str,
    ):
        if code is None or code == '':
            return None
        input_values = get_value(code, 'INPUT_METRIC_LIST')
        output_values = get_value(code, 'OUTPUT_METRIC_LIST')
        input_field = []
        for key in input_values:
            for v in input_values[key]:
                input_field.append({
                    'domain': key,
                    'field': v,
                    'chinese': ''
                })
        output_field = []
        for key in output_values:
            for v in output_values[key]:
                output_field.append({
                    'domain': key,
                    'field': v,
                    'chinese': ''
                })

        twins_algorithm = TwinsAlgorithm(
            model=model,
            code=code,
            inputField=input_field,
            outField=output_field
        )
        twins_algorithm.save()
        model.algorithm = twins_algorithm
        return twins_algorithm
        # return {'code': 'OK', 'msg': '算法创建成功', 'data': twins_algorithm}


class TwinsAlgorithmSimilar(db.Document):
    """算法相近表"""
    __tablename__ = 't_twins_algorithm_similar'

    algorithm = db.ReferenceField(TwinsAlgorithm)
    similar = db.ListField(db.ReferenceField(TwinsAlgorithm), comment='相似算法')


class TwinsAlgorithmRelationship(db.Document):
    """算法关系表"""
    __tablename__ = 't_twins_algorithm_relationship'

    father = db.ReferenceField(TwinsAlgorithm, commnet='父算法')
    child = db.ReferenceField(TwinsAlgorithm, commnet='子算法')

    @staticmethod
    def get_relationship(algorithm: TwinsAlgorithm):
        fathers = TwinsAlgorithmRelationship.objects(child=algorithm)
        childs = TwinsAlgorithmRelationship.objects(father=algorithm)
        return fathers, childs

# class TwinsAlgorithmModelRelationship(db.Document):
#     """算法关系表"""
#     __tablename__ = 't_twins_algorithm_relationship'
#


# class TwinsAlgorithmType(db.Document):
#     """算法类型表"""
#     __tablename__ = 't_twins_algorithm_type'
#
#     name = db.StringField(required=True, unique=True, null=False, default='', comment='算法类型名称')
