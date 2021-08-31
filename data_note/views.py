from models import *
from . import data_note_view
from util.result_wrapper import JSONWrapper
from flask import request
from flask_flok import db
from data_note import services as my_functions
from config import Config  # 获取flok的ip和端口

# .filter_by若不存在，.all()返回[]，.first()返回None

@data_note_view.route('/note_dataset/synchronization', methods=["GET"])
def synchronize_note_dataset():
    '''
    同步数据集，'fast'为true表示立即返回，为false表示等待返回，id为标注集id
    :return:
    '''
    try:
        params = {
            'id':request.args.get('id',''),
            'fast':request.args.get('fast','true')
        }
        ret,info = my_functions.pre_synchronice(params)

        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_dataset/start_note', methods=["GET"])
def start_note():
    '''
    开始标注，若data_id为none，随机选一个未标注的图片返回，否则返回data_id图片；
    show_type有全部图片、已标注、未标注三种可能，返回对应的情况
    note_dataset_id为标注集id
    :return:
    '''
    try:
        params={
            'data_id': request.args.get('data_id', None),
            'note_dataset_id': request.args.get('note_dataset_id', None),
            'show_type':request.args.get('show_type',None)
        }
        ret,info = my_functions.start_note(params=params)
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))



@data_note_view.route('/note_dataset/add', methods=["POST"])
def add_note_dataset():
    try:
        params = {
            'name':request.form.get('name','未命名'),
            'note_dataset_type_id':request.form.get('data_type','missed'),
            'note_type_id':request.form.get('note_type','missed'),
            'description':request.form.get('description',''),
            'path':request.form.get('path','missed'),
        }
        note_dataset,info = my_functions.add_note_dataset(params=params)
        if note_dataset is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(note_dataset.id)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_dataset/edit', methods=["POST"])
def edit_note_dataset():
    try:
        params = {
            'id':request.form.get('id', ''),
            'name': request.form.get('name', None),
            'description': request.form.get('description', None),
        }
        note_dataset, info = my_functions.edit_note_dataset(params=params)
        if note_dataset is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(note_dataset.id)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_dataset/delete', methods=["GET"])
def delete_note_dataset():
    try:
        params = {
            'id':request.args.get('id', ''),
        }
        success, info = my_functions.delete_note_dataset(params=params)
        if not success:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(params['id']+'删除成功！')
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_dataset/query', methods=["GET"])
def query_note_dataset():
    try:
        params = {
            'id':request.args.get('id', ''),
        }
        ret, info = my_functions.query_note_dataset(params=params)
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_dataset/list', methods=["GET"])
def get_note_dataset_list():
    try:
        ret, info = my_functions.list_note_dataset()
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_dataset_type/list', methods=["GET"])
def get_note_dataset_type_list():
    try:
        ret, info = my_functions.list_note_dataset_type()
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_type/list', methods=["GET"])
def get_note_type_list():
    try:
        params = {
            'note_dataset_type_id': request.args.get('note_dataset_type_id', ''),
        }
        ret, info = my_functions.list_note_type(params=params)
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note/add',methods=['POST'])
def add_note():
    try:
        params = {
            'name': request.form.get('name', '未命名'),
            'note_dataset_id': request.form.get('note_dataset_id', 'missed'),
            'color': request.form.get('color', 'missed'),
        }
        note, info = my_functions.add_note(params=params)
        if note is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(note.id)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note/edit',methods=['POST'])
def edit_note():
    try:
        params = {
            'id': request.form.get('id', ''),
            'name': request.form.get('name', None),
            'color': request.form.get('color', None),
            'note_dataset_id': request.form.get('note_dataset_id', 'missed'),
        }
        note, info = my_functions.edit_note(params=params)
        if note is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(note.id)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note/delete',methods=['GET'])
def delete_note():
    try:
        params = {
            'id': request.args.get('id', ''),
        }
        success, info = my_functions.delete_note(params=params)
        if not success:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(params['id'] + '删除成功！')
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note/list',methods=['GET'])
def get_note_list():
    try:
        params = {
            'note_dataset_id': request.args.get('note_dataset_id', ''),
        }
        ret, info = my_functions.list_note(params=params)
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_info/save',methods=['POST'])
def save_note_info():
    '''
    保存标注信息，data_id为数据id
    note_infos为标注信息
    :return:
    '''
    try:
        note_infos = request.form.get('note_infos', '未命名')
        note_infos = json.loads(note_infos)
        data_id = request.form.get('data_id', '未命名')
        success, info = my_functions.save_note_info(note_infos=note_infos,data_id=data_id)
        if not success:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(data_id+"标注信息保留成功")
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_info/list',methods=['GET'])
def get_note_info_list():
    try:
        data_id = request.args.get('data_id', '未命名')
        ret, info = my_functions.get_note_info_list(data_id=data_id)
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/picture/get',methods=['GET'])
def get_picture():
    '''
    总览界面的图片获取接口
    :return:
    '''
    try:
        params = {
            'page': request.args.get('page',1),
            'num': request.args.get('num',8),
            'with_note': request.args.get('with_note',None),
            'value': request.args.get('value',''),
            'note_dataset_id':request.args.get('note_dataset_id',''),
        }
        ret, info = my_functions.get_pictures(params=params)
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/picture_group/get',methods=['GET'])
def get_picture_group():
    '''
    标注界面的右下方图片组获取接口
    :return:
    '''
    try:
        params = {
            'offset': request.args.get('offset',1),
            'num': request.args.get('num',8),
            'direction':request.args.get('direction','init'),
            'with_note': request.args.get('with_note',None),
            'value': request.args.get('value',''),
            'note_dataset_id':request.args.get('note_dataset_id',''),
            'last_total_num':request.args.get('last_total_num',0),
        }
        ret, info = my_functions.get_picture_group(params=params)
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))


@data_note_view.route('/note_dataset/upload',methods=['GET'])
def upload_dataset_to_anylearn():
    '''
    打包上传图片到anylearn
    :return:
    '''
    try:
        params = {
            'id': request.args.get('id',''),
            'name':request.args.get('name',None),
            'fast':request.args.get('fast','true')
        }
        ret, info = my_functions.pre_upload(params)
        if ret is None:
            return JSONWrapper.fail(info)
        else:
            return JSONWrapper.success(ret)
    except Exception as e:
        return JSONWrapper.fail(str(e))