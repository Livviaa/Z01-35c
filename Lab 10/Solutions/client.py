from tkinter import END, scrolledtext, BOTH, LEFT, ANCHOR

import openapi_client
from openapi_client import ApiException
import tkinter as tk
import requests
import socketio

from pprint import pprint

configuration = openapi_client.Configuration(
    host="http://127.0.0.1:5000"
)
sio = socketio.Client()

username = ""


@sio.event
def login_register():
    print("login_register triggered!")
    refreshUserList()


@sio.event
def message(data):
    print("message triggered!")
    try:
        selected_user = str(listbox.get(ANCHOR)).split()[0]
    except:
        selected_user = None

    if data["receiver"] != username and data["sender"] != username:
        return
    else:
        if selected_user and data["sender"] == selected_user:
            getMessages()
        elif data["sender"] != selected_user:
            refreshUserList()


@sio.event
def read(data):
    print("read triggered!")
    try:
        selected_user = str(listbox.get(ANCHOR)).split()[0]
    except:
        selected_user = None

    if selected_user and data["sender"] == username and data["receiver"] == selected_user:
        getMessages()


def getMessages(*args):
    sent_by = listbox.get(ANCHOR)
    data = "{\"meta\": { \"method\": \"getMessage\", \"args\":  {\"sent_by\": \"" + str(sent_by).split()[0] + \
           "\", \"userName\": \"" + username + "\"}}}"
    custom_header = dict()
    custom_header['Content-Type'] = 'application/json'
    custom_header['Accept'] = 'application/vnd.api+json'

    response = requests.post("http://127.0.0.1:5000/api/Messages/getMessage", data=data, headers=custom_header).json()
    chatWindow.delete('1.0', END)
    pprint(response)
    if response["meta"]["result"]["messages"] is not None:
        for message in response["meta"]["result"]["messages"]:
            if message["readDate"] != "":
                readDate = "Odczytano:\n" + 3 * '\t' + message["readDate"]
            else:
                readDate = "Nie odczytano"

            if message["receiver"] == username:
                chatWindow.insert(END, message["sender"] + " napisał:\n" + message["text"] + "\nWysłano:\n" + message[
                    "sendDate"] + "\n\n")
            else:
                chatWindow.insert(END, 3 * '\t' + "Napisałeś: " + "\n" + 3 * '\t' + message[
                    "text"] + "\n" + 3 * '\t' + readDate + "\n\n")


def sendMessage():
    with openapi_client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = openapi_client.UsersApi(api_client)
        message_text = messageWindow.get("1.0", END)
        receiver = str(listbox.get(ANCHOR)).split()[0]

        meta = {
            "method": "sendMessage",
            "args": {
                "sender": username,
                "receiver": receiver,
                "text": message_text
            }
        }

        post_user_send_message = openapi_client.PostUserSendMessage(meta=meta)
        # print(message_text)

        try:
            # sending a message to a specific user
            api_instance.send_message0(post_user_send_message)
            # chatWindow.insert(END, username + " -> " + receiver + ": " + message_text)
        except openapi_client.ApiException as e:
            print("Exception when calling MessagesApi->send_receiver_username_message_post: %s\n" % e)
        getMessages()


def countUnreadMessages(sent_by: str):
    meta = {
        "method": "getUnreadMessages",
        "args": {
            "user": username,
            "sent_by": sent_by
        }
    }

    # Enter a context with an instance of the API client
    with openapi_client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = openapi_client.MessagesApi(api_client)
        post_message_get_unread_messages = openapi_client.PostMessageGetUnreadMessages(
            meta=meta)  # PostMessageGetUnreadMessages | Returns count of unread messages

        try:
            # getUnreadMessages
            api_response = api_instance.get_unread_messages0(post_message_get_unread_messages)
            return api_response.to_dict()["meta"]["result"]["result"]

        except ApiException as e:
            print("Exception when calling MessagesApi->get_unread_messages0: %s\n" % e)
            return ""


def login(user_login: str, password: str):
    meta = {
        "method": "loginUser",
        "args": {
            "login": user_login,
            "password": password
        }
    }

    # Enter a context with an instance of the API client
    with openapi_client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = openapi_client.UsersApi(api_client)
        post_user_login_user = openapi_client.PostUserLoginUser(meta=meta)  # PostUserLoginUser | loginUser

        try:
            # loginUser
            api_response = api_instance.login_user0(post_user_login_user)
            if api_response.to_dict()["meta"]["result"]["result"] == 'failed':
                return False
            else:
                sio.connect("http://127.0.0.1:5000")
                return True
        except ApiException as e:
            print("Exception when calling UsersApi->login_user0: %s\n" % e)
            return False


def register():
    global username
    username = username_entry.get()
    password = password_entry.get()

    meta = {
        "method": "registerUser",
        "args": {
            "login": username,
            "password": password
        }
    }

    # Enter a context with an instance of the API client
    with openapi_client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = openapi_client.UsersApi(api_client)
        post_user_register_user = openapi_client.PostUserRegisterUser(meta=meta)  # PostUserRegisterUser | registerUser

        try:
            # registerUser
            api_response = api_instance.register_user0(post_user_register_user)
            if api_response.to_dict()["meta"]["result"]["result"] == 'failed':
                error_lbl.config(text="Podany login jest już zajęty!")
                return False
            else:
                error_lbl.config(text="Zarejestrowano pomyślnie! Zaloguj się.")
                return True
        except ApiException as e:
            print("Exception when calling UsersApi->register_user0: %s\n" % e)
            return False


def logoutUser():
    if username == "":
        root.destroy()
        return

    meta = {
        "method": "logoutUser",
        "args": {
            "login": username
        }

    }

    # Enter a context with an instance of the API client
    with openapi_client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = openapi_client.UsersApi(api_client)
        post_user_logout_user = openapi_client.PostUserLogoutUser(meta=meta)  # PostUserLogoutUser | logoutUser

        try:
            # logoutUser
            sio.disconnect()
            api_instance.logout_user0(post_user_logout_user)
        except ApiException as e:
            print("Exception when calling UsersApi->logout_user0: %s\n" % e)

    root.destroy()


def refreshUserList():
    # with openapi_client.ApiClient() as api_client:
    #     # Create an instance of the API class
    #     api_instance = openapi_client.UsersApi(api_client)
    #
    # try:
    #     # GetAllUsers
    #     api_response = api_instance.get_all_users0()
    #     pprint(api_response)
    #     return []
    # except ApiException as e:
    #     print("Exception when calling UsersApi->get_all_users0: %s\n" % e)
    #     return []

    api_response = requests.get("http://127.0.0.1:5000/api/Users/getAllUsers").json()
    users = api_response["meta"]["result"]["users"]

    listbox.delete(0, END)

    for user in users:
        if user["username"] == username:
            continue
        if user["online_status"]:
            status = "Online"
        else:
            status = "Offline"

        listbox.insert('end', user["username"] + " (" + status + ") " + countUnreadMessages(user["username"]))


def loginDraw(root):
    global error_lbl
    error_lbl = tk.Label(root, text="")
    username_lbl = tk.Label(root, text="Podaj login:")
    password_lbl = tk.Label(root, text="Podaj hasło:")
    global username_entry
    global password_entry
    username_entry = tk.Entry(root)
    password_entry = tk.Entry(root, show="*")
    btn_login = tk.Button(root, text="Zaloguj", command=lambda: validateLoginAndDrawChat(root))
    btn_register = tk.Button(root, text="Zarejestruj", command=register)
    error_lbl.pack()
    username_lbl.pack()
    username_entry.pack()
    password_lbl.pack()
    password_entry.pack()
    btn_login.pack()
    btn_register.pack()


def validateLoginAndDrawChat(root):
    global username
    username = username_entry.get()
    password = password_entry.get()

    if login(username, password):
        for elem in root.winfo_children():
            elem.destroy()
        logged_lbl = tk.Label(root, text="Zalogowany jako: " + username)
        logged_lbl.place(x=280, y=0)

        global listbox
        listbox = tk.Listbox(root, width=30, height=10, font=('New Times Roman', 11))
        listbox.pack(side=LEFT, fill=BOTH)
        scrollbar = tk.Scrollbar(root)
        scrollbar.pack(side=LEFT, fill=BOTH)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        listbox.bind("<<ListboxSelect>>", getMessages)

        global chatWindow
        chatWindow = scrolledtext.ScrolledText(root, width=47, height=16)
        chatWindow.place(x=280, y=20)

        global messageWindow
        messageWindow = tk.Text(root, font=('New Times Roman', 11), width=40, height=5)
        messageWindow.place(x=280, y=305)

        btn_message = tk.Button(root, text='Wyślij', bg='papaya whip', width=8, height=3, command=sendMessage)
        btn_message.place(x=610, y=320)

        refreshUserList()
    else:
        error_lbl.config(text="Zły login/hasło!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chatapp")
    root.geometry("680x400")
    root.protocol("WM_DELETE_WINDOW", logoutUser)
    loginDraw(root)
    root.mainloop()
