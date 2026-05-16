import socket
import threading

def receive_messages(sock):
    """持续接收服务器消息并显示"""
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if data:
                print(f"\r{data}\n> ", end='')
            else:
                break
        except:
            break

def main():
    host = '127.0.0.1'
    port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # 先发送昵称
    nickname = input("请输入你的昵称: ")
    sock.send(nickname.encode('utf-8'))

    # 启动接收线程
    thread = threading.Thread(target=receive_messages, args=(sock,))
    thread.daemon = True
    thread.start()

    print("欢迎来到聊天室！")
    print("命令: /users 查看在线用户, @昵称 消息 私聊, /quit 退出")
    while True:
        msg = input("> ")
        if msg == '/quit':
            break
        sock.send(msg.encode('utf-8'))

    sock.close()

if __name__ == '__main__':
    main()