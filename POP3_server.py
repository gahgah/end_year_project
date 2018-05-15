# -*- coding: utf-8 -*-
from threading import Thread
from SMTP_Server import database
import socket
from log import LogFile



IP = '0.0.0.0'
PORT = 1500
QUEUE_SIZE = 10
LOGIN_MESSAGE = "+OK POP3 server ready"
USER_EXIST = "+OK User accepted"
NO_SUCH_FILE = "-ERR no such message, only {0} messages in maildrop"
NO_SUCH_USER = "-ERR no such email adress"


def receive(client_socket, func):
    """
    :param func: the exit funcsion of the while loop.
    :param client_socket: the comm socket
    :return: the data thet was recived from the socket
    """
    #FIXME: add return none if timeout (add timeout) cann end the prog with sys.exit()
    data = ""
    while func(data):
        data += client_socket.recv(1)
    log2.log("RECV:" + data, 1)
    return data

def login(client_socket):
    client_socket.sendall(LOGIN_MESSAGE)
    log2.log("SEND:" + LOGIN_MESSAGE, 1)
    data = receive(client_socket, lambda m: "\r\n" not in m)
    if data[:4] == "USER":
        user = data[data.find(" ") + 1:data.find("\r\n")]
        while not database.is_have(user):
            client_socket.sendall(NO_SUCH_USER)
            log2.log("SEND:" + NO_SUCH_USER, 1)
            data = receive(client_socket, lambda m: "\r\n" not in m)
            print "d" +data
            print "u" +user
            user = data[data.find(" ") + 1:data.find("\r\n")]

        client_socket.sendall(USER_EXIST)
        log2.log("SEND:" + USER_EXIST, 1)
        return user, "+OK"
    else:
        pass #FIXME:



def HendelClient(client_socket, client_address):
    user, eror = login(client_socket)

    if eror != "+OK":
        print 'dont find user'
    user_data = database.GetUserData(user)
    data = receive(client_socket, lambda m: "\r\n" not in m)
    if not data == "START\r\n":
        pass #FIXME:
    responce = "+OK "
    responce += str(user_data.get_emails_num())
    responce += " massages ("
    responce += str(user_data.get_emails_sum_length())
    responce += ")"
    client_socket.sendall(responce)
    log2.log("SEND:" + responce, 1)
    while data != "QUIT\r\n":
        if data[:4] == "LIST":
            if data == "LIST\r\n":
                responce = "+OK "
                responce += str(user_data.get_emails_num())
                responce += " massages ("
                responce += str(user_data.get_emails_sum_length())
                responce += ")"
                client_socket.sendall(responce)
                log2.log("SEND:" + responce, 1)
            elif any(char.isdigit() for char in data):
                print 'LIST x'
                index = filter(lambda char: char.isdigit(), data)
                index = int(index)
                if user_data.IsExistRecive(index):
                    responce = "+OK "
                    responce += index
                    responce += " massages ("
                    responce += user_data.get_email_length(index)
                    responce += ")"
                    client_socket.sendall(responce)
                    log2.log("SEND:" + responce, 1)
                else:
                    responce = NO_SUCH_FILE.format(user_data.get_emails_num())
                    client_socket.sendall(responce)
                    log2.log("SEND:" + responce, 1)

        elif data == "":
            pass

        data = receive(client_socket, lambda m: "\r\n" not in m)




def main():
    """
    Add Documentation here
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        log2.log("Listening for connections on port %d" % PORT, 2)

        while True:
            client_socket, client_address = server_socket.accept()
            thread = Thread(target=HendelClient, args=(client_socket, client_address))
            log2.log("new connection from " + str(client_address), 2)
            thread.start()
    except socket.error as err:
        log2.log('received socket exception - ' + str(err), 3)
    finally:
        server_socket.close()


if __name__ == '__main__':
    global log2
    log2 = LogFile("pop3.log", '%(levelname)s:%(message)s')
    main()