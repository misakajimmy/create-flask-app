# coding: utf-8
"""
基础数据表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from hmac import compare_digest

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from .. import db
from ..tool import get_age


class AdminUser(db.Document):
    """管理员用户表"""
    __tablename__ = "t_admin_user"

    account = db.StringField(required=True, unique=True, null=False, default="", comment="登录账号")
    _password = db.StringField(null=False, default="", comment="登录密码")
    phone = db.StringField(null=False, default="", comment="手机号")
    nickname = db.StringField(null=False, default="", comment="昵称")
    avatar_url = db.StringField(null=False, default="", comment="头像URL")
    sex = db.IntField(null=False, default="0", comment="性别，0未知，1男性，2女性")
    birthday = db.DateTimeField(comment="生日")
    app_channel = db.StringField(null=False, default="", comment="APP渠道")
    app_version = db.StringField(null=False, default="", comment="APP版本")
    os_type = db.StringField(null=False, default="", comment="系统类型")
    os_version = db.StringField(null=False, default="", comment="系统版本")
    remark = db.StringField(null=False, default="", comment="备注")
    status = db.IntField(null=False, default="1", comment="状态，0无效，1有效")
    create_time = db.DateTimeField(null=False, default=datetime.now(), comment="创建时间")
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment="更新时间"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_pwd):
        self._password = generate_password_hash(raw_pwd)

    def check_password(self, password, is_hash=False):
        if is_hash:
            return compare_digest(self.password, password)
        return check_password_hash(self.password, password)

    @property
    def age(self):
        return get_age(self.birthday)


class VerifySMS(db.Document):
    """短信验证码表"""
    __tablename__ = "t_verify_sms"

    app_name = db.StringField(null=False, default="", comment="应用名称")
    business = db.StringField(null=False, default="", comment="业务名称")
    business_id = db.StringField(null=False, default="", comment="业务流水ID")
    account = db.StringField(null=False, default="", comment="账号")
    phone = db.StringField(null=False, default="", comment="手机号")
    code = db.StringField(null=False, default="", comment="短信验证码")
    status = db.IntField(null=False, default="0", comment="状态，0未使用，1已使用")
    create_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment="创建时间"
    )
    update_time = db.DateTimeField(
        null=False,
        default=datetime.now(),
        comment="更新时间"
    )
