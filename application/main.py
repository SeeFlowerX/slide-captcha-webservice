from flask import Flask, request
from flask import jsonify
from config import config
import tempfile
from urllib.request import urlretrieve
from darknet import load_net, load_meta, detect, save_predict
from flask_basicauth import BasicAuth


net = load_net(config['network']['cfg'],config['network']['weight'],0)
meta = load_meta(config['network']['meta'])


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
        res = detect(net, meta, fp.name)
    
    # predict center
    has_center = False
    center = {"x":None,"y":None}
    for r in res:
        has_center = True
        center = {"x":r[2][0],"y":r[2][1]}
    save_predict(fp.name, res)

    return jsonify({
        "success": True, 
        "result": res, 
        "has_center":has_center,
        "center":center})
