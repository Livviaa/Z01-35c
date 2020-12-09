from flask import Flask
from flask_restful import Api, Resource, abort
from collections import defaultdict
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
api = Api(app)

messages = defaultdict(list)

SWAGGER_URL = '/swagger'
API_URL = '/static/serverAPI.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "ChatApp Server API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


def abort_if_no_message(username):
    if username not in messages:
        abort(404, message="There's no message for {} ".format(username))


class ClientGetMessages(Resource):
    def get(self, username):
        abort_if_no_message(username)
        return {"messages": messages.pop(str(username))}


class ClientSendMessage(Resource):
    def post(self, receiver_username, message):
        messages[str(receiver_username)].append(message)
        return {"status": "success"}


api.add_resource(ClientGetMessages, "/get/<string:username>")
api.add_resource(ClientSendMessage, "/send/<string:receiver_username>/<string:message>")


if __name__ == '__main__':
    app.run(host='localhost')
