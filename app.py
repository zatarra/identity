from flask import Flask, jsonify, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import uuid
import json
import os
import glob
from flask_cors import CORS

app =   Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST"])

app.url_map.strict_slashes = False

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def open_db():
  with open("domains.json", "r") as r:
    _tmp = json.load(r)
    return _tmp

def save_db(contents):
  with open("domains.json", "w+") as r:
    _tmp = json.dump(contents, r, indent=2)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_extension(filename):
    if '.' not in filename:
      raise Exception("Extension not found")

    return filename.rsplit('.', 1)[1].lower()

def add_domain(domain, authorized_thirdparties):
    _tmp = open_db()

    if request.args.get('key', None) !=  _tmp['config']["admin_key"]:
      raise Exception("Invalid management key")

    if domain in _tmp['domains']:
      raise Exception("Domain already registered")
    key = uuid.uuid4().hex
    _tmp["domains"][domain] = {"key": key, "authorized_thirdparties": authorized_thirdparties, "image_key": uuid.uuid4().hex}
    save_db(_tmp)
    return {"key": key}

def delete_domain(domain):
    _tmp =open_db()
    if domain not in _tmp['domains']:
      raise Exception("Domain does not exist")
    
    if request.args.get('key', None) not in [_tmp["domains"][domain]["key"], _tmp['config']["admin_key"]]:
      raise Exception("Invalid management key")

    del _tmp["domains"][domain]
    save_db(_tmp)
    return "domain deleted"

def authorize_thirdparty(domain, authorized_thirdparties):
    _tmp =open_db()
    if domain not in _tmp['domains']:
      raise Exception("Domain does not exist")

    if request.args.get('key', None) not in [_tmp["domains"][domain]["key"],  _tmp['config']["admin_key"]]:
      raise Exception("Invalid management key")
    
    if isinstance(authorized_thirdparties, list):
      _tmp["domains"][domain]["authorized_thirdparties"] = _tmp["domains"][domain]["authorized_thirdparties"] + authorized_thirdparties 
    else:
      _tmp["domains"][domain]["authorized_thirdparties"].append(authorized_thirdparties)
    save_db(_tmp)
    return _tmp["domains"][domain]["authorized_thirdparties"]

def revoke_thirdparty(domain, thirdparty):
    _tmp =open_db()
    if domain not in _tmp['domains']:
      raise Exception("Domain does not exist")

    if request.args.get('key', None) not in [_tmp["domains"][domain]["key"], _tmp['config']["admin_key"]]:
      raise Exception("Invalid management key")

    _tmp["domains"][domain]["authorized_thirdparties"].remove(thirdparty)
    save_db(_tmp)
    return _tmp["domains"][domain]["authorized_thirdparties"]

@app.route('/')
def index():
  return jsonify({"actions": ["add", "delete", "authorize_thirdparty", "revoke_thirdparty"], "image": "<id>", "upload": "<filename>"})

@app.route('/actions', methods=['POST'])
def actions():
  try:
    _data = request.json
    if "action" not in _data:
      return "Invalid request"

    if _data["action"] == "add":
      if "domain" not in _data:
        return "Missing domain"
      return add_domain(_data['domain'], _data.get("authorized_thirdparties", []))
    elif _data["action"] == "delete":
      if "domain" not in _data:
        return "Missing domain"
      return delete_domain(_data['domain'])
    elif _data["action"] == "authorize_thirdparty":
      if "domain" not in _data:
        return "Missing domain"
      if "authorized_thirdparties" not in _data:
        return "Missing list of authorized thirdparty domains"
      return authorize_thirdparty(_data['domain'], _data['authorized_thirdparties'])
    elif _data["action"] == "revoke_thirdparty":
      if "domain" not in _data:
        return "Missing domain"
      if "authorized_thirdparties" not in _data:
        return "Missing thirdparty domain to be revoked"
      return revoke_thirdparty(_data['domain'], _data['authorized_thirdparties'])
    else:
      return "Unknown error"
  except Exception as e:
    return str(e), 500

@app.route('/image/<name>/<thirdparty>')
@app.route('/image/<name>')
def download_file(name, thirdparty=None):
  try:
    _tmp = open_db()
    if name not in _tmp['domains']:
      raise Exception("Could not find domain")

    if thirdparty != None and thirdparty not in _tmp['domains'][name]["authorized_thirdparties"]:
      raise Exception("thirdparty not authorized to use the logo")

    image = glob.glob(f"{app.config['UPLOAD_FOLDER']}/{ _tmp['domains'][name]['image_key']}*")[0]
    return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(image))
  except Exception as e:
    return f"{str(e)}", 500

@app.route('/upload', methods=['POST'])
def upload_file():
  try:
    if request.method == 'POST':
        _post_form = request.form
        if "domain" not in _post_form or "key" not in _post_form:
          raise Exception("Missing domain or key")
        _tmp = open_db()        
  
        if _post_form["domain"] not in _tmp["domains"]:
            raise Exception("invalid combination of management key and domain")
        if _post_form.get("key", None) not in [_tmp["domains"][_post_form['domain']]["key"], _tmp['config']["admin_key"]]: 
          raise Exception("invalid combination of management key and domain")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            filename = f"{_tmp['domains'][_post_form['domain']]['image_key']}.{secure_filename(file_extension(file.filename))}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return "Upload image"
  except Exception as e:
    return f"Invalid request: {str(e)}", 500
if __name__ == '__main__':
    app.run(debug=True)
