import  socket
import time
from html.entities import name2codepoint
from typing import List, Any
from html.parser import HTMLParser


SERVER = ""
DEF_PORT = 80
#ISO-8859-1
FORMAT= "ISO-8859-1"
# depends on the html response header
HEADER =2048

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)





def send(msg,client):
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


def isResoponseSuccesful(respons):
    firstlineindex=respons.find('\n')
    elems=respons[:firstlineindex].split()
    return elems[1].startswith('2')

def redirection(respons):
    firstlineindex = respons.find('\n')
    elems = respons[:firstlineindex].split()
    return elems[1].startswith('3')

def chunked_transfer(respons):
    start=respons.find("Transfer-Encoding")
    end= respons.find('\n',start)
    index = respons.find("chunked",start,end)
    return index!=-1

def isImageContent(response):
    start = response.find("Content-Type")
    end = response.find('\n',start)
    return response.find("image",start,end) != -1
def remove_htm_file(path):
    if len(path) < 4 :
        return path
    if path[-3:] == "htm" :
        return ""
        #index = path.rfind('/')
        #if index == -1 :
            #return ""
        #return path[:index+1]
    return path
def remove_html(path):
    if len(path) < 5 :
        return path
    if path[-5:] == "html/":
        index = path[:-1].rfind('/')
        return path[:index + 1]
    return path
class MyHTMLParser(HTMLParser):
    htmldoc=""
    host=""
    link=""
    port =0
    def set_host(self,path):
        self.host = remove_html(path)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        self.htmldoc += c

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        self.htmldoc += c

    def handle_starttag(self, tag, attrs):
        self.htmldoc += '<'+tag
        if tag == "img":
            for attr in attrs:
                self.htmldoc += " "
                if attr[0] == "src":
                    #attr[1] is of the form "http:......." so the first and last elements should not be passed?????IS IT REALLY SO
                    #print(attr[1])
                    image_adress=""
                    if attr[1].find("http") == 0:
                        image_adress = attr[1]
                    elif self.link != "":
                        if self.link[-1] == '/' or attr[1][0] == '/':
                            image_adress = self.link + attr[1]
                        else :
                            image_adress = self.link + '/' + attr[1]
                    else:
                        image_adress = self.host + attr[1]
                    #print(image_adress)
                    image_name = get_requenst(image_adress,self.port,client)
                    #image_name = -1
                    #COULD CHANGE FOR THE ERROR SITUATIONS
                    if image_name != -1 and image_name is not None:
                        self.htmldoc += attr[0] + "=" + '"' + image_name + '"'
                else:
                    self.htmldoc += attr[0] + "=" + attr[1]

            self.htmldoc += ">"
        elif tag == "a":
            for attr in attrs:
                self.htmldoc += " "
                if attr[0] == "href":
                    if attr[1].find("http") == 0:
                        self.link = attr[1]
                    else:
                        self.link = self.host + remove_htm_file(attr[1])
                self.htmldoc += attr[0] + "=" + attr[1]
            self.htmldoc += ">"
        else:
            for attr in attrs:
                self.htmldoc += " "
                self.htmldoc += attr[0] + "=" + attr[1]
            self.htmldoc += ">"

    def handle_endtag(self, tag):
        if tag == "a":
            self.link = ""
        self.htmldoc += "</" + tag + '>'

    def handle_data(self, data):
        self.htmldoc += data

    def handle_decl(self, data):
        self.htmldoc += "<!" + data + ">"

    def handle_comment(self, data):
        self.htmldoc += "<!-- " + data + " -->"



def make_host_correct(host):
    if host[-1] != '/':
        return host +'/'
    return host

def make_valid_file_name(name):
    l = len(name)
    i=0
    new_name=""
    while i<l:
        if name[i] == '/' or name[i] == ':' or name[i] == '*' or name[i] == '?' or name[i] == '"' or name[i] == '>' or name[i] == '<' or name[i] == '|':
            pass
        else:
            new_name += name[i]
        i += 1
    return new_name

#host= adress without http://
def save_file(header,body,host,port):
    if isImageContent(header) :
        img_encoding_index = header.find("Content-Type")
        end_line = header.find('\n', img_encoding_index)
        elems = header[img_encoding_index:end_line].split()
        img_encoding = elems[1]
        extension_index = img_encoding.find('/') + 1
        extension = img_encoding[extension_index:]
        data = body.encode(FORMAT)
        image_name = host  # + '.' + extension
        with open(make_valid_file_name(image_name), 'wb') as f:
            f.write(data)
        return make_valid_file_name(image_name)
    else:
        parser = MyHTMLParser()
        #parser.host=make_host_correct(host)
        parser.set_host(make_host_correct(host))
        parser.port =port
        parser.feed(body)
        file_name = host + ".html"
        with open(make_valid_file_name(file_name), 'w') as f:
            f.write(parser.htmldoc)
        #parser.htmldoc = ""
        return make_valid_file_name(file_name)
prev_host = ""
#location of the form http://www.example.com/
def get_requenst(location , port,client):
    #print(location)
    client.detach()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if location.find("https://") != -1 :
        print("https can not be handled")
        return -1
    index = location.find("//") +2
    end = location.find('/',index)
    ip=""
    host=""
    rest=""
    try:
        if end != -1 :
            host = location[index:end]
            rest = location[end:]
        else:
            host = location[index:]
            rest = '/'
        ip = socket.gethostbyname(host)
    except:
        print("Host does not exist")
        return -1
    try:
        client.connect((ip, port))
        request="GET " + rest  + " HTTP/1.1" + '\r\n' + "Host: " + host + '\r\n\r\n'
        send(request,client)
    except socket.timeout:
        print("socket timeout")
        return -1
    except InterruptedError:
        print("interupted")
        return -1
    encoded_response = client.recv(HEADER)
    # ANOTHER WAY COULD BE TO GET THE LENGTH FIRTST AND THEN BASED ON THAT SET THE BUFFER SIZE FOR THE REST
    encoded_response = recv_timeout(client, encoded_response)
    respons = encoded_response.decode(FORMAT)
    if isResoponseSuccesful(respons):
        body_index = respons.find('\r\n\r\n')
        #+2 for the carriage of the last line
        header = respons[:body_index+2]
        print(header)
        charset_index = header.find("charset=")
        charset =FORMAT
        if charset_index != -1 :
            charset_index += len("charset=")
            charset_end = header.find('\r\n',charset_index)
            charelems = header[charset_index:charset_end].split()
            charset = charelems[0]
        body_index += 4
        if chunked_transfer(respons):
            while respons.find("\r\n0\r\n") == -1:
                encoded_response = recv_timeout(client, encoded_response)
                respons = encoded_response.decode(FORMAT)
            # possible rest of the header in the end
            encoded_response = recv_timeout(client, encoded_response)
            respons = encoded_response.decode(FORMAT)
            chunk_index = body_index
            chunk_index = respons.find('\r\n', chunk_index)
            body = ""
            tail = ""
            i = 0
            while chunk_index != -1:
                next = respons.find('\r\n', chunk_index + 2)
                if i % 2 == 0 and respons[chunk_index - 1] != 0 and next != -1:
                    body += respons[chunk_index + 2:next]
                    if respons[chunk_index - 1] == 0:
                        tail = respons[chunk_index + 2:next]
                i += 1
                chunk_index = next
            header += tail
            new_location = location[:location.rfind('/')+1]
            file = save_file(header,body,location,port)
            return file
        else:
            body = respons[body_index:]
            new_location = location[:location.rfind('/')+1]
            file = save_file(header,body,location,port)
            return file
            # THE last element of respons is \n so not part of the html body
    elif redirection(respons):
        index = respons.find("Location")
        end = respons.find('\n', index)
        elems = respons[index:end].split()
        path = elems[1]
        get_requenst(path, DEF_PORT,client)
    else:
        print(respons)
        #print("bad request")
        return -1

def head_request(location,port,client) :
    client.detach()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    index = location.find("//") + 2
    end = location.find('/', index)
    ip = ""
    host = ""
    rest = ""
    try:
        if end != -1:
            host = location[index:end]
            rest = location[end:]
        else:
            host = location[index:]
            rest = '/'
        ip = socket.gethostbyname(host)
    except:
        print("Host does not exist")
    try:
        client.connect((ip, port))
        request = "HEAD " + rest + " HTTP/1.1" + '\r\n' + "Host: " + host + '\r\n\r\n'
        send(request, client)
    except socket.timeout:
        print("socket timeout")
    except InterruptedError:
        print("interupted")
    encoded_response = client.recv(HEADER)
    respons = encoded_response.decode(FORMAT)
    print(respons)

def put_or_post_request(location,port,client,message,type):
    client.detach()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    index = location.find("//") + 2
    end = location.find('/', index)
    ip = ""
    host = ""
    rest = ""
    try:
        if end != -1:
            host = location[index:end]
            rest = location[end:]
        else:
            host = location[index:]
            rest = '/'
        ip = socket.gethostbyname(host)
    except:
        print("Host does not exist")
    try:
        client.connect((ip, port))
        request = type + " " + rest + " HTTP/1.1" + '\r\n' + "Host: " + host + '\r\n\r\n' +message
        send(request, client)
    except socket.timeout:
        print("socket timeout")
    except InterruptedError:
        print("interupted")
    encoded_response = client.recv(HEADER)
    respons = encoded_response.decode(FORMAT)
    print(respons)

#t=socket.gethostbyname("gecko.es.berkley.edu")
#print(t)
while True :
    msg= input("")
    if msg =="STOP" :
        client.close()
        break
    elems = msg.split()
    host = ""
    port = ""
    host = elems[1]
    if len(elems) < 3:
        port = DEF_PORT
    else:
        port = int(elems[2])
    if elems[0] == "GET":
        get_requenst(host,port,client)
    elif elems[0] == "HEAD" :
        head_request(host,port,client)
    elif elems[0] == "PUT" or elems[0] == "POST" :
        message = input("GIVE THE MESSAGE BODY:")
        put_or_post_request(host,port,client,message,elems[0])

    else:
        print("UNKNOWN COMMAND")


print("clinent terminating")
