# coding: utf-8
"""
数孪模型接口
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
数孪模型相关基础接口
"""
import json
from typing import List

from flask import g

from src.api import api, need_login
from src.model.model import TwinsModel, TwinsRelationship, TwinDomain, TwinsModelType
from src.model.twins import TwinsTag, TwinsAuthor, TwinsScene

from src.response import api_return
from src.tool import is_version


def format_model(twin_model: TwinsModel):
    return {
        '_id': str(twin_model.id),
        'name': twin_model.name,
        'chinese_name': twin_model.chinese_name,
        'version': twin_model.package.version,
        'tags': list(map(
            lambda x: x.name,
            twin_model.tags)),
        'author': twin_model.package.author.name,
        'industry': twin_model.package.industry.name,
        'scene': twin_model.package.scene.name,
        'icon_url': twin_model.icon_url,
        'package': twin_model.package.name,
        'type': twin_model.type.name,
        'update_time': str(twin_model.update_time)
    }


def format_models(twin_models: List[TwinsModel]):
    return list(map(format_model, twin_models))


###################################################################
# 列出数孪接口
###################################################################
@api.route('/model', methods=['GET'])
# # @need_login
def list_model():
    """
    #group  数孪
    #name   列出数孪包
    #desc   列出数孪包
    #example
    {
        "code": 0,
        "msg": "数孪列出成功",
        "data": [
            {
                "name": "hello-0",
                "chinese_name": "你好",
                "version": "v0.1.1",
                "tags": [
                    "a",
                    "b",
                    "c"
                ],
                "author": "misaka",
                "industry": "industry-test",
                "scene": "scene-test-0",
                "package": "scene-test-0",
                "type": "预测"
            }
        ]
    }
    """
    twin_models = TwinsModel.objects().all_fields()
    data = TwinsModel.format_models(twin_models)

    return api_return('OK', '数孪列出成功', data)


###################################################################
# 列出最新版本的数孪接口
###################################################################
@api.route('/model/latest', methods=['GET'])
# # @need_login
def list_latest_model():
    """
    #group  数孪
    #name   列出最新数孪包
    #desc   列出最新数孪包
    #example
    {
        "code": 0,
        "msg": "数孪列出成功",
        "data": [
            {
                "name": "hello-0",
                "chinese_name": "你好",
                "version": "v0.1.1",
                "tags": [
                    "a",
                    "b",
                    "c"
                ],
                "author": "misaka",
                "industry": "industry-test",
                "scene": "scene-test-0",
                "package": "scene-test-0",
                "type": "预测"
            }
        ]
    }
    """
    twin_scene = TwinsScene.objects().all_fields()
    models = []
    for scene in twin_scene:
        if scene.last is not None:
            models += scene.last.models
    data = TwinsModel.format_models(models)

    return api_return('OK', '数孪列出成功', data)


###################################################################
# 创建数孪接口
###################################################################
# @api.route('/model', methods=['POST'])
# # @need_login
# def update_model():
#     """
#     #group  数孪
#     #name   创建数孪
#     #desc   创建数孪
#     #param  name            <str>     数孪名称
#     #param  chinese_name    <str>     中文名称
#     #param  version         <str>     版本
#     #param  tags            <str>     标签
#     #param  author          <str>     作者
#     #param  industry        <str>     行业
#     #param  scene           <str>     创建
#     #param  type            <str>     功能类型
#     #example
#     {
#         "code": 0,
#         "msg": "数孪创建成功",
#         "data": {
#             "name": "hello-0",
#             "chinese_name": "你好",
#             "version": "v0.1.1",
#             "tags": [
#                 "a",
#                 "b",
#                 "c"
#             ],
#             "author": "misaka",
#             "industry": "industry-test",
#             "scene": "scene-test-0",
#             "package": "scene-test-0",
#             "type": "预测"
#         }
#     }
#     """
#     name = str(g.request_data.get('name', '')).strip()
#     chinese_name = str(g.request_data.get('chinese_name', '')).strip()
#     version = str(g.request_data.get('version', '')).strip()
#     tags = g.request_data.get('tags', '')
#     author = str(g.request_data.get('author', '')).strip()
#     industry = str(g.request_data.get('industry', '')).strip()
#     scene = str(g.request_data.get('scene', '')).strip()
#     # package = str(g.request_data.get('package', '')).strip()
#     model_type = str(g.request_data.get('type', '')).strip()
#
#     if not name:
#         return api_return('PARAM_NOT_FOUND', '缺少数孪名称')
#     if not chinese_name:
#         return api_return('PARAM_NOT_FOUND', '缺少中文名称')
#     if not version:
#         return api_return('PARAM_NOT_FOUND', '缺少版本')
#     if not tags:
#         tags = []
#     if not author:
#         return api_return('PARAM_NOT_FOUND', '缺少作者')
#     if not industry:
#         return api_return('PARAM_NOT_FOUND', '缺少行业')
#     if not scene:
#         return api_return('PARAM_NOT_FOUND', '缺少场景')
#     # if not package:
#     #     return api_return('PARAM_NOT_FOUND', '缺少数孪包')
#     if not model_type:
#         return api_return('PARAM_NOT_FOUND', '缺少功能类型')
#
#     res = TwinsModel.create(
#         name=name,
#         chinese_name=chinese_name,
#         version=version,
#         tags=tags,
#         author_name=author,
#         industry_name=industry,
#         scene_name=scene,
#         package_name=scene,
#         model_type=model_type
#     )
#
#     if res['code'] == 'OK' and res['data']:
#         res['data'] = format_model(res['data'])
#         return api_return(code=res['code'], msg=res['msg'], data=(res['data']))
#     else:
#         return api_return(code=res['code'], msg=res['msg'])


###################################################################
# 创建数孪接口
###################################################################
@api.route('/model', methods=['POST'])
# @need_login
def update_model():
    _id = str(g.request_data.get('id', '')).strip()
    name = str(g.request_data.get('name', '')).strip()
    chinese_name = str(g.request_data.get('chinese_name', '')).strip()
    version = str(g.request_data.get('version', '')).strip()
    model_type = str(g.request_data.get('type', '')).strip()
    author = str(g.request_data.get('author', '')).strip()
    tags = g.request_data.get('tags', '')

    if not _id:
        return api_return('PARAM_NOT_FOUND', '缺少数孪ID')
    if not version:
        return api_return('PARAM_NOT_FOUND', '缺少数孪版本')
    if not is_version(version):
        return api_return('PARAM_FORMAT_ERROR', '版本格式错误')

    twin_model = TwinsModel.objects(id=_id).first()
    if not twin_model:
        return {'code': 'DATA_NOT_FOUND', 'msg': '数孪模型不存在'}
    if name:
        twin_model.name = name
    if chinese_name:
        twin_model.chinese_name = chinese_name
    if version:
        twin_model.version = version
    if model_type:
        twin_model_type = TwinsModelType.get(model_type)
        twin_model.type = twin_model_type
    if author:
        twin_model_author = TwinsAuthor.get(author)
        twin_model.author = twin_model_author
    if tags:
        twin_model_tags = TwinsTag.get_tags(tags)
        twin_model.tags = twin_model_tags
    twin_model.save()
    return api_return('OK', '数孪模型更新成功', twin_model.format_model())


###################################################################
# 删除模型接口
###################################################################
@api.route('/model', methods=['DELETE'])
# @need_login
def delete_model():
    """
    #group  数孪
    #name   删除数孪
    #desc   删除数孪
    #param  name            <str>     数孪名称
    #example
    {
        "name" : "model-name"
    }
    """
    name = str(g.request_data.get('name', '')).strip()

    if not name:
        return api_return('PARAM_NOT_FOUND', '缺少数孪名称')

    twin = TwinsModel.objects(name=name).first()
    if not twin:
        return {'code': 'DATA_NOT_FOUND', 'msg': '数孪不存在'}

    twin.delete()
    return {'code': 'OK', 'msg': '数孪删除成功', 'data': {
        'name': name
    }}


###################################################################
# 列出父子数孪接口
###################################################################
@api.route('/twins/relationship', methods=['GET'])
# @need_login
def model_get_relationship():
    """
    #group  数孪
    #name   列出数孪关系
    #desc   列出数孪关系
    #param  name           <str>     数孪名称
    #example
    {
        "code": "OK",
        "data": {
            "father": [],
            "child": []
        },
        "msg": "数孪关系创建成功"
    }
    """
    name = str(g.request_data.get('name', '')).strip()

    if not name:
        return api_return('PARAM_NOT_FOUND', '缺少数孪名称')

    model = TwinsModel.objects(name=name).first()
    if not model:
        return {'code': 'DATA_NOT_FOUND', 'msg': '数孪不存在'}

    father, child = TwinsRelationship.get_relationship(model=model)
    fathers = list(map(lambda x: x.child, father))
    childs = list(map(lambda x: x.father, child))

    return {'code': 'OK', 'msg': '数孪关系列出成功', 'data': {
        'fathers': format_models(fathers),
        'childs': format_models(childs),
    }}


###################################################################
# 增加父子数孪接口
###################################################################
@api.route('/twins/relationship', methods=['POST'])
# @need_login
def model_add_relationship():
    """
    #group  数孪
    #name   创建数孪关系
    #desc   创建数孪关系
    #param  father           <str>     父数孪
    #param  child            <str>     子数孪
    #example
    {
        "code": "OK",
        "data": {
            "child": {
                "author": "misaka",
                "chinese_name": "你好",
                "industry": "industry-test",
                "name": "hello-1",
                "package": "scene-test-0",
                "scene": "scene-test-0",
                "tags": [
                    "a",
                    "b",
                    "c"
                ],
                "type": "预测",
                "version": "v0.1.1"
            },
            "father": {
                "author": "misaka",
                "chinese_name": "你好",
                "industry": "industry-test",
                "name": "hello-0",
                "package": "scene-test-0",
                "scene": "scene-test-0",
                "tags": [
                    "a",
                    "b",
                    "c"
                ],
                "type": "预测",
                "version": "v0.1.1"
            }
        },
        "msg": "数孪关系删除成功"
    }
    """
    father = str(g.request_data.get('father', '')).strip()
    child = str(g.request_data.get('child', '')).strip()

    if not father:
        return api_return('PARAM_NOT_FOUND', '缺少父数孪名称')
    if not child:
        return api_return('PARAM_NOT_FOUND', '缺少子数孪名称')

    father_model = TwinsModel.objects(name=father).first()
    if not father_model:
        return {'code': 'DATA_NOT_FOUND', 'msg': '父数孪不存在'}
    child_model = TwinsModel.objects(name=child).first()
    if not child_model:
        return {'code': 'DATA_NOT_FOUND', 'msg': '子数孪不存在'}

    twin_model = TwinsRelationship.objects(father=father_model, child=child_model).first()
    if twin_model:
        return {'code': 'DATA_EXIST', 'msg': '数孪关系已存在'}

    twin_model = TwinsRelationship(father=father_model, child=child_model)
    twin_model.save()

    return {'code': 'OK', 'msg': '数孪关系创建成功', 'data': {
        'father': format_model(father_model),
        'child': format_model(child_model),
    }}


###################################################################
# 删除父子数孪接口
###################################################################
@api.route('/twins/relationship', methods=['DELETE'])
# @need_login
def model_delete_relationship():
    """
    #group  数孪
    #name   删除数孪关系
    #desc   删除数孪关系
    #param  father           <str>     父数孪
    #param  child            <str>     子数孪
    #example
    {
        "code": "OK",
        "msg": "数孪创建成功",
        "data": {
            "author": "misaka",
            "chinese_name": "你好",
            "industry": "industry-test",
            "name": "hello-0",
            "package": "scene-test-0",
            "scene": "scene-test-0",
            "tags": [
                "a",
                "b",
                "c",
            ],
            "type": "预测",
            "version": "v0.1.1"
        }
    """
    father = str(g.request_data.get('father', '')).strip()
    child = str(g.request_data.get('child', '')).strip()

    if not father:
        return api_return('PARAM_NOT_FOUND', '缺少父数孪名称')
    if not child:
        return api_return('PARAM_NOT_FOUND', '缺少子数孪名称')

    father_model = TwinsModel.objects(name=father).first()
    if not father_model:
        return {'code': 'DATA_NOT_FOUND', 'msg': '父数孪不存在'}
    child_model = TwinsModel.objects(name=child).first()
    if not child_model:
        return {'code': 'DATA_NOT_FOUND', 'msg': '子数孪不存在'}

    twin_model = TwinsRelationship.objects(father=father_model, child=child_model).first()
    if not twin_model:
        return {'code': 'DATA_EXIST', 'msg': '数孪关系不存在'}

    twin_model.delete()

    return {'code': 'OK', 'msg': '数孪关系删除成功', 'data': {
        'father': format_model(father_model),
        'child': format_model(child_model),
    }}


###################################################################
# 增加数孪标签接口
###################################################################
@api.route('/twins/tag', methods=['POST'])
# @need_login
def model_add_tag():
    """
    #group  数孪
    #name   增加数孪标签
    #desc   增加数孪标签
    #param  name            <str>     数孪名称
    #param  tags            <str>     标签
    #example
    {
        "code": "OK",
        "data": {
            "author": "misaka",
            "chinese_name": "你好",
            "industry": "industry-test",
            "name": "hello-0",
            "package": "scene-test-0",
            "scene": "scene-test-0",
            "tags": [
                "a",
                "b",
                "c",
            ],
            "type": "预测",
            "version": "v0.1.1"
        },
        "msg": "数孪创建成功"
    }
    """
    name = str(g.request_data.get('name', '')).strip()
    tags = g.request_data.get('tags', '')

    if not name:
        return api_return('PARAM_NOT_FOUND', '缺少数孪名称')
    if not tags:
        tags = []

    twin = TwinsModel.objects(name=name).first()
    if not twin:
        return {'code': 'DATA_NOT_FOUND', 'msg': '数孪不存在'}

    twin.add_tags(tags=tags)

    return {'code': 'OK', 'msg': '数孪标签更新成功', 'data': format_model(twin)}


###################################################################
# 删除数孪标签接口
###################################################################
@api.route('/twins/tag', methods=['DELETE'])
# @need_login
def model_delete_tag():
    """
    #group  数孪
    #name   删除数孪标签
    #desc   删除数孪标签
    #param  name            <str>     数孪名称
    #param  tags            <str>     标签
    #example
    {
        "code": "OK",
        "data": {
            "author": "misaka",
            "chinese_name": "你好",
            "industry": "industry-test",
            "name": "hello-0",
            "package": "scene-test-0",
            "scene": "scene-test-0",
            "tags": [
                "a",
                "b",
                "c",
            ],
            "type": "预测",
            "version": "v0.1.1"
        },
        "msg": "数孪创建成功"
    }
    """
    name = str(g.request_data.get('name', '')).strip()
    tags = g.request_data.get('tags', '')

    if not name:
        return api_return('PARAM_NOT_FOUND', '缺少数孪名称')
    if not tags:
        tags = []
    else:
        tags = tags.split(',')

    twin = TwinsModel.objects(name=name).first()
    if not twin:
        return api_return('DATA_NOT_FOUND', '数孪不存在')

    twin.delete_tags(tags=tags)

    return api_return('OK', '数孪标签更新成功', format_model(twin))


def format_domain(domains):
    res = list(map(
        lambda x: {
            'name': x.name,
            'kind': x.kind
        },
        domains))


###################################################################
# 列出数域接口
###################################################################
@api.route('/model/domain', methods=['GET'])
# @need_login
def list_domain():
    model_id = str(g.request_data.get('model', '')).strip()

    if not model_id:
        return api_return('PARAM_NOT_FOUND', '缺少数孪模型ID')

    model = TwinsModel.objects(id=model_id).first()
    if not model:
        return api_return('DATA_NOT_FOUND', '数孪模型不存在')

    domains = TwinDomain.format_domains(model.domains)
    return api_return('OK', '数域查询成功', domains)
