# coding: utf-8
"""
数孪包以及相关表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from datetime import date, datetime
from typing import List

from flask import current_app

from .. import db
from ..response import api_return
from ..tool import compare_version


class TwinsAuthor(db.Document):
    """作者表"""
    __tablename__ = 't_twins_author'

    name = db.StringField(required=True, unique=True, null=False, default='', comment='作者名称')
    create_time = db.DateTimeField(null=False, default=datetime.now(), comment='创建时间')
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment='更新时间'
    )

    @staticmethod
    def get(name):
        author = TwinsAuthor.objects(name=name).first()
        if not author:
            author = TwinsAuthor(name=name)
            author.save()
        return author

    def format(self):
        return self.name


class TwinsIndustry(db.Document):
    """行业表"""
    __tablename__ = 't_twin_industry'

    name = db.StringField(required=True, unique=True, null=False, default='', comment='行业名称')
    create_time = db.DateTimeField(null=False, default=datetime.now(), comment='创建时间')
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment='更新时间'
    )

    @staticmethod
    def get(name):
        # 检查行业
        twin_industry = TwinsIndustry.objects(name=name).first()
        if not twin_industry:
            twin_industry = TwinsIndustry(name=name)
            twin_industry.save()
        return twin_industry

    def format(self):
        return self.name


class TwinsScene(db.Document):
    """行业表"""
    __tablename__ = 't_twins_scene'

    name = db.StringField(required=True, unique=True, null=False, default='', comment='场景名称')
    industry = db.ReferenceField(TwinsIndustry, commnet='行业名称')
    packages = db.ListField(db.ReferenceField('ModelPackage'), default=[])
    last = db.ReferenceField('ModelPackage')
    create_time = db.DateTimeField(null=False, default=datetime.now(), comment='创建时间')
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment='更新时间'
    )

    @staticmethod
    def get(name: str, industry: TwinsIndustry):
        twin_scene = TwinsScene.objects(name=name, industry=industry).first()
        if not twin_scene:
            twin_scene = TwinsScene(name=name, industry=industry)
            twin_scene.save()
        return twin_scene

    def package_add(self, package):
        if not self.last:
            self.last = package
            package.is_last = True
            package.save()
        else:
            if compare_version(package.version, self.last.version):
                self.last.is_last = False
                self.last.save()
                self.last = package
                package.is_last = True
                package.save()
        self.packages.append(package)
        self.save()

    def format(self):
        return self.name

    def model_num(self):
        return self.last.model_num()

    def domain_num(self, latest_package=None):
        p = 0
        o = 0
        c = 0
        for package in self.packages:
            primary_num, operational_num, control_num = package.domain_num(latest_package=latest_package)
            p += primary_num
            o += operational_num
            c += control_num
        return p, o, c


class TwinsTag(db.Document):
    """标签表"""
    __tablename__ = 't_twins_tag'

    name = db.StringField(required=True, unique=True, null=False, default='', comment='标签名称')
    create_time = db.DateTimeField(null=False, default=datetime.now(), comment='创建时间')
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment='更新时间'
    )

    @staticmethod
    def get(name):
        twin_tag = TwinsTag.objects(name=name).first()
        if not twin_tag:
            twin_tag = TwinsTag(name=name)
            twin_tag.save()
        return twin_tag

    @staticmethod
    def get_tags(tags: List[str]):
        model_tags = []
        for tag in tags:
            model_tag = TwinsTag.get(name=tag)
            model_tags.append(model_tag)
        return model_tags

    @staticmethod
    def format_tags(tags):
        return list(map(
            lambda x: x.name, tags))


class ModelPackage(db.Document):
    """数孪包表"""
    __tablename__ = 't_twins_model_package'

    name = db.StringField(required=True, null=False, default='', comment='数孪包名称')
    scene = db.ReferenceField(TwinsScene, commnet='场景名称')
    industry = db.ReferenceField(TwinsIndustry, commnet='行业名称')
    version = db.StringField(default='0.1.0', comment='版本')
    author = db.ReferenceField(TwinsAuthor)
    dictionary = db.ListField(db.ReferenceField('TwinDictionary'), default=[])
    models = db.ListField(db.ReferenceField('TwinsModel'), null=False, default=[], comment='数孪模型')
    is_last = db.BooleanField(default=False)
    create_time = db.DateTimeField(null=False, default=datetime.now(), comment='创建时间')
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment='更新时间'
    )

    @staticmethod
    def exist(name, version):
        # 检查数孪包
        model_package_num = ModelPackage.objects(name=name, version=version).count()
        return model_package_num > 0

    @staticmethod
    def create(name, scene, industry, version, author):
        # 检查行业
        twin_industry = TwinsIndustry.get(name=industry)
        twin_scene = TwinsScene.objects(name=scene).first()
        # 检查场景
        if twin_scene:
            pass
            # if len(twin_scene.packages) > 0 and twin_scene.packages[0].name != name:
            #     current_app.logger.debug('场景已存在: twins_scene:%s', scene)
            #     return {'code': 'DATA_EXIST', 'msg': '场景已被数孪包使用', 'data': {
            #         'scene': twin_scene.name,
            #         'package': twin_scene.packages[0].name
            #     }}
        else:
            twin_scene = TwinsScene(name=scene, industry=twin_industry)
            twin_scene.save()

        author = TwinsAuthor.get(author)

        model_package = ModelPackage.objects(name=name, version=version).first()
        if not model_package:
            model_package = ModelPackage(
                name=name,
                scene=twin_scene,
                industry=twin_industry,
                version=version,
                author=author
            )
            model_package.save()
            twin_scene.package_add(model_package)
        return {'code': 'OK', 'msg': '数孪包创建成功', 'data': model_package}

    @staticmethod
    def remove(name):
        model_package = ModelPackage.objects(name=name).first()
        if not model_package:
            current_app.logger.debug('模型包不存在: model_package:%s', name)
            return {'code': 'DATA_NOT_FOUND', 'msg': '数孪包不存在'}

        data = {
            'name': model_package.name,
            'scene': model_package.scene.name,
            'industry': model_package.industry.name
        }
        model_package.scene.delete()
        model_package.delete()
        return {'code': 'OK', 'msg': '数孪包删除成功', 'data': data}

    def model_num(self):
        return len(self.models)

    def domain_num(self, latest_package=None):
        from .model import TwinDomainsColumn

        if not latest_package:
            primary_num = TwinDomainsColumn.objects(package=self, kind='primary').count()
            operational_num = TwinDomainsColumn.objects(package=self, kind='operational').count()
            control_num = TwinDomainsColumn.objects(package=self, kind='control').count()
        else:
            primary_num = TwinDomainsColumn.objects(package=self, kind='primary', package__in=latest_package).count()
            operational_num = TwinDomainsColumn.objects(package=self, kind='operational',
                                                        package__in=latest_package).count()
            control_num = TwinDomainsColumn.objects(package=self, kind='control', package__in=latest_package).count()
        return primary_num, operational_num, control_num

    def add_dictionary(self, dictionary):
        if dictionary not in self.dictionary:
            self.dictionary.append(dictionary)
            self.save()

    def add_dictionaries(self, dictionaries):
        if not dictionaries == self.dictionary:
            self.dictionary = dictionaries
            self.save()

    def add_model(self, model):
        if model not in self.models:
            self.models.append(model)
            self.save()

    def add_models(self, models):
        if not models == self.models:
            self.models = models
            self.save()

    def format(self):
        from .model import TwinDictionary, TwinsModel
        return {
            '_id': str(self.id),
            'name': self.name,
            'version': self.version,
            'scene': self.scene.format(),
            'industry': self.industry.format(),
            'author': self.author.format(),
            'dictionary': TwinDictionary.format_dictionaries(self.dictionary),
            'models': TwinsModel.format_models(self.models),
            'update_time': str(self.update_time),
        }

    @staticmethod
    def get(name, scene, industry):
        model_package = ModelPackage.objects(name=name).first()
        if not model_package:
            model_package = ModelPackage.create(name=name, scene=scene, industry=industry)
            if model_package['code'] == 'OK':
                return model_package['data']
            else:
                return None
        return model_package
