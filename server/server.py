from flask import Flask, jsonify, request, make_response, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# Load default configuration and then local settings to override the default one.
app.config.from_object('settings.settings')
app.config.from_object('settings.local_settings')
db = SQLAlchemy(app)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class Clipboard(db.Model):
    username = db.Column(db.String(80), unique=True, primary_key=True)
    text = db.Column(db.Text, unique=False)

    def __init__(self, username, text):
        self.username = username
        self.text = text

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/clipboard/<user_name>',  methods=['GET', 'POST'])
def clipboard(user_name):
    clip_element = Clipboard.query.filter_by(username=user_name).first()
    if clip_element:
        if request.method == 'POST':
            content = request.get_json(force=True)
            clip_element.text = content['text']
            db.session.add(clip_element)
            db.session.commit()
            return make_response("", 200)
        else:
            return jsonify(text=clip_element.text)
    abort(404)



@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    Convert exceptions to json to return as part of the api.
    :param error: The actual exception
    :return: A json representation.
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()
