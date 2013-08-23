import json
import requests

data = json.loads(requests.get('http://veyepar.nextdayvideo.com:8080/main/C/pyconca/S/pyconca2013.json').text)

for talk in data:
    print 'UPDATE schedule_presentation SET pyvideo_url="%s" WHERE id=%s;' % (talk['fields']['public_url'], talk['fields']['conf_key'])
