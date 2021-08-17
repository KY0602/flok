import shutil
import time
import zipfile
from model import services as anylearn
from dataset import services as file_sys
from models import *
import requests
import json
import math
from threading import Thread
from config import Config
import sys, os
import csv

NORMAL_STATE=1
SYNCING_STATE=0
SYNC_FAIL=-1
UPLAODING_STATUE=2
UPLAODING_FAIL=-2

def add_note_dataset(params,fast='true'):
    '''
    :param params: 字典类型，内含name，note_dataset_type_id，note_type_id，description，path
    :return:
    '''
    note_dataset = NoteDataset()
    id = note_dataset.id
    note_dataset.name = params['name']
    note_dataset.note_dataset_type_id = params['note_dataset_type_id']
    note_dataset.note_type_id = params['note_type_id']
    note_dataset.description = params['description']
    note_dataset.path = params['path']
    db.session.add(note_dataset)
    try:
        db.session.commit()
        if fast=='true':
            Thread(target=init_note_dataset, args=(id, params['path'])).start()
            return note_dataset, 'ok'
        else:
            return init_note_dataset(id,params['path'])
    except Exception as e:
        db.session.rollback()
        return None,str(e)


def init_note_dataset(note_dataset_id,path):
    '''
    :param note_dataset_id: 标注集id
    :param path: 数据集路径
    :return:
    '''
    # 根据路径拿到所有数据
    try:
        note_dataset = NoteDataset.query.get(note_dataset_id)
        data_instances = []
        if note_dataset.note_dataset_type_id == "27bbe41cca3e43d1b8515b35a6ffb1ab":
            data_instances = file_sys.get_image_file_dict_list(path)
        elif note_dataset.note_dataset_type_id == "4624cf7bc59c4636a89a7ee2fbfcf931":
            data_instances = file_sys.get_audio_file_dict_list(path)
    except Exception:
        return None,'路径有误'

    for items in data_instances:
        if items is None:
            continue
        data_ins = PictureInstance()
        data_ins.name = items['file_name']
        data_ins.src = items['url']
        data_ins.note_dataset_id = note_dataset_id
        db.session.add(data_ins)

    note_dataset.state = NORMAL_STATE
    try:
        db.session.commit()
        return note_dataset,'ok'
    except Exception as e:
        print(e)
        db.session.rollback()
        try:
            note_dataset = NoteDataset.query.get(note_dataset_id)
            note_dataset.state = SYNC_FAIL
            db.session.commit()
        except Exception as e:
            return None,'修改失败'
        return None,str(e)


def pre_synchronice(params):
    '''

    :param params:dict,参数包括fast，id
    :return:
    '''
    fast = params['fast']
    note_dataset = NoteDataset.query.get(params['id'])
    if note_dataset is None:
        return None, '数据库中无此id的标注集'
    note_dataset.state=SYNCING_STATE
    path = note_dataset.path
    try:
        db.session.commit()
        if fast=='true':
            Thread(target=synchronize_note_dataset, args=(params['id'],path)).start()
            return 'ok','ok'
        else:
            return synchronize_note_dataset(params['id'],path)
    except Exception as e:
        db.session.rollback()
        return None,str(e)


def synchronize_note_dataset(note_dataset_id,path):
    PictureInstance.query.filter_by(note_dataset_id=note_dataset_id).update({'is_delete': True})
    note_dataset = NoteDataset.query.get(note_dataset_id)
    data_instances = []
    if note_dataset.note_dataset_type_id == "27bbe41cca3e43d1b8515b35a6ffb1ab":
        data_instances = file_sys.get_image_file_dict_list(path)
    elif note_dataset.note_dataset_type_id == "4624cf7bc59c4636a89a7ee2fbfcf931":
        data_instances = file_sys.get_audio_file_dict_list(path)

    for items in data_instances:
        if items is None:
            continue
        tmp = PictureInstance.query.filter_by(note_dataset_id=note_dataset_id,src=items['url']).first()
        if tmp is None:
            data_ins = PictureInstance()
            data_ins.name = items['file_name']
            data_ins.src = items['url']
            data_ins.note_dataset_id = note_dataset_id
            db.session.add(data_ins)
        else:
            tmp.is_delete=False

    to_del = PictureInstance.query.filter_by(note_dataset_id=note_dataset_id,is_delete=True).all()
    for item in to_del:
        db.session.delete(item)
    note_dataset.state=NORMAL_STATE
    try:
        db.session.commit()
        return note_dataset, 'ok'
    except Exception as e:
        print(e)
        db.session.rollback()
        try:
            note_dataset = NoteDataset.query.get(note_dataset_id)
            note_dataset.state = SYNC_FAIL
            db.session.commit()
        except Exception as e:
            return None, '修改失败'
        return None, str(e)


def edit_note_dataset(params):
    '''
    :param params: dict,参数包括id，
    :return:
    '''
    note_dataset = NoteDataset.query.get(params['id'])
    if note_dataset is None:
        return None, '数据库中无此id的标注集'
    if params['name']:
        note_dataset.name=params['name']
    if params['description']:
        note_dataset.description=params['description']
    try:
        db.session.commit()
        return note_dataset, 'ok'
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_note_dataset(params):
    '''
    :param params: dict,参数包括id
    :return:
    '''
    note_dataset = NoteDataset.query.get(params['id'])
    if note_dataset is None:
        return None, '数据库中无此id的标注集'
    db.session.delete(note_dataset)
    try:
        db.session.commit()
        return True, 'ok'
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def query_note_dataset(params):
    '''
    :param params: dict,参数包括id
    :return:
    '''
    note_dataset = NoteDataset.query.get(params['id'])
    if note_dataset is None:
        return None, '数据库中无此id的标注集'
    ret={}

    main_info={}
    main_info['id']=note_dataset.id
    main_info['name']=note_dataset.name
    main_info['note_dataset_type_id']=note_dataset.note_dataset_type_id
    main_info['note_type_id']=note_dataset.note_type_id
    main_info['note_type'] = note_dataset.note_type.name
    main_info['path']=note_dataset.path
    main_info['description']=note_dataset.description
    main_info['state'] = note_dataset.state
    ret['main_info'] = main_info

    title_list=[]
    title_list.append({
        'label': '全部数据',
        'number': len(note_dataset.picture_instances),
        'name': 'first',
    })
    title_list.append({
        'label': '已标注数据',
        'number': PictureInstance.query.filter_by(note_dataset_id=params['id'],is_note=True).count(),
        'name': 'second',
    })
    title_list.append({
        'label': '未标注数据',
        'number': PictureInstance.query.filter_by(note_dataset_id=params['id'],is_note=False).count(),
        'name': 'third',
    })
    ret['title_list'] = title_list

    return ret,'ok'


def list_note_dataset():
    note_datasets = NoteDataset.query.all()
    ret=[]
    for note_dataset in note_datasets:
        item={}
        item['id'] = note_dataset.id    #标注集ID#
        item['name'] = note_dataset.name    #标注集名字#
        item['note_dataset_type_id'] = note_dataset.note_dataset_type_id    #数据集类型#
        item['note_type_id'] = note_dataset.note_type_id    #标注类型ID#
        item['note_type'] = note_dataset.note_type.name     #标注类型名字#
        item['data_type'] = note_dataset.note_dataset_type.name     #数据集类型名字#
        item['state'] = note_dataset.state      #标注集状态#
        item['file_num'] = len(note_dataset.picture_instances)      #标注集中文件数#
        item['description']=note_dataset.description        #标注集描述#
        item['path'] = note_dataset.path    #标注集路径#
        num = PictureInstance.query.filter_by(note_dataset_id=note_dataset.id,is_note=True).count()     #标注集中已被标注个数#
        item['process'] = str(num)+'/'+str(item['file_num'])    #“已被标注个数”/“总个数”#
        ret.append(item)
    return ret, 'ok'


def list_note_dataset_type():
    note_dataset_types = NoteDatasetType.query.all()
    ret = []
    for note_dataset_type in note_dataset_types:
        item = {}
        item['id'] = note_dataset_type.id   #数据集类型ID#
        item['label'] = note_dataset_type.name      #数据集类型名字#
        item['value'] = note_dataset_type.id    #数据集类型ID#
        ret.append(item)
    return ret, 'ok'


def list_note_type(params):
    '''
    :param params: dict,参数包括note_dataset_type_id
    :return:
    '''
    note_dataset_type_id =params['note_dataset_type_id']
    note_types = NoteType.query.filter_by(note_dataset_type_id=note_dataset_type_id).all()
    ret={}
    notes = []
    for note_type in note_types:
        item = {}
        item['id'] = note_type.id   #标注类型ID#
        item['label'] = note_type.name      #标注类型名字#
        item['value'] = note_type.id        #标注类型ID#
        notes.append(item)
    ret['note_types'] = notes

    paths=[]
    datasets=()
    if note_dataset_type_id == "27bbe41cca3e43d1b8515b35a6ffb1ab":
        datasets = Dataset.query.filter_by(type='image').all()
    elif note_dataset_type_id == "4624cf7bc59c4636a89a7ee2fbfcf931":
        datasets = Dataset.query.filter_by(type='audio').all()
    for dataset in datasets:
        item = {}
        item['id'] = dataset.nickname
        item['label'] = dataset.nickname
        item['value'] = dataset.nickname
        paths.append(item)
    ret['paths'] = paths

    return ret, 'ok'


def add_note(params):
    '''
    :param params: dict,参数包括name,note_dataset_id,color
    :return:
    '''
    exist = LabelInstance.query.filter_by(name=params['name'],note_dataset_id=params['note_dataset_id']).first()
    if exist is not None:
        return None,'标签名重复'
    note = LabelInstance()
    note.name = params['name']
    note.note_dataset_id = params['note_dataset_id']
    note.color = params['color']
    db.session.add(note)
    try:
        db.session.commit()
        return note, 'ok'
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def edit_note(params):
    '''
    :param params: dict,参数包括id,name,color,note_dataset_id
    :return:
    '''
    exist = LabelInstance.query.filter_by(name=params['name'],note_dataset_id=params['note_dataset_id']).first()
    if exist is not None and exist.id!=params['id']:
        return None, '标签名重复'
    note = LabelInstance.query.get(params['id'])
    if note is None:
        return None, '数据库中无此id的标签'
    if params['name']:
        note.name = params['name']
    if params['color']:
        note.color = params['color']
    try:
        db.session.commit()
        return note, 'ok'
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_note(params):
    '''
    :param params: dict,参数包括id
    :return:
    '''
    note = LabelInstance.query.get(params['id'])
    if note is None:
        return None, '数据库中无此id的标签'
    relation_pic_labs = note.relation_pic_labs
    for rel in relation_pic_labs:
        if len(rel.picture_instance.relation_pic_labs)==1:
            rel.picture_instance.is_note=False
    db.session.delete(note)
    try:
        db.session.commit()
        return True, 'ok'
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def list_note(params):
    '''
    :param params: dict,参数包括note_dataset_id
    :return:
    '''
    note_dataset_id = params['note_dataset_id']
    notes = LabelInstance.query.filter_by(note_dataset_id=note_dataset_id).all()
    ret = []
    for note in notes:
        item = {}
        item['id'] = note.id
        item['name'] = note.name
        item['color'] = note.color
        item['is_edit'] = False
        ret.append(item)
    return ret, 'ok'


def save_note_info(note_infos, picture_id):

    picture = PictureInstance.query.get(picture_id)
    if picture is None:
        return None, '数据库中无此id的数据'
    labels = picture.relation_pic_labs
    for label in labels:
        db.session.delete(label)

    for note_info in note_infos:
        label = RelationPicLab()
        label.note_data_id = picture_id
        label.label_id = note_info['label_id']
        try:
            label.content = json.dumps(note_info['content'])
        except Exception as e:
            label.content = note_info['content']
        db.session.add(label)
    try:
        if len(note_infos)>0:
            picture.is_note=True
        else:
            picture.is_note=False
        db.session.commit()
        return True,'ok'
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def get_note_info_list(picture_id):
    picture = PictureInstance.query.get(picture_id)
    if picture is None:
        return None, '数据库中无此id的数据'
    labels = picture.relation_pic_labs
    ret=[]
    for label in labels:
        item={}
        item['id'] = label.label_id
        item['label_id'] = label.label_id
        try:
            item['content'] = json.loads(label.content)
        except Exception as e:
            item['content'] = label.content
        item['name'] = label.label_instance.name
        item['color'] = label.label_instance.color
        ret.append(item)
    return ret,'ok'


def get_pictures(params):
    '''
    :param params: dict,参数包括note_dataset_id,num,page,value,with_note
    :return:
    '''
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    note_dataset = NoteDataset.query.get(params['note_dataset_id'])
    num = params['num']
    page = params['page']

    if int(page)==0:
        page=1
    if note_dataset is None:
        return None, '数据库中无此id的标注集'
    if params['value'] != '':
        pic_list = PictureInstance.query.filter_by(note_dataset_id=params['note_dataset_id']).\
            filter(PictureInstance.name.ilike("%" + params['value'] + "%"))
    else:
        pic_list = PictureInstance.query.filter_by(note_dataset_id=params['note_dataset_id'])
    if params['with_note'] is None:
        pass
    elif params['with_note']=='true':
        pic_list = pic_list.filter(PictureInstance.is_note == True)
    else:
        pic_list = pic_list.filter(PictureInstance.is_note == False)

    pic_list = sorted(pic_list, key=lambda cp: cp.create_time.strftime(TIME_FORMAT), reverse=False)

    page_max_num = math.ceil(len(pic_list) / int(num))
    if int(page) > page_max_num:
        page=page_max_num
    start = (int(page) - 1) * int(num) + 1
    end = min(len(pic_list),start+int(num)-1)
    # 计数
    count=start-1
    output_data = []

    for pic_item in pic_list[start - 1:end]:
        item={}
        item['id'] = pic_item.id
        item['name'] = pic_item.name
        item['src'] = pic_item.src
        item['order'] = count
        count+=1
        output_data.append(item)

    output_data.append({'total_page_num': page_max_num, 'total_data_num': len(pic_list)})
    return output_data,'ok'


def get_picture_group(params):
    '''
    :param params: dict,参数包括note_dataset_id,num(每页个数),offset(相对初始偏移)
    ,direction(方向 上一组/下一组),last_total_num(上次总数量)
    :return:
    '''
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    note_dataset = NoteDataset.query.get(params['note_dataset_id'])
    num = int(params['num'])
    offset = int(params['offset'])
    direction = params['direction']
    last_total_num = int(params['last_total_num'])


    if note_dataset is None:
        return None, '数据库中无此id的标注集'
    if params['value'] != '':
        pic_list = PictureInstance.query.filter_by(note_dataset_id=params['note_dataset_id']). \
            filter(PictureInstance.name.ilike("%" + params['value'] + "%"))
    else:
        pic_list = PictureInstance.query.filter_by(note_dataset_id=params['note_dataset_id'])

    if params['with_note'] is None:
        start = offset + 1
        pic_list = sorted(pic_list, key=lambda cp: cp.create_time.strftime(TIME_FORMAT), reverse=False)
        end = min(len(pic_list), start + int(num) - 1)
    elif params['with_note'] == 'true':
        pic_list = pic_list.filter(PictureInstance.is_note == True)
        pic_list = sorted(pic_list, key=lambda cp: cp.create_time.strftime(TIME_FORMAT), reverse=False)
        if direction=='next':
            noted_num = last_total_num-len(pic_list)
            start = offset + 1 - noted_num
            end = min(len(pic_list), start + int(num) - 1)
        else:
            start = offset + 1
            end = min(len(pic_list), start + int(num) - 1)
    else:
        pic_list = pic_list.filter(PictureInstance.is_note == False)
        pic_list = sorted(pic_list, key=lambda cp: cp.create_time.strftime(TIME_FORMAT), reverse=False)
        if direction=='next':
            noted_num = last_total_num-len(pic_list)
            start = offset + 1 - noted_num
            end = min(len(pic_list), start + int(num) - 1)
        else:
            start = offset + 1
            end = min(len(pic_list), start + int(num) - 1)

    # 计数
    count = 0
    output_data = []
    offset = start - 1
    if direction == 'init':
        # offset = 0
        start = offset - (offset % num) + 1
        end = min(len(pic_list), start + int(num) - 1)
        offset = start - 1
    for pic_item in pic_list[start - 1:end]:
        item = {}
        item['id'] = pic_item.id
        item['name'] = pic_item.name
        item['src'] = pic_item.src
        item['order'] = count
        item['offset'] = offset
        count += 1
        offset += 1
        output_data.append(item)

    output_data.append({'total_data_num': len(pic_list)})
    return output_data, 'ok'


def start_note(params):
    '''
    :param params: dict,参数包括 pic_id, note_dataset_id, show_type
    :return:
    '''
    ret = {}
    if params['pic_id'] is None:
        if params['note_dataset_id'] is None:
            return None,{'status':False,'info':'缺少参数'}
        pic = PictureInstance.query.filter_by(note_dataset_id=params['note_dataset_id'],is_note=False).first()
        ret['show_type'] = 'third'
        if pic is None:
            return None,{'status':True,'info':'您已全部标注'}
    else:
        ret['show_type'] = params['show_type']
        pic = PictureInstance.query.filter_by(id=params['pic_id']).first()
        if pic is None:
            return None,{'status':False,'info':'不存在该数据'}


    ret['id'] = pic.id
    ret['src'] = pic.src
    ret['name'] = pic.name
    return ret,'ok'


def pre_upload(params):
    '''
    :param params: dict,参数包括
    :return:
    '''
    ret = anylearn.connect_anylearn()
    #if ret != 'ok':
        #return None,ret
    fast = params['fast']
    name = params['name']
    note_dataset = NoteDataset.query.get(params['id'])
    if note_dataset is None:
        return None, '数据库中无此id的标注集'
    if name is None:
        name = note_dataset.name
    note_dataset.state=UPLAODING_STATUE
    try:
        db.session.commit()
        if fast=='true':
            Thread(target=upload_dataset_to_anylearn, args=(params['id'],name)).start()
            return 'ok','ok'
        else:
            return upload_dataset_to_anylearn(params['id'],name)
    except Exception as e:
        db.session.rollback()
        return None,str(e)


def upload_dataset_to_anylearn(note_dataset_id,name):
    dir_id = uuid.uuid4().hex
    if not os.path.exists(Config.ANYLEARN):
        os.mkdir(Config.ANYLEARN)
    tmp_dir = os.path.join(Config.ANYLEARN, dir_id)  # 函数下所有文件暂存的地方，最后被删掉的目录
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    file_news = os.path.join(Config.ANYLEARN, dir_id + '.zip')  # 压缩后文件夹的名字
    id = None
    try:
        store_standard_dataset(note_dataset_id, tmp_dir)
        note_dataset = NoteDataset.query.get(note_dataset_id)

        # 目标检测打包
        if note_dataset.note_type_id == '822e2bc74cb749d1b617162a05dfd8fa':
            labels = note_dataset.label_instances
            pictures = note_dataset.picture_instances
            with open(os.path.join(tmp_dir, 'labels.txt'), 'w') as f:
                for label in labels:
                    f.write(label.name+'\n')
                f.close()
            count=0

            pic_dir = os.path.join(tmp_dir, 'Images')
            os.mkdir(pic_dir)
            label_dir = os.path.join(tmp_dir, 'Labels')
            os.mkdir(label_dir)

            for picture in pictures:
                src = picture.src
                pic_path = os.path.join(pic_dir, str(count)+'.jpg')
                label_path = os.path.join(label_dir, str(count)+'.txt')
                count+=1
                relation_pic_labs = picture.relation_pic_labs
                with open(label_path, 'w') as f:
                    f.write(str(len(relation_pic_labs)))
                    for rel in relation_pic_labs:
                        content = json.loads(rel.content)
                        f.write('\n' + str(int(content['left']))+' '+str(int(content['top']))+' '
                                +str(int(content['width']+content['left']))+' '
                                +str(int(content['height']+content['top']))+' '
                                +str(rel.label_instance.name))
                    f.close()
                FLOK_URL = 'http://' + Config.SERVER_IP + ":" + Config.SERVER_PORT
                response = requests.get(FLOK_URL+str(src))
                # 获取的文本实际上是图片的二进制文本
                img = response.content
                # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
                with open(pic_path, 'wb') as f:
                    f.write(img)
                f.close()

        elif note_dataset.note_type_id == 'a030fd61081c4f6e8acf096b5718edec':
            labels = note_dataset.label_instances
            audios = note_dataset.picture_instances
            with open(os.path.join(tmp_dir, 'labels.txt'), 'w') as f:
                for label in labels:
                    f.write(label.name + '\n')
                f.close()
            count = 0

            audio_dir = os.path.join(tmp_dir, 'Audios')
            os.mkdir(audio_dir)

            for audio in audios:
                src = audio.src
                audio_path = os.path.join(audio_dir, str(count) + '.wav')
                count += 1
                relation_pic_labs = audio.relation_pic_labs
                FLOK_URL = 'http://' + Config.SERVER_IP + ":" + Config.SERVER_PORT
                response = requests.get(FLOK_URL + str(src))
                # 获取的文本实际上是图片的二进制文本
                data_ins = response.content
                # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
                with open(audio_path, 'wb') as f:
                    f.write(data_ins)
                f.close()

        # 图像分类打包
        elif note_dataset.note_type_id == '3d1fa034aa0b4ffe8f7198c027cf959e' or note_dataset.note_type_id == '669d056db83c4280b5a3b72d4f92be35':
            labels = note_dataset.label_instances
            for label in labels:
                label_dir = os.path.join(tmp_dir,label.name)
                os.mkdir(label_dir)
                relation_pic_labs = RelationPicLab.query.filter_by(label_id=label.id).all()
                count=0
                for rel in relation_pic_labs:
                    data_path = ()
                    if note_dataset.note_dataset_type_id == '27bbe41cca3e43d1b8515b35a6ffb1ab':
                        data_path = os.path.join(label_dir,str(count)+'.jpg')
                    elif note_dataset.note_dataset_type_id == '4624cf7bc59c4636a89a7ee2fbfcf931':
                        data_path = os.path.join(label_dir,str(count)+'.wav')
                    count+=1
                    src = rel.note_data_instance.src
                    FLOK_URL = 'http://' + Config.SERVER_IP + ":" + Config.SERVER_PORT
                    response = requests.get(FLOK_URL+str(src))
                    # 获取的文本实际上是图片的二进制文本
                    data_ins = response.content
                    # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
                    with open(data_path, 'wb') as f:
                        f.write(data_ins)
                    f.close()

        startdir = tmp_dir  # 要压缩的文件夹路径
        if (os.path.exists(file_news)):
            os.remove(file_news)
        z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)  # 参数一：文件夹名
        for dirpath, dirnames, filenames in os.walk(startdir):
            fpath = dirpath.replace(startdir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
            fpath = fpath and fpath + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
            for filename in filenames:
                z.write(os.path.join(dirpath, filename), fpath + filename)
        print('压缩成功')
        z.close()

        shutil.rmtree(tmp_dir)

        data_params = {'name': name, 'description': '', 'filename': dir_id + '.zip'}
        id,info = anylearn.anylearn_add_dataset(data_params['name'],data_params['filename'],data_params['description'])
        if id is None:
            print(info)
            raise Exception

        ret,info = anylearn.update_project()
        if ret is None:
            print(info)
            raise Exception

        tmp_file = open(file_news, 'rb')
        file = tmp_file.read()
        tmp_file.close()
        data = {
            'file_id': id,
            'chunk': 0
        }
        file = {'file': file}
        anylearn.anylearn_resource_upload2(data, file)
        anylearn.anylearn_resource_upload_finish2(data)

        if (os.path.exists(file_news)):
            os.remove(file_news)
        note_dataset.state = NORMAL_STATE
        db.session.commit()
        return 'ok', 'ok'
    except Exception as e:
        print(e)
        if (os.path.exists(tmp_dir)):
            os.remove(tmp_dir)
        if (os.path.exists(file_news)):
            os.remove(file_news)
        if id is not None:
            anylearn.anylearn_delete_dataset(id)
        try:
            note_dataset = NoteDataset.query.get(note_dataset_id)
            note_dataset.state = UPLAODING_FAIL
            db.session.commit()
        except Exception as e:
            return None, '修改失败'
        return None, str(e)

def store_standard_dataset(note_dataset_id, dir):
    note_dataset = NoteDataset.query.get(note_dataset_id)
    csv_dir = os.path.join(dir, 'data_output.csv')

    #Classify(Image)
    if note_dataset.note_type_id == '3d1fa034aa0b4ffe8f7198c027cf959e':
        with open(csv_dir, mode='w', newline='') as csv_out:
            fieldnames = ['sound_id', 'tags']
            writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
            writer.writeheader()
            labels = note_dataset.label_instances
            for label in labels:
                relation_pic_labs = RelationPicLab.query.filter_by(label_id=label.id).all()
                count = 0
                for rel in relation_pic_labs:
                    writer.writerow({'sound_id': rel.label_instance.name + '/' + str(count) + '.jpg', 'tags': rel.label_instance.name})
                    count += 1

    #Cut(Image)
    elif note_dataset.note_type_id == '822e2bc74cb749d1b617162a05dfd8fa':
        with open(csv_dir, mode='w', newline='') as csv_out:
            fieldnames = ['audio', 'id', 'label']
            writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
            writer.writeheader()
            path ='audios/'
            data_ins = note_dataset.picture_instances
            count = 0
            for data in data_ins:
                relation_pic_labs = data.relation_pic_labs
                data_tmp = []
                for rel in relation_pic_labs:
                    content_conv = {}
                    content = json.loads(rel.content)
                    content_conv['left'] = str(int(content['left']))
                    content_conv['top'] = str(int(content['top']))
                    content_conv['right'] = str(int(content['width'] + content['left']))
                    content_conv['bottom'] = str(int(content['height'] + content['top']))
                    content_conv['labels'] = rel.label_instance.name
                    data_tmp.append(content_conv)
                writer.writerow({'audio': path + str(count) + '.jpg', 'id': count, 'label': json.dumps(data_tmp)})
                count += 1

    #Classify(Audio)
    elif note_dataset.note_type_id == '669d056db83c4280b5a3b72d4f92be35':
        with open(csv_dir, mode='w', newline='') as csv_out:
            fieldnames = ['sound_id', 'tags']
            writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
            writer.writeheader()
            labels = note_dataset.label_instances
            for label in labels:
                relation_pic_labs = RelationPicLab.query.filter_by(label_id=label.id).all()
                count = 0
                for rel in relation_pic_labs:
                    writer.writerow({'sound_id': rel.label_instance.name + '/' + str(count) + '.wav', 'tags': rel.label_instance.name})
                    count += 1

    #Cut(Audio)
    elif note_dataset.note_type_id == 'a030fd61081c4f6e8acf096b5718edec':
        with open(csv_dir, mode='w', newline='') as csv_out:
            fieldnames = ['audio', 'id', 'label']
            writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
            writer.writeheader()
            path ='Audios/'
            data_ins = note_dataset.picture_instances
            count = 0
            for data in data_ins:
                relation_pic_labs = data.relation_pic_labs
                data_tmp = []
                for rel in relation_pic_labs:
                    content_conv = {}
                    content = json.loads(rel.content)
                    content_conv['start'] = str(round(float(content['start']),2))
                    content_conv['end'] = str(round(float(content['end']),2))
                    content_conv['labels'] = rel.label_instance.name
                    data_tmp.append(content_conv)
                writer.writerow({'audio': path + str(count) + '.wav', 'id': count, 'label': json.dumps(data_tmp)})
                count += 1


