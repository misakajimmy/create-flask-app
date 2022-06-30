# coding: utf-8
"""
算法表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from datetime import date, datetime
from typing import List

from .twins import TwinsAuthor, TwinsTag, TwinsScene, TwinsIndustry, ModelPackage
from .. import db


class TwinsAlgorithm(db.Document):
    """算法表"""
    __tablename__ = 't_twins_algorithm'

    # industry = db.ReferenceField(TwinsIndustry, commnet='算法行业')
    scene = db.ReferenceField(TwinsScene, commnet='算法场景')
    industry = db.ReferenceField(TwinsIndustry, commnet='算法行业')
    name = db.StringField(required=True, unique=True, null=False, default='', comment='算法名称')
    chinese_name = db.StringField(default='', comment='算法中文名称')
    description = db.StringField(default='', comment='算法描述')
    tags = db.ListField(db.ReferenceField(TwinsTag), default=[], comment='标签')
    version = db.StringField(default='0.1.0', comment='版本')
    author = db.ReferenceField(TwinsAuthor)

    def add_tags(self, tags: List[str]):
        model_tags = TwinsTag.get_tags(tags=tags)
        for tag in model_tags:
            if tag not in self.tags:
                self.tags.append(tag)
        self.save()

    def delete_tags(self, tags: List[str]):
        model_tags = TwinsTag.get_tags(tags=tags)
        for tag in model_tags:
            if tag in self.tags:
                self.tags.remove(tag)
        self.save()

    @staticmethod
    def exist(name):
        twin_algorithm_num = TwinsAlgorithm.objects(name=name).count()
        return twin_algorithm_num > 0

    @staticmethod
    def create(
            name: str, chinese_name: str, description: str, version: str, tags: List[str],
            scene_name: str, industry_name: str, author_name: str,
    ):
        # 检查算法是否存在
        if TwinsAlgorithm.exist(name):
            return {'code': 'DATA_EXIST', 'msg': '算法已存在'}
        author = TwinsAuthor.get(author_name)
        industry = TwinsIndustry.get(industry_name)
        scene = TwinsScene.get(name=scene_name, industry=industry)
        model_tags = TwinsTag.get_tags(tags=tags)

        twins_algorithm = TwinsAlgorithm(
            scene=scene,
            industry=industry,
            name=name,
            chinese_name=chinese_name,
            description=description,
            tags=model_tags,
            author=author,
            version=version
        )
        twins_algorithm.save()
        return {'code': 'OK', 'msg': '算法创建成功', 'data': twins_algorithm}


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
