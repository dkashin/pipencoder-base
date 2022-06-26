
#from __future__ import unicode_literals
#from youtube_dl import YoutubeDL
#from youtube_dl.utils import DownloadError, ExtractorError

  # Single:
  # https://www.youtube.com/watch?v=DPfHHls50-w
  #
  # Part of playlist:
  # https://www.youtube.com/watch?v=dwV04XuiWq4&list=PLCsuqbR8ZoiDF6iBf3Zw6v1jYBNRfCuWC
  #
  # Playlist:
  # https://www.youtube.com/playlist?list=PLr9odFCQgyWKTIozQ_QYM-46T6S7PCoWQ
  #

  # Check Youtube links
#  def CheckYoutube(self, url = None, format_id = None, pl_flat = False):
#    media_data = None
#    try:
#      ydl_opt = {
#        'logger': self.logger,
#        'skip_download': True,
#        'noplaylist': True,
#        'extract_flat': 'in_playlist',
##        'playlist_items': '1,3,5',
#        'dump_single_json': True,
#        'geo_bypass': True,
#        'cachedir': False
##        'ignoreerrors': False
##        'nocheckcertificate': True,
##        'prefer_insecure': True,
##        'listformats': True
#      }
#      try:
#        with YoutubeDL(ydl_opt) as ydl:
#          parsed_data = ydl.extract_info(url)
          #self.logger.debug('[CheckTools] parsed_data: ' + str(json.dumps(parsed_data, indent = 2, sort_keys = True)))
#          msg = 'No media data found'
#          if 'entries' in parsed_data:
#            #entries = parsed_data.get('entries')
#            #media_data = [ { 'id': e.get('id'), 'title': e.get('title') } for e in entries  ]
#            #msg = 'OK'
#            msg = 'Playlists are not supported'
#          elif 'formats' in parsed_data:
#            media_data = parsed_data.get('formats')
#            if format_id:
#              self.logger.debug('[CheckTools] Youtube requested format ID: ' + format_id)
#              media_data_by_id = None
#              for md in media_data:
#                if md.get('format_id') == format_id:
#                  media_data_by_id = md
#                  break
#              media_data = media_data_by_id
#            msg = 'OK'
#      except (DownloadError, ExtractorError) as e:
#        msg = str(e).split('ERROR: ')[1]
#        raise
#    except:
#      msg = 'Exception error'
#      raise
#    if media_data:
#      media_data = { 'streams': media_data }
#    else:
#      self.logger.error('[CheckTools] Youtube check: ' + msg)
#    return media_data, msg
