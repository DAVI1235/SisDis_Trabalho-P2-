import socket, time, datetime, sys

F = 10

def montar(tipo, pid):
    base = tipo + "|" + pid + "|"
    return (base + "0" * (F - len(base))).encode()

def receber(sock):
    buf = b""
    while len(buf) < F:
        buf += sock.recv(F - len(buf))
    return buf[0:1].decode()   # retorna só o tipo

def main():
    pid   = sys.argv[1]
    r     = int(sys.argv[2])
    k     = float(sys.argv[3])
    host  = sys.argv[4] if len(sys.argv) > 4 else "localhost"
    porta = int(sys.argv[5]) if len(sys.argv) > 5 else 8082

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, porta))

    # apresenta-se ao coordenador com tipo "0" (não é REQUEST)
    sock.sendall(montar("0", pid))

    for i in range(r):
        sock.sendall(montar("1", pid))          # REQUEST
        print(f"pid={pid} REQUEST ({i+1}/{r})")

        receber(sock)                            # espera GRANT (bloqueia aqui)
        print(f"pid={pid} GRANT recebido")

        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open("resultado.txt", "a") as f:
            f.write(f"{pid} {agora}\n")
        time.sleep(k)

        sock.sendall(montar("3", pid))          # RELEASE
        print(f"pid={pid} RELEASE\n")

    sock.close()

if __name__ == "__main__":
    main()
