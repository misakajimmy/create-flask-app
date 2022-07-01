# coding: utf-8
"""
数孪包接口
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
数孪包相关基础接口
"""
import io
import json
import uuid

from flask import g, current_app, request

from src import storage
from src.model.model import TwinsModel, TwinDomainsColumn, TwinsModelType
from src.model.twins import ModelPackage, TwinsScene, TwinsIndustry, TwinsAuthor

from src.response import api_return

from src.api import api, need_login, login_user, logout_user


###################################################################
# 列出行业接口
###################################################################
@api.route('/industry', methods=['GET'])
def list_industry():
    """
    #group  数孪
    #name   列出行业
    #desc   列出行业
    #example
    {
        'code': 0,
        'msg': '成功',
        'data': {}
    }
    """
    i = TwinsIndustry.objects().all_fields()
    data = list(
        map(lambda x: {
            'name': x.name
        }, i))

    return api_return('OK', '行业列出成功', data=data)


###################################################################
# 列出场景接口
###################################################################
@api.route('/scene', methods=['GET'])
def list_scene():
    """
    #group  数孪
    #name   列出场景
    #desc   列出场景
    #example
    {
        "code": 0,
        "msg": "场景列出成功",
        "data": [
            {
                "name": "scene1",
                "industry": "industry1"
            }
        ]
    }
    """
    s = TwinsScene.objects().all_fields()
    data = list(
        map(lambda x: {
            'name': x.name,
            'industry': x.industry.name
        }, s))

    return api_return('OK', '场景列出成功', data=data)


###################################################################
# 列出作者接口
###################################################################
@api.route('/author', methods=['GET'])
def list_author():
    """
    #group  数孪
    #name   列出作者
    #desc   列出作者
    #example
    {
        "code": 0,
        "msg": "场景列出成功",
        "data": [
            {
                "name": "scene1",
                "industry": "industry1"
            }
        ]
    }
    """
    a = TwinsAuthor.objects().all_fields()
    data = list(
        map(lambda x: {
            'name': str(x.name)
        }, a))

    return api_return('OK', '作者列出成功', data=data)


###################################################################
# 列出数孪包接口
###################################################################
@api.route('/model-package', methods=['GET'])
# @need_login
def list_model_package():
    """
    #group  数孪
    #name   列出数孪包
    #desc   列出数孪包
    #example
    {
        'code': 0,
        'msg': '成功',
        'data': {'code': '123456'}
    }
    """
    model_packages = ModelPackage.objects().all_fields()
    data = list(
        map(lambda x: {'name': x.name, 'scene': x.scene.name, 'industry': x.scene.industry.name}, model_packages))

    return api_return('OK', '数孪包列出成功', data=data)


###################################################################
# 创建数孪包接口
###################################################################
@api.route('/model-package', methods=['POST'])
# @need_login
def create_model_package():
    """
    #group  数孪
    #name   创建数孪包
    #desc   创建数孪包
    #param  name      <str>     数孪包名称
    #param  scene     <str>     场景名称
    #param  industry     <str>     行业名称
    #example
    {
        "code": 0,
        "msg": "数孪包创建成功",
        "data": {
            "name": "hello",
            "scene": "test"
        }
    }
    """
    name = str(g.request_data.get('name', '')).strip()
    scene = str(g.request_data.get('scene', '')).strip()
    industry = str(g.request_data.get('industry', '')).strip()

    if not name:
        return api_return('PARAM_NOT_FOUND', '缺少数孪包名称')
    if not scene:
        return api_return('PARAM_NOT_FOUND', '缺少场景名称')
    if not industry:
        return api_return('PARAM_NOT_FOUND', '缺少行业名称')

    res = ModelPackage.create(name=name, scene=scene, industry=industry)
    if res['code'] == 'OK':
        res['data'] = {
            'name': res['data'].name,
            'scene': res['data'].scene.name,
            'industry': res['data'].industry.name
        }
        return api_return(code=res['code'], msg=res['msg'], data=(res['data']))
    else:
        return api_return(code=res['code'], msg=res['msg'])


###################################################################
# 删除数孪包接口
###################################################################
@api.route('/model-package', methods=['DELETE'])
# @need_login
def delete_model_package():
    """
    #group  数孪
    #name   删除数孪包
    #desc   删除数孪包
    #param  name      <str>     数孪包名称
    #example
    {
        "code": 0,
        "msg": "数孪包删除成功",
        "data": {
            "name": "hello"
        }
    }
    """
    name = str(g.request_data.get('name', '')).strip()
    if not name:
        return api_return('PARAM_NOT_FOUND', '缺少数孪包名称')

    res = ModelPackage.remove(name=name)

    if res.get('data'):
        return api_return(code=res['code'], msg=res['msg'], data=(res['data']))
    else:
        return api_return(code=res['code'], msg=res['msg'])


###################################################################
# 列出统计数据接口
###################################################################
@api.route('/static/all', methods=['GET'])
def get_static():
    industry_num = TwinsIndustry.objects().count()
    scene_num = TwinsScene.objects().count()
    model_num = TwinsModel.objects().count()
    algorithm_num = 0
    primary_num = TwinDomainsColumn.objects(kind='primary').count()
    operational_num = TwinDomainsColumn.objects(kind='operational').count()
    control_num = TwinDomainsColumn.objects(kind='control').count()

    data = {
        'industry': industry_num,
        'scene': scene_num,
        'model': model_num,
        'algorithm': algorithm_num,
        'primary': primary_num,
        'operational': operational_num,
        'control': control_num,
    }
    return api_return('OK', '统计数据列出成功', data=data)


###################################################################
# 列出最新模型统计数据接口
###################################################################
@api.route('/static/latest', methods=['GET'])
def get_latest_static():
    industry_num = TwinsIndustry.objects().count()
    scene_num = TwinsScene.objects().count()
    latest_package = ModelPackage.objects(is_last=True).all_fields()
    model_num = TwinsModel.objects(package__in=latest_package).count()
    algorithm_num = 0
    primary_num = TwinDomainsColumn.objects(kind='primary', package__in=latest_package).count()
    operational_num = TwinDomainsColumn.objects(kind='operational', package__in=latest_package).count()
    control_num = TwinDomainsColumn.objects(kind='control', package__in=latest_package).count()

    data = {
        'industry': industry_num,
        'scene': scene_num,
        'model': model_num,
        'algorithm': algorithm_num,
        'primary': primary_num,
        'operational': operational_num,
        'control': control_num,
    }
    return api_return('OK', '统计数据列出成功', data=data)


###################################################################
# 列出场景模型包统计接口
###################################################################
@api.route('/static/scene-model', methods=['GET'])
def get_scene_model_static():
    industry = str(g.request_data.get('industry', '')).strip()
    if industry:
        industry = TwinsIndustry.objects().first()
        scenes = TwinsScene.objects(industry=industry).all_fields()
    else:
        scenes = TwinsScene.objects().all_fields()
    res = []
    for scene in scenes:
        res.append({
            'industry': scene.industry.name,
            'scene': scene.name,
            'model': scene.model_num()
        })
    data = {
        'industries': list(map(lambda x: x.name, TwinsIndustry.objects().all_fields())),
        'scenes': res
    }
    return api_return('OK', '场景模型包统计数据列出成功', data=data)


###################################################################
# 列出场景模型包统计接口
###################################################################
@api.route('/static/model-domain', methods=['GET'])
def get_model_domain_static():
    industry = str(g.request_data.get('industry', '')).strip()
    if industry:
        industry = TwinsIndustry.objects().first()
        scenes = TwinsScene.objects(industry=industry).all_fields()
    else:
        scenes = TwinsScene.objects().all_fields()
    res = []
    for scene in scenes:
        primary_num, operational_num, control_num = scene.domain_num()
        res.append({
            'scene': scene.name,
            'model': {
                'primary': primary_num,
                'operational': operational_num,
                'control': control_num,
            }
        })
    return api_return('OK', '场景数域统计数据列出成功', data=res)


###################################################################
# 列出最新场景模型包统计接口
###################################################################
@api.route('/static/model-domain/latest', methods=['GET'])
def get_latest_model_domain_static():
    industry = str(g.request_data.get('industry', '')).strip()
    latest_package = ModelPackage.objects(is_last=True).all_fields()
    if industry:
        industry = TwinsIndustry.objects(name=industry).first()
        scenes = TwinsScene.objects(industry=industry).all_fields()
    else:
        scenes = TwinsScene.objects().all_fields()
    res = []
    for scene in scenes:
        primary_num, operational_num, control_num = scene.domain_num(latest_package=latest_package)
        res.append({
            'scene': scene.name,
            'model': {
                'primary': primary_num,
                'operational': operational_num,
                'control': control_num,
            }
        })
    return api_return('OK', '场景数域统计数据列出成功', data=res)


###################################################################
# 列出场景模型包统计接口
###################################################################
@api.route('/model/three', methods=['POST'])
def upload_3D():
    bucket_name = current_app.config.get('MINIO_3D_MODEL')

    model_id = str(g.request_data.get('model_id', '')).strip()
    model_file = request.files.get('file')

    if not model_id:
        current_app.logger.debug('缺少模型ID')
        return api_return('PARAM_ERROR', '缺少模型ID')
    if not model_file:
        current_app.logger.debug('模型错误: model file model_id:%s', model_id)
        return api_return('PARAM_ERROR', '模型错误')

    model = TwinsModel.objects(id=model_id).first()
    if not model:
        current_app.logger.debug('找不到数孪模型: model not found model_id:%s', model_id)
        return api_return('DATA_NOT_FOUND', '找不到数孪模型')

    if not storage.client.bucket_exists(bucket_name):
        storage.client.make_bucket(bucket_name)

    object_name = str(uuid.uuid1())
    data = model_file.stream.read()

    result = storage.client.put_object(
        bucket_name=bucket_name, object_name=object_name, data=io.BytesIO(data),
        length=len(data),
        content_type=model_file.content_type, )

    # 删除旧的模型
    if model.three_model:
        old_model = model.three_model.split('/')[-1]
        result = storage.client.remove_object(bucket_name=bucket_name, object_name=old_model)
        if not result:
            current_app.logger.error('旧模型删除失败: twins_model:%s, old_model:%s', model.id, old_model)

    # 将地址替换为自有域名，然后更新模型地址
    own_model_domain = current_app.config.get('MINIO_DIST_URL')
    upload_url = own_model_domain + bucket_name + '/' + object_name
    model.three_model = upload_url
    try:
        model.save()
        current_app.logger.info('上传成功: model:%s, three_model:%s', model.id, model.three_model)
        return api_return('OK', '上传成功', {'model_url': model.three_model})
    except Exception as e:
        current_app.logger.error('上传失败, model:%s, %s', model.id, e)
        return api_return('FAILED', '上传失败')


###################################################################
# 列出数孪类型接口
###################################################################
@api.route('/types', methods=['GET'])
def get_types():
    types = TwinsModelType.objects().all_fields()
    types = TwinsModelType.format_types(types)
    return api_return('OK', '数孪类型列出成功', data=types)
