###################################################################
# 数孪包导入接口
###################################################################
import json
import os.path
import shutil
import uuid

from flask import g, current_app, request

from src import storage
from src.api import api, need_login
import tarfile

from src.model.twins import ModelPackage
from src.model.model import TwinsModel, TwinDomain, TwinDictionary, TwinDictionaryColumn, TwinDomainsColumn
from src.response import api_return
from src.tool import is_version


def save_image(path):
    image_path = path + '/images'
    bucket_name = current_app.config.get('MINIO_MODEL_IMAGE_BUCKET')
    images = os.listdir(image_path)
    res = {}
    for image in images:
        image_name = str(uuid.uuid1())
        res[image] = image_name
        storage.client.fput_object(bucket_name, image_name, image_path + '/' + image, content_type='image/png')
    return res


def decode_model_packages(path, industry, scene, version, author):
    file_path = path + '/modelpackages.json'
    o = open(file_path, 'r')
    data = json.loads(o.read())
    o.close()

    name = data[0]['name']
    model = ModelPackage.create(
        name=name,
        industry=industry,
        scene=scene,
        version=version,
        author=author,
    )
    return model


def decode_models(path, package, images, author):
    file_path = path + '/models.json'
    o = open(file_path, 'r')
    datas = json.loads(o.read())
    o.close()

    own_avatar_domain = current_app.config.get('MINIO_DIST_URL')
    bucket_name = current_app.config.get('MINIO_MODEL_IMAGE_BUCKET')
    res = {}
    models = []
    for data in datas:
        name = ''
        chinese = ''
        icon = ''
        icon_url = ''
        try:
            name = data['attributes']['name']
            chinese = data['attributes']['label']['i18n']['zh-CN']
            icon = data['attributes']['icon']
            icon_url = own_avatar_domain + bucket_name + '/' + images[icon.split('/')[-1]]
        except:
            pass

        twin_model = TwinsModel.create(
            package=package,
            name=name,
            chinese_name=chinese,
            icon=icon,
            author=author,
            icon_url=icon_url,
            model_type=''
        )
        res[data['_id']] = twin_model
        if twin_model['code'] == 'OK':
            models.append(twin_model['data'])
    package.add_models(models)
    return res


def decode_domains(path, package, models):
    file_path = path + '/domains.json'
    o = open(file_path, 'r')
    datas = json.loads(o.read())
    o.close()

    index = 0
    dictionary_list = [x for x in datas if not x.get('model_id')]
    domain_list = [x for x in datas if x.get('model_id')]

    dictionary_map = {}
    twin_dictionary_column_map = {}
    dictionaries = []
    for dictionary in dictionary_list:
        try:
            twin_dictionary = TwinDictionary.create(
                package=package,
                name=dictionary['name'],
                kind=dictionary['kind'],
            )
            dictionary_map[dictionary['_id']] = twin_dictionary
            dictionaries.append(twin_dictionary)
            twin_dictionary_columns = TwinDictionaryColumn.create_columns(
                package=package,
                dictionary=twin_dictionary,
                columns=dictionary['columns']
            )
            twin_dictionary_column_map.update(twin_dictionary_columns)
        except:
            pass
    package.add_dictionaries(dictionaries)

    domain_models = {}
    for domain in domain_list:
        try:
            twin_domain = TwinDomain.create(
                package=package,
                name=domain['name'],
                kind=domain['kind'],
                model=models.get(domain['model_id']),
                parent=dictionary_map.get(domain['parent_id']),
            )
            if not domain_models.get(domain['model_id']):
                domain_models[domain['model_id']] = []
            domain_models[domain['model_id']].append(twin_domain)
            columns = list(map(
                lambda x: twin_dictionary_column_map[x['parent_id']],
                domain['columns']
            ))
            TwinDomainsColumn.create_columns(
                package=package,
                model=models.get(domain['model_id']),
                domain=twin_domain,
                columns=columns,
                kind=domain['kind'],
            )
        except:
            pass
    for domain_id in domain_models:
        model = models[domain_id]
        model.add_domains(domain_models[domain_id])
    return


@api.route('/model/import', methods=['POST'])
@need_login
def model_import():
    industry = str(g.request_data.get('industry', '')).strip()
    scene = str(g.request_data.get('scene', '')).strip()
    author = str(g.request_data.get('author', '')).strip()
    version = str(g.request_data.get('version', '')).strip()

    if not version:
        version = '1.0.0'
    if not is_version(version):
        return api_return('PARAM_FORMAT_ERROR', '版本格式错误')

    file = request.files.get('file')
    if file.filename.endswith('tar.gz'):
        # 暂存文件
        tmp_dir = current_app.config.get('TMP_DIR')
        tmp_name = str(uuid.uuid1())
        tmp_zip_file = tmp_dir + '/' + tmp_name + '.tar.gz'
        file.save(tmp_zip_file)

        # 解压文件
        tmp_model_dir = tmp_dir + '/' + tmp_name
        if not os.path.isdir(tmp_model_dir):
            os.mkdir(tmp_model_dir)

        t = tarfile.open(tmp_zip_file)
        t.extractall(path=tmp_model_dir)
        t.close()

        os.remove(tmp_zip_file)

        project_path = tmp_model_dir + '/project'

        images = save_image(project_path)
        package = decode_model_packages(
            path=project_path,
            industry=industry,
            scene=scene,
            version=version,
            author=author
        )
        if package['code'] != 'OK':
            return api_return(code=package['code'], msg=package['msg'], data=(package['data']))
        package = package.get('data')
        models = decode_models(
            path=project_path,
            package=package,
            images=images,
            author=author,
        )
        for key in models:
            if models[key]['code'] != 'OK':
                return api_return(code=models[key]['code'], msg=models[key]['msg'], data=(models[key]['data']))
            else:
                models[key] = models[key]['data']
        decode_domains(project_path, package, models)

        shutil.rmtree(tmp_model_dir)

        res = package.format()
        return api_return('OK', '模型上传成功', res)


    return api_return('OK', '模型上传成功', )
