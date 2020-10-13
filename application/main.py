from flask import Flask, request
from flask import jsonify
from config import config
import tempfile
from urllib.request import urlretrieve
from darknet import load_net, load_meta, detect
from flask_basicauth import BasicAuth


net = load_net(config['network']['cfg'].encode('utf-8'),
                config['network']['weight'].encode('utf-8'),0)
meta = load_meta(config['network']['meta'].encode('utf-8'))


app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'jerry'
app.config['BASIC_AUTH_PASSWORD'] = 'love_code'

basic_auth = BasicAuth(app)


@app.route('/detect-center',methods=['POST'])
@basic_auth.required
def detect_image():
    img_url = request.form.get('img_url')

    with tempfile.NamedTemporaryFile(delete=False) as fp:
        urlretrieve(img_url, fp.name)
        res = detect(net, meta, fp.name.encode('utf-8'))
    
    # predict center
    has_center = False
    center = {"x":None,"y":None}
    for r in res:
        has_center = True
        center = {"x":r[2][0],"y":r[2][1]}

    return jsonify({
        "success": True, 
        "result": res, 
        "has_center":has_center,
        "center":center})

app.run(debug=True,host='0.0.0.0')
