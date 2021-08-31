# -*- coding:utf-8 -*-
from flask_flok import db, get_user
from datetime import datetime, timezone
import json
import uuid


class Base(object):
    def to_json(self, transform_date=False):
        json_exclude = getattr(self, '__json_exclude__', set())
        if transform_date:
            self_dict = {}
            for key, value in self.__dict__.items():
                if not key.startswith('_') and key not in json_exclude:
                    if isinstance(value, datetime):
                        self_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        self_dict[key] = value
            return self_dict
        return {key: value for key, value in self.__dict__.items()
                if not key.startswith('_')
                and key not in json_exclude}


class User(db.Model, Base):
    __tablename__ = 'users'
    id = db.Column(db.String(32), primary_key=True)
    login_name = db.Column(db.String(50))
    passwd = db.Column(db.String(50))
    components= db.relationship("Component", backref="author", lazy='dynamic')
    applications = db.relationship("Application", backref="author", lazy='dynamic')
    workbooks = db.relationship("Workbook", backref="author", lazy='dynamic')
    def __repr__(self):
        return '<User %r>' % self.login_name
    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class Component(db.Model, Base):
    __tablename__ = 'components'
    id = db.Column(db.String(32), primary_key=True)
    nickname = db.Column(db.String(50))
    operator_id = db.Column(db.String(32), db.ForeignKey('operators.id', deferrable=True, initially="DEFERRED"))
    description = db.Column(db.String(500), nullable=True)
    group_id = db.Column(db.String(32))
    author_id = db.Column(db.String(32), db.ForeignKey('users.id', deferrable=True, initially="DEFERRED"),nullable=True)
    create_time = db.Column(db.DateTime,default=datetime.now)
    update_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    statistic = db.relationship("ComponentStatistic", backref="component", lazy='dynamic')

    def __init__(self, description=None, author_id=None):
        self.description = description
        self.author_id = author_id
        self.id = str(uuid.uuid4()).replace("-", "")
    def __iter__(self):
        yield 'id', self.id
        yield 'nickname', self.nickname
        yield 'operator_id', self.operator_id
        yield 'description', self.description
        yield 'group_id', self.group_id
        yield 'author_id', self.author_id
        yield 'create_time', self.create_time
        yield 'update_time', self.update_time
        yield 'statistic', self.statistic

    def __repr__(self):
        return '<Operator %r>' % self.nickname

    def to_dict(self):
        '''将对象转换为字典数据'''
        comp_dict = {
            'id':self.id,
            "operator_id": self.operator_id,
            'update_time':self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return comp_dict



class Operator(db.Model, Base):
    __tablename__ = 'operators'
    id = db.Column(db.String(32), primary_key=True)
    dev_language = db.Column(db.String(50))
    wrapper_name = db.Column(db.String(100), unique=True)
    run_env_type = db.Column(db.String(50))
    impl_path = db.Column(db.String(200))
    entry_class = db.Column(db.String(200))
    version_code = db.Column(db.String(200))
    built_in = db.Column(db.Boolean,default=False)
    is_deleted = db.Column(db.Boolean,default=False)
    is_concurrent = db.Column(db.Boolean,default=False)
    algorithm_type_id = db.Column(db.String(32), db.ForeignKey('algorithm_type.id', deferrable=True, initially="DEFERRED"))
    is_preview = db.Column(db.Boolean, default=False)
    need_execute = db.Column(db.Boolean, default=False)
    plt_owner = db.Column(db.String(32))
    plt_creator = db.Column(db.String(32))
    plt_createtime = db.Column(db.DateTime, default=datetime.now)
    plt_lastmodifer = db.Column(db.String(32), onupdate=get_user)
    plt_lastmodifytime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    components = db.relationship("Component", backref="operator", lazy='dynamic')
    ports = db.relationship("Port", backref="operator", lazy='dynamic')
    parameters = db.relationship("Parameter", backref="operator", lazy='dynamic')
    nodes = db.relationship("Node", backref="operator", lazy='dynamic')

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")
        self.plt_owner = get_user()
        self.plt_creator = get_user()
        self.plt_lastmodifer = get_user()

    def __repr__(self):
        return '<Operator %r>' % self.wrapper_name




class Tag(db.Model, Base):
    __tablename__ = 'tag'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(200))

    def __repr__(self):
        return '<Tag %r>' % self.name
    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class OperatorTag(db.Model, Base):
    __tablename__ = 'operator_tag'
    id = db.Column(db.String(32), primary_key=True)
    operator_id = db.Column(db.String(32), db.ForeignKey('operators.id', deferrable=True, initially="DEFERRED"),
                            nullable=True)
    tag_id = db.Column(db.String(32), db.ForeignKey('tag.id', deferrable=True, initially="DEFERRED"), nullable=True)

    def __repr__(self):
        return '<OperatorTag %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")




class ComponentStatistic(db.Model, Base):
    __tablename__ = 'component_statistics'
    id = db.Column(db.String(32), primary_key=True)
    using_count = db.Column(db.Integer)
    component_id = db.Column(db.String(32), db.ForeignKey('components.id', deferrable=True, initially="DEFERRED"))

    def __repr__(self):
        return '<OperatorStatistic %r>' % self.id

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class Datasource(db.Model, Base):
    __tablename__ = 'datasources'
    id = db.Column(db.String(32), primary_key=True)
    nickname = db.Column(db.String(50))
    type = db.Column(db.String(100))
    ip = db.Column(db.String(255))
    port = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    description = db.Column(db.String(255))
    database_name = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.now)
    HDFS_path = db.Column(db.String(255))

    #datasets = db.relationship("Dataset", backref="datasources", lazy='dynamic')

    def __repr__(self):
        return '<Datasource %r>' % self.nickname

    def __init__(self, login_name=None, passwd=None,description=None):
        self.login_name = login_name
        self.passwd = passwd
        self.description = description
        self.id = str(uuid.uuid4()).replace("-", "")


class Dataset(db.Model, Base):
    __tablename__ = 'datasets'
    id = db.Column(db.String(32), primary_key=True)
    nickname = db.Column(db.String(50))
    description = db.Column(db.String(500))
    datasource_id = db.Column(db.String(255), db.ForeignKey('datasources.id', deferrable=True, initially="DEFERRED"))
    datasource_name = db.Column(db.String(255))
    group_id = db.Column(db.String(32))
    create_time = db.Column(db.DateTime, default=datetime.now)
    sql = db.Column(db.String(255))
    delimiter = db.Column(db.String(255))
    device = db.Column(db.String(255))
    metrics = db.Column(db.String(255))
    starttime = db.Column(db.String(255))
    endtime = db.Column(db.String(255))
    window = db.Column(db.String(255))
    delta_t = db.Column(db.String(255))
    display = db.Column(db.String(255))
    match_selection = db.Column(db.String(255))
    header_text = db.Column(db.String(255))
    type = db.Column(db.String(32))
    path=db.Column(db.String(255))

    #datasource_id = db.Column(db.String(32), db.ForeignKey('datasources.id', deferrable=True, initially="DEFERRED"))
    def __init__(self, description=None, datasource_id=None, definition=None):
        self.description = description
        self.datasource_id = datasource_id
        self.definition = definition
        self.id = str(uuid.uuid4()).replace("-", "")

    def __repr__(self):
        return '<Dataset %r>' % self.nickname

    def to_dict(self):
        '''将对象转换为字典数据'''
        ds_dict = {
            'id':self.id,
            "nickname": self.nickname,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'description':self.description,
            'datasource_id':self.datasource_id,
            'datasource_name':self.datasource_name,
            'sql':self.sql,
            'delimiter':self.delimiter,
            'device':self.device,
            'metrics':self.metrics,
            'starttime':self.starttime,
            'endtime':self.endtime,
            'window':self.window,
            'delta_t':self.delta_t,
            'display':self.display,
            'match_selection':self.match_selection,
            'header_text':self.header_text,
            'group_id':self.group_id,
            'type':self.type,
            'path':self.path
        }
        return ds_dict

class DatasetBind(db.Model, Base):
    __tablename__ = 'dataset_bind'
    id = db.Column(db.String(32), primary_key=True)
    category_id = db.Column(db.String(32))
    category = db.Column(db.String(20))
    usage_type = db.Column(db.String(10))
    dataset_id = db.Column(db.String(32))

    def __init__(self, category_id=None, category=None, usage_type=None, dataset_id=None):
        self.id = str(uuid.uuid4()).replace("-", "")
        self.category_id = category_id
        self.category = category
        self.usage_type = usage_type
        self.dataset_id = dataset_id

    def __repr__(self):
        return "<DatasetBind(category_id='%s', category='%s', dataset_id='%s')>" \
               % (self.category_id, self.category, self.dataset_id)


class Parameter_format(db.Model, Base):
    __tablename__ = 'parameter_format'
    id = db.Column(db.String(255), primary_key=True)
    operator_id = db.Column(db.String(255))
    type = db.Column(db.String(255))
    name = db.Column(db.String(255))
    left = db.Column(db.String(255))
    right = db.Column(db.String(255))
    regex = db.Column(db.String(255))
    default = db.Column(db.String(255))

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")

    def __repr__(self):
        return '<Parameter_format %r>' % self.nickname


class Model(db.Model, Base):
    __tablename__ = 'model'
    id = db.Column(db.String(32), primary_key=True)
    path =db.Column(db.String(200))
    nickname = db.Column(db.String(50))
    description = db.Column(db.String(500),nullable=True)
    framework_type = db.Column(db.String(50))
    instruction = db.Column(db.String(100))

    def __repr__(self):
        return '<Model %r>' % self.id

    def __init__(self, description=None):
        self.description = description
        self.id = str(uuid.uuid4()).replace("-", "")


class Port(db.Model, Base):
    __tablename__ = 'ports'
    id = db.Column(db.String(32), primary_key=True)
    default_name = db.Column(db.String(50))
    port_value_type = db.Column(db.String(50))
    port_type = db.Column(db.String(10))        # in, out
    datalink_num = db.Column(db.Integer)        #最大允许连接的数据流个数
    order_in_operator = db.Column(db.Integer)
    operator_id = db.Column(db.String(32), db.ForeignKey('operators.id', deferrable=True, initially="DEFERRED"))
    port_data_type_id = db.Column(db.String(32), db.ForeignKey('data_type.id', deferrable=True, initially="DEFERRED"))

    in_port_instances = db.relationship("InPortInstance", backref="port", lazy='dynamic')
    out_port_instances = db.relationship("OutPortInstance", backref="port", lazy='dynamic')

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")

    def __repr__(self):
        return '<Port %r>' % self.default_name

class FormatType(db.Model, Base):
    __tablename__ = 'format_type'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    label = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    built_in = db.Column(db.Boolean, default=False)
    is_anylearn = db.Column(db.Boolean, default=False)
    format_params = db.relationship("FormatParams", backref="format_type", lazy='dynamic')
    paramter = db.relationship("Parameter", backref="format_type", lazy='dynamic')
    value_type = db.Column(db.String(50))
    def __init__(self, default_value=None,candidates=None, format=None):
        self.id = str(uuid.uuid4()).replace("-", "")

    def __repr__(self):
        return '<FormatType %r>' % self.label


class FormatParams(db.Model, Base):
    __tablename__ = 'format_params'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    value_type = db.Column(db.String(50))
    type_id = db.Column(db.String(32), db.ForeignKey('format_type.id', deferrable=True, initially="DEFERRED"))
    var_name = db.Column(db.String(50))
    def __init__(self, default_value=None,candidates=None, format=None):
        self.id = str(uuid.uuid4()).replace("-", "")

    def __repr__(self):
        return '<FormatParams %r>' % self.name


class Parameter(db.Model, Base):
    __tablename__ = 'parameters'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100))
    nickname = db.Column(db.String(100))
    order_in_operator = db.Column(db.Integer)
    value_type = db.Column(db.String(50))
    candidates = db.Column(db.String(50))
    format = db.Column(db.String(50))
    default_value = db.Column(db.String(100),nullable=True)
    operator_id = db.Column(db.String(32), db.ForeignKey('operators.id', deferrable=True, initially="DEFERRED"))
    format_id = db.Column(db.String(32), db.ForeignKey('format_type.id', deferrable=True, initially="DEFERRED"))
    format_params = db.Column(db.String(1000))
    pattern = db.Column(db.String(200))
    description = db.Column(db.String(1000))
    parameter_instances = db.relationship("ParameterInstance", backref="param", lazy='dynamic')
    def __init__(self, default_value=None,candidates=None, format=None):
        self.default_value = default_value
        self.candidates = candidates
        self.format = format
        self.id = str(uuid.uuid4()).replace("-", "")

    def __repr__(self):
        return '<Parameter %r>' % self.name


class Application(db.Model, Base):
    __tablename__ = 'applications'
    id = db.Column(db.String(32), primary_key=True)
    nickname = db.Column(db.String(50))
    workflow_id = db.Column(db.String(32), db.ForeignKey('workflows.id', deferrable=True, initially="DEFERRED"))
    author_id = db.Column(db.String(32), db.ForeignKey('users.id', deferrable=True, initially="DEFERRED"), nullable=True)
    create_time = db.Column(db.DateTime,default=datetime.now)
    layout = db.Column(db.Text)
    definition = db.Column(db.Text)
    description = db.Column(db.Text)
    parent_app_id = db.Column(db.Text)
    type = db.Column(db.Integer) # 0:不打包 1：打包
    application_config = db.relationship("ApplicationConfigs", backref="application", lazy='dynamic')
    application_runtime = db.relationship("ApplicationRuntime", backref="application", lazy='dynamic')
    application_variables = db.relationship("ApplicationVariable", backref="application", lazy='dynamic')
    application_returns = db.relationship("ApplicationReturn", backref="application", lazy='dynamic')

    def __repr__(self):
        return '<Application %r>' % self.nickname

    def __init__(self, author_id=None, description=None):
        self.author_id = author_id
        self.description = description
        self.id = str(uuid.uuid4()).replace("-", "")


class ApplicationVariable(db.Model, Base):
    __tablename__ = 'application_variables'
    id = db.Column(db.String(32), primary_key=True)
    value_type = db.Column(db.String(50))
    default_value = db.Column(db.String(50))
    value = db.Column(db.String(1000))
    name = db.Column(db.String(50))
    note = db.Column(db.String(100))
    application_id = db.Column(db.String(32), db.ForeignKey('applications.id', deferrable=True, initially="DEFERRED"),
                               nullable=True)

    def __repr__(self):
        return '<ApplicationVariable %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class ApplicationReturn(db.Model, Base):
    __tablename__ = 'application_returns'
    id = db.Column(db.String(32), primary_key=True)
    application_id = db.Column(db.String(32), db.ForeignKey('applications.id', deferrable=True, initially="DEFERRED"),
                               nullable=True)
    node_id = db.Column(db.String(100), nullable=True)
    out_port_id = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return '<ApplicationReturn %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class Exceptions(db.Model, Base):
    __tablename__ = 'exceptions'
    id = db.Column(db.String(32), primary_key=True)
    exception_code = db.Column(db.Integer)
    exception_message = db.Column(db.String(500))
    def __repr__(self):
        return '<Exceptions %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class Workflow(db.Model, Base):
    __tablename__ = 'workflows'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    workflow_type = db.Column(db.String(20))
    layout = db.Column(db.Text)
    definition = db.Column(db.Text)
    workbook_id = db.Column(db.String(32), db.ForeignKey('workbooks.id', deferrable=True, initially="DEFERRED"))
    version_code = db.Column(db.String(50))
    previous_version_code = db.Column(db.String(50))
    author_id = db.Column(db.String(32))
    created_at = db.Column(db.DateTime,default=datetime.now)
    recent_workflow_runtime_id = db.Column(db.String(32))
    description = db.Column(db.String(1000))
    streaming_type = db.Column(db.String(32), db.ForeignKey('algorithm_type.id', deferrable=True, initially="DEFERRED"))
    applications = db.relationship("Application", backref="workflow", lazy='dynamic')
    nodes = db.relationship("Node", backref="workflow", lazy='dynamic')
    workflow_runtime = db.relationship("WorkflowRuntime", backref="workflow", lazy='dynamic')
    workflow_variables = db.relationship("WorkflowVariable", backref="workflow", lazy='dynamic')
    workflow_returns = db.relationship("WorkflowReturn", backref="workflow", lazy='dynamic')

    def __repr__(self):
        return '<Workflow %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class ApplicationConfigs(db.Model, Base):
    __tablename__ = 'application_configs'
    id = db.Column(db.String(32), primary_key=True)
    show_id = db.Column(db.String(32))
    name = db.Column(db.String(50))
    description = db.Column(db.String(500))
    author_id = db.Column(db.String(32))
    created_at = db.Column(db.DateTime,default=datetime.now)
    last_edited = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    is_packaged = db.Column(db.Boolean, default=False)
    status = db.Column(db.Integer)
    config_variables = db.Column(db.Text)
    timing_type = db.Column(db.String(50))
    timing_content = db.Column(db.String(200))
    core = db.Column(db.Integer)
    executor_cores = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    driver_memory = db.Column(db.Integer)
    priority = db.Column(db.String(50))
    exception_type = db.Column(db.String(50))
    restart_number = db.Column(db.Integer)
    storage_type = db.Column(db.Text)
    max_duration = db.Column(db.String(100))
    application_id = db.Column(db.String(32), db.ForeignKey('applications.id', deferrable=True, initially="DEFERRED"), nullable=True)
    dag_id = db.Column(db.String(100))
    plt_owner = db.Column(db.String(32))
    plt_creator = db.Column(db.String(32))
    plt_createtime = db.Column(db.DateTime, default=datetime.now)
    plt_lastmodifer = db.Column(db.String(32), onupdate=get_user)
    plt_lastmodifytime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    application_runtimes = db.relationship("ApplicationRuntime", backref="application_config", lazy='dynamic')

    def __repr__(self):
        return json.dumps({'id':self.id,
                           'show_id':self.show_id,
                           'name': self.name,
                           'description':self.description,
                           'author_id':self.author_id,
                           'created_at':self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                           'last_edited':self.last_edited.strftime("%Y-%m-%d %H:%M:%S"),
                           'is_deleted':self.is_deleted,
                           'is_packaged':self.is_packaged,
                           'status':self.status,
                           'config_variables':self.config_variables,
                           'timing_type':self.timing_type,
                           'timing_content':self.timing_content,
                           'core':self.core,
                           'executor_cores':self.executor_cores,
                           'memory':self.memory,
                           'driver_memory':self.driver_memory,
                           'priority':self.priority,
                           'exception_type':self.exception_type,
                           'restart_number':self.restart_number,
                           'storage_type':self.storage_type,
                           'max_duration':self.max_duration})

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")
        self.plt_owner = get_user()
        self.plt_creator = get_user()
        self.plt_lastmodifer = get_user()


class WorkflowVariable(db.Model, Base):
    __tablename__ = 'workflow_variables'
    id = db.Column(db.String(32), primary_key=True)
    value_type = db.Column(db.String(50))
    default_value = db.Column(db.String(50))
    value = db.Column(db.String(50))
    name = db.Column(db.String(50))
    note = db.Column(db.String(100))
    dataset_value = db.Column(db.String(50))
    workflow_id = db.Column(db.String(32), db.ForeignKey('workflows.id', deferrable=True, initially="DEFERRED"),
                            nullable=True)

    def __repr__(self):
        return '<WorkflowVariable %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class WorkflowReturn(db.Model, Base):
    __tablename__ = 'workflow_returns'
    id = db.Column(db.String(32), primary_key=True)
    workflow_id = db.Column(db.String(32), db.ForeignKey('workflows.id', deferrable=True, initially="DEFERRED"),
                            nullable=True)
    node_id = db.Column(db.String(100), nullable=True)
    out_port_id = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return '<WorkflowReturn %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class Workbook(db.Model, Base):
    __tablename__ = 'workbooks'
    id = db.Column(db.String(32), primary_key=True)
    nickname = db.Column(db.String(50))
    author_id = db.Column(db.String(32),db.ForeignKey('users.id', deferrable=True, initially="DEFERRED"),
                          nullable=True)
    last_edited = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean)
    description=db.Column(db.String(200))
    recent_generator_workflow_id = db.Column(db.String(32))
    recent_application_workflow_id = db.Column(db.String(32))
    workflows = db.relationship("Workflow", backref="workbook", lazy='dynamic')
    parent_workflow_id = db.Column(db.String(32))
    plt_owner = db.Column(db.String(32))
    plt_creator = db.Column(db.String(32))
    plt_createtime = db.Column(db.DateTime, default=datetime.now)
    plt_lastmodifer = db.Column(db.String(32), onupdate=get_user)
    plt_lastmodifytime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    group_id = db.Column(db.String(32))

    def __repr__(self):
        return '<Workbook %r>' % self.nickname

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")
        self.plt_owner = get_user()
        self.plt_creator = get_user()
        self.plt_lastmodifer = get_user()



class Node(db.Model, Base):
    __tablename__ = 'nodes'
    id = db.Column(db.String(32), primary_key=True)
    operator_id = db.Column(db.String(32), db.ForeignKey('operators.id', deferrable=True, initially="DEFERRED"))
    workflow_id = db.Column(db.String(32), db.ForeignKey('workflows.id', deferrable=True, initially="DEFERRED"))
    nodeid_in_workflow = db.Column(db.String(100))
    parameter_instances = db.relationship("ParameterInstance", backref="node", lazy='dynamic')
    in_port_instances = db.relationship("InPortInstance", backref="node", lazy='dynamic')
    out_port_instances = db.relationship("OutPortInstance", backref="node", lazy='dynamic')
    application_id = db.Column(db.String(32), db.ForeignKey('applications.id', deferrable=True, initially="DEFERRED"),
                               nullable=True)

    def __repr__(self):
        return '<Node %r>' % self.id

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class ParameterInstance(db.Model, Base):
    __tablename__ = 'parameter_instances'
    id = db.Column(db.String(32), primary_key=True)
    node_id = db.Column(db.String(32), db.ForeignKey('nodes.id', deferrable=True, initially="DEFERRED"))
    param_id = db.Column(db.String(32), db.ForeignKey('parameters.id', deferrable=True, initially="DEFERRED"))
    param_value = db.Column(db.Text)

    def __repr__(self):
        return 'ParameterInstance %r>' % self.id

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class InPortInstance(db.Model, Base):
    __tablename__ = 'in_port_instances'
    id = db.Column(db.String(32), primary_key=True)
    node_id = db.Column(db.String(32), db.ForeignKey('nodes.id', deferrable=True, initially="DEFERRED"))
    port_id = db.Column(db.String(32), db.ForeignKey('ports.id', deferrable=True, initially="DEFERRED"))
    out_port_id = db.Column(db.String(32), db.ForeignKey('out_port_instances.id', deferrable=True, initially="DEFERRED")) #接收的前置out_port

    def __repr__(self):
        return '<InPortInstance %r>' % self.id

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class OutPortInstance(db.Model, Base):
    __tablename__ = 'out_port_instances'
    id = db.Column(db.String(32), primary_key=True)
    node_id = db.Column(db.String(32), db.ForeignKey('nodes.id', deferrable=True, initially="DEFERRED"))
    port_id = db.Column(db.String(32), db.ForeignKey('ports.id', deferrable=True, initially="DEFERRED"))
    nickname = db.Column(db.String(50))
    in_port_instances = db.relationship("InPortInstance", backref="out_port", lazy='dynamic')
    node_runtime_outputs = db.relationship("NodeRuntimeOutput", backref="out_port", lazy='dynamic')

    def __repr__(self):
        return '<OutPortInstance %r>' % self.nickname
    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")



class WorkflowRuntime(db.Model, Base):
    __tablename__ = 'workflow_runtime'
    id = db.Column(db.String(32), primary_key=True)
    workflow_id = db.Column(db.String(32), db.ForeignKey('workflows.id', deferrable=True, initially="DEFERRED"))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20),default="running")
    node_runtime = db.relationship("NodeRuntime", backref="workflow_runtime", lazy='dynamic')

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class NodeRuntime(db.Model, Base):
    __tablename__ = 'node_runtime'
    id = db.Column(db.String(32), primary_key=True)
    node_id = db.Column(db.String(32), db.ForeignKey('nodes.id', deferrable=True, initially="DEFERRED"))
    workflow_runtime_id = db.Column(db.String(32), db.ForeignKey('workflow_runtime.id', deferrable=True, initially="DEFERRED"))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="undo")
    node_runtime_outputs = db.relationship("NodeRuntimeOutput", backref="node_runtime", lazy='dynamic')
    application_runtime_id = db.Column(db.String(32))

    def __repr__(self):
        return '<NodeRuntime %r>' % self.id
    def __init__(self, node_id=None, workflow_runtime_id=None, application_runtime_id=None, status=None):
        self.id = str(uuid.uuid4()).replace("-", "")
        self.node_id = node_id
        self.workflow_runtime_id = workflow_runtime_id
        self.application_runtime_id = application_runtime_id
        self.status = status



#并行子流程节点关联
class NodesSubflow(db.Model, Base):
    __tablename__ = 'nodes_subflow'
    id = db.Column(db.String(32), primary_key=True)
    node_id = db.Column(db.String(100))
    workflow_id = db.Column(db.String(32))
    f_workbook_id=db.Column(db.String(32))

    def __repr__(self):
        return '<NodesSubflow %r>' % self.id
    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")



#子流程节点关联
class NodesSubWorkflow(db.Model, Base):
    __tablename__ = 'nodes_sub_workflow'
    id = db.Column(db.String(32), primary_key=True)
    node_id_workflow = db.Column(db.String(100))
    workbook_id = db.Column(db.String(32))
    f_workbook_id=db.Column(db.String(32))

    def __repr__(self):
        return '<NodesSubWorkflow %r>' % self.id
    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")



class NodeRuntimeOutput(db.Model, Base):
    __tablename__ = 'node_runtime_outputs'
    id = db.Column(db.String(32), primary_key=True)
    node_runtime_id = db.Column(db.String(32), db.ForeignKey('node_runtime.id', deferrable=True, initially="DEFERRED"))
    out_port_id = db.Column(db.String(32), db.ForeignKey('out_port_instances.id', deferrable=True, initially="DEFERRED"))
    path = db.Column(db.String(200))
    iteration_count = db.Column(db.Integer)
    visualization_node_id = db.Column(db.String(32), db.ForeignKey('visualization_nodes.id', deferrable=True, initially="DEFERRED"))
    format = db.Column(db.String(50))
    location = db.Column(db.String(50))

    def __repr__(self):
        return '<NodeRuntimeOutput %r>' % self.id
    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")



class VisualizationNode(db.Model, Base):
    __tablename__ = 'visualization_nodes'
    id = db.Column(db.String(32), primary_key=True)
    file_name = db.Column(db.String(200))
    file_path = db.Column(db.String(200))
    status = db.Column(db.String(20),default="running")
    node_runtime_outputs = db.relationship("NodeRuntimeOutput", backref="visualization_nodes", lazy='dynamic')

    def __repr__(self):
        return '<VisualizationNode %r>' % self.id
    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")



class ApplicationRuntime(db.Model, Base):
    __tablename__ = 'application_runtime'
    id = db.Column(db.String(32), primary_key=True)
    application_id = db.Column(db.String(32), db.ForeignKey('applications.id', deferrable=True, initially="DEFERRED"))
    application_config_id = db.Column(db.String(32), db.ForeignKey('application_configs.id', deferrable=True, initially="DEFERRED"))
    start_time = db.Column(db.DateTime)
    definition = db.Column(db.Text)
    remain_restart_times = db.Column(db.Integer)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20),default="running")
    is_subflow = db.Column(db.Integer,default=0)
    terminate_type = db.Column(db.String(100))
    terminate_reason = db.Column(db.Text)
    exception_id = db.Column(db.String(32),db.ForeignKey('exceptions.id', deferrable=True, initially="DEFERRED"))
    stream_job_id = db.Column(db.String(32))
    application_runtime_output = db.relationship("ApplicationRuntimeOutput", backref="application_runtime", lazy='dynamic')
    plt_owner = db.Column(db.String(32))
    plt_creator = db.Column(db.String(32))
    plt_createtime = db.Column(db.DateTime, default=datetime.now)
    plt_lastmodifer = db.Column(db.String(32))
    plt_lastmodifytime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class ApplicationRuntimeOutput(db.Model, Base):
    __tablename__ = 'application_runtime_outputs'
    id = db.Column(db.String(32), primary_key=True)
    application_runtime_id = db.Column(db.String(32), db.ForeignKey('application_runtime.id', deferrable=True, initially="DEFERRED"))
    node_id = db.Column(db.String(32))
    out_port_id = db.Column(db.String(32))
    path = db.Column(db.String(200))

    def __repr__(self):
        return '<ApplicationRuntimeOutput %r>' % self.id
    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class RunEnvironment(db.Model, Base):
    __tablename__ = 'run_environment'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(50))
    package_info = db.Column(db.String(100))
    allowed_input_type= db.Column(db.String(100))
    allowed_output_type = db.Column(db.String(100))
    data_dict = db.Column(db.Text)
    start_type = db.Column(db.String(50))
    start_content = db.Column(db.Text)
    end_type = db.Column(db.String(50))
    end_content = db.Column(db.Text)
    query_interval = db.Column(db.Integer)

    def __repr__(self):
        return '<RunEnvironment %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")


class Environment(db.Model):
    __tablename__ = 'environment'
    id = db.Column(db.String(32), primary_key=True)
    group = db.Column(db.String(50))  # python, spark, pyspark
    fullname = db.Column(db.String(50))  # Python Remote, Python Local
    unique_name = db.Column(db.String(30), unique=True, nullable=False)  # python_remote_1
    logo = db.Column(db.Text)
    # variables = db.Column(db.Text)
    star = db.Column(db.Boolean)
    pin = db.Column(db.Boolean)
    variables = db.Column(db.PickleType)
    cmd = db.Column(db.Text)
    environment_bind = db.relationship('EnvironmentBind', cascade='all')

    def __repr__(self):
        return "<Environment {}".format(self.unique_name)

    def __init__(self, group, star, pin, fullname, unique_name, logo="", variables="", cmd=""):
        self.id = uuid.uuid4().hex
        self.group = group
        self.star = star
        self.pin = pin
        self.fullname = fullname
        self.unique_name = unique_name
        self.logo = logo
        self.variables = variables
        self.cmd = cmd


class EnvironmentCluster(db.Model):
    __tablename__ = 'environment_cluster'
    id = db.Column(db.String(32), primary_key=True)
    group = db.Column(db.String(50))  # python, spark, pyspark
    ip = db.Column(db.String(20))
    port = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    state = db.Column(db.String(20))
    info = db.Column(db.String(30))
    # last_update = db.Column(db.String(30))

    def __init__(self, group, ip, port, username, password, state, info, last_update=None):
        self.id = uuid.uuid4().hex
        self.group = group
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.state = state
        self.info = info
        # self.last_update = last_update


class EnvironmentBind(db.Model):
    __tablename__ = 'environment_bind'
    id = db.Column(db.String(32), primary_key=True)
    category_id = db.Column(db.String(32))  # if equal to 0, means system
    category = db.Column(db.String(20))  # system, template, config, operator level
    environment_id = db.Column(db.String(32), db.ForeignKey('environment.id', deferrable=True, initially="DEFERRED"))

    def __init__(self, category_id, category, environment_id):
        self.id = uuid.uuid4().hex
        self.category_id = category_id
        self.category = category
        self.environment_id = environment_id


class EnvironmentGlobal(db.Model):
    __tablename__ = 'environment_global'
    id = db.Column(db.String(32), primary_key=True)
    value = db.Column(db.PickleType)

    def __init__(self, value):
        self.id = uuid.uuid4().hex
        self.value = value


class SystemConfig(db.Model, Base):
    __tablename__ = 'system_config'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    value = db.Column(db.String(100))
    value_type = db.Column(db.String(30))
    description = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.now)
    last_edited = db.Column(db.DateTime)

    def __init__(self, name, value, value_type, desc):
        self.id = uuid.uuid4().hex
        self.name = name
        self.value = str(value)
        self.value_type = value_type
        self.description = desc
        self.created_at = datetime.now()
        self.last_edited = self.created_at

    def __repr__(self):
        return '<SystemConfig %r>' % self.name

    def transform_to_json(self):
        self_dict = {}
        json_exclude = getattr(self, '__json_exclude__', set())
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key not in json_exclude:
                if isinstance(value,datetime):
                    self_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    self_dict[key] = value
        if self.value_type=='bool':
            self_dict['value']=self.value=='true'
        elif self.value_type=='int':
            self_dict['value']=int(self.value)
        elif self.value_type=='float':
            self_dict['value']=float(self.value)
        return self_dict


class FlokEnum(db.Model, Base):
    __tablename__ = 'flok_enum'
    id = db.Column(db.String(32), primary_key=True)
    enum_name = db.Column(db.String(50))
    enum_value = db.Column(db.String(50))
    value_type = db.Column(db.String(32))

    def __init__(self, name, value, value_type):
        self.id = uuid.uuid4().hex
        self.enum_name = name
        self.enum_value = value
        self.value_type = value_type

    def __repr__(self):
        return '<SystemConfig %r>' % self.name


class AlgorithmType(db.Model, Base):
    __tablename__ = 'algorithm_type'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_edited = db.Column(db.DateTime)
    description = db.Column(db.Text)
    run_environment_type_id = db.Column(db.String(32), db.ForeignKey('run_environment_type.id', deferrable=True, initially="DEFERRED"))
    dev_language_id = db.Column(db.String(32), db.ForeignKey('dev_language.id', deferrable=True, initially="DEFERRED"))
    is_streaming = db.Column(db.Boolean)

    operators = db.relationship('Operator', backref='algorithm_type')
    run_env_submits = db.relationship('RunEnvSubmit', backref='algorithm_type')

    def __init__(self, name, description):
        self.id = uuid.uuid4().hex
        self.name = name
        self.created_at = datetime.now()
        self.last_edited = datetime.now()
        self.description = description

    def __repr__(self):
        return '<AlgorithmType %r>' % self.name


class DevLanguage(db.Model, Base):
    __tablename__ = 'dev_language'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_edited = db.Column(db.DateTime)
    description = db.Column(db.Text)

    algorithm_types = db.relationship('AlgorithmType', backref='dev_language')
    support_run_environment_types = db.relationship('RunEnvironmentType', secondary="algorithm_type",
                                                    backref='support_dev_languages')


    def __init__(self, name, description):
        self.id = uuid.uuid4().hex
        self.name = name
        self.created_at = datetime.now()
        self.last_edited = datetime.now()
        self.description = description

    def __repr__(self):
        return '<DevLanguage %r>' % self.name


class RunEnvironmentType(db.Model, Base):
    __tablename__ = 'run_environment_type'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_edited = db.Column(db.DateTime)
    description = db.Column(db.Text)
    default_data_environment_type_id = db.Column(db.String(32), db.ForeignKey('data_environment_type.id', deferrable=True, initially="DEFERRED"))

    algorithm_types = db.relationship('AlgorithmType', backref='run_environment_type')
    run_envs = db.relationship('RunEnv', backref='run_environment_type')

    def __init__(self, name, description):
        self.id = uuid.uuid4().hex
        self.name = name
        self.created_at = datetime.now()
        self.last_edited = datetime.now()
        self.description = description

    def __repr__(self):
        return '<RunEnvironmentType %r>' % self.name


run_environment_data_type = db.Table('run_environment_data_type',
                                     db.Column('run_environment_type_id', db.String(32),
                                               db.ForeignKey('run_environment_type.id', deferrable=True, initially="DEFERRED"), primary_key=True),
                                     db.Column('data_type_id', db.String(32), db.ForeignKey('data_type.id', deferrable=True, initially="DEFERRED"), primary_key=True))


class DataType(db.Model, Base):
    __tablename__ = 'data_type'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_edited = db.Column(db.DateTime)
    description = db.Column(db.Text)
    default_format_id = db.Column(db.String(32), db.ForeignKey('data_format.id', deferrable=True, initially="DEFERRED"))

    support_run_environment_types = db.relationship('RunEnvironmentType', secondary=run_environment_data_type,
                                                    backref='support_data_types')
    include_formats = db.relationship('DataFormat', backref='type', lazy='dynamic',
                                      primaryjoin='DataFormat.type_id==DataType.id')
    ports = db.relationship('Port', backref='data_type')

    def __init__(self, name, description):
        self.id = uuid.uuid4().hex
        self.name = name
        self.created_at = datetime.now()
        self.last_edited = datetime.now()
        self.description = description

    def __repr__(self):
        return '<DataType %r>' % self.name


class DataFormat(db.Model, Base):
    __tablename__ = 'data_format'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_edited = db.Column(db.DateTime)
    description = db.Column(db.Text)
    type_id = db.Column(db.String(32), db.ForeignKey('data_type.id', deferrable=True, initially="DEFERRED"))

    default_used_types = db.relationship('DataType', backref='default_format', lazy='dynamic',
                                         primaryjoin='DataType.default_format_id==DataFormat.id')

    def __init__(self, name, description):
        self.id = uuid.uuid4().hex
        self.name = name
        self.created_at = datetime.now()
        self.last_edited = datetime.now()
        self.description = description

    def __repr__(self):
        return '<DataFormat %r>' % self.name


run_data_environment_type = db.Table('run_data_environment_type',
                                     db.Column('run_environment_type_id', db.String(32),
                                               db.ForeignKey('run_environment_type.id', deferrable=True, initially="DEFERRED"), primary_key=True),
                                     db.Column('data_environment_type_id', db.String(32),
                                               db.ForeignKey('data_environment_type.id', deferrable=True, initially="DEFERRED"), primary_key=True))


class DataEnvironmentType(db.Model, Base):
    __tablename__ = 'data_environment_type'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_edited = db.Column(db.DateTime)
    description = db.Column(db.Text)
    variables = db.Column(db.Text)
    default_environment_id = db.Column(db.String(32), db.ForeignKey('data_environment.id', deferrable=True, initially="DEFERRED"))

    support_run_environment_types = db.relationship('RunEnvironmentType', secondary=run_data_environment_type,
                                                    backref='support_data_environment_types')
    include_environments = db.relationship('DataEnvironment', backref='type', lazy='dynamic',
                                           primaryjoin='DataEnvironment.type_id==DataEnvironmentType.id')
    default_used_run_environment_type = db.relationship("RunEnvironmentType", backref="default_data_environment_type")

    def __init__(self, name, description):
        self.id = uuid.uuid4().hex
        self.name = name
        self.created_at = datetime.now()
        self.last_edited = datetime.now()
        self.description = description

    def __repr__(self):
        return '<DataEnvironmentType %r>' % self.name


application_config_data_environment = db.Table('application_config_data_environment',
                                               db.Column('application_config_id', db.String(32),
                                                         db.ForeignKey('application_configs.id', deferrable=True, initially="DEFERRED"), primary_key=True),
                                               db.Column('data_environment_id', db.String(32),
                                                         db.ForeignKey('data_environment.id', deferrable=True, initially="DEFERRED"), primary_key=True))


class DataEnvironment(db.Model, Base):
    __tablename__ = 'data_environment'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_edited = db.Column(db.DateTime)
    description = db.Column(db.Text)
    type_id = db.Column(db.String(32), db.ForeignKey('data_environment_type.id', deferrable=True, initially="DEFERRED"))
    prefix = db.Column(db.String(255))
    connection = db.Column(db.String(255))
    variables = db.Column(db.Text)

    using_application_configs = db.relationship('ApplicationConfigs', secondary=application_config_data_environment,
                                                backref='using_data_environments')
    default_used_types = db.relationship('DataEnvironmentType', backref='default_environment', lazy='dynamic',
                                         primaryjoin='DataEnvironmentType.default_environment_id==DataEnvironment.id')

    def __init__(self, name, description):
        self.id = uuid.uuid4().hex
        self.name = name
        self.created_at = datetime.now()
        self.last_edited = datetime.now()
        self.description = description

    def __repr__(self):
        return '<DataEnvironment %r>' % self.name


class RunEnv(db.Model, Base):
    __tablename__ = 'run_env'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.Text)
    master_ip = db.Column(db.String(20))
    username = db.Column(db.String(20))
    port = db.Column(db.String(20))
    password = db.Column(db.String(20))
    version = db.Column(db.String(20))
    monitor = db.Column(db.String(40))
    default_env_variables = db.Column(db.Text)
    path_on_master = db.Column(db.String(255))

    run_env_type_id = db.Column(db.String(32), db.ForeignKey('run_environment_type.id', deferrable=True, initially="DEFERRED"))
    run_env_binds = db.relationship('RunEnvBind', backref='run_env')
    run_env_submits = db.relationship('RunEnvSubmit', backref='run_env')

    def __init__(self, name, description, master_ip, username, port, password, monitor, version, default_env_variables, path_on_master):
        self.id = uuid.uuid4().hex
        self.name = name
        self.description = description
        self.master_ip = master_ip
        self.username = username
        self.port = port
        self.password = password
        self.monitor = monitor
        self.version = version
        self.default_env_variables = default_env_variables
        self.path_on_master = path_on_master


class RunEnvBind(db.Model, Base):
    __tablename__ = 'run_env_bind'
    id = db.Column(db.String(32), primary_key=True)
    category_id = db.Column(db.String(32))
    category = db.Column(db.String(20))  # system, template, config, operator
    env_variables = db.Column(db.Text)

    run_env_id = db.Column(db.String(32), db.ForeignKey('run_env.id', deferrable=True, initially="DEFERRED"))  # we can infer run_env_type from run_env

    def __init__(self, category_id, category, env_variables):
        self.id = uuid.uuid4().hex
        self.category_id = category_id
        self.category = category
        self.env_variables = env_variables


class RunEnvSubmit(db.Model, Base):
    __tablename__ = 'run_env_submit'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(20))
    command = db.Column(db.Text)

    run_env_id = db.Column(db.String(32), db.ForeignKey('run_env.id', deferrable=True, initially="DEFERRED"))
    algorithm_type_id = db.Column(db.String(32), db.ForeignKey('algorithm_type.id', deferrable=True, initially="DEFERRED"))

    def __init__(self, name, command):
        self.id = uuid.uuid4().hex
        self.name = name
        self.command = command


class RunEnvParameter(db.Model, Base):
    __tablename__ = 'run_env_parameter'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(20))
    nickname = db.Column(db.String(20))
    default_value = db.Column(db.Text)
    version = db.Column(db.String(20))

    run_env_type_id = db.Column(db.String(32), db.ForeignKey('run_environment_type.id', deferrable=True, initially="DEFERRED"))

    def __init__(self, name, nickname, default_value, version, env_type_id=None):
        self.id = uuid.uuid4().hex
        self.name = name
        self.nickname = nickname
        self.default_value = default_value
        self.version = version
        self.run_env_type_id = env_type_id


class AutovisChart(db.Model,Base):
    __tablename__ = 'autovis_chart'
    id=db.Column(db.String(32),primary_key=True)
    name =db.Column(db.String(40))
    chart_id=db.Column(db.String(10))
    dashboard_id=db.Column(db.String(10))
    dashboard_url=db.Column(db.String(256))
    def __init__(self,name,chart_id,dashboard_id,dashboard_url):
        self.id=uuid.uuid4().hex
        self.name=name
        self.chart_id=chart_id
        self.dashboard_id=dashboard_id
        self.dashboard_url=dashboard_url
    def __repr__(self):
        return 'AutovisChart: %s '% self.name

class Categories(db.Model, Base):
    __tablename__ = 'categories'
    id = db.Column(db.String(32), primary_key=True)
    module_name = db.Column(db.String(50))
    category = db.Column(db.Text)
    label = db.Column(db.String(32))

    def __init__(self, module_name, category,label):
        self.id = uuid.uuid4().hex
        self.module_name = module_name
        self.category = category
        self.label = label

    def __repr__(self):
        return '<Categories %r>' % self.module_name

class NoteDataset(db.Model,Base):
    __tablename__ = 'note_dataset'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    note_dataset_type_id = db.Column(db.String(32), db.ForeignKey('note_dataset_type.id'))
    note_type_id = db.Column(db.String(32), db.ForeignKey('note_type.id'))
    description=db.Column(db.String(200))
    path=db.Column(db.String(200))
    # state为0表示同步中，为1表示可正常使用，为-1表示同步出错，
    # 为2表示上传anylearn中，为-2表示上传失败
    state = db.Column(db.Integer,default=0)

    note_data_instances=db.relationship("NoteDataInstance",backref="note_dataset",cascade="all, delete")
    label_instances = db.relationship("LabelInstance",backref="note_dataset",cascade="all, delete")

    def __repr__(self):
        return '<NoteDataset %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")

class NoteDatasetType(db.Model,Base):
    __tablename__ = 'note_dataset_type'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    note_types = db.relationship("NoteType",backref="note_dataset_type")

    note_datasets = db.relationship("NoteDataset",backref="note_dataset_type")

    def __repr__(self):
        return '<NoteDatasetType %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")

class NoteType(db.Model,Base):
    __tablename__ = 'note_type'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    note_dataset_type_id = db.Column(db.String(32),db.ForeignKey('note_dataset_type.id'))

    note_datasets = db.relationship("NoteDataset",backref="note_type")

    def __repr__(self):
        return '<NoteType %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")

class NoteDataInstance(db.Model,Base):
    __tablename__ = 'note_data_instance'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    is_note = db.Column(db.Boolean,default=False)
    src = db.Column(db.String(255))
    is_delete = db.Column(db.Boolean,default=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    note_dataset_id = db.Column(db.String(32), db.ForeignKey('note_dataset.id'))

    relation_data_labels = db.relationship("RelationDataLabel",backref="note_data_instance",cascade="all, delete")

    def __repr__(self):
        return '<NoteDataInstance %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")

class LabelInstance(db.Model,Base):
    __tablename__ = 'label_instance'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50))
    color = db.Column(db.String(255))
    note_dataset_id = db.Column(db.String(32), db.ForeignKey('note_dataset.id'))

    relation_data_labels = db.relationship("RelationDataLabel",backref="label_instance",cascade="all, delete")

    def __repr__(self):
        return '<LabelInstance %r>' % self.name

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")

class RelationDataLabel(db.Model,Base):
    __tablename__ = 'relation_data_label'
    id = db.Column(db.String(32), primary_key=True)
    label_id = db.Column(db.String(32), db.ForeignKey('label_instance.id'))
    note_data_id = db.Column(db.String(32), db.ForeignKey('note_data_instance.id'))
    content = db.Column(db.String(512))

    def __repr__(self):
        return '<RelationDataLabel %r>' % self.content

    def __init__(self):
        self.id = str(uuid.uuid4()).replace("-", "")