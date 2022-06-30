###################################################################
# 数孪包导出接口
###################################################################
import datetime
import json
import shutil
import tarfile
import uuid
from openpyxl import Workbook

import os.path
from bson import ObjectId
from flask import g, current_app

from src import storage
from src.api import api
from src.model.model import TwinsModel
from src.model.twins import TwinsIndustry, TwinsScene, ModelPackage
from src.response import api_return


def make_targz(output_filename, source_dir):
    """
    一次性打包目录为tar.gz
    :param output_filename: 压缩文件名
    :param source_dir: 需要打包的目录
    :return: bool
    """
    try:
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

        return True
    except Exception as e:
        print(e)
        return False


def export_model(models, name, conflict):
    tmp_dir = current_app.config.get('TMP_DIR')
    tmp_name = str(uuid.uuid1())
    tmp_zip_file = tmp_dir + '/' + tmp_name + '.tar.gz'
    version = '1.26'

    tmp_model_dir = tmp_dir + '/' + tmp_name
    if not os.path.isdir(tmp_model_dir):
        os.mkdir(tmp_model_dir)

    tmp_project_dir = tmp_model_dir + '/project'
    if not os.path.isdir(tmp_project_dir):
        os.mkdir(tmp_project_dir)

    tmp_image_dir = tmp_project_dir + '/images'
    if not os.path.isdir(tmp_image_dir):
        os.mkdir(tmp_image_dir)

    tmp_file_dir = tmp_project_dir + '/files'
    if not os.path.isdir(tmp_file_dir):
        os.mkdir(tmp_file_dir)

    package_id = str(ObjectId())
    model_package_id = str(ObjectId())

    project = 'hello'
    scope = 'scope'

    packages = []
    models_export = []

    bucket_name = current_app.config.get('MINIO_MODEL_IMAGE_BUCKET')
    for model_id in models:
        twin_model = TwinsModel.objects(id=model_id).first()
        if not twin_model:
            return api_return('DATA_NOT_FOUND', '模型不存在')
        if twin_model not in models_export:
            models_export.append(twin_model)
        if twin_model.package not in packages:
            packages.append(twin_model.package)

    domains = []
    # 合并数据字典
    for package in packages:
        for dictionary in package.dictionary:
            _id = str(dictionary.id)
            model_name = dictionary.name
            dictionary_data = dictionary.dump(model_package_id, package_id, _id, model_name, project, scope)
            domains.append(dictionary_data)

    models = []
    # 合并数域
    for model in models_export:
        package_name = model.name
        image_name = None
        if model.icon_url and model.icon_url != '':
            icon_data = model.icon_url.split('/')
            image_name = str(ObjectId())
            image_path = tmp_image_dir + '/' + image_name
            storage.client.fget_object(icon_data[-2], icon_data[-1], image_path)
            model['icon'] = "/api/v2/images/" + image_name
        model_package = model.dump(model_package_id, package_id, package_id, project, scope, image_name)
        models.append(model_package)
        for domain in model.domains:
            _id = str(domain.id)
            domain_data = domain.dump(str(model.id), model_package_id, package_id, _id, project, scope)
            domains.append(domain_data)

    domains.reverse()

    dump_metadata = {
        "version": version
    }
    files_metadata = [
        {
            "_id": package_id,
            "capabilities": {
                "canAddChildren": True,
                "canCopy": True,
                "canDelete": True,
                "canDownload": False,
                "canEdit": True,
                "canListChildren": True,
                "canRemoveChildren": True,
                "canRename": True
            },
            "encrypted": False,
            "model_package_id": model_package_id,
            "modifiedTime": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
            "name": "root",
            "package_id": package_id,
            "project": project,
            "scope": scope,
            "type": "dir"
        }
    ]
    modelpackages = [
        {
            "_id": model_package_id,
            "name": name,
            "package_id": package_id,
            "project": project,
            "scope": version
        }
    ]
    axis = []
    tags = []

    with open(tmp_project_dir + '/domains.json', 'w') as f:
        json.dump(domains, f)
        f.close()

    with open(tmp_project_dir + '/models.json', 'w') as f:
        json.dump(models, f)
        f.close()

    with open(tmp_project_dir + '/dump_metadata.json', 'w') as f:
        json.dump(dump_metadata, f)
        f.close()

    with open(tmp_project_dir + '/files_metadata.json', 'w') as f:
        json.dump(files_metadata, f)
        f.close()

    with open(tmp_project_dir + '/modelpackages.json', 'w') as f:
        json.dump(modelpackages, f)
        f.close()

    with open(tmp_project_dir + '/axis.json', 'w') as f:
        json.dump(axis, f)
        f.close()

    with open(tmp_project_dir + '/tags.json', 'w') as f:
        json.dump(tags, f)
        f.close()
    tar_file = tmp_model_dir + '/' + name + '.tar.gz'
    make_targz(tar_file, tmp_project_dir)
    bucket_name = current_app.config.get('MINIO_PACKAGE_DOWNLOAD_BUCKET')
    tar_name = str(ObjectId()) + '.tar.gz'
    storage.client.fput_object(bucket_name, tar_name, tar_file)

    own_domain = current_app.config.get('MINIO_DIST_URL')
    upload_url = own_domain + bucket_name + '/' + tar_name

    shutil.rmtree(tmp_model_dir)
    return upload_url


@api.route('/model/export/models', methods=['POST'])
def models_export():
    models = g.request_data.get('models', '')
    name = str(g.request_data.get('name', '')).strip()
    conflict = g.request_data.get('conflict', '')

    upload_url = export_model(models, name, conflict)

    return api_return('OK', '数孪导出成功', data=upload_url)


@api.route('/model/export/scene', methods=['POST'])
def scene_models_export():
    industry = str(g.request_data.get('industry', '')).strip()
    scene = str(g.request_data.get('scene', '')).strip()
    version = str(g.request_data.get('version', '')).strip()

    twin_industry = TwinsIndustry.objects(name=industry).first()
    twin_scene = TwinsScene.objects(name=scene).first()
    model_package = ModelPackage.objects(industry=twin_industry, scene=twin_scene, version=version).first()

    upload_url = export_model(list(map(
        lambda x: x.id,
        model_package.models)),
        model_package.name, [])

    return api_return('OK', '数孪导出成功', data=upload_url)


@api.route('/model/export/model', methods=['POST'])
def model_export():
    model = str(g.request_data.get('model', '')).strip()

    if not model:
        return api_return('PARAM_NOT_FOUND', '缺乏模型ID')
    twin_model = TwinsModel.objects(id=model).first()
    if not twin_model:
        return api_return('DATA_NOT_FOUND', '找不到此模型')

    workbook = Workbook()
    for domain in twin_model.domains:
        if domain.kind == 'primary':
            sheet_name = 'P#' + domain.name
            rows = [
                'ID', 'Type', 'SecondaryDomain', 'Label.i18n.en-US', 'Label.i18n.zh-CN', 'Unit', 'Category',
                'Category.i18n.en-US', 'Category.i18n.zh-CN', 'Note.i18n.en-US', 'Note.i18n.zh-CN', 'Decimals',
                'Min', 'Max', 'Lower', 'Upper', 'FixedLen', 'MinLen', 'MaxLen', 'Validation-regex'
            ]
        elif domain.kind == 'operational':
            sheet_name = 'O#' + domain.name
            rows = [
                'ID', 'Enable', 'Type', 'DefaultStats', 'FieldType', 'SourceType', 'Timeseries', 'Snapshot',
                'Resolution', 'Raw Resolution', 'Label.i18n.en-US', 'Label.i18n.zh-CN', 'Unit', 'Scaling',
                'Category', 'Category.i18n.en-US', 'Category.i18n.zh-CN', 'Note.i18n.en-US',
                'Note.i18n.zh-CN', 'Decimals', 'Min', 'Max', 'Lower', 'Upper', 'FixedLen', 'MinLen',
                'MaxLen', 'Validation-regex', 'Formula',
            ]
        else:
            sheet_name = 'C#' + domain.name
            rows = [
                'ID', 'Type', 'Label.i18n.en-US', 'Label.i18n.zh-CN', 'Unit', 'Note.i18n.en-US',
                'Note.i18n.zh-CN', 'Min', 'Max', 'Lower', 'Upper'
            ]
        sheet = workbook.create_sheet(sheet_name)
        sheet.append(rows)
        for column in domain.columns:
            sheet.append([column.parent.name])

    workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))
    tmp_dir = current_app.config.get('TMP_DIR')
    tmp_name = str(uuid.uuid1())
    tmp_xlsx_file = tmp_dir + '/' + tmp_name + '.xlsx'
    workbook.save(tmp_xlsx_file)

    bucket_name = current_app.config.get('MINIO_PACKAGE_DOWNLOAD_BUCKET')
    tar_name = str(ObjectId()) + '.xlsx'
    storage.client.fput_object(bucket_name, tar_name, tmp_xlsx_file)

    os.remove(tmp_xlsx_file)

    own_domain = current_app.config.get('MINIO_DIST_URL')
    upload_url = own_domain + bucket_name + '/' + tar_name

    return api_return('OK', '数孪导出成功', upload_url)
