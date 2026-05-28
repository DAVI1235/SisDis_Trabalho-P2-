# thread interface for cordinator

import threading

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
                # deve ter um contador em um arraylist de inteiro com 0 inicialmente, e vai acrescentando a cada resposta, em uma função diferente, recebe como argumento o pid do processo e então faz o acrescimo
            case 3:
                print("encerrar")


def qt_vzs_proc_atendido(processo_id):
    Dicionario_Contador = {} # liga chave de contador com o n vezes processo chamado
    
    if  Dicionario_Contador.get(processo_id) == None: # testa para ver se elemento ja existe na lista
        Dicionario_Contador[processo_id] = 0 # adiciona um com chave igual associada a valor 0
    else: # processo novo.
        contador = Dicionario_Contador.get(processo_id) # get valor da chave processo_id
        contador += 1 # incrementa 1
        Dicionario_Contador[processo_id]= contador














