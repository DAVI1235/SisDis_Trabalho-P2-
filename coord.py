import socket, threading, queue, datetime, sys
#queue para fila thread-safe de eventos
#datetime para timestamps no log
#sys para pegar argumentos da linha de comando


F = 10  # tamanho fixo de toda mensagem em bytes

def montar(tipo, pid):
    # tipo: "1"=REQUEST  "2"=GRANT  "3"=RELEASE  "0"=CONECTAR
    base = tipo + "|" + pid + "|"
    return (base + "0" * (F - len(base))).encode() #adiciona zeros a direita para completar F bytes

def desmontar(raw): #faz o inverso de montar, retornando tipo e pid
    partes = raw.decode().split("|")
    return partes[0], partes[1]   # tipo, pid
#recebe em bytes, transforma em string e corta ela utilizando o pipe como separador, retornando o tipo e o pid

# variaveis globais compartilhada entre todas as threads
fila      = []   # (pid, socket) aguardando GRANT
#Lista de tuplas (pid, conn) dos processos esperando para entrar rc
sockets   = {}  
#dicionario do pid para conexão para saber qual socket pertence a qual processo 
contagem  = {}   # pid -> vezes atendido
#dicionario  pid -> numero, quantas vzs cada processo foi atendido
lock      = threading.Lock()
#trava de exclusão mutua dentro do proprio coordenador, quando uma thread faz (with lock) as outras que tentam entrar naquel bloco ficam pausadas esperando
eventos   = queue.Queue()
#fila thread-safe. as thread de leitura jogam mensagens aqui com .put(), e a thread do algorithm pega com .get() 
parar     = threading.Event()
#flag que quando ativada com parar.set() sinaliza para todas as threads encerrarem

def log(direcao, tipo, pid):
#Registra cada mensagem enviada ou recebida, e pega o momneto atual para colocar no coord.log

    agora = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    linha = f"[{agora}] {direcao} tipo={tipo} pid={pid}"
    print(linha)
    open("coord.log", "a").write(linha + "\n")


def ler_processo(conn):
#roda uma thread dedicada para cada processo conectado, funciona como uma recepcionista, espera o cliente falar , traduz a mensagem e colocar em uma fila de eventos para o algoritmo processar, e ainda limpra a conexão quando o processo fecha a conexão
    while not parar.is_set(): #loop infinito até a flag, essa flag é ativada quando o coordenador é encerrado, e todas as threads param
        try:
            raw = conn.recv(F) #fica bloqueado esperando receber uma mensagem do processo de tamanho F bytes
            if not raw: #quando o processo fecha a conexão, raw fica vazio e a thread encerra
                break
            tipo, pid = desmontar(raw) #pega os 10 bytes recebidos e transforma em tipo e pid
            log("RECV", tipo, pid)
            eventos.put((tipo, pid, conn)) #joga na fila de eventos para a thread do algoritmo pegar e processar (LEMBRAR de colocar isso no relatorio (IMPORTANTE !!!))
            #funciona com uma tupla de tres informacoes, oque processar, quem e o processo qual e o canal de comunicacao com ele
        except:
            break


def aceitar(server):
    while not parar.is_set():
        try:
            server.settimeout(1) #para não ficar bloqueado esperando conexões, e poder encerrar quando a flag parar for ativada
            conn, _ = server.accept() 

            raw = conn.recv(F)
            tipo, pid = desmontar(raw)
            #assim que o processo se conecta, ele envia uma mensagem do tipo "0" = CONECTAR, com o pid do processo
            #NÃO chamamos log() aqui de propósito: tipo=0 é só apresentação/handshake, não é um evento do algoritmo de exclusão mútua,
            #então não deve aparecer nem no terminal nem no coord.log (só REQUEST=1, GRANT=2, RELEASE=3 devem aparecer)
            with lock: #lock para garantir que apenas uma thread acesse as variaveis globais de cada vez, evitando problemas de concorrencia
                sockets[pid] = conn #define o dicionario de sockets, associando o pid do processo com a conexão socket
                contagem[pid] = 0 #inicializa a contagem de atendimentos para o processo que acabou de se conectar
            # NÃO joga nos eventos — é só apresentação, não REQUEST
            threading.Thread(target=ler_processo, args=(conn,), daemon=True).start() #daemon=True garante que se fechar o programa principal do coordenador, todas as threads filhas também serão encerradas
            #cria uma thread para ficar lendo mensagens do processo conectado, e essa thread vai colocar as mensagens na fila de eventos para o algoritmo processar
        except socket.timeout:
            continue
        except:
            break


def algoritmo(): #responsavel por implementar o algoritmo de exclusão mutua centralizado, ele que decide quem tem o direito de acessar a regiao critica
    # OBS: não existe mais flag de "rc_livre". A própria fila é a fonte da verdade:
    # a CABEÇA da fila (fila[0]) é sempre quem está com a RC (ou quem acabou de receber o Grant).
    # Os demais elementos são quem ainda está esperando, na ordem de chegada.
    while not parar.is_set(): #loop que fica rodando continuamente para procesar os pedidos dos clientes, até que o administrador decida encerrar o programa
        try:
            tipo, pid, conn = eventos.get(timeout=0.5) 
            #vai ate a fila e retira o pedido mais antigo. desempacota as tres informacoes tipo ouqe o processor quer (1, 3), pid quem esta pedidno, conn o canal do socket para reponder o processo
            #se a fa de eventos estiver vazia(ngm pediu nada) o codigo não fica travado ali esperando para sempre ele espera por no maximo 0.5 segundos se nada aparecer nesse tempo ele desiste e joga um alarme chando queue.Empty
        except queue.Empty:
            continue

        if tipo == "1":  # REQUEST
            with lock:
                fila.append((pid, conn)) #o pedido sempre entra no fim da fila (igual ao Q.add do slide)
                eh_cabeca = fila[0][0] == pid #se ele caiu na cabeça da fila, é porque a fila estava vazia antes -> RC estava livre
            if eh_cabeca:
                conn.sendall(montar("2", pid)) #manda Grant direto, pois ele é o único/primeiro da fila
                log("SEND", "2", pid)
            # se não for cabeça, ele só fica esperando na fila até receber o Grant quando chegar sua vez (no RELEASE de quem está na frente)

        elif tipo == "3":  # RELEASE
            with lock:
                contagem[pid] += 1 #atualiza a contagem de atendimentos para o processo que acabou de liberar a rc
                if fila and fila[0][0] == pid: #remove da fila quem estava na RC (deve ser sempre a cabeça)
                    fila.pop(0)
                tem_prox = len(fila) > 0 #verifica se tem alguem esperando na fila
                if tem_prox:
                    prox_pid, prox_conn = fila[0] #cabeça da fila é o próximo a entrar -> NÃO remove ainda, só remove quando ELE der release
            if tem_prox:
                prox_conn.sendall(montar("2", prox_pid)) #envia grant para o proximo processo
                log("SEND", "2", prox_pid)


def main():
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8082 #configura a porta e cria o servidor

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", porta))
    server.listen(20)
    open("coord.log", "w").close() #serve apeans para limpar o log antigo toda vez que o programa começa do zero
    print(f"Coordenador na porta {porta}. Comandos: q=fila  c=contagem  e=encerrar")

    threading.Thread(target=aceitar,   args=(server,), daemon=True).start() #cria uma thread para ficar aceitando conexoes de clientes e vigiando a porta
    threading.Thread(target=algoritmo,               daemon=True).start() #criar outra thread para gerenciar quem entra e sai da rc
    #ambas tem daemon=True para garantir que se o programa principal do coordenador for encerrado, todas as threads filhas também serão encerradas

    if not sys.stdin.isatty():
        parar.wait()
        return

    while True:
        cmd = input("> ")
        if cmd == "q":
            with lock:
                print("Fila:", [p for p, _ in fila] if fila else "vazia") #exibe a fila de processos esperando para entrar na rc
        elif cmd == "c":
            with lock:
                print("Atendimentos:", contagem) #c mostra quantos acessos cada processo conseguiu fazer
        elif cmd == "e":
            parar.set()
            server.close()
            print("Encerrado.") #e termina oprograma e fechao  servidor 
            break

if __name__ == "__main__":
    main()
