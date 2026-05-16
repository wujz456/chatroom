import socket
import threading

# 存储客户端连接和昵称的映射 {conn: nickname}
clients = {}
nickname_to_conn = {}
lock = threading.Lock()

def broadcast(message, sender_conn=None):
    """广播给所有客户端（可选排除发送者）"""
    with lock:
        for conn in list(clients.keys()):
            if conn != sender_conn:
                try:
                    conn.send(message.encode('utf-8'))
                except:
                    conn.close()
                    if conn in clients:
                        del clients[conn]

def private_message(target_nickname, message, sender_nickname):
    """发送私聊消息"""
    with lock:
        if target_nickname in nickname_to_conn:
            target_conn = nickname_to_conn[target_nickname]
            try:
                target_conn.send(f"[私聊] {sender_nickname}: {message}".encode('utf-8'))
                return True
            except:
                return False
        return False

def list_users(conn):
    """返回当前在线用户列表"""
    with lock:
        users = list(clients.values())
        conn.send(f"在线用户: {', '.join(users)}".encode('utf-8'))

def handle_client(conn, addr):
    print(f"新连接: {addr}")
    # 1. 接收昵称
    try:
        nickname = conn.recv(1024).decode('utf-8').strip()
        if not nickname:
            conn.close()
            return
    except:
        conn.close()
        return

    with lock:
        clients[conn] = nickname
        nickname_to_conn[nickname] = conn

    broadcast(f"【系统】{nickname} 加入聊天室", sender_conn=None)
    print(f"当前在线: {list(clients.values())}")

    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            # 解析命令
            if data == '/users':
                list_users(conn)
                continue
            if data.startswith('@'):
                # 私聊格式: @昵称 消息内容
                parts = data.split(' ', 1)
                if len(parts) == 2:
                    target_nick = parts[0][1:]  # 去掉@
                    msg_content = parts[1]
                    success = private_message(target_nick, msg_content, nickname)
                    if not success:
                        conn.send(f"【系统】用户 {target_nick} 不在线或不存在".encode('utf-8'))
                else:
                    conn.send("【系统】私聊格式错误，应使用 @昵称 消息".encode('utf-8'))
            else:
                # 公聊
                broadcast(f"[公聊] {nickname}: {data}", sender_conn=conn)
    except Exception as e:
        print(f"错误: {e}")
    finally:
        with lock:
            if conn in clients:
                del clients[conn]
            if nickname in nickname_to_conn:
                del nickname_to_conn[nickname]
        conn.close()
        broadcast(f"【系统】{nickname} 离开聊天室", sender_conn=None)
        print(f"{addr} 断开")

def main():
    host = '0.0.0.0'
    port = 12345
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"聊天室服务器启动，监听 {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    main()