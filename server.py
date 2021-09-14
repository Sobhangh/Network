import socket
import threading
import os.path
import time
from typing import List, Any

hostname = socket.gethostname()
SERVER = socket.gethostbyname(hostname)
print(SERVER)
PORT = 5050
HEADER = 2048
FORMAT = "ISO-8859-1"


def send(msg, client):
    message = msg.encode(FORMAT)
    client.send(message)

def recv_timeout(the_socket, response, timeout=1):
    # make socket non blocking
    the_socket.setblocking(0)
    # total data partwise in an array
    total_data: List[Any] = []
    data = ''
    # beginning time
    begin = time.time()
    while 1:
        # if you got some data, then break after timeout
        if total_data and time.time() - begin > timeout:
            break
        # if you got no data at all, wait a little longer, twice the timeout
        elif time.time() - begin > timeout * 2:
            break
        # recv something
        try:
            data = the_socket.recv(HEADER)
            if data:
                response += data
                total_data.append(data)
                # change the beginning time for measurement
                begin = time.time()
            else:
                # sleep for sometime to indicate a gap
                time.sleep(0.5)
        except:
            pass
    # join all parts to make final string
    the_socket.setblocking(2)
    return response

def recv_timeout(the_socket, response, timeout=0.1):
    # make socket non blocking
    the_socket.setblocking(0)
    # total data partwise in an array
    total_data: List[Any] = []
    data = ''
    # beginning time
    begin = time.time()
    while 1:
        # if you got some data, then break after timeout
        if total_data and time.time() - begin > timeout:
            break
        # if you got no data at all, wait a little longer, twice the timeout
        elif time.time() - begin > timeout * 2:
            break
        # recv something
        try:
            data = the_socket.recv(HEADER)
            if data:
                response += data
                total_data.append(data)
                # change the beginning time for measurement
                begin = time.time()
            else:
                # sleep for sometime to indicate a gap
                time.sleep(0.05)
        except:
            pass
    # join all parts to make final string
    the_socket.setblocking(2)
    return response


def is_host_correct(request):
    start = request.find("Host")
    if start == -1:
        return False
    return True


""" 
end = request.find('\r\n',start)
    elems = request[start:end].split()
    print(request)
    if elems[1] == SERVER or elems[1] == hostname:
        return True
    return False 
"""


def get_file(path):
    if path[0] == '/':
        try:
            with open(path[1:], "rb") as f:
                return f.read()
                # Do something with the file
        except IOError:
            return 404
    return 400


def month_to_int(m):
    if m == "Jan":
        return 1
    if m == "Feb":
        return 2
    if m == "Mar":
        return 3
    if m == "Apr":
        return 4
    if m == "May":
        return 5
    if m == "Jun":
        return 6
    if m == "Jul":
        return 7
    if m == "Aug":
        return 8
    if m == "Sep":
        return 9
    if m == "Oct":
        return 10
    if m == "Nov":
        return 11
    if m == "Dec":
        return 12


# x is in asc format but y can have any of the html formats
def x_is_after_y(x, y):
    elemx = x.split()
    elemy = y.split()
    # (yeary,monthy,dayy,houry)
    datey = ["", "", "", ""]
    if y.find(",") == -1:
        datey = [elemy[4], elemy[1], elemy[2], elemy[3]]
    elif y.find("-") == -1:
        datey = [elemy[3], elemy[2], elemy[1], elemy[4]]
    else:
        datey2 = elemy[1].split("-")
        datey = ["20" + datey2[2], datey2[1], datey2[0], elemy[2]]
    if int(elemx[4]) > int(datey[0]):
        return True
    elif int(elemx[4]) < int(datey[0]):
        return False
    if month_to_int(elemx[1]) > month_to_int(datey[1]):
        return True
    elif month_to_int(elemx[1]) < month_to_int(datey[1]):
        return False
    if int(elemx[2]) > int(datey[2]):
        return True
    elif int(elemx[2]) < int(datey[2]):
        return False
    hmsx = elemx[3].split(':')
    hmsy = datey[3].split(':')
    if int(hmsx[0]) > int(hmsy[0]):
        return True
    elif int(hmsx[0]) < int(hmsy[0]):
        return False
    if int(hmsx[1]) > int(hmsy[1]):
        return True
    elif int(hmsx[1]) < int(hmsy[1]):
        return False
    if int(hmsx[2]) > int(hmsy[2]):
        return True
    elif int(hmsx[2]) < int(hmsy[2]):
        return False
    return True


def modified(header, path):
    index = header.find("If-Modified-Since")
    if index == -1:
        return True
    last_modified = time.asctime(time.gmtime(os.path.getmtime(path)))
    start = header.find(": ", index) + 2
    end = header.find('\r\n', start)
    date = header[start:end]
    return x_is_after_y(last_modified, date)


def make_response_header(status, type, length):
    header = "HTTP/1.1 "
    if status == 200:
        header += str(200)
        header += " OK"
        header += '\r\n'
        if type == "html":
            header += "Content-Type: text/html"
            header += '\r\n'
        else:
            header += "Content-Type: image/"
            header += type
            header += '\r\n'
    elif status == 400:
        header += str(400)
        header += " Bad Request"
        header += '\r\n'
        header += "Content-Type: text/html"
        header += '\r\n'
    elif status == 404:
        header += str(404)
        header += " Not Found"
        header += '\r\n'
        header += "Content-Type: text/html"
        header += '\r\n'
    elif status == 500:
        header += str(500)
        header += " Server Error"
        header += '\r\n'
        header += "Content-Type: text/html"
        header += '\r\n'
    elif status == 304:
        header += str(304)
        header += " Not Modified"
        header += '\r\n'
        header += "Content-Type: text/html"
        header += '\r\n'
    header += "Date: "
    header += time.asctime(time.gmtime())
    header += '\r\n'

    header += "Content-Length: "
    header += str(length)
    header += '\r\n\r\n'
    return header


def make_html_error(status):
    message = ""
    if status == 400:
        message = "400 Bad Request"
    elif status == 404:
        message = "404 Not Found"
    elif status == 500:
        message = "500 Server Error"
    elif status == 304:
        message = "304 Not Modified"
    response = "<html>\n<head><title>" + message + "</title></head>\n<body>\n<center><h1>" + message + "</h1></center><hr><center>nginx</center></body></html>"
    return response


def get_content_type(path):
    index = path.rfind('.')
    return path[index + 1:]


def handle_request(data, client):
    request = data.decode(FORMAT)#.rstrip()
    #print(request)
    elems = request.split()
    if not is_host_correct(request):
        body = make_html_error(400)
        nbbyte = len(body.encode(FORMAT))
        header = make_response_header(400, "html", nbbyte)
        send(header + body, client)
        return
    if not modified(request, elems[1]):
        body = make_html_error(304)
        nbbyte = len(body.encode(FORMAT))
        header = make_response_header(304, "html", nbbyte)
        send(header + body, client)
        return
    if elems[0] == "GET":
        # TO DO : MAKE A SEPARATE FUNCTION TO HANDLE GET
        print("Received a GET request...")
        #print(elems[1])
        file = get_file(elems[1])
        if file == 400 or file == 404:
            # THERE COULD COME AN ERROR BODY LATER
            body = make_html_error(file)
            nbbyte = len(body.encode(FORMAT))
            header = make_response_header(file, "html", nbbyte)
            send(header + body, client)
        else:
            type = get_content_type(elems[1])
            nbbyte = len(file)
            header = make_response_header(200, type, nbbyte)
            message = header.encode(FORMAT) + file
            client.send(message)
    elif elems[0] == "HEAD":
        print("Received a HEAD request...")
        file = get_file(elems[1])
        if request.find("Host:") == -1:
            file = 400
        if file == 400 or file == 404:
            # THERE COULD COME AN ERROR BODY LATER
            body = make_html_error(file)
            nbbyte = len(body.encode(FORMAT))
            header = make_response_header(file, "html", nbbyte)
            send(header, client)
        else:
            type = get_content_type(elems[1])
            nbbyte = len(file)
            header = make_response_header(200, type, nbbyte)
            message = header.encode(FORMAT)
            client.send(message)
    elif elems[0] == "POST":
        print("Received a POST request...")
        body_index = request.find("\r\n\r\n") + 4
        body = request[body_index:]
        status = 200
        path=elems[1]
        if elems[1][0] == '/' and elems[1].find('/',1) == -1:
            path=elems[1][1:]
        try:
            with open(path, "a") as f:
                f.write(body)
        except IOError:
            status = 500
        header = make_response_header(status, "html", 0)
        send(header, client)
    elif elems[0] == "PUT":
        print("Received a PUT request...")
        body_index = request.find("\r\n\r\n") + 4
        body = request[body_index:]
        status = 200
        path = elems[1]
        if elems[1][0] == '/' and elems[1].find('/',1) == -1:
            path = elems[1][1:]
        try:
            with open(path, "x") as f:
                f.write(body)
        except FileExistsError:
            status = 400
        header = make_response_header(status, "html", 0)
        send(header, client)


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            # check that for http 1.1
            #print("Client connected")
            client.settimeout(60)
            threading.Thread(target=self.listenToClient, args=(client, address)).start()

    def listenToClient(self, client, address):
        size = 2048
        while True:
            try:
                data = bytes()
                data = recv_timeout(client, data)
                if data != b'':
                    handle_request(data, client)
            except:
                client.close()
                print("Client Disconnected")
                return False


ThreadedServer(SERVER, PORT).listen()
