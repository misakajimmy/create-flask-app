# coding: utf-8
"""
算法接口
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
算法相关基础接口
"""
from typing import List

from flask import g

from src.api import api, need_login

###################################################################
# 列出算法接口
###################################################################
from src.model.algorithm import TwinsAlgorithm, TwinsAlgorithmRelationship
from src.model.model import TwinsModel
from src.response import api_return


# def format_algorithm(algorithm: TwinsAlgorithm):
#     return {
#         'name': algorithm.name,
#         'scene': algorithm.scene.name,
#         'chinese': algorithm.chinese_name,
#         'description': algorithm.description,
#         'tags': list(map(
#             lambda x: x.name,
#             algorithm.tags)),
#         'version': algorithm.version,
#         'author': algorithm.author.name
#     }
#
#
# def format_algorithms(algorithms: List[TwinsAlgorithm]):
#     return list(map(format_algorithm, algorithms))
#
#
# @api.route('/algorithm', methods=['GET'])
# @need_login
# def list_algorithm():
#     """
#     #group  数孪
#     #name   列出算法
#     #desc   列出算法
#     #example
#     """
#     algorithm = TwinsAlgorithm.objects().all_fields()
#     data = format_algorithms(algorithm)
#
#     return api_return('OK', '算法列出成功', data=data)
#
#
# @api.route('/algorithm', methods=['POST'])
# @need_login
# def create_algorithm():
#     """
#     #group  数孪
#     #name   创建算法
#     #desc   创建算法
#     #param  name            <str>     算法名称
#     #param  scene           <str>     场景名称
#     #param  industry        <str>     行业名称
#     #param  chinese_name    <str>     中文名称
#     #param  description     <str>     算法描述
#     #param  tags            <str>     标签
#     #param  version         <str>     版本
#     #param  author          <str>     作者
#     #example
#     {
#         "code": 0,
#         "msg": "数孪包创建成功",
#         "data": {
#             "name": "hello",
#             "scene": "test"
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
#     description = str(g.request_data.get('description', '')).strip()
#
#     if not name:
#         return api_return('PARAM_NOT_FOUND', '缺少算法名称')
#     if not chinese_name:
#         chinese_name = ''
#     if not author:
#         return api_return('PARAM_NOT_FOUND', '缺少作者名称')
#     if not industry:
#         return api_return('PARAM_NOT_FOUND', '缺少行业名称')
#     if not scene:
#         return api_return('PARAM_NOT_FOUND', '缺少场景名称')
#
#     # res = TwinsAlgorithm.create(
#     #     name=name,
#     #     chinese_name=chinese_name,
#     #     version=version,
#     #     tags=tags,
#     #     author_name=author,
#     #     industry_name=industry,
#     #     scene_name=scene,
#     #     description=description
#     # )
#     # if res['code'] == 'OK' and res['data']:
#     #     res['data'] = format_algorithm(res['data'])
#     #     return api_return(code=res['code'], msg=res['msg'], data=(res['data']))
#     # else:
#     #     return api_return(code=res['code'], msg=res['msg'])
#
#
# ###################################################################
# # 删除算法接口
# ###################################################################
# @api.route('/algorithm', methods=['DELETE'])
# @need_login
# def delete_algorithm():
#     """
#     #group  数孪
#     #name   创建算法
#     #desc   创建算法
#     #param  name            <str>     算法名称
#     #example
#     {
#         "code": 0,
#         "msg": "数孪包创建成功",
#         "data": {
#             "name": "hello",
#             "scene": "test"
#         }
#     }
#     """
#     name = str(g.request_data.get('name', '')).strip()
#
#     if not name:
#         return api_return('PARAM_NOT_FOUND', '缺少数孪名称')
#
#     algorithm = TwinsAlgorithm.objects(name=name).first()
#     if not algorithm:
#         return {'code': 'DATA_NOT_FOUND', 'msg': '算法不存在'}
#
#     algorithm.delete()
#     return {
#         'code': 'OK',
#         'msg': '算法删除成功',
#         'data': {
#             'name': name
#         }
#     }
#
#
# ###################################################################
# # 列出父子算法接口
# ###################################################################
# @api.route('/algorithm/relationship', methods=['GET'])
# @need_login
# def algorithm_list_relationship():
#     """
#     #group  数孪
#     #name   列出算法关系
#     #desc   列出算法关系
#     #param  name           <str>     算法名称
#     #example
#     {
#         "code": "OK",
#         "data": {
#             "father": [],
#             "child": []
#         },
#         "msg": "算法关系创建成功"
#     }
#     """
#     name = str(g.request_data.get('name', '')).strip()
#
#     if not name:
#         return api_return('PARAM_NOT_FOUND', '缺少算法名称')
#
#     algorithm = TwinsAlgorithm.objects(name=name).first()
#     if not algorithm:
#         return {'code': 'DATA_NOT_FOUND', 'msg': '算法不存在'}
#
#     father, child = TwinsAlgorithmRelationship.get_relationship(algorithm=algorithm)
#     fathers = list(map(lambda x: x.child, father))
#     childs = list(map(lambda x: x.father, child))
#
#     return {'code': 'OK', 'msg': '算法关系列出成功', 'data': {
#         'fathers': format_algorithms(fathers),
#         'childs': format_algorithms(childs),
#     }}
#
#
# ###################################################################
# # 增加父子算法接口
# ###################################################################
# @api.route('/algorithm/relationship', methods=['POST'])
# @need_login
# def algorithm_add_relationship():
#     """
#     #group  数孪
#     #name   创建算法关系
#     #desc   创建算法关系
#     #param  father           <str>     父算法
#     #param  child            <str>     子算法
#     return
#     """
#     father = str(g.request_data.get('father', '')).strip()
#     child = str(g.request_data.get('child', '')).strip()
#
#     if not father:
#         return api_return('PARAM_NOT_FOUND', '缺少父算法名称')
#     if not child:
#         return api_return('PARAM_NOT_FOUND', '缺少子算法名称')
#     father_algorithm = TwinsAlgorithm.objects(name=father).first()
#     if not father_algorithm:
#         return {'code': 'DATA_NOT_FOUND', 'msg': '父算法不存在'}
#     child_algorithm = TwinsAlgorithm.objects(name=child).first()
#     if not child_algorithm:
#         return {'code': 'DATA_NOT_FOUND', 'msg': '子算法不存在'}
#
#     twin_algorithm = TwinsAlgorithmRelationship.objects(father=father_algorithm, child=child_algorithm).first()
#     if twin_algorithm:
#         return {'code': 'DATA_EXIST', 'msg': '算法关系已存在'}
#
#     twin_algorithm = TwinsAlgorithmRelationship(father=father_algorithm, child=child_algorithm)
#     twin_algorithm.save()
#
#     return {'code': 'OK', 'msg': '数孪关系创建成功', 'data': {
#         'father': format_algorithm(father_algorithm),
#         'child': format_algorithm(child_algorithm),
#     }}
#
#
# ###################################################################
# # 删除父子数孪接口
# ###################################################################
# @api.route('/algorithm/relationship', methods=['DELETE'])
# @need_login
# def algorithm_delete_relationship():
#     """
#     #group  数孪
#     #name   删除算法关系
#     #desc   删除算法关系
#     #param  father           <str>     父算法
#     #param  child            <str>     子算法
#     #example
#     """
#     father = str(g.request_data.get('father', '')).strip()
#     child = str(g.request_data.get('child', '')).strip()
#
#     if not father:
#         return api_return('PARAM_NOT_FOUND', '缺少父算法名称')
#     if not child:
#         return api_return('PARAM_NOT_FOUND', '缺少子算法名称')
#     father_algorithm = TwinsAlgorithm.objects(name=father).first()
#     if not father_algorithm:
#         return {'code': 'DATA_NOT_FOUND', 'msg': '父算法不存在'}
#     child_algorithm = TwinsAlgorithm.objects(name=child).first()
#     if not child_algorithm:
#         return {'code': 'DATA_NOT_FOUND', 'msg': '子算法不存在'}
#
#     twin_algorithm = TwinsAlgorithmRelationship.objects(father=father_algorithm, child=child_algorithm).first()
#     if not twin_algorithm:
#         return {'code': 'DATA_EXIST', 'msg': '算法关系不存在'}
#
#     twin_algorithm.delete()
#
#     return {'code': 'OK', 'msg': '数孪关系删除成功', 'data': {
#         'father': format_algorithm(father_algorithm),
#         'child': format_algorithm(child_algorithm),
#     }}
#
#
# ###################################################################
# # 增加算法标签接口
# ###################################################################
# @api.route('/algorithm/tag', methods=['POST'])
# @need_login
# def algorithm_add_tag():
#     """
#     #group  数孪
#     #name   增加算法标签
#     #desc   增加算法标签
#     #param  name            <str>     算法名称
#     #param  tags            <str>     标签
#     #example
#     """
#     name = str(g.request_data.get('name', '')).strip()
#     tags = g.request_data.get('tags', '')
#
#     if not name:
#         return api_return('PARAM_NOT_FOUND', '缺少算法名称')
#     if not tags:
#         tags = []
#
#     algorithm = TwinsAlgorithm.objects(name=name).first()
#     if not algorithm:
#         return {'code': 'DATA_NOT_FOUND', 'msg': '算法不存在'}
#
#     algorithm.add_tags(tags=tags)
#
#     return {'code': 'OK', 'msg': '算法标签更新成功', 'data': format_algorithm(algorithm)}
#
#
# ###################################################################
# # 删除算法标签接口
# ###################################################################
# @api.route('/algorithm/tag', methods=['DELETE'])
# @need_login
# def algorithm_delete_tag():
#     """
#     #group  数孪
#     #name   删除算法标签
#     #desc   删除算法标签
#     #param  name            <str>     算法名称
#     #param  tags            <str>     标签
#     #example
#     {
#         "code": "OK",
#         "data": {
#             "author": "misaka",
#             "chinese_name": "你好",
#             "industry": "industry-test",
#             "name": "hello-0",
#             "package": "scene-test-0",
#             "scene": "scene-test-0",
#             "tags": [
#                 "a",
#                 "b",
#                 "c",
#             ],
#             "type": "预测",
#             "version": "v0.1.1"
#         },
#         "msg": "数孪创建成功"
#     }
#     """
#     name = str(g.request_data.get('name', '')).strip()
#     tags = g.request_data.get('tags', '')
#
#     if not name:
#         return api_return('PARAM_NOT_FOUND', '缺少算法名称')
#     if not tags:
#         tags = []
#     else:
#         tags = tags.split(',')
#
#     algorithm = TwinsAlgorithm.objects(name=name).first()
#     if not algorithm:
#         return {'code': 'DATA_NOT_FOUND', 'msg': '算法不存在'}
#
#     algorithm.delete_tags(tags=tags)
#
#     return {'code': 'OK', 'msg': '算法标签更新成功', 'data': format_algorithm(algorithm)}

