import socket # importa funções para socket
import time # importa funções para tempo
import os # para usar o getpid
import random # para usar ramdom.ramdom


def client(host, port, n, pid):  # define uma função cliente : quando chamado por outro codigo python passar os argumentos
    # Cria socket define familha de endereços e ???
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    # Conecta socket ao servidor, pegando o endereço do servidor e a porta para se conectar
    server_address = (host, port) 
    # Imprime
    print ("Connecting to %s port %s" % server_address) 
    sock.connect(server_address) 

    # Send data 
    q1 = len(str(pid))
    q2 = len(str(n))
    q = 8 - (q1+q2)
    message = q*"0" + "|{A}|{B}".format(A = pid, B = n)
    
    # tratamento de erro
    try: 
        # envia requisiçao para entrar em regiao critica 10 bytes
       

        print ("Enviando REQUEST %s Com pid: %d" % message, n,pid) 
        stime = random.random() # gera um valor real entre 0 e 1
        for i in range(n): # envia n mensagens
            sock.sendall(message.encode('utf-8'))
            sock.sendall(pid.encode('utf-8'))
            time.sleep(stime) # espera entre 0 a 1 segundo em numero real


        # Recebe resposta do servidor
        amount_received = 0 
        amount_expected = len(message)

        while amount_received < amount_expected: 
            data = sock.recv(16) 
            amount_received += len(data) 
            print ("Received: %s" % data)

        if data.decode('utf-8') == "GRANT": # se receber permissão para entrar na região crítica 
            f = open("resultado.txt", "a") # abre o arquivo resultado.txt para escrita em anexo
            f.write()

    except socket.error as e:  # da erro no scoket
        print ("Socket error: %s" %str(e)) 
    except Exception as e: # qualquer outra exceção
        print ("Alguma outra exceção: %s" %str(e)) 
    finally: # sempre executa
        print ("Closing connection to the server") 
        sock.close() 

client('localhost', 8082, 5,1) # executa a função cliente