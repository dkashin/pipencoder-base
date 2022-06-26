
import uuid

from sqlalchemy import Column, Integer, Float, Text, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from flask_login import UserMixin
from datetime import datetime, timedelta
from .extensions import bcrypt
from .database import Base, engine


class SharedMixin(object):
    """A mixin that adds a surrogate UUID4 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = { 'extend_existing': True }

    id = Column(String, primary_key = True, unique = True, default = lambda: str(uuid.uuid4().hex))

    @classmethod
    def get_by_id(cls, id):
      """ Get record by ID """
      try:
        return cls.query.filter_by(id = id).first()
      except:
        return None


class APIKey(Base):


  def __init__(self, username = None, key = None, expire = None):
    self.username = username
    self.key = key
    self.expire = expire or (datetime.now() + timedelta(hours = 1))


  __tablename__ = 'APIKey'
  id = Column(Integer, primary_key = True, unique = True, autoincrement = True)
  username = Column(String, ForeignKey('User.username'))
  key = Column(String, nullable = False)
  expire = Column(DateTime)


class User(Base, SharedMixin, UserMixin):


  def __init__(self, alias = None, username = 'default', password = 'secret', admin = False):
    self.alias = alias
    self.username = username
    self.password = bcrypt.generate_password_hash(password)
    self.admin = admin

  __tablename__ = 'User'
#  id = Column(String, primary_key = True, default = lambda: str(uuid.uuid4().hex), unique = True)
  alias = Column(String)
  username = Column(String, unique = True, nullable = False)
  password = Column(String, nullable = False)
  admin = Column(Boolean, default = False)
  su = Column(Boolean, default = False)
  api_keys = relationship('APIKey', backref = 'User', lazy = 'dynamic', cascade = 'all, delete, delete-orphan')
  api_keys_limit = Column(Integer, default = 5)
  registered = Column(DateTime, default = datetime.now())
  last_login = Column(DateTime, default = datetime.now())

  @property
  def serialize(self):
    return {
      'id': self.id,
      'alias': self.alias,
      'username': self.username,
      'admin': self.admin,
      'registered': self.registered.isoformat() if self.registered else datetime.now(),
      'last_login': self.last_login.isoformat() if self.last_login else datetime.now()
    }


class Job(Base, SharedMixin):

    __tablename__ = 'Job'
#    id = Column(String, primary_key = True, default = lambda: str(uuid.uuid4().hex), unique = True)
    sid = Column(Integer, autoincrement = True)
    job_name = Column(String)
    abort_on_errors = Column(Integer)
    abort_on_empty_output = Column(Integer, default = 1)
    ignore_unknown = Column(Integer, default = 1)
    max_error_rate = Column(Float, default = 0.75)
    check_source = Column(Boolean, default = True)
    check_target = Column(Boolean, default = True)
    check_timeout = Column(Integer, default = 30)
    thumb_render = Column(String(16), default = 'libavcodec')
    thumb_interval = Column(Integer, default = 50)
# TODO: JSON for source types
    source_main = Column(String)
    source_main_ext = Column(JSON)
    source_main_type = Column(String(16))
    source_main_decoder = Column(String(32))
    source_main_decoder_err_detect = Column(String(32))
    source_main_decoder_deinterlace = Column(String(16))
    source_main_decoder_scale = Column(String(16))
    source_main_loop = Column(Integer)
    source_main_udp_overrun = Column(Integer, default = 1)
    source_main_udp_buffer = Column(Integer)
    source_main_udp_timeout = Column(Integer)
    source_main_srt_mode = Column(String(32))
    source_main_srt_passphrase = Column(String(80))
    source_main_http_reconnect = Column(Integer, default = 1)
    source_main_merge_pmt_versions = Column(Integer, default = 1)
    source_bak = Column(String)
    source_bak_ext = Column(JSON)
    source_bak_type = Column(String(16))
    source_bak_decoder = Column(String(32))
    source_bak_decoder_err_detect = Column(String(32))
    source_bak_decoder_deinterlace = Column(String(16))
    source_bak_decoder_scale = Column(String(16))
    source_bak_loop = Column(Integer)
    source_bak_udp_overrun = Column(Integer, default = 1)
    source_bak_udp_buffer = Column(Integer)
    source_bak_udp_timeout = Column(Integer)
    source_bak_srt_mode = Column(String(32))
    source_bak_srt_passphrase = Column(String(80))
    source_bak_http_reconnect = Column(Integer, default = 1)
    source_bak_merge_pmt_versions = Column(Integer, default = 1)
    source_fail = Column(String)
    source_fail_ext = Column(JSON)
    source_fail_type = Column(String(16))
    source_fail_decoder = Column(String(32))
    source_fail_decoder_err_detect = Column(String(32))
    source_fail_decoder_deinterlace = Column(String(16))
    source_fail_decoder_scale = Column(String(16))
    source_fail_loop = Column(Integer)
    source_fail_udp_overrun = Column(Integer, default = 1)
    source_fail_udp_buffer = Column(Integer)
    source_fail_udp_timeout = Column(Integer)
    source_fail_srt_mode = Column(String(32))
    source_fail_srt_passphrase = Column(String(80))
    source_fail_http_reconnect = Column(Integer, default = 1)
    source_fail_merge_pmt_versions = Column(Integer, default = 1)
    source_active = Column(String(16), default = 'main')
    source_main_bak_rr = Column(Integer, default = 1)
    hls_abr_active = Column(Integer, default = 0)
    hls_abr_server = Column(String)
    hls_abr_list_name = Column(String)
    hls_abr_basename = Column(String)
    hls_abr_url = Column(String)
    hls_drm_active = Column(Integer, default = 0)
    hls_drm_type = Column(String)
    hls_drm_key_type = Column(String(16))
    hls_drm_key_user = Column(String)
    hls_drm_key_password = Column(String)
    hls_drm_key = Column(String)
    hls_drm_key_url = Column(String)
    hls_drm_key_iv = Column(String)
    profile = relationship('Profile', backref = 'Job', lazy = 'dynamic', cascade = 'all, delete, delete-orphan')
    label = Column(String)
    run_status = Column(String(32), default = 'OFF')
    retries = Column(Integer, default = 0)
    start_time = Column(DateTime)
    uptime = Column(String(128))
    sys_stats = Column(JSON)

    @property
    def serialize(self):
      json = {
        'job_data': {
          'id': self.id,
          'sid': self.sid,
          'job_name' : self.job_name,
          'abort_on_errors': bool(self.abort_on_errors),
          'abort_on_empty_output': bool(self.abort_on_empty_output),
          'ignore_unknown': bool(self.ignore_unknown),
          'max_error_rate': self.max_error_rate,
          'check_timeout': self.check_timeout,
          'check_source': self.check_source,
          'check_target': self.check_target,
          'thumb_render': self.thumb_render,
          'thumb_interval': self.thumb_interval,
          'source_main': self.source_main,
          'source_main_ext': self.source_main_ext,
          'source_main_type': self.source_main_type,
          'source_main_decoder': self.source_main_decoder,
          'source_main_decoder_err_detect': self.source_main_decoder_err_detect,
          'source_main_decoder_deinterlace': self.source_main_decoder_deinterlace,
          'source_main_decoder_scale': self.source_main_decoder_scale,
          'source_main_loop': bool(self.source_main_loop),
          'source_main_udp_overrun': bool(self.source_main_udp_overrun),
          'source_main_udp_buffer': self.source_main_udp_buffer,
          'source_main_udp_timeout': self.source_main_udp_timeout,
          'source_main_srt_mode': self.source_main_srt_mode,
          'source_main_srt_passphrase': self.source_main_srt_passphrase,
          'source_main_http_reconnect': bool(self.source_main_http_reconnect),
          'source_main_merge_pmt_versions': bool(self.source_main_merge_pmt_versions),
          'source_bak': self.source_bak,
          'source_bak_ext': self.source_bak_ext,
          'source_bak_type': self.source_bak_type,
          'source_bak_decoder': self.source_bak_decoder,
          'source_bak_decoder_err_detect': self.source_bak_decoder_err_detect,
          'source_bak_decoder_deinterlace': self.source_bak_decoder_deinterlace,
          'source_bak_decoder_scale': self.source_bak_decoder_scale,
          'source_bak_loop': bool(self.source_bak_loop),
          'source_bak_udp_overrun': bool(self.source_bak_udp_overrun),
          'source_bak_udp_buffer': self.source_bak_udp_buffer,
          'source_bak_udp_timeout': self.source_bak_udp_timeout,
          'source_bak_srt_mode': self.source_bak_srt_mode,
          'source_bak_srt_passphrase': self.source_bak_srt_passphrase,
          'source_bak_http_reconnect': bool(self.source_bak_http_reconnect),
          'source_bak_merge_pmt_versions': bool(self.source_bak_merge_pmt_versions),
          'source_fail': self.source_fail,
          'source_fail_ext': self.source_fail_ext,
          'source_fail_type': self.source_fail_type,
          'source_fail_decoder': self.source_fail_decoder,
          'source_fail_decoder_err_detect': self.source_fail_decoder_err_detect,
          'source_fail_decoder_deinterlace': self.source_fail_decoder_deinterlace,
          'source_fail_decoder_scale': self.source_fail_decoder_scale,
          'source_fail_loop': bool(self.source_fail_loop),
          'source_fail_udp_overrun': bool(self.source_fail_udp_overrun),
          'source_fail_udp_buffer': self.source_fail_udp_buffer,
          'source_fail_udp_timeout': self.source_fail_udp_timeout,
          'source_fail_srt_mode': self.source_fail_srt_mode,
          'source_fail_srt_passphrase': self.source_fail_srt_passphrase,
          'source_fail_http_reconnect': bool(self.source_fail_http_reconnect),
          'source_fail_merge_pmt_versions': bool(self.source_fail_merge_pmt_versions),
          'source_active': self.source_active,
          'source_main_bak_rr': bool(self.source_main_bak_rr),
          'hls_abr_server': self.hls_abr_server,
          'hls_abr_active': bool(self.hls_abr_active),
          'hls_abr_list_name': self.hls_abr_list_name,
          'hls_abr_basename': self.hls_abr_basename,
          'hls_drm_active': bool(self.hls_drm_active),
          'hls_drm_type': self.hls_drm_type,
          'hls_drm_key_type': self.hls_drm_key_type,
          'hls_drm_key': self.hls_drm_key,
          'hls_drm_key_user': self.hls_drm_key_user,
          'hls_drm_key_password': self.hls_drm_key_password,
          'hls_drm_key_url': self.hls_drm_key_url,
          'hls_drm_key_iv': self.hls_drm_key_iv,
          'run_status': self.run_status,
          'retries': self.retries
        },
        'profile': [ i.serialize for i in self.profile.all() ]
      }
      return json


class Profile(Base):

    __tablename__ = 'Profile'
    id = Column(Integer, primary_key = True, autoincrement = True)
    parent_id = Column(Integer, ForeignKey('Job.id'))
# PIDs
    main_vpid = Column(String(8))
    main_apid = Column(String(8))
    main_dpid = Column(String(8))
    bak_vpid = Column(String(8))
    bak_apid = Column(String(8))
    bak_dpid = Column(String(8))
    fail_vpid = Column(String(8))
    fail_apid = Column(String(8))
    fail_dpid = Column(String(8))
# Presets
    vpreset = Column(String)
    apreset = Column(String)
    dpreset = Column(String)
    nvenc_gpu = Column(String(8))
# Filters
    venc_di = Column(String(32))
    venc_psize = Column(String(32))
# Metadata
    stream_metadata = Column(JSON)
    stream_pids = Column(JSON)
# Format wrapper
    target = relationship('Target', backref = 'Profile', lazy = 'dynamic', cascade = 'all, delete, delete-orphan')

    @property
    def serialize(self):
      return {
        'id': self.id,
        'main_vpid': self.main_vpid,
        'main_apid': self.main_apid,
        'main_dpid': self.main_dpid,
        'bak_vpid': self.bak_vpid,
        'bak_apid': self.bak_apid,
        'bak_dpid': self.bak_dpid,
        'fail_vpid': self.fail_vpid,
        'fail_apid': self.fail_apid,
        'fail_dpid': self.fail_dpid,
        'vpreset': self.vpreset,
        'apreset': self.apreset,
        'dpreset': self.dpreset,
        'nvenc_gpu': self.nvenc_gpu,
        'venc_di': self.venc_di,
        'venc_psize': self.venc_psize,
        'stream_metadata': self.stream_metadata,
        'stream_pids': self.stream_pids,
        'target': [ i.serialize for i in self.target.all() ]
      }


class Target(Base):

    __tablename__ = 'Target'
    id = Column(Integer, primary_key = True, autoincrement = True)
    parent_id = Column(Integer, ForeignKey('Profile.id'))
# TODO: make stream_srv connetion to Server table
    target_type = Column(String)
    device_name = Column(String)
    stream_srv = Column(String)
    stream_type = Column(String(64), default = 'HLS')
    stream_name = Column(String)
    stream_app = Column(String)
    hls_abr_asset = Column(Integer, default = 0)
    hls_abr_bandwidth = Column(Integer, default = 512)
    hls_abr_resolution = Column(String(32))
    hls_abr_codecs = Column(String)
    hls_drm_asset = Column(Integer, default = 0)
    hls_list_size = Column(Integer, default = 8)
    hls_list_name = Column(String)
    hls_seg_time = Column(Integer, default = 8)
    hls_seg_format = Column(String(16), default = 'Timestamp')
    hls_seg_name = Column(String, default = '%Y%m%d%H%M%S')
    hls_seg_abs_path = Column(Integer, default = 0)
    udp_ip = Column(String(32))
    udp_port = Column(Integer, default = 1234)
    udp_pkt_size = Column(Integer, default = 1316)
    mpegts_muxrate = Column(Integer)
    mpegts_pcr_period = Column(Integer, default = 20)
    mpegts_pat_period = Column(Float, default = 0.1)
    mpegts_sdt_period = Column(Float, default = 0.5)
    mpegts_flags = Column(JSON)
    srt_mode = Column(String(32))
    srt_ip = Column(String(32))
    srt_port = Column(Integer, default = 1234)
    srt_pkt_size = Column(Integer, default = 1316)
    srt_maxbw = Column(Integer, default = 0)
    srt_pbkeylen = Column(Integer, default = 0)
    srt_passphrase = Column(String(80))
    preview = Column(String)

    @property
    def serialize(self):
      return {
      # TODO: return only fileds according to stream type
        'id': self.id,
        'target_type': self.target_type,
        'device_name': self.device_name,
        'stream_srv': self.stream_srv,
        'stream_type': self.stream_type,
        'stream_name': self.stream_name,
        'stream_app': self.stream_app,
        'hls_abr_asset': bool(self.hls_abr_asset),
        'hls_abr_bandwidth': self.hls_abr_bandwidth,
        'hls_abr_resolution': self.hls_abr_resolution,
        'hls_abr_codecs': self.hls_abr_codecs,
        'hls_drm_asset': bool(self.hls_drm_asset),
        'hls_list_size': self.hls_list_size,
        'hls_list_name': self.hls_list_name,
        'hls_seg_time': self.hls_seg_time,
        'hls_seg_format': self.hls_seg_format,
        'hls_seg_name': self.hls_seg_name,
        'hls_seg_abs_path': bool(self.hls_seg_abs_path),
        'udp_ip': self.udp_ip,
        'udp_port': self.udp_port,
        'udp_pkt_size': self.udp_pkt_size,
        'mpegts_muxrate': self.mpegts_muxrate,
        'mpegts_pcr_period': self.mpegts_pcr_period,
        'mpegts_pat_period': self.mpegts_pat_period,
        'mpegts_sdt_period': self.mpegts_sdt_period,
        'mpegts_flags': self.mpegts_flags,
        'srt_mode': self.srt_mode,
        'srt_ip': self.srt_ip,
        'srt_port': self.srt_port,
        'srt_pkt_size': self.srt_pkt_size,
        'srt_maxbw': self.srt_maxbw,
        'srt_pbkeylen': self.srt_pbkeylen,
        'srt_passphrase': self.srt_passphrase
      }


class Server(Base, SharedMixin):

    __tablename__ = 'Server'
#    id = Column(String, primary_key = True, default = lambda: str(uuid.uuid4().hex), unique = True)
    name = Column(String, nullable = False)
    ip = Column(String(32), nullable = False)
    rtmp_srv = Column(String())
    hls_srv = Column(String())
#    smooth_srv = Column(String())

    def features(self):
      features_list = []
      if self.rtmp_srv:
        features_list.append({ 'name': 'RTMP', 'url': self.rtmp_srv })
      if self.hls_srv:
        features_list.append({ 'name': 'HLS', 'url': self.hls_srv })
#      if self.smooth_srv:
#        features_list.append({ 'name': 'Smooth', 'url': self.smooth_srv })
      if self.ip == 'localhost':
        features_list.append({ 'name': 'UDP', 'url': 'udp://' })
        features_list.append({ 'name': 'SRT', 'url': 'srt://' })
      return features_list

    @property
    def serialize(self):
      json = {
        'id': self.id,
        'name': self.name,
        'ip': self.ip,
        'features': self.features()
      }
      return json

class Settings(Base, SharedMixin):

    __tablename__ = 'Settings'
#    id = Column(String, primary_key = True, default = lambda: str(uuid.uuid4().hex), unique = True)
    update_path = Column(String)
#    account_email = Column(String)
    node_api_key = Column(String)
    node_id = Column(String)
    callback_url = Column(String)
    version = Column(String(16), nullable = False)
    default_fail_src = Column(String, nullable = False)
    default_fail_type = Column(String(16), nullable = False)
    default_fail_decoder = Column(String(32))
    default_fail_decoder_err_detect = Column(String(32))
    default_fail_vpid = Column(String(8))
    default_fail_apid = Column(String(8))
    default_fail_dpid = Column(String(8))
    default_fail_loop = Column(Integer, default = 1)
    default_fail_udp_overrun = Column(Integer, default = 1)
    default_fail_udp_buffer = Column(Integer)
    default_fail_udp_timeout = Column(Integer)
    default_srt_mode = Column(String(32))
    default_srt_passphrase = Column(String(80))
    default_fail_http_reconnect = Column(Integer, default = 1)
    default_fail_merge_pmt_versions = Column(Integer, default = 1)
    smtp_host = Column(String)
    smtp_port = Column(Integer)
    smtp_user = Column(String)
    smtp_pass = Column(String)
    smtp_ssl = Column(Integer)
    smtp_tls = Column(Integer)
    alarm_master = Column(Integer)
    alarm_master_email = Column(Text)
    alarm_master_subject = Column(Text)
    alarm_error = Column(Integer)
    alarm_error_email = Column(Text)
    alarm_error_subject = Column(Text)
    alarm_error_period = Column(Integer)
    alarm_error_value = Column(Integer)
    alarm_action = Column(Integer)
    alarm_action_email = Column(Text)
    alarm_action_subject = Column(Text)
    alarm_action_count = Column(Integer)

    @property
    def serialize(self):
      return {
        'id': self.id,
        'update_path': self.update_path,
#        'node_id': self.node_id,
        'callback_url': self.callback_url,
        'default_fail_src': self.default_fail_src,
        'default_fail_type': self.default_fail_type,
        'default_fail_decoder': self.default_fail_decoder,
        'default_fail_decoder_err_detect': self.default_fail_decoder_err_detect,
        'default_fail_vpid': self.default_fail_vpid,
        'default_fail_apid': self.default_fail_apid,
        'default_fail_dpid': self.default_fail_dpid,
        'default_fail_loop': bool(self.default_fail_loop),
        'default_fail_udp_overrun': bool(self.default_fail_udp_overrun),
        'default_fail_udp_buffer': self.default_fail_udp_buffer,
        'default_fail_udp_timeout': self.default_fail_udp_timeout,
        'default_srt_mode': self.default_srt_mode,
        'default_srt_passphrase': self.default_srt_passphrase,
        'default_fail_http_reconnect': bool(self.default_fail_http_reconnect),
        'default_fail_merge_pmt_versions': bool(self.default_fail_merge_pmt_versions),
        'smtp_host': self.smtp_host,
        'smtp_port': self.smtp_port,
        'smtp_user': self.smtp_user,
        'smtp_pass': self.smtp_pass,
        'smtp_ssl': bool(self.smtp_ssl),
        'smtp_tls': bool(self.smtp_tls),
        'alarm_master': bool(self.alarm_master),
        'alarm_master_email': self.alarm_master_email,
        'alarm_master_subject': self.alarm_master_subject,
        'alarm_error': bool(self.alarm_error),
        'alarm_error_email': self.alarm_error_email,
        'alarm_error_subject': self.alarm_error_subject,
        'alarm_error_period': self.alarm_error_period,
        'alarm_error_value': self.alarm_error_value,
        'alarm_action': bool(self.alarm_action),
        'alarm_action_email': self.alarm_action_email,
        'alarm_action_subject': self.alarm_action_subject,
        'alarm_action_count': self.alarm_action_count
      }

