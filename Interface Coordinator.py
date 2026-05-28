# thread interface for cordinator

import threading
import socket


#variaveis globais
Dicionario_Contador = {}
Fila = []
def interface():
    i = 1 
    while i != 3:
        print("1- imprimir fila de pedidos\n 2 - imprimir quantas vezes cada processo foi atendido \n 3 -  encerrar execução")
        match i:
            case 1:
                print("imprimir fila de pedidos atual")
                #pega todos os processos na lista
            case 2: 
                print("imprimir quantas vezes cada processo foi atendido")
            case 3:
                print("encerrar")
                return




def Contador_de_processos(processo_id):
     # liga chave de contador com o n vezes processo chamado
    
    if  Dicionario_Contador.get(processo_id) == None: # testa para ver se elemento ja existe na lista
        Dicionario_Contador[processo_id] = 0 # adiciona um com chave igual associada a valor 0
    else: # processo novo.
        contador = Dicionario_Contador.get(processo_id) # get valor da chave processo_id
        contador += 1 # incrementa 1
        Dicionario_Contador[processo_id]= contador
    return


def fila_de_pedidos():


    return


def qt_vzs_proc_atendido():

    for key, value in Dicionario_Contador.items():
        print(f"processo:{key} vezes atendido:{value}")
    return

def servidor(n):
    # uma thread para receber conexão com novo processo
    addr =("localhost",8082)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(addr)
    servidor.listen()
    thread = threading.Thread(target=mensagens, args=(servidor,n))
    #problema pode fazer inicialização do n no script por fora?
#socket.create_server(addr, family= AF_INET, backlog = None, reuse_port = False, dualstack_ipv6 = False) # cria servidor, problema: faz tudo de uma vez só inicizaliza da o bind e faz o listen
# family AF_INET : ele trabalha com endereços ipv4
# backlog : serve para dar o numero de processos na fila ouvido pelo listen.
#reuse_port : serve para servidor multithread? : reusa mesmos dados do de host e porta pelo que entendi





def mensagens(servidor,n):
    i = 0
    request_counter =0
    grant_counter = 0
    release_counter = 0
    MSG_GRANT = 2
    MSG_RELEASE = 1


    while i != 1:
        conexao, endereco = servidor.accept() # aceita conexões
        data = socket.recv(4096) # pode ser que tenha que mudar
        tipo,pid = parse_msg(data.decode('utf-8')) # quebra a string em partes
       
        if tipo == 1: # verifica se é request
            Fila.append(pid)
            request_counter =+ 1

        elif tipo == 3:
            Fila.pop(pid)
            release_counter =+ 1
        elif  Fila.count != 0:
            if grant_counter == release_counter:
                servidor.sendall(MSG_GRANT)
            #libera da fila
 



def msgparser(data):
# ele vai recebe uma mensagem :
# ele vai separar o conteudo da mensagem
# então
    return



def parse_msg(raw: bytes):
    """Retorna (tipo, pid) ou (None, None)."""
    try:
        text = raw.decode('utf-8').strip()
        partes = text.split(SEP)
        return partes[0], partes[1]
    except Exception:
        return None, None


# envia grant assincrono    
def lastmsg():
