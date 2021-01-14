from safrs import SAFRSBase, SAFRSAPI
from safrs import jsonapi_rpc  # rpc decorator
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_socketio import SocketIO, emit

# app = Flask(__name__)

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

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def loginUser(self, login, password):
        '''
            description: loginUser
            summary: loginUser
            args:
                login: "login"
                password: "password"
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
        '''
        user = db.session.query(User).filter_by(login=login).first()
        if user is None or password != user.password or user.online_status:
            return {"result": "failed"}
        user.online_status = True
        db.session.add(user)
        db.session.commit()
        socketio.emit("login_register")

        return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def logoutUser(self, login):
        """
            description: logoutUser
            summary: logoutUser
            args:
                login: login
        """
        user = db.session.query(User).filter_by(login=login).first()
        if user is not None:
            user.online_status = False
            db.session.commit()
            socketio.emit("login_register")

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def registerUser(self, login, password):
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
        if user is not None:
            return {"result": "failed"}
        user = User(login=login, password=password)
        db.session.add(user)
        db.session.commit()
        socketio.emit("login_register")
        return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['GET'])
    def getLoggedUsers(self):
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
    @jsonapi_rpc(http_methods=['GET'])
    def getAllUsers(self):
        """
            description: GetAllUsers
            summary: GetAllUsers
            responses:
                '200':
                    description: "ChatApp Users"
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    users:
                                        type: array
                                        items:
                                            type: object
                                            properties:
                                                username:
                                                    type: string
                                                online_status:
                                                    type: string
        """
        users = {"users": []}
        for user in db.session.query(User).all():
            tmp = {
                "username": user.login,
                "online_status": user.online_status
            }
            users['users'].append(tmp)
        return users

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def sendMessage(self, sender, receiver, text):
        """
            description: Send a message to a specify user
            summary: sendMessage
            args:
                sender: sender
                receiver: receiver
                text: text
        """
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        message = Message(sender=sender, receiver=receiver, text=text, sendDate=now)
        db.session.add(message)
        db.session.commit()
        socketio.emit("message", {"sender": sender, "receiver": receiver})


class Message(SAFRSBase, db.Model):
    """
        description: Message description
    """

    __tablename__ = "Messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.String, nullable=False)
    receiver = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    sendDate = db.Column(db.String)
    readDate = db.Column(db.String, default="")

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def getMessage(self, userName, sent_by):
        """
            description: Gets a message from specified user
            summary: getMessage
            args:
                userName: userName
                sent_by: sent_by
            responses:
                200:
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    messages:
                                        type: array
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: integer
                                                sender:
                                                    type: string
                                                receiver:
                                                    type: string
                                                text:
                                                    type: string
                                                sendDate:
                                                    type: string
                                                readDate:
                                                    type: string
        """

        result = {"messages": []}

        def bothSideGetMsg(_user, _sent_by):
            isRead = False
            for message in db.session.query(Message).filter_by(sender=_sent_by, receiver=_user).order_by("id").all():
                msg = dict()
                msg["id"] = message.id
                msg["sender"] = message.sender
                msg["receiver"] = message.receiver
                msg["text"] = message.text
                msg["sendDate"] = message.sendDate
                if message.readDate == "" and message.receiver == userName:
                    message.readDate = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    isRead = True
                    db.session.commit()
                msg["readDate"] = message.readDate
                result["messages"].append(msg)
            return isRead

        read = bothSideGetMsg(userName, sent_by)
        bothSideGetMsg(sent_by, userName)

        if read:
            socketio.emit("read", {"sender": sent_by, "receiver": userName})

        result["messages"].sort(key=lambda item: item["id"])
        return result

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def getUnreadMessages(self, user, sent_by):
        """
            description: GetUnreadMessages
            summary: GetUnreadMessages
            args:
                user: user
                sent_by: sent_by
            responses:
                '200':
                    description: "OK"
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

        unread_counter = 0

        for message in db.session.query(Message).filter_by(sender=sent_by, receiver=user, readDate="").all():
            unread_counter += 1

        return {"result": str(unread_counter)}


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
    socketio = SocketIO(app)
    socketio.run(app)
