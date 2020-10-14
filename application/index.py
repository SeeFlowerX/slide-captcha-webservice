from urllib.parse import urlparse
from main import app

base_path = ''

# aliyun FC 
def handler(environ, start_response):
    # 如果没有使用自定义域名
    if environ['fc.request_uri'].startswith("/2016-08-15/proxy"):
      parsed_tuple = urlparse(environ['fc.request_uri'])
      li = parsed_tuple.path.split('/')
      global base_path
      if not base_path:
          base_path = "/".join(li[0:5])

      context = environ['fc.context']
      environ['HTTP_HOST'] = '{}.{}.fc.aliyuncs.com'.format(context.account_id, context.region)
      environ['SCRIPT_NAME'] = base_path + '/'
     
    return app(environ, start_response)
