import socket, threading, queue, datetime, sys

# ── protocolo ──────────────────────────────────────────────────────────────
F = 10  # tamanho fixo de toda mensagem em bytes

def montar(tipo, pid):
    # tipo: "1"=REQUEST  "2"=GRANT  "3"=RELEASE  "0"=CONECTAR
    base = tipo + "|" + pid + "|"
    return (base + "0" * (F - len(base))).encode()

def desmontar(raw):
    partes = raw.decode().split("|")
    return partes[0], partes[1]   # tipo, pid

# ── estado global ──────────────────────────────────────────────────────────
fila      = []   # (pid, socket) aguardando GRANT
sockets   = {}   # pid -> socket
contagem  = {}   # pid -> vezes atendido
lock      = threading.Lock()
eventos   = queue.Queue()
parar     = threading.Event()

def log(direcao, tipo, pid):
    agora = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    linha = f"[{agora}] {direcao} tipo={tipo} pid={pid}"
    print(linha)
    open("coord.log", "a").write(linha + "\n")

# ── lê mensagens de um processo e joga nos eventos ─────────────────────────
def ler_processo(conn):
    while not parar.is_set():
        try:
            raw = conn.recv(F)
            if not raw:
                break
            tipo, pid = desmontar(raw)
            log("RECV", tipo, pid)
            eventos.put((tipo, pid, conn))
        except:
            break

# ── aceita novas conexões ──────────────────────────────────────────────────
def aceitar(server):
    while not parar.is_set():
        try:
            server.settimeout(1)
            conn, _ = server.accept()
            # primeiro recv: mensagem "0|pid|..." só para registrar o processo
            raw = conn.recv(F)
            tipo, pid = desmontar(raw)
            log("RECV", tipo, pid)
            with lock:
                sockets[pid] = conn
                contagem[pid] = 0
            # NÃO joga nos eventos — é só apresentação, não REQUEST
            threading.Thread(target=ler_processo, args=(conn,), daemon=True).start()
        except socket.timeout:
            continue
        except:
            break

# ── algoritmo de exclusão mútua ────────────────────────────────────────────
def algoritmo():
    rc_livre = True
    while not parar.is_set():
        try:
            tipo, pid, conn = eventos.get(timeout=0.5)
        except queue.Empty:
            continue

        if tipo == "1":  # REQUEST
            with lock:
                fila.append((pid, conn))
            if rc_livre:
                rc_livre = False
                with lock:
                    prox_pid, prox_conn = fila.pop(0)
                prox_conn.sendall(montar("2", prox_pid))
                log("SEND", "2", prox_pid)

        elif tipo == "3":  # RELEASE
            with lock:
                contagem[pid] += 1
                tem_prox = len(fila) > 0
                if tem_prox:
                    prox_pid, prox_conn = fila.pop(0)
            if tem_prox:
                prox_conn.sendall(montar("2", prox_pid))
                log("SEND", "2", prox_pid)
            else:
                rc_livre = True

# ── interface do terminal ──────────────────────────────────────────────────
def main():
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8082

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", porta))
    server.listen(20)
    open("coord.log", "w").close()
    print(f"Coordenador na porta {porta}. Comandos: q=fila  c=contagem  e=encerrar")

    threading.Thread(target=aceitar,   args=(server,), daemon=True).start()
    threading.Thread(target=algoritmo,               daemon=True).start()

    if not sys.stdin.isatty():
        parar.wait()
        return

    while True:
        cmd = input("> ")
        if cmd == "q":
            with lock:
                print("Fila:", [p for p, _ in fila] if fila else "vazia")
        elif cmd == "c":
            with lock:
                print("Atendimentos:", contagem)
        elif cmd == "e":
            parar.set()
            server.close()
            print("Encerrado.")
            break

if __name__ == "__main__":
    main()
