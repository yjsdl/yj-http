import socket
import re
import threading

def server_client(new_socket):
    """为这个客户端返回数据"""
    # 1.接收浏览器发送过来的请求
    # GET /HTTP/1.1
    request = new_socket.recv(1024).decode("utf-8")
    #print("======>"*50)
    #print(request)
    
    request_lines = request.splitlines()
    print("")
    print("----"*20)
    print(request_lines)
    file_name = ""
    ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
    if ret:
        file_name = ret.group(1)
        #print("-"*10,file_name)
        if file_name == "/":
            file_name = "/index.html"
    




    # 2.返回http格式的数据给浏览器
    try:
        f = open("./html" + file_name, "rb")
    except:
        response = "HTTP/1.1 404 NOT FOUND\r\n"
        response += "\r\n"
        response += "------not found---"
        new_socket.send(response.encode("utf-8"))
    else:
        html_content = f.read()
        f.close()
        # 2.1准备发送给浏览器的数据...header
        response = "HTTP/1.1 200 OK\r\n"
        response += "\r\n"
        # 2.2准备发送给浏览器的数据...boy
        # response += "hahahaha"

        # 将response.header发送给浏览器
        new_socket.send(response.encode("utf-8"))
        # 将response.body发送给浏览器
        new_socket.send(html_content)
    # 3.关闭套接字
    new_socket.close()


def main():
    # 1.创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    # 2.绑定
    tcp_server_socket.bind(("",7890))
    # 3.变为监听套接字
    while True:

        tcp_server_socket.listen(128)
        # 4.等待客户链接
        new_socket, client_addr = tcp_server_socket.accept()
        # 5.为这个客户服务
        p = threading.Thread(target=server_client, args=(new_socket,))
        p.start()
        #new_socket.close()
    # 6.关闭监听套接字
    tcp_server_socket.close()



if __name__ == "__main__":
    main()
