import sys
import socket
import threading

def server_loop(local_host, local_port):

    server =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
        print "[*] listening on %s:%d" % (local_host, local_port)
    except:
        print "[!!] Failed to listen on %s:%d" % (local_host, local_port)
        print "[!!] Check for other listening socketd or correct permissions."
        sys.exit(0)

    server.listen(5)

    while True:
        try:
            client_socket, addr = server.accept()
        except KeyboardInterrupt:
            server.close
            print "[*] Proxy Server Closing"
            sys.exit(1)

        # exibe informacoes sobre a conexao local
        print "[==>] Received incoming connection from %s:%d" % (local_host, local_port)

        #inicia uma thread para conversar com o host remoto
        proxy_thread = threading.Thread(target=get_remote_info_exec_proxy, args=(client_socket,))

        proxy_thread.start()

def receive_from(connection):

    buffer = ""

    # definimos um timeout de 2 segundos; de acordo com
    # seu alvo, pode ser que esse valor precise ser ajustado
    connection.settimeout(2)

    try:
        # continua lendo em buffer ate
        # que nao haja mais dados
        # ou a temporizacao expire
        while True:
            data = connection.recv(4096)

            if not data:
                break
            else:
                buffer += data
    except:
        pass

    return buffer


def get_remote_info_exec_proxy(client_socket):
    local_data = receive_from(client_socket)
    #print local_data
    if len(local_data):
        try:
            line0 = local_data.split('\n')[0];

            url = line0.split(' ')[1]

            http_pos = url.find("://")
            if (http_pos == -1):
                temp = url
            else:
                temp = url[(http_pos+3):]

            port_pos = temp.find(":")

            webserver_pos = temp.find("/")
            if webserver_pos == -1:
                webserver_pos = len(temp)

            webserver = ""
            port = -1

            if (port_pos == -1 or webserver_pos < port_pos):
                port = 80
                webserver = temp[:webserver_pos]
            else:
                port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
                webserver = temp[:port_pos]

            proxy_server(client_socket, webserver, port, local_data)
        except Exception, e:
            print e
            print "Data:"
            print local_data
            print


def is_bloked(remote_host):
    list = []
    list.append('hotmail.com')

    if remote_host in list:
        return True

    return False

# modifica qualquer resposta destinada ao host local
def get_bloked_message():
        return  "<!DOCTYPE html> <html> <body> <h1>Blocked page</h1>  <p>:)</p> </body> </html> "


def proxy_server(client_socket, remote_host, remote_port, local_data):

    print "[==>] Solicitado %s:%d" % (remote_host, remote_port)

    # Se o remote host estiver bloqueado, devolve uma mensagem padrao
    if is_bloked(remote_host):
        client_socket.send(get_bloked_message())
    else:
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))

        if len(local_data):
            # envia os dados ao host remoto
            remote_socket.send(local_data)

            # recebe a resposta
            remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print "[<==] Received %d bytes from %s." % len(remote_buffer, remote_host)

            # envia dados ao handler de resposta
            remote_buffer = response_handler(remote_host, remote_buffer)

            # envia  a resposta para socket local
            client_socket.send(remote_buffer)

        remote_socket.close()
    client_socket.close()
    print "[*] Closing connections."



def main():

    # sem parsing sofisticado de linha de comando nesse caso
    if len(sys.argv[1:]) != 2:
        print "Usage: ./HTTPProxy.py [localhost] [localport]"
        print "Exemple: ./HTTPProxy.py 127.0.0.1 80"
        sys.exit(0)

    # define parametros para ouvir localmente
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])


    # agora coloca em acao nosso socket q ue ficara ouvindo
    server_loop(local_host, local_port)

main()
