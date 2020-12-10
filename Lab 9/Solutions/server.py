from safrs import SAFRSBase, SAFRSAPI
from safrs import jsonapi_rpc  # rpc decorator
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy

try:
    from flask_admin import Admin
    from flask_admin.contrib import sqla
except:
    print("Failed to import flask-admin")

app = Flask(__name__)

# This html will be rendered in the swagger UI
description = """
based on: https://github.com/thomaxxl/safrs
"""

db = SQLAlchemy()

class User(SAFRSBase, db.Model):
    __tablename__ = "Users"

    login = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    online_status = db.Column(db.Boolean, default=False, nullable=False)

    # sent = db.relationship('Message', back_populates='user', primaryjoin='Users.sent == Message.id', lazy=True)
    # received = db.relationship('Message', back_populates='user', primaryjoin='Users.reveived == Message.id', lazy=True)

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def loginUser(cls, login, password):
        """
            description: loginUser
            summary: loginUser
            args:
                login: login
                password: password
            responses:
                '200':
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    result:
                                        type: object
                                        properties:
                                            result: string
        """
        user = db.session.query(User).filter_by(login=login).first()
        if user is None or password != user.password or user.online_status:
            return {"result": "failed"}
        user.online_status = True
        db.session.add(user)
        db.session.commit()
        return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def logoutUser(cls, login):
        """
            description: logoutUser
            summary: logoutUser
            args:
                login: login
        """
        db.session.query(User).filter_by(login=login).first().online_status = False
        db.session.commit()

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def registerUser(cls, login, password):
        """
            description: registerUser
            summary: registerUser
            args:
                login: login
                password: password
            responses:
                '200':
                    description: OK
                    schema:
                        type: object,
                        properties:
                            meta:
                                type: object,
                                properties:
                                    result:
                                        type: object,
                                        properties:
                                            result: string
        """
        user = db.session.query(User).filter_by(login=login).first()
        if user is not None:
            return {"result": "failed"}
        user = User(login=login, password=password)
        db.session.add(user)
        db.session.commit()
        return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['GET'])
    def getLoggedUsers(cls, *args, **kwargs):
        """
            description: GetLoggedUsers
            summary: GetLoggedUsers
            responses:
                '200':
                    description: "OnlineUsers"
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    result:
                                        type: object
                                        properties:
                                            users:
                                                type: array
                                                items: string
        """
        users_online = {"users": []}
        for user in db.session.query(User).filter_by(online_status=True).all():
            users_online['users'].append(user.login)
        return users_online

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def sendMessage(cls, sender, receiver, text):
        """
            description: Send a message to a specify user
            summary: sendMessage
            args:
                sender: sender
                receiver: receiver
                text: text
        """

        message = Message(sender=sender, receiver=receiver, text=text)
        db.session.add(message)
        db.session.commit()


class Message(SAFRSBase, db.Model):
    """
        description: Message description
    """

    __tablename__ = "Messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.String, db.ForeignKey('Users.login'), nullable=False)
    receiver = db.Column(db.String, db.ForeignKey('Users.login'), nullable=False)
    text = db.Column(db.String, nullable=False)

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def getMessage(cls, user, sent_by):
        """
            description: Send a message to a specify user
            summary: sendMessage
            args:
                user: user
                sent_by: sent_by
            responses:
                '200':
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    messages:
                                        type: array,
                                        items:
                                            type: object,
                                            properties:
                                                id:
                                                    type: integer,
                                                sender:
                                                    type: string,
                                                receiver:
                                                    type: string,
                                                text:
                                                    type: string
        """

        result = {"messages": []}

        def bothSideGetMsg(_user, _sent_by):
            for message in db.session.query(Message).filter_by(sender=_sent_by, receiver=_user).order_by("id").all():
                msg = dict()
                msg["id"] = message.id
                msg["sender"] = message.sender
                msg["receiver"] = message.receiver
                msg["text"] = message.text
                result['msg'].append(msg)

        bothSideGetMsg(user, sent_by)
        bothSideGetMsg(sent_by, user)
        return result


# def abort_if_no_message(username):
#     if username not in messages:
#         abort(404, message="There's no message for {} ".format(username))
#
#
# class ClientGetMessages(Resource):
#     def get(self, username):
#         abort_if_no_message(username)
#         return {"messages": messages.pop(str(username))}
#
#
# class ClientSendMessage(Resource):
#     def post(self, receiver_username, message):
#         messages[str(receiver_username)].append(message)
#         return {"status": "success"}


# api.add_resource(ClientGetMessages, "/get/<string:username>")
# api.add_resource(ClientSendMessage, "/send/<string:receiver_username>/<string:message>")


def start_api(swagger_host="127.0.0.1", PORT=None):
    # Needed because we don't want to implicitly commit when using flask-admin
    SAFRSBase.db_commit = False

    with app.app_context():
        db.init_app(app)
        db.create_all()

        db.session.commit()

        custom_swagger = {
            "info": {"title": "ChatAPP"},
        }  # Customized swagger will be merged

        api = SAFRSAPI(
            app,
            host=swagger_host,
            port=PORT,
            prefix=API_PREFIX,
            custom_swagger=custom_swagger,
            schemes=["http"],
            description=description,
        )

        for model in [User, Message]:
            # Create an API endpoint
            api.expose_object(model)

        # see if we can add the flask-admin views
        try:
            admin = Admin(app, url="/admin")
            for model in [User, Message]:
                admin.add_view(sqla.ModelView(model, db.session))
        except Exception as exc:
            print(f"Failed to add flask-admin view {exc}")


API_PREFIX = "/api"  # swagger location
app = Flask("ChatAPP", template_folder="/home/thomaxxl/mysite/templates")
app.secret_key = "not so secret"

app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///",
                  DEBUG=True)  # DEBUG will also show safrs log messages + exception messages


@app.route("/")
def goto_api():
    return redirect(API_PREFIX)


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5000
    start_api(HOST, PORT)

    app.run(host=HOST, port=PORT, threaded=False)
