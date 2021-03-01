import socket
import re
import select

def server_client(new_socket, request):
    """为这个客户端返回数据"""
    # 1.接收浏览器发送过来的请求
    # GET /HTTP/1.1
    #request = new_socket.recv(1024).decode("utf-8")
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
        response_body = html_content

        response_header = "HTTP/1.1 200 OK\r\n"
        response_header += "Content length:%d\r\n" % len(response_body)
        response_header += "\r\n"
        response = response_header.encode("utf-8") + response_body
        new_socket.send(response)


def main():
    # 1.创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    # 2.绑定
    tcp_server_socket.bind(("",7890))
    # 3.变为监听套接字
    tcp_server_socket.listen(128)
    tcp_server_socket.setblocking(False) # 将套接字变为非堵塞

    # 创建一个epoll对象
    epl = select.epoll()

    # 将监听套接字对应的fd注册到epoll
    epl.register(tcp_server_socket.fileno(), select.EPOLLIN)

    fd_event_dict = dict()
    while True:
        
        fd_event_list = epl.poll() # 默认会堵塞，直到os监测到数据到来，通过事件通知告诉这个程序，此时才会解堵塞
        # [(fd, event), (套接字对应的文件描述符，这个文件描述符是什么事件)]
        for fd, event in fd_event_list:
            # 等待新客户端的链接
            if fd == tcp_server_socket.fileno():
                new_socket, client_addr = tcp_server_socket.accept()
                epl.register(new_socket.fileno(), select.EPOLLIN)
                fd_event_dict[new_socket.fileno()] = new_socket
            elif event == select.EPOLLIN:
                # 判断已经链接的客户端是否有数据·发送过来
                recv_data = fd_event_dict[fd].recv(1024).decode("utf-8")
                if recv_data:
                    server_client(fd_event_dict[fd], recv_data)
                else:
                    fd_event_dict[fd].close()
                    epl.unregister(fd)
                    del fd_event_dict[fd]
    # 6.关闭监听套接字
    tcp_server_socket.close()



if __name__ == "__main__":
    main()
