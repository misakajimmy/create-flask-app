# coding: utf-8
"""
数孪以及数孪数据表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from datetime import date, datetime
from typing import List

from flask import current_app

from .twins import TwinsIndustry, ModelPackage, TwinsAuthor, TwinsTag, TwinsScene
from .. import db


class TwinsModelType(db.Document):
    """类型表"""
    __tablename__ = 't_twins_type'

    name = db.StringField(required=True, unique=True, null=False, default='', comment='类型名称')
    create_time = db.DateTimeField(null=False, default=datetime.now(), comment='创建时间')
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment='更新时间'
    )

    @staticmethod
    def get(name):
        twin_type = TwinsModelType.objects(name=name).first()
        if not twin_type:
            twin_type = TwinsModelType(name=name)
            twin_type.save()
        return twin_type

    @staticmethod
    def format_types(types):
        return list(
            map(lambda x: x.format(), types))

    def format(self):
        return self.name


class TwinDictionaryColumn(db.Document):
    __tablename__ = 't_twins_dictionary_column'

    package = db.ReferenceField(ModelPackage)
    dictionary = db.ReferenceField('TwinDictionary')
    name = db.StringField()
    label = db.DictField()
    default_aggregation = db.StringField()
    field_type = db.StringField()
    resolution = db.StringField()
    column_type = db.StringField()
    note = db.DictField()
    unit = db.DictField()
    category = db.DictField()

    @staticmethod
    def create_column(
            package, dictionary, name, label, default_aggregation,
            field_type, resolution, column_type, note, unit, category):
        column = TwinDictionaryColumn.objects(package=package, dictionary=dictionary, name=name).first()
        if not column:
            column = TwinDictionaryColumn(package=package, dictionary=dictionary, name=name)
        column.label = label
        column.default_aggregation = default_aggregation
        column.field_type = field_type
        column.resolution = resolution
        column.column_type = column_type
        column.note = note
        column.unit = unit
        column.category = category
        column.save()
        return column

    @staticmethod
    def create_columns(package, dictionary, columns, ):
        res = {}
        cols = []
        for column in columns:
            dictionary_column = TwinDictionaryColumn.create_column(
                package=package,
                dictionary=dictionary,
                name=column.get('id'),
                label=column.get('label'),
                default_aggregation=column.get('default_aggregation'),
                field_type=column.get('field_type'),
                resolution=column.get('resolution'),
                column_type=column.get('type'),
                note=column.get('note'),
                unit=column.get('unit'),
                category=column.get('category'),
            )
            cols.append(dictionary_column)
            res[column['_id']] = dictionary_column
        dictionary.columns_add(cols)
        return res

    def format_column(self):
        return {
            'name': self.name,
            'label': self.label,
            'default_aggregation': self.default_aggregation,
            'field_type': self.field_type,
            'resolution': self.resolution,
            'column_type': self.column_type,
            'note': self.note,
            'unit': self.unit,
            'category': self.category
        }

    def dump(self):
        res = {
            "_id": str(self.id),
            "id": self.name,
        }
        if self.field_type:
            res['field_type'] = self.field_type
        if self.column_type:
            res['type'] = self.column_type
        if self.label:
            res['label'] = self.label
        if self.unit:
            res['unit'] = self.unit
        if self.note:
            res['note'] = self.note
        if self.resolution:
            res['resolution'] = self.resolution
        if self.default_aggregation:
            res['default_aggregation'] = self.default_aggregation
        return res

    @staticmethod
    def delete_columns(columns):
        for column in columns:
            column.delete()

    @staticmethod
    def format_columns(columns):
        res = []
        for column in columns:
            res.append(column.format_column())
        return res


class TwinDictionary(db.Document):
    __tablename__ = 't_twins_dictionary'

    package = db.ReferenceField(ModelPackage)
    kind = db.StringField()
    name = db.StringField()
    columns = db.ListField(db.ReferenceField('TwinDictionaryColumn', dbref=False), default=[])

    @staticmethod
    def create(package, name, kind):
        dictionary = TwinDictionary.objects(package=package, name=name).first()
        if not dictionary:
            dictionary = TwinDictionary(package=package, name=name)
        dictionary.kind = kind
        dictionary.save()
        return dictionary

    def column_add(self, column):
        if column not in self.columns:
            self.columns.append(column)
            self.save()

    def columns_add(self, columns):
        if not columns == self.columns:
            self.columns = columns
            self.save()

    def dump(self, model_package_id, package_id, _id, name, project, scope):
        return {
            '_id': _id,
            "kind": self.kind,
            "model_package_id": model_package_id,
            "name": name,
            "package_id": package_id,
            "project": project,
            "scope": scope,
            "columns": list(map(
                lambda x: x.dump(),
                self.columns))
        }

    @staticmethod
    def format_dictionaries(dictionaries):
        res = []
        for dictionary in dictionaries:
            res.append({
                'name': dictionary.name,
                'kind': dictionary.kind,
                'columns': TwinDictionaryColumn.format_columns(dictionary.columns)
            })
        return res


class TwinDomainsColumn(db.Document):
    __tablename__ = 't_twins_domain_column'

    package = db.ReferenceField(ModelPackage)
    model = db.ReferenceField('TwinsModel')
    parent = db.ReferenceField(TwinDictionaryColumn)
    domain = db.ReferenceField('TwinDomain')
    kind = db.StringField()

    @staticmethod
    def create_column(package, model, domain, parent, kind):
        column = TwinDomainsColumn.objects(
            package=package, model=model, domain=domain, parent=parent, kind=kind).first()
        if not column:
            column = TwinDomainsColumn(package=package, model=model, domain=domain, parent=parent, kind=kind)
            column.save()
        domain.add_column(column)
        return column

    @staticmethod
    def create_columns(package, model, domain, columns, kind):
        for col in columns:
            TwinDomainsColumn.create_column(package, model, domain, parent=col, kind=kind)
        return

    @staticmethod
    def delete_columns(columns):
        for column in columns:
            column.delete()

    @staticmethod
    def format_columns(columns):
        return list(map(
            lambda x: x.parent.format_column(),
            columns
        ))

    def dump(self):
        return {
            "_id": str(self.id),
            "parent_id": str(self.parent.id)
        }


class TwinDomain(db.Document):
    """数域表"""
    __tablename__ = 't_twins_domain'

    name = db.StringField()
    model = db.ReferenceField('TwinsModel')
    parent = db.ReferenceField('TwinDictionary')
    package = db.ReferenceField(ModelPackage)
    kind = db.StringField()
    columns = db.ListField(db.ReferenceField(TwinDomainsColumn), default=[])

    @staticmethod
    def create(package, name: str, kind: str, model=None, parent=None):
        twin_domain = TwinDomain.objects(package=package, model=model, name=name).first()
        if not twin_domain:
            twin_domain = TwinDomain(package=package, model=model, name=name)
        TwinDomainsColumn.delete_columns(twin_domain.columns)
        twin_domain.kind = kind
        twin_domain.parent = parent
        twin_domain.columns = []
        twin_domain.save()
        return twin_domain

    def add_column(self, column):
        if column not in self.columns:
            self.columns.append(column)
            self.save()

    @staticmethod
    def format_domains(domains):
        return list(map(
            lambda x: {
                'name': x.name,
                'kind': x.kind,
                'columns': TwinDomainsColumn.format_columns(x.columns)
            },
            domains
        ))

    def dump(self, model_id, model_package_id, package_id, _id, project, scope):
        return {
            "_id": _id,
            "columns": list(map(
                lambda x: x.dump(),
                self.columns)),
            "kind": self.kind,
            "model_id": model_id,
            "model_package_id": model_package_id,
            "name": self.name,
            "package_id": package_id,
            "parent_id": str(self.parent.id),
            "project": project,
            "scope": scope
        }


class TwinsModel(db.Document):
    """数孪表"""
    __tablename__ = 't_twins_model'

    package = db.ReferenceField(ModelPackage, required=True, commnet='数孪包')
    name = db.StringField(required=True, null=False, default='', comment='数孪名称')
    chinese_name = db.StringField(default='', comment='中文名称')
    icon = db.StringField(default='', comment='图标')
    icon_url = db.StringField(default='', comment='图标地址')
    tags = db.ListField(db.ReferenceField(TwinsTag), comment='标签')
    type = db.ReferenceField(TwinsModelType)
    domains = db.ListField(db.ReferenceField(TwinDomain), default=[])
    author = db.ReferenceField(TwinsAuthor)
    create_time = db.DateTimeField(null=False, default=datetime.now(), comment='创建时间')
    three_model = db.StringField(default='', comment='图标地址')
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment='更新时间'
    )

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

    @property
    def tag(self):
        return list(
            map(
                lambda y: y.name,
                self.tags
            )
        )

    @staticmethod
    def exist(name):
        # 检查数孪包
        twin_model_num = TwinsModel.objects(name=name).count()
        return twin_model_num > 0

    @staticmethod
    def create(
            package: ModelPackage,
            name: str,
            chinese_name: str,
            model_type: str,
            icon: str,
            author: str,
            icon_url: str,
            tags: List[str] = [],
    ):
        twin_type = TwinsModelType.get(model_type)
        model_tags = TwinsTag.get_tags(tags=tags)
        author = TwinsAuthor.get(author)

        twins_model = TwinsModel.objects(
            name=name,
            package=package,
        ).first()
        if not twins_model:
            twins_model = TwinsModel()

        twins_model.name = name
        twins_model.package = package
        twins_model.chinese_name = chinese_name
        twins_model.icon = icon
        twins_model.icon_url = icon_url
        twins_model.tags = model_tags
        twins_model.type = twin_type
        twins_model.author = author
        twins_model.save()
        return {'code': 'OK', 'msg': '数孪创建成功', 'data': twins_model}

    def format_model(self):
        return {
            '_id': str(self.id),
            'name': self.name,
            'chinese_name': self.chinese_name,
            'icon': self.icon,
            'icon_url': self.icon_url,
            'tags': TwinsTag.format_tags(self.tags),
            'type': self.type.format(),
            'domain': TwinDomain.format_domains(self.domains),
            'update_time': str(self.update_time),
            'author': self.package.author.format(),
            'scene': self.package.scene.format(),
            'industry': self.package.industry.format(),
            'version': self.package.version,
            'three_model': self.three_model,
        }

    @staticmethod
    def format_models(models):
        return list(map(
            lambda x: x.format_model(),
            models
        ))

    def add_domains(self, domains):
        if not domains == self.domains:
            self.domains = domains
            self.save()

    def dump(
            self, model_package_id: str, package_id: str, package_obj_id: str, project: str, scope: str,
            icon: str = None):
        res = {
            "_id": str(self.id),
            "attributes": {
                "abstract": True,
                "axis": {},
                "label": {
                    "i18n": {
                        "en-US": self.name,
                        "zh-CN": self.chinese_name
                    }
                },
                "name": self.name
            },
            "coordinates": {},
            "model_package_id": model_package_id,
            "package_id": package_id,
            "package_obj_id": package_obj_id,
            "project": project,
            "relations": {
                "in_sub_class_of": []
            },
            "scope": scope,
            "template_id": ""
        }
        if icon:
            res['attributes']['icon'] = "/api/v2/images/" + icon
        return res


class TwinsRelationship(db.Document):
    """数孪表"""
    __tablename__ = 't_twins_relationship'

    father = db.ReferenceField(TwinsModel, commnet='父数孪')
    child = db.ReferenceField(TwinsModel, commnet='子数孪')

    @staticmethod
    def get_relationship(model: TwinsModel):
        fathers = TwinsRelationship.objects(child=model)
        childs = TwinsRelationship.objects(father=model)
        return fathers, childs
