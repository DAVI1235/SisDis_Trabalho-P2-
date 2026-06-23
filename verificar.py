import sys
"""
Abre o resultado.txt e o coord.log e analisa matematicmante se o seu coordenador cometeu alguma falha de exclusao mutua
"""
n, r = int(sys.argv[1]), int(sys.argv[2]) #passa o numero de processo (n) e repeticoes (r) que usou no teste


linhas = open("resultado.txt").readlines() #le o arquivo onde os processos escreveram o chega se a quantidade total de linhas é exatamente n x r se o total bater ele exibe "ok", se tiver alguma coisa errada exibe "erro"
print(f"Linhas: {len(linhas)} (esperado {n*r})", "OK" if len(linhas)==n*r else "ERRO")



"""
cria um dicionario para contar quantas vzs cada pid escreveu individualmente no arquivo, no final, ele confere se cada um  dos processos conseguiu escrever exatamente r vezes , isso garante
que nenhum processo foi "esquecido" ou ignorado pelo coordenador
"""
contagem = {}  
for linha in linhas: # (as linhas de resultado.txt)
    pid = linha.split()[0]
    contagem[pid] = contagem.get(pid, 0) + 1

for pid, cnt in sorted(contagem.items()):
    print(f"  pid={pid}: {cnt} escritas", "OK" if cnt==r else "ERRO")


grants, releases = [], []
grant_ativo = False
erro_intercalado = False

for linha in open("coord.log"):
    p = linha.split()
    if len(p) < 4: continue
    direcao = p[1]
    tipo    = p[2].split("=")[1]
    pid     = p[3].split("=")[1]

    if direcao == "SEND" and tipo == "2":    # GRANT
        if grant_ativo:
            erro_intercalado = True
        grant_ativo = True
        grants.append(pid)
    elif direcao == "RECV" and tipo == "3":  # RELEASE
        grant_ativo = False
        releases.append(pid)

print("GRANT/RELEASE intercalados:", "v" if not erro_intercalado else "x")
print("Ordem REQUEST==RELEASE:    ", "v" if grants==releases else "x")
