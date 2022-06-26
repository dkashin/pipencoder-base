
import os, json, requests, psutil, shutil, signal, binascii, shlex, threading
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError

from main.tools import _FileTools, _SystemTools
from main.common.config import app_config
from main.common.log import LogManager
from main.common.models import Server, Settings


# FFMPEG CLI constructor class
class MediaPipe(LogManager):


  def __init__(self, query = None, job_id = None, logger = None):
    self.logger = logger or self.LogNull()
    if query or job_id:
      self.Init(query = query, job_id = job_id, logger = logger)


  ### MediaPipe class init
  def Init(self, query = None, job_id = None, logger = None):
    try:
      self.logger = logger or self.LogNull()
      self.logger.debug('[MediaPipe] Init started')
      self.query = query
      self.job_id = str(self.query.id)
      self.job_sid = str(self.query.sid)
      self.gpu_stats = _SystemTools.GPUStats()
      self.gpu_stats = self.gpu_stats if 'dev_data' in list(self.gpu_stats.keys()) else None
      self.profiles_all = query.profile.all()
      self.targets_all = [ target for profile in self.profiles_all for target in profile.target.all() ]
      self.profile_targets_all = {
        profile.id: [ target for target in profile.target.all() ] for profile in self.profiles_all
      }
      #self.logger.debug('[MediaPipe] profile_targets_all ' + str(self.profile_targets_all))
      self.target_first = query.profile.first().target.first()
      self.target_first_type = self.target_first.target_type
      self.target_first_stype = self.target_first.stream_type
      self.target_first_url, self.target_first_server = self.TargetURL(target = self.target_first)
      self.failover_use = bool(self.query.source_fail)
      self.source_all = self.SourceGetAll()
      self.source_ext = {}
      self.source_youtube = False
      self.source, self.source_opt = self.Source()
      self.merge_pmt_versions = ''
      self.logger.debug('[MediaPipe] Init complete')
    except:
      self.logger.error('[MediaPipe] Init exception error')
      raise

    # TODO:
    # if query or job_id:
    #  self.init_complete = True
    #
    # if self.init_complete:
    #   < execute childs allowed >


  # Get root HLS dir
  def HLSDir(self, server = None, absolute = True):
    if server:
      hls_abr_basename = ''
      if self.query.hls_abr_basename and self.query.hls_abr_active:
        hls_abr_basename = self.query.hls_abr_basename
      if server.ip == 'localhost':
        hls_root_dir = os.path.join(app_config.HLS_DIR, hls_abr_basename)
      else:
        if absolute:
          hls_root_dir = os.path.join(server.hls_srv, hls_abr_basename)
        else:
          hls_root_dir = hls_abr_basename
    else:
      hls_root_dir = ''
    return hls_root_dir


  # Get HLS ABR master manifest (playlist)
  def ABRManifestPath(self, server = None, absolute = True):
    if server:
      abr_manifest_path = os.path.join(self.HLSDir(server = server, absolute = absolute), str(self.query.hls_abr_list_name) + app_config.HLS_MANIFEST_EXT)
    else:
      abr_manifest_path = ''
    return abr_manifest_path


  # Create HLS ABR master manifest (playlist)
  def ABRStreamMeta(self, target = None):
    data_rate = ', BANDWIDTH=' + str(target.hls_abr_bandwidth)
    resolution = ''
    if target.hls_abr_resolution:
      resolution = ', RESOLUTION=' + target.hls_abr_resolution
    codecs = ''
    if target.hls_abr_codecs:
      codecs = ', CODECS="' + target.hls_abr_codecs + '"'
    abr_stream_meta = '#EXT-X-STREAM-INF:PROGRAM-ID=1' + data_rate + resolution + codecs + '\n' + target.stream_name + '/' + target.hls_list_name + app_config.HLS_MANIFEST_EXT + '\n'
    return abr_stream_meta


  # HLS ABR Target options
  def ABRManifestCreate(self, srv_id = None, content = ''):
    try:
      server = Server.query.filter_by(id = srv_id).first()
      if server:
        content = '#EXTM3U\n' + content
        abr_manifest = self.ABRManifestPath(server = server)
        if server.ip == 'localhost':
          if not os.path.isfile(abr_manifest):
            with open(abr_manifest, 'w+') as am:
              am.write(content)
          self.logger.info('[MediaPipe] HLS ABR manifest created (' + abr_manifest + ')')
        else:
          r = requests.get(abr_manifest, timeout = 3)
          if r.status_code >= 200 and r.status_code < 400:
            self.logger.info('[MediaPipe] HLS ABR manifest exists (HTTP ' + str(r.status_code) + ', ' + abr_manifest + ')')
          else:
            r = requests.put(abr_manifest, data = content, timeout = 3)
            if r.status_code >= 200 and r.status_code < 400:
              self.logger.info('[MediaPipe] HLS ABR manifest created (' + abr_manifest + ')')
            else:
              self.logger.info('[MediaPipe] HLS ABR manifest failed (HTTP ' + str(r.status_code) + ', ' + abr_manifest + ')')
      else:
        self.logger.info('[MediaPipe] HLS ABR manifest failed (no server)')
    except:
      self.logger.info('[MediaPipe] HLS ABR manifest exception error')
      raise


  # Loop console system absolute path
  def SourceLoopFile(self):
    return (os.path.join(app_config.LOOP_DIR, self.job_id + '.txt'))


  # Thumbnail system absolute path
  def ThumbPath(self):
    thumb_path = os.path.join(app_config.SS_DIR_SYS, self.job_id + '.jpg')
    self.logger.info('[MediaPipe] ThumbPath: ' + thumb_path)
    return thumb_path


  # Thumbnail relative web path
  def ThumbPathWeb(self):
    thumb_path = os.path.join(app_config.SS_DIR_WEB, self.job_id + '.jpg')
    self.logger.info('[MediaPipe] ThumbPath: Web folder ' + thumb_path)
    return thumb_path


  # Image source options
  def SourceImage(self, options = {}):
    source = os.path.join(app_config.IMAGES_DIR, options['source'])
    source_opt = ' -loop 1 -r 30 -i ' + source
    return source, source_opt


  # Clip source options
  def SourceClip(self, options = {}, log = True):
    loop = options['loop']
    source = os.path.join(app_config.CLIPS_DIR, options['source'])
    if log:
      self.logger.info('[MediaPipe] Loop source: ' + str(bool(loop)))
    if loop:
      loop = ' -stream_loop -1'
    else:
      loop = ''
    source_opt = ' -re' + str(loop) + ' -i ' + str(source)
    return source, source_opt


  # Device source options
  def SourceDevice(self, options = {}, log = True):
    demuxer_opt = ''
    source = options['source']
    self.source_ext = options['source_ext']['value']
    self.logger.info('[MediaPipe] source_ext: ' + str(self.source_ext))
    try:
      dev_opt = self.source_ext.get(source)
      for key in list(dev_opt.keys()):
        if key != 'brand':
          if key == 'format_code':
            self.logger.info('[MediaPipe] format_code: ' + str(dev_opt[key]))
            options = dev_opt[key].split('\t')[1]
          else:
            options = dev_opt[key]
          demuxer_opt += ' -' + key + ' ' + str(options)
      demuxer_opt += ' -f ' + dev_opt['brand']
    except:
      self.logger.warning('[MediaPipe] Device options exception warning')
      raise
    source_opt = ''.join([ demuxer_opt, ' -i \"', source, '\"' ])
    self.logger.info('[MediaPipe] Device source_opt: ' + str(source_opt))
    return source, source_opt


  # URL source options
  def SourceURL(self, options = {}, log = True):
    demuxer_opt = ''
    opt_udp_overrun = ''
    opt_udp_buffer = ''
    opt_udp_timeout = ''
    opt_srt = ''
    source = options['source']
    self.source_ext = options['source_ext']['value']
    loop = options['loop']
    if any(str in source for str in [ 'srt://' ]):
      self.logger.info('[MediaPipe] SRT source parsing')
      opt_srt = '?pkt_size=1316'
      srt_mode = str(options['srt_mode'])
      srt_passphrase = options['srt_passphrase']
      if srt_mode:
        self.logger.info('[MediaPipe] SRT mode: ' + srt_mode)
        opt_srt += '&mode=' + srt_mode
      if srt_passphrase:
        self.logger.info('[MediaPipe] SRT passphrase: ' + srt_passphrase)
        opt_srt += '&passphrase=' + str(srt_passphrase)
    if any(str in source for str in [ 'udp://' ]):
      udp_overrun = options['udp_overrun']
      udp_buffer = options['udp_buffer']
      udp_timeout = options['udp_timeout']
      self.logger.info('[MediaPipe] UDP source parsing')
      if udp_overrun:
        opt_udp_overrun = '?overrun_nonfatal=1'
        self.logger.info('[MediaPipe] UDP overrun enabled')
      if udp_buffer:
        opt_udp_buffer = 'fifo_size=' + str(int(udp_buffer * 1024 * 1024 / 188))
        self.logger.info('[MediaPipe] UDP buffer (' + str(udp_buffer) + 'k)')
        if udp_overrun:
          opt_udp_buffer = '&' + opt_udp_buffer
        else:
          opt_udp_buffer = '?' + opt_udp_buffer
      if udp_timeout:
        opt_udp_timeout = 'timeout=' + str(udp_timeout * 1000000)
        self.logger.info('[MediaPipe] UDP timeout (' + str(udp_timeout) + 's)')
        if udp_overrun or udp_buffer:
          opt_udp_timeout = '&' + opt_udp_timeout
        else:
          opt_udp_timeout = '?' + opt_udp_timeout
    elif loop:
      if log:
        self.logger.info('[MediaPipe] Loop source: ' + str(bool(loop)))
      demuxer_opt += ' -re -stream_loop -1'
    if any(str in source for str in [ 'http://', 'https://' ]):
      demuxer_opt += ' -re'
      if '.m3u8' in source:
        demuxer_opt += ' -http_persistent 1 -http_multiple 1'
      if self.source_ext and ('://www.youtube.com' in source):
        self.logger.info('[MediaPipe] Youtube link detected: ID ' + str(self.source_ext['format_id']))
        source = self.source_ext['url']
        self.source_youtube = True
      if options['http_reconnect']:
        demuxer_opt += ' -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -reconnect_at_eof 1'
#   thread_queue_size = ' -thread_queue_size 1024 '
    source_opt = ''.join([ demuxer_opt, ' -i \"', source, opt_udp_overrun, opt_udp_buffer, opt_udp_timeout, opt_srt, '\"' ])
    return source, source_opt


  # Source category select (main/backup/failover)
  def SourceType(self):
    options = {}
    if self.query.source_active == 'failover' and self.failover_use:
      if self.query.source_fail_type == 'Default':
        self.settings = Settings.query.first()
        options = {
          'source': self.settings.default_fail_src,
          'source_ext': {},
          'type': self.settings.default_fail_type,
          'decoder': self.settings.default_fail_decoder,
          'decoder_err_detect': self.settings.default_fail_decoder_err_detect,
          'loop': self.settings.default_fail_loop,
          'udp_overrun': self.settings.default_fail_udp_overrun,
          'udp_buffer': self.settings.default_fail_udp_buffer,
          'udp_timeout': self.settings.default_fail_udp_timeout,
          'srt_mode': self.settings.default_srt_mode,
          'srt_passphrase': self.settings.default_srt_passphrase,
          'http_reconnect': self.settings.default_fail_http_reconnect,
          'merge_pmt_versions': self.settings.default_fail_merge_pmt_versions
        }
      else:
        options = {
          'source': self.query.source_fail,
          'source_ext': { 'key': 'source_fail_ext', 'value': self.query.source_fail_ext },
          'type': self.query.source_fail_type,
          'decoder': self.query.source_fail_decoder,
          'decoder_err_detect': self.query.source_fail_decoder_err_detect,
          'decoder_deinterlace': self.query.source_fail_decoder_deinterlace,
          'decoder_scale': self.query.source_fail_decoder_scale,
          'loop': self.query.source_fail_loop,
          'udp_overrun': self.query.source_fail_udp_overrun,
          'udp_buffer': self.query.source_fail_udp_buffer,
          'udp_timeout': self.query.source_fail_udp_timeout,
          'srt_mode': self.query.source_fail_srt_mode,
          'srt_passphrase': self.query.source_fail_srt_passphrase,
          'http_reconnect': self.query.source_fail_http_reconnect,
          'merge_pmt_versions': self.query.source_fail_merge_pmt_versions
        }
    elif self.query.source_active == 'backup' and self.query.source_bak:
      options = {
        'source': self.query.source_bak,
        'source_ext': { 'key': 'source_bak_ext', 'value': self.query.source_bak_ext },
        'type': self.query.source_bak_type,
        'decoder': self.query.source_bak_decoder,
        'decoder_err_detect': self.query.source_bak_decoder_err_detect,
        'decoder_deinterlace': self.query.source_bak_decoder_deinterlace,
        'decoder_scale': self.query.source_bak_decoder_scale,
        'loop': self.query.source_bak_loop,
        'udp_overrun': self.query.source_bak_udp_overrun,
        'udp_buffer': self.query.source_bak_udp_buffer,
        'udp_timeout': self.query.source_bak_udp_timeout,
        'srt_mode': self.query.source_bak_srt_mode,
        'srt_passphrase': self.query.source_bak_srt_passphrase,
        'http_reconnect': self.query.source_bak_http_reconnect,
        'merge_pmt_versions': self.query.source_bak_merge_pmt_versions
      }
    else:
      options = {
        'source': self.query.source_main,
        'source_ext': { 'key': 'source_main_ext', 'value': self.query.source_main_ext },
        'type': self.query.source_main_type,
        'decoder': self.query.source_main_decoder,
        'decoder_err_detect': self.query.source_main_decoder_err_detect,
        'decoder_deinterlace': self.query.source_main_decoder_deinterlace,
        'decoder_scale': self.query.source_main_decoder_scale,
        'loop': self.query.source_main_loop,
        'udp_overrun': self.query.source_main_udp_overrun,
        'udp_buffer': self.query.source_main_udp_buffer,
        'udp_timeout': self.query.source_main_udp_timeout,
        'srt_mode': self.query.source_main_srt_mode,
        'srt_passphrase': self.query.source_main_srt_passphrase,
        'http_reconnect': self.query.source_main_http_reconnect,
        'merge_pmt_versions': self.query.source_main_merge_pmt_versions
      }
    return options


  # Source options parsing
  def Source(self):
    self.source_type_options = self.SourceType()
    self.logger.info('[MediaPipe] Source: ' + self.query.source_active)
    self.logger.info('[MediaPipe] ' + self.source_type_options['type'] + ': ' + self.source_type_options['source'])
    if self.source_type_options['type'] == 'Image':
      source, source_opt = self.SourceImage(options = self.source_type_options)
    elif self.source_type_options['type'] == 'Clip':
      source, source_opt = self.SourceClip(options = self.source_type_options)
    elif self.source_type_options['type'] == 'Device':
      source, source_opt = self.SourceDevice(options = self.source_type_options)
    else:
      source, source_opt = self.SourceURL(options = self.source_type_options)
    if any(str in source for str in [ 'udp://', 'srt://', '.ts', '.mpeg', '.mpg' ]) and self.source_type_options['merge_pmt_versions']:
      self.merge_pmt_versions = ' -merge_pmt_versions 1'
    return source, source_opt


  # All available sources parse
  def SourceGetAll(self):
    options = [
      { 'role': 'main', 'type': self.query.source_main_type, 'source': self.query.source_main, 'loop': self.query.source_main_loop },
      { 'role': 'backup', 'type': self.query.source_bak_type, 'source': self.query.source_bak, 'loop': self.query.source_bak_loop }
    ]
    source_all = {}
    for opt in options:
      if opt['source']:
        if opt['type'] == 'Image':
          source_all[opt['role']], source_opt = self.SourceImage(options = opt)
        elif opt['type'] == 'Clip':
          source_all[opt['role']], source_opt = self.SourceClip(options = opt, log = False)
        else:
          source_all[opt['role']] = opt['source']
    return source_all


  def DecoderOptions(self):
    decoder_opt = ' -threads 1 -fflags +genpts'
    self.decoder = self.source_type_options['decoder']
    self.logger.info('[MediaPipe] DecoderOptions: Decoder ' + str(self.decoder))
    self.decoder_scale = self.source_type_options['decoder_scale']
    self.decoder_deinterlace = self.source_type_options['decoder_deinterlace']
    if self.gpu_stats:
      gpu_filter = self.NVENCGetStats(value = [ 'gpu', 'gram' ])
      self.logger.info('[MediaPipe] DecoderOptions: Selecting GPU-' + str(gpu_filter) + ' for video filters')
      self.cuvid_upload = 'format=nv12,hwupload_cuda=device=' + gpu_filter + ','
      self.cuvid_download = ',hwdownload,format=nv12'
      if self.decoder:
        gpu_decoder = self.NVENCGetStats(value = [ 'dec_util', 'gram' ])
        self.logger.info('[MediaPipe] DecoderOptions: Selecting GPU-' + str(gpu_decoder) + ' for video decoding')
        decoder_opt += ' -c:v ' + self.decoder + ' -gpu ' + gpu_decoder
        if self.decoder_deinterlace:
          decoder_opt += ' -deint ' + self.decoder_deinterlace + ' -drop_second_field 1'
          self.logger.info('[MediaPipe] DecoderOptions: Deinterlace enabled (' + self.decoder_deinterlace + ')')
        if self.decoder_scale:
          self.decoder_scale = str(self.decoder_scale)
          decoder_opt += ' -resize ' + self.decoder_scale
          self.logger.info('[MediaPipe] DecoderOptions: Scale enabled (' + self.decoder_scale + ')')
    else:
      self.cuvid_upload = ''
      self.cuvid_download = ''
      self.logger.info('[MediaPipe] DecoderOptions: GPU decoding is not available')
    decoder_err_detect = self.source_type_options['decoder_err_detect']
    if decoder_err_detect:
      decoder_opt += ' -err_detect ' + decoder_err_detect
      self.logger.info('[MediaPipe] DecoderOptions: Error detect (' + decoder_err_detect + ')')
    return decoder_opt


  # Stream(s) mapping
  def StreamMap(self, profile = None):
    self.has_video = None
    self.has_audio = None
    self.has_data = None
    if self.query.source_active == 'failover' and self.failover_use:
      if self.query.source_fail_type == 'Default':
        vpid = self.settings.default_fail_vpid
        apid = self.settings.default_fail_apid
        dpid = self.settings.default_fail_dpid
      else:
        vpid = profile.fail_vpid
        apid = profile.fail_apid
        dpid = profile.fail_dpid
    elif self.query.source_active == 'main':
      vpid = profile.main_vpid
      apid = profile.main_apid
      dpid = profile.main_dpid
    else:
      vpid = profile.bak_vpid
      apid = profile.bak_apid
      dpid = profile.bak_dpid
    map_log = 'No stream selected'
    if vpid or apid or dpid:
      if vpid:
        mapping = ' -map 0:' + str(vpid)
        self.has_video = str(vpid)
        map_log = str(vpid) + ' (video)'
      else:
        mapping = ' -vn '
      if apid:
        mapping += ' -map 0:' + str(apid)
        self.has_audio = str(apid)
        map_log += ', ' + str(apid) + ' (audio)'
      else:
        mapping += ' -an'
      if dpid:
        mapping += ' -map 0:' + str(dpid)
        self.has_data = str(dpid)
        map_log += ', ' + str(dpid) + ' (data)'
      else:
        mapping += ' -dn'
    else:
      self.has_video = 'v'
      self.has_audio = 'a'
      self.has_data = 'd'
      mapping = ' -map 0'
      map_log = 'auto'
    self.logger.info('[MediaPipe] Stream mapping: ' + map_log)
    return mapping


  # Metadata mapping
  def MetadataMap(self, profile = None):
    md_map = ''
    try:
      self.logger.debug('[MediaPipe] Metadata: ' + str(profile.stream_metadata))
      if profile.stream_metadata:
        for pmd_key in list(profile.stream_metadata.keys()):
          md_map += ' -metadata ' + str(pmd_key) + '=\"' + str(profile.stream_metadata.get(pmd_key)) + '\"'
      self.logger.debug('[MediaPipe] mapping: ' + md_map)
    except:
      self.logger.error('[MediaPipe] MetadataMap: Exception error')
      raise
    return md_map


  # Target PID define
  def PIDMap(self, profile = None):
    pid_map = ''
    try:
      self.logger.debug('[MediaPipe] PID(s) mapping: ' + str(profile.stream_pids))
      if profile.stream_pids:
        pid_map = ' ' + profile.stream_pids
    except:
      self.logger.error('[MediaPipe] PIDMap: Exception error')
      raise
    return pid_map


  # Thumbnail settings
  def Thumbnail(self):
    if self.has_video and self.query.thumb_render:
      self.logger.info('[MediaPipe] Thumbnail: Enabled (' + str(self.query.thumb_render) + ')')
      self.logger.info('[MediaPipe] Thumbnail: Interval ' + str(self.query.thumb_interval) + ' frames')
      if self.query.thumb_render == 'cuvid':
        if self.gpu_stats:
          thumb_filter = 'thumbnail_cuda=' + str(self.query.thumb_interval) + ',scale_cuda=480:360'
          thumb_cmd = ' -threads:v 1 -an -map 0:' + self.has_video + ' -filter:v \"' + self.cuvid_upload + thumb_filter + self.cuvid_download + '\" -q:v 12 -update 1 ' + self.ThumbPath()
          return thumb_cmd
        else:
          self.logger.info('[MediaPipe] Thumbnail: GPU is not available')
      elif self.query.thumb_render == 'libavcodec':
        thumb_cmd =  ' -threads:v 1 -an -map 0:' + self.has_video + ' -filter:v \"select=not(mod(n\,' + str(self.query.thumb_interval) + ')),scale=480:360\" -q:v 12 -vsync vfr -update 1 ' + self.ThumbPath()
        return thumb_cmd
    self.logger.info('[MediaPipe] Thumbnail: Disabled')
    return ''


  # Load preset settings from JSON file
  def LoadPreset(self, preset_type = None, preset_name = None):
    pd = os.path.join(app_config.PRESETS_DIR, preset_type, preset_name)
    with open(pd) as preset_data:
      data = json.load(preset_data)
    self.logger.info('[MediaPipe] Preset load: ' + preset_name + ' (' + preset_type + ')')
    return data


  # CLI options mapping
  def EncMapping(self, option = None, value = None):
    options = {
      # Video
      'vcodec': ' -c:v ' + value,
      'vpreset': ' -preset:v ' + value,
      'vprofile': ' -profile:v ' + value,
      'level': ' -level ' + value,
      'vbitrate': ' -b:v ' + value + 'k',
      'cbr': ' -cbr ' + value,
      'minrate': ' -minrate ' + value + 'k',
      'maxrate': ' -maxrate ' + value + 'k',
      'vbuffer': ' -bufsize:v ' + value + 'k',
      'subsample': ' -pix_fmt ' + value,
      'fps': ' -r ' + value,
      'gop': ' -g ' + value,
      'strict_gop': ' -strict_gop ' + value,
      'coder': ' -coder ' + value,
      'rc': ' -rc ' + value,
      'rc_lookahead': ' -rc-lookahead ' + value,
      'zerolatency': ' -tune zerolatency ' if value == 'True' else '',
      'spatial_aq': ' -spatial-aq ' + value,
      'temporal_aq': ' -temporal-aq ' + value,
      'keyint_min': ' -keyint_min ' + value,
      'keyframes': ' -force_key_frames "expr:gte(t,n_forced*' + value + ')" -forced-idr 1',
      'cc_copy': ' -a53cc ' + value,
      'vcustom': ' ' + value + ' ',
      # Audio
      'acodec': ' -c:a ' + value,
      'abitrate': ' -b:a ' + value + 'k',
      'channels': ' -ac ' + value,
      'sample_rate': ' -ar ' + value,
      'acustom': ' ' + value + ' '
      # channels = ' -af pan="mono|c0=0.5*FC+0.15*FL+0.15*BL+0.15*FR+0.15*BR"'
      # channels = ' -af pan="stereo|c0=0.5*FC+0.3*FL+0.3*BL|c1=0.5*FC+0.3*FR+0.3*BR"'
    }
    return options[option]


  # GPU average stats
  def NVENCGetStats(self, value = [ 'gpu', 'gram' ]):
    gpu_idx = '0'
    if self.gpu_stats:
      dev_data = self.gpu_stats['dev_data']
      if dev_data[0]['dev_name'] == 'GPU Average':
        dev_data.pop(0)
      #self.logger.info('dev_data: ' + str(dev_data))
      la_total = []
      for idx, stat in enumerate(dev_data):
        dev_opt = stat['dev_opt']
        self.logger.info('dev_opt: ' + str(dev_opt))
        la = sum(dev_opt[v] for v in value)
        la_total.append(la)
      self.logger.info('la_total: ' + str(la_total))
      self.logger.info('la_total.min: ' + str(min(la_total)))
      gpu_idx = str(la_total.index(min(la_total)))
    return gpu_idx


  # NVENC settings
  def NVENCSetup(self, profile = None):
    nvenc_setup = ''
    try:
      if self.gpu_stats:
        if profile.nvenc_gpu:
          if profile.nvenc_gpu == 'auto':
            gpu_encoder = self.NVENCGetStats(value = [ 'enc_util', 'gram' ])
            self.logger.info('[MediaPipe] vEncoder: gpu_encoder ' + str(gpu_encoder))
          else:
            gpu_encoder = profile.nvenc_gpu
        else:
          gpu_encoder = 'any'
        nvenc_setup = ' -gpu ' + str(gpu_encoder)
        self.logger.info('[MediaPipe] vEncoder: GPU encoding enabled (device: ' + str(gpu_encoder) + ')')
      else:
        self.logger.info('[MediaPipe] vEncoder: GPU encoding is not available')
    except:
      self.logger.info('[MediaPipe] vEncoder: GPU encoding init error')
      raise
    return nvenc_setup


  # Video encnoder settings
  def vEncoder(self, profile = None):
    venc_cmd = ''
    if self.has_video:
      self.logger.info('[MediaPipe] vEncoder: enabled')
      vprofile_data = self.LoadPreset(preset_type = 'video', preset_name = profile.vpreset)
      if vprofile_data['vcodec'] != 'copy':
        if 'nvenc' in vprofile_data['vcodec']:
          vprofile_data['vcodec'] = vprofile_data['vcodec'] + self.NVENCSetup(profile = profile)
        vopt_order = [ 'vcodec', 'vpreset', 'vprofile', 'level', 'vbitrate', 'vbuffer', 'maxrate', 'cbr', 'subsample', 'fps', 'gop', 'keyint_min', 'strict_gop', 'coder', 'rc', 'rc_lookahead', 'zerolatency', 'spatial_aq', 'temporal_aq', 'keyframes', 'cc_copy', 'vcustom' ]
        for option in vopt_order:
          if option in vprofile_data and vprofile_data[option]:
            venc_cmd += self.EncMapping(option = option, value = str(vprofile_data[option]))
        venc_cmd += self.vFilters(profile = profile)
        self.venc_enabled = True
      else:
        if self.source_type_options['type'] == 'URL' and not self.source_type_options['loop']:
          self.source_opt = ' -re ' + self.source_opt
        venc_cmd = ' -c:v copy'
        self.venc_enabled = False
        self.logger.info('[MediaPipe] vEncoder: stream copy')
#        if 'rtmp://' in self.source_type_options['source']:
#          self.logger.info('[MediaPipe] vEncoder: bitstream filter applied (h264_mp4toannexb)')
#          venc_cmd += ' -bsf:v h264_mp4toannexb'
    else:
      self.logger.info('[MediaPipe] vEncoder: disabled')
    return venc_cmd


  # Video filters
  def vFilters(self, profile = None):
    vfilters = ''
    if profile.venc_psize:
      if self.decoder_scale:
        self.logger.warning('[MediaPipe] vFilter: Resize (omited due to decoder options)')
      else:
        scale_value = profile.venc_psize.replace('x', ':')
        if self.gpu_stats:
          self.logger.info('[MediaPipe] vFilter: Resize CUDA (' + scale_value + ')')
          vfilters = 'scale_cuda=' + scale_value
        else:
          self.logger.info('[MediaPipe] vFilter: Resize libavfilter (' + scale_value + ')')
          vfilters = 'scale=' + scale_value
    if profile.venc_di:
      if self.decoder_deinterlace:
        self.logger.warning('[MediaPipe] vFilter: Deinterlace (omited due to decoder options)')
      else:
        if self.gpu_stats:
          self.logger.info('[MediaPipe] vFilter: Deinterlace CUDA')
          if profile.venc_psize and not self.decoder_scale:
            vfilters += ',yadif_cuda=mode=' + profile.venc_di + ':parity=auto:deint=all'
          else:
            vfilters = 'yadif_cuda=mode=' + profile.venc_di + ':parity=auto:deint=all'
        else:
          self.logger.info('[MediaPipe] vFilter: Deinterlace libavfilter')
          if profile.venc_psize and not self.decoder_scale:
            vfilters += ',yadif=mode=' + profile.venc_di + ':parity=auto:deint=all'
          else:
            vfilters = 'yadif=mode=' + profile.venc_di + ':parity=auto:deint=all'
    if vfilters:
      vfilters = ' -filter:v ' + self.cuvid_upload + vfilters + self.cuvid_download
    else:
      self.logger.info('[MediaPipe] vFilter: No filter(s) applied')
    return vfilters


  # Audio encoder
  def aEncoder(self, profile = None):
    aenc_cmd = ''
    if self.has_audio:
      self.logger.info('[MediaPipe] aEncoder: enabled')
      aprofile_data = self.LoadPreset(preset_type = 'audio', preset_name = profile.apreset)
      if aprofile_data['acodec'] != 'copy':
        aopt_order = [ 'acodec', 'abitrate', 'channels', 'sample_rate', 'acustom' ]
        for option in aopt_order:
          if option in aprofile_data:
            aenc_cmd += self.EncMapping(option = option, value = str(aprofile_data[option]))
        aenc_cmd += self.aFilters(profile = profile)
#        self.aenc_enabled = True
      else:
        aenc_cmd = ' -c:a copy'
#        self.aenc_enabled = False
        self.logger.info('[MediaPipe] aEncoder: stream copy')
    else:
      self.logger.info('[MediaPipe] aFilter: No filter(s) applied')
    return aenc_cmd


  # Data encoder
  def dEncoder(self, profile = None):
    denc_cmd = ''
    if self.has_data:
      self.logger.info('[MediaPipe] dEncoder: enabled')
      if profile.dpreset == 'scte35':
        denc_cmd = ' -enable_scte'
        self.scte35_enabled = True
        self.logger.info('[MediaPipe] dEncoder: SCTE-35 decoder enabled')
      elif profile.dpreset == 'copy':
        denc_cmd = ' -c:d copy'
        self.logger.info('[MediaPipe] dEncoder: stream copy')
    return denc_cmd


  # Audio filters settings
  def aFilters(self, profile = None):
    afilters = ''
  #afilters = '-filter:a aresample=' + str(profile.sample_rate) + ':resampler=soxr:async=1'
    return afilters


  # Device target
  def TargetDevice(self, target = None):
    cmd = '[f=decklink:onfail=ignore]' + target.device_name
    self.logger.info('[MediaPipe] Device: ' + target.device_name)
    return cmd


  # RTMP Target options
  def TargetRTMP(self, target = None, url = None):
    cmd = '[f=flv:onfail=ignore:bsfs/v=h264_mp4toannexb:bsfs/a=aac_adtstoasc]' + url
    self.logger.info('[MediaPipe] RTMP app: ' + target.stream_app)
    return cmd


  # MPEGTS Target options
  def MPEGTSOptions(self, target = None):
    mpegts_opt = ''
    self.logger.info('[MediaPipe] MPEGTS muxrate: ' + str(target.mpegts_muxrate))
    self.logger.info('[MediaPipe] MPEGTS PCR period: ' + str(target.mpegts_pcr_period))
    self.logger.info('[MediaPipe] MPEGTS PAT period: ' + str(target.mpegts_pat_period))
    self.logger.info('[MediaPipe] MPEGTS SDT period: ' + str(target.mpegts_sdt_period))
    self.logger.info('[MediaPipe] UDP packet size: ' + str(target.udp_pkt_size))
    ts_flag_map = ''
    if target.mpegts_flags:
      for ts_flag in list(target.mpegts_flags.keys()):
        if target.mpegts_flags.get(ts_flag):
          ts_flag_map += '+' + ts_flag
      if ts_flag_map:
        ts_flag_map = ':mpegts_flags=' + ts_flag_map
    mpegts_opt += (':muxrate=' + str(target.mpegts_muxrate)) if target.mpegts_muxrate else ''
    mpegts_opt += ':pcr_period=' + str((target.mpegts_pcr_period) or 20)
    mpegts_opt += ':pat_period=' + str((target.mpegts_pat_period) or 0.1)
    mpegts_opt += ':sdt_period=' + str((target.mpegts_sdt_period) or 0.5)
    mpegts_opt += ts_flag_map
    return mpegts_opt


  # UDP Target options
  def TargetUDP(self, target = None, url = None):
    return '[f=mpegts:onfail=ignore' + self.MPEGTSOptions(target = target) + ']' + str(url) + '?pkt_size=' + str(target.udp_pkt_size)


  # SRT Target options
  def TargetSRT(self, target = None, url = None):
    target_opt = '?pkt_size=' + str(target.srt_pkt_size) + '&mode=' + str(target.srt_mode)
    self.logger.info('[MediaPipe] SRT packet size: ' + str(target.srt_pkt_size))
    if target.srt_maxbw:
      target_opt += '&maxbw=' + str(target.srt_maxbw)
      self.logger.info('[MediaPipe] SRT maximum sending bandwidth: ' + str(target.srt_maxbw))
    if target.srt_passphrase:
      target_opt += '&passphrase=' + str(target.srt_passphrase)
      self.logger.info('[MediaPipe] SRT passphrase: ' + str(target.srt_passphrase))
    if target.srt_pbkeylen:
      target_opt += '&pbkeylen=' + str(target.srt_pbkeylen)
      self.logger.info('[MediaPipe] SRT encryption key length: ' + str(target.srt_pbkeylen))
    cmd = '[f=mpegts:onfail=ignore' + self.MPEGTSOptions(target = target) + ']' + str(url) + target_opt
    return cmd


  # HLS Target options
  def DRM_HLS(self, hls_drm_asset = False, hls_profile_dir = '', server_ip = None):
    try:
      drm_cmd = ''
      if self.query.hls_drm_active and hls_drm_asset:
        drm_type = 'aes-128'
        self.logger.info('[MediaPipe] HLS DRM type: ' + drm_type)
    #    if self.query.hls_drm_type == 'AES-128':
    #      drm_type = 'aes'
        drm_dir_keys = os.path.join(app_config.DRM_DIR, drm_type, 'keys')
        if not os.path.isdir(drm_dir_keys):
          os.makedirs(drm_dir_keys)
        drm_file_key = os.path.join(drm_dir_keys, self.query.id + '.key')
        drm_file_key_content = ''
        if self.query.hls_drm_key_type == 'Local':
          drm_key_url = self.query.id + '.key'
          try:
            drm_file_key_content = binascii.unhexlify(self.query.hls_drm_key)
            self.logger.debug('[MediaPipe] HLS DRM key content: hex to binary encoded')
          except:
            drm_file_key_content = self.query.hls_drm_key
            self.logger.warning('[MediaPipe] HLS DRM key content: Not a hex value, encoding binary')
        if self.query.hls_drm_key_type == 'Remote':
          drm_key_url = self.query.hls_drm_key_url
          try:
            self.logger.debug('[MediaPipe] HLS DRM remote key: Remote key request')
            r = requests.get(drm_key_url, auth = (self.query.hls_drm_key_user, self.query.hls_drm_key_password), timeout = 3, stream = True)
            if r.status_code >= 200 and r.status_code < 400:
              drm_file_key_content = r
          except:
            self.logger.warning('[MediaPipe] HLS DRM remote key: Remote key request error')
        with open(drm_file_key, 'wb') as key:
          key.write(drm_file_key_content)
        if self.query.hls_drm_key_type == 'Local':
          if server_ip == 'localhost':
            shutil.copy(drm_file_key, hls_profile_dir)
          else:
            drm_file_key_put = os.path.join(hls_profile_dir, drm_key_url)
            r = requests.put(drm_file_key_put, data = drm_file_key_content, timeout = 3)
  #      self.logger.debug('[MediaPipe] HLS DRM key HEX: ' + binascii.hexlify(drm_file_key_content))
        drm_dir_keyinfo = os.path.join(app_config.DRM_DIR, drm_type, 'keyinfo')
        if not os.path.isdir(drm_dir_keyinfo):
          os.makedirs(drm_dir_keyinfo)
        drm_file_keyinfo = os.path.join(drm_dir_keyinfo, self.query.id + '.keyinfo')
        drm_file_keyinfo_content = drm_key_url + '\n' + drm_file_key + '\n' + self.query.hls_drm_key_iv
        with open(drm_file_keyinfo, 'w') as keyinfo:
          keyinfo.write(drm_file_keyinfo_content)
        self.logger.debug('[MediaPipe] HLS DRM keyinfo: ' + drm_file_keyinfo)
        self.logger.debug('[MediaPipe] HLS DRM key URL: ' + drm_key_url)
        self.logger.debug('[MediaPipe] HLS DRM key file: ' + drm_file_key)
        self.logger.debug('[MediaPipe] HLS DRM IV: ' + self.query.hls_drm_key_iv)
        drm_cmd = ':hls_key_info_file=' + drm_file_keyinfo
    except:
      self.logger.error('[MediaPipe] HLS DRM: Exception error')
      raise
    return drm_cmd


  # HLS Target options
  def TargetHLS(self, target = None, server = None, url = None):
    if server:
      hls_profile_dir = os.path.join(self.HLSDir(server = server), target.stream_name)
      hls_list_size = 'f=hls:onfail=ignore:hls_list_size=' + str(target.hls_list_size)
      hls_time = ':hls_time=' + str(target.hls_seg_time)
      hls_segment_filename = ':hls_segment_filename=' + os.path.join("\\'" + hls_profile_dir, target.hls_seg_name + ".ts\\'")
      if server.ip == 'localhost':
        hls_method = ''
        hls_flags = ':hls_flags=delete_segments+periodic_rekey'
        srv_type = 'Local'
        if not os.path.isdir(hls_profile_dir):
          os.makedirs(hls_profile_dir)
      else:
        hls_method = ':method=PUT'
        hls_flags = ':hls_flags=periodic_rekey'
        srv_type = 'Remote'
      if target.hls_seg_format == 'Sequence':
        segment_mode = ':hls_wrap=16'
      elif target.hls_seg_abs_path and (server.ip != 'localhost'):
        segment_mode = ':use_localtime=1:use_localtime_mkdir=1'
      else:
        segment_mode = ':use_localtime=1'
      drm = self.DRM_HLS(hls_drm_asset = target.hls_drm_asset, hls_profile_dir = hls_profile_dir, server_ip = server.ip)
      cmd = '[' + hls_list_size + hls_time + hls_segment_filename + drm + hls_method + hls_flags + segment_mode + ']' + url
      self.logger.info('[MediaPipe] HLS dir: ' + srv_type + ' (' + hls_profile_dir + ')')
      self.logger.info('[MediaPipe] HLS Segments format: ' + target.hls_seg_format + ' (' + target.hls_seg_name + ')')
      self.logger.info('[MediaPipe] HLS Manifest size: ' + str(target.hls_list_size))
    else:
      self.logger.warning('[MediaPipe] HLS target is unavailable (no server)')
    return cmd


  # Smooth Target options
  #  def TargetSmooth(self, target = None):
  #    url =  'http://' + server.ip + ':' + str(server.port) + '/' + target.stream_app + '/' + target.stream_name + '.isml/manifest'
  #    cmd = ' -movflags isml+frag_keyframe -f ismv ' + '"http://' + self.query_srv.ip + ':' + str(self.query_srv.port) + '/' + target.stream_app + '/' + target.stream_name + '.keyos/Streams(LiveStream)?encryptedString=606c6df3-d6da-490f-b24c-3e16d626cce1&kid=3a40aa9e-9585-41d4-85b6-2a9db450d581&cid=f6079edd-77ac-427e-871b-63d928e496a6"'
  #    ss_server = self.query_srv.ip + ':' + str(self.query_srv.port)
  #    NewSS = SmoothPP()
  #    NewSS.Create(ss_server, target.stream_app, target.stream_name)
  #    return url, cmd


  # Icecast Target options
  #  def TargetIcecast(self, target = None):
  #    url =  'icecast://source:radio1@' + server.ip + ':' + server.server_port + server.app + '/' + self.query.stream_name
  #    return url, cmd


  # Target options apply by type
  def TargetURL(self, target = None):
    if target.target_type == 'Stream':
      server = Server.query.filter_by(id = target.stream_srv).first()
      if server:
        if target.stream_type == 'RTMP':
          url = os.path.join(server.rtmp_srv, target.stream_app, target.stream_name)
        elif target.stream_type == 'UDP':
          url = 'udp://' + target.udp_ip + ':' + str(target.udp_port)
        elif target.stream_type == 'SRT':
          url = 'srt://' + target.srt_ip + ':' + str(target.srt_port)
        elif target.stream_type == 'HLS':
          hls_profile_dir = os.path.join(self.HLSDir(server = server), target.stream_name)
          manifest_name = target.hls_list_name + app_config.HLS_MANIFEST_EXT
          url = os.path.join(hls_profile_dir, manifest_name)
      else:
        url = ''
    if target.target_type == 'Device':
      url = target.device_name
      server = ''
    return url, server



  # Target options apply by type
  def Targets(self, target = None):
    self.logger.info('[MediaPipe] Target type: ' + target.target_type)
    url, server = self.TargetURL(target = target)
    if target.target_type == 'Stream':
      self.logger.info('[MediaPipe] Stream type: ' + target.stream_type + ' (' + url + ')')
      if target.stream_type == 'RTMP':
        cmd = self.TargetRTMP(target = target, url = url)
      elif target.stream_type == 'UDP':
        cmd = self.TargetUDP(target = target, url = url)
      elif target.stream_type == 'SRT':
        cmd = self.TargetSRT(target = target, url = url)
      elif target.stream_type == 'HLS':
        cmd = self.TargetHLS(target = target, server = server, url = url)
    if target.target_type == 'Device':
      cmd = self.TargetDevice(target = target)
    return url, cmd


  # Parse all profiles associated with the Job
  def ParseProfiles(self):
    profiles_cmd = ''
    manifest_content = ''
    self.scte35_enabled = False
    self.logger.info('[MediaPipe] ' + str(len(self.profiles_all)) + ' Profile(s) found')
    for idx, profile in enumerate(self.profiles_all):
      self.logger.info('[MediaPipe] Profile #' + str(idx) + ':')
      stream_map = self.StreamMap(profile = profile)
      metadata_map = self.MetadataMap(profile = profile)
      pid_map = self.PIDMap(profile = profile)
      vencoder_cmd = self.vEncoder(profile = profile)
      aencoder_cmd = self.aEncoder(profile = profile)
      dencoder_cmd = self.dEncoder(profile = profile)
      self.logger.info(f'[MediaPipe] Profile ID: {profile.id}')
      target_cmd, abr_content, abr_srv_id = self.ParseTargets(targets = self.profile_targets_all[profile.id])
      if abr_content:
        manifest_content += abr_content
        srv_id = abr_srv_id
      max_muxing_queue_size = ' -max_muxing_queue_size 4096'
      profiles_cmd += vencoder_cmd + aencoder_cmd + dencoder_cmd + stream_map + pid_map + metadata_map + max_muxing_queue_size + target_cmd
    if manifest_content:
      self.ABRManifestCreate(srv_id = srv_id, content = manifest_content)
    return profiles_cmd


  # Parse all targets associated with the Profile
  def ParseTargets(self, targets = None):
    target_cmd = ''
    abr_content = ''
    abr_server = None
    self.logger.info('[MediaPipe] ' + str(len(targets)) + ' Target(s) found')
    for idx, target in enumerate(targets):
      self.logger.info('[MediaPipe] Target #' + str(idx) + ':')
      if target_cmd:
        target_cmd += '|'
      if self.query.hls_abr_active and target.stream_srv == self.query.hls_abr_server and target.hls_abr_asset:
        abr_content = abr_content + self.ABRStreamMeta(target = target)
        abr_server = target.stream_srv
        self.logger.info('[MediaPipe] Target is a part of ABR asset')
      url, cmd = self.Targets(target = target)
      target_cmd += cmd
    else:
      target_cmd = ' -flags +global_header+cgop -f tee \"' + target_cmd + '\"'
    return target_cmd, abr_content, abr_server


  def Security(self, source = ''):
    security = ''
    user_agent = ''
    extensions = ''
    protocols = ''
    user_agent = ''
    url_pattern = [ 'http://', 'https://' ]
    if any(str in source for str in url_pattern):
      if '.m3u8' in source:
        extensions = ' -allowed_extensions key,ts'
      protocols = ' -protocol_whitelist file,crypto,tcp,tls,http,https'
      user_agent = ' -user_agent "Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0"'
      security = extensions + protocols + user_agent
    return security


  # Global options init
  def GlobalOptions(self):
    global_opt = ' -hide_banner -y -loglevel level+quiet'
    if self.query.abort_on_errors:
      global_opt += ' -xerror'
    if self.query.abort_on_empty_output:
      global_opt += ' -abort_on empty_output'
    if self.query.max_error_rate:
      global_opt += ' -max_error_rate ' + str(self.query.max_error_rate)
    if self.query.ignore_unknown:
      global_opt += ' -ignore_unknown'
    return global_opt


  # ffmpeg CLI pipeline init
  def FFCmdInit(self):
    cmd = ''
    try:
#      log = 'FFREPORT=file=' + log_name + ':level=40 '
      progress_name = self.job_id + '_progress' + app_config.LOG_FILE_EXT
      progress_log = ' -progress ' + os.path.join(app_config.LOG_DIR_JOBS, progress_name)
      vstats_name = self.job_id + '_vstats' + app_config.LOG_FILE_EXT
      vstats_log = ' -vstats_file ' + os.path.join(app_config.LOG_DIR_JOBS, vstats_name)
      global_opt = self.GlobalOptions()
      self.source, self.source_opt = self.Source()
      decoder_opt = self.DecoderOptions()
      security = self.Security(source = self.source)
      profiles_cmd = self.ParseProfiles()
      thumbnail = self.Thumbnail()
      if self.scte35_enabled:
        ffmpeg_bin = app_config.FFMPEG_SCTE35_BIN
      else:
        ffmpeg_bin = app_config.FFMPEG_BIN
        if self.merge_pmt_versions:
          self.source_opt = self.merge_pmt_versions + self.source_opt
      stdout = ' 2>/dev/null'
      cmd = ffmpeg_bin + global_opt + security + decoder_opt + self.source_opt + thumbnail + profiles_cmd + stdout
      self.logger.debug('[MediaPipe] FFCmdInit: ' + str(cmd))
    except:
      self.logger.debug('[MediaPipe] FFCmdInit: Exception error')
      raise
    return cmd


  def _Process(self):
    try:
      cmd = self.FFCmdInit()
      #cmd = shlex.split(cmd)
      self.logger.debug('[MediaPipe] _Process: cmd ' + str(cmd))
      self.logger.info('[MediaPipe] _Process: Encoder started')
      encoder_name = self.job_id + '_encoder' + app_config.LOG_FILE_EXT
      encoder_log = 'file=' + os.path.join(app_config.LOG_DIR_JOBS, encoder_name) + ':level=24'
      env = os.environ.copy()
      env['FFREPORT'] = encoder_log
      stderr = open(os.devnull, 'w')
      stdout = open(os.devnull, 'w')
      Popen(cmd, env = env, shell = True, close_fds = True, preexec_fn = _SystemTools.SubProcessSetup, stdout = stdout, stderr = stderr)
#      p = Popen(cmd, env = env, close_fds = True, preexec_fn = _SystemTools.SubProcessSetup)
#      p.stdin.close()
#      p.stdout.close()
#      p.stderr.close()
#      p.wait()
    except CalledProcessError as e:
#      msg = str(e.output if e.output else e)
#      self.logger.error('[MediaPipe] _Process: CalledProcessError: ' + msg)
      self.logger.error('[MediaPipe] _Process: Encoder runtime error, refer to encoder log')
#      raise
    except:
      self.logger.error('[MediaPipe] _Process: Exception error')
      raise
    return


  def _Thread(self):
    t = threading.Thread(target = self._Process)
    t.daemon = True
    t.start()


  ### Start encoding process ###
  def EncoderStart(self, thread = True):
    try:
      self.logger.info('[MediaPipe] EncoderStart: Initialize')
      if thread:
        self._Thread()
      else:
        self._Process()
    except:
      self.logger.info('[MediaPipe] EncoderStart: Exception error')
      raise


  # Stop encoding process
  def EncoderStop(self, wipe_media = True, wipe_logs = False):
    self.logger.info('[MediaPipe] Stopping encoder')
    for proc in psutil.process_iter():
      try:
        proc_info = proc.as_dict(attrs = [ 'name', 'pid', 'cmdline' ])
        p_name = proc_info.get('name')
        p_cmdline = ' '.join(proc_info.get('cmdline'))
        p_namespace = [ 'ffmpeg', 'ffmpeg_scte35', 'ffprobe' ]
        p_pattern = [ self.target_first_url ]
#        p_pattern = [ self.source, self.target_first_url ]
        if any(p_name in ns for ns in p_namespace):
          p_pid = None
          search = any if p_name == 'ffprobe' else all
          if search(p in p_cmdline for p in p_pattern):
            _SystemTools.PIDKill(pid_list = [ proc_info.get('pid') ])
            self.logger.info('[MediaPipe] Encoder stop: OK')
      except:
        self.logger.error('[MediaPipe] Encoder stop: Exception error')
    self.WipeAssets(media = wipe_media, logs = wipe_logs)


  # Return all assets for selected Job (logs, source files, targets, etc)
  def JobAssets(self, media = True, logs = False):
    assets = []
    if media:
      assets.append({ 'file': True, 'path': self.ThumbPath(), 'remote': False })
      abr_exist = False
      for target in self.targets_all:
        if target.target_type == 'Stream' and target.stream_type == 'HLS':
          url, server = self.TargetURL(target = target)
          if server:
            hls_profile_dir = os.path.join(self.HLSDir(server = server), target.stream_name)
            assets.append({ 'file': False, 'path': hls_profile_dir + '/', 'remote': bool(server.ip != 'localhost') })
            if target.hls_abr_asset and (not abr_exist):
              abr_exist = True
              abr_manifest = self.ABRManifestPath(server = server)
              assets.append({ 'file': True, 'path': abr_manifest, 'remote': bool(server.ip != 'localhost') })
    if logs:
      job_logs = _FileTools.ListDir(dir = app_config.LOG_DIR_JOBS, ext = '.log', pattern = self.job_id, abs_path = True)
      for log in job_logs:
        assets.append({ 'file': True, 'path': log, 'remote': False  })
    self.logger.info('[MediaPipe] Media assets: ' + str(assets))
    return assets


  # Wipe all assets for selected Job (logs, source files, targets, etc)
  def WipeAssets(self, media = True, logs = False):
    try:
      assets = self.JobAssets(media = media, logs = logs)
      for a in assets:
        try:
          a_path = a.get('path')
          if a.get('remote'):
            r = requests.request('DELETE', a_path, timeout = 3)
            self.logger.debug('[MediaPipe] Remote asset delete (HTTP ' + str(r.status_code) + ', ' + a_path + ')')
          else:
            if a.get('file'):
              if os.path.isfile(a_path):
                os.remove(a_path)
            else:
              shutil.rmtree(a_path)
        except:
          self.logger.debug('[MediaPipe] Asset delete exception (' + a_path + ')')
      self.logger.info('[MediaPipe] Media assets were wiped')
      if logs:
        self.LogClose(logger = self.logger)
    except:
      self.logger.debug('[MediaPipe] Asset delete exception')
