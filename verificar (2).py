import sys
"""
Le restultados.txt e chege numero total de linhas, escritas por processo e se os timestamps só crescem  (dois processo na regiao critia ao mesmo
tempo gerariam timestamps fora de ordem) le coord.log e chega se GRANT E RELEASE estao sempre intercalador e se a ordem de quem entou na RC
e a mesma de quem saiu
"""
n, r = int(sys.argv[1]), int(sys.argv[2])


linhas = open("resultado.txt").readlines()
print(f"Linhas: {len(linhas)} (esperado {n*r})", "✅" if len(linhas)==n*r else "❌")

contagem = {}
for linha in linhas:
    pid = linha.split()[0]
    contagem[pid] = contagem.get(pid, 0) + 1

for pid, cnt in sorted(contagem.items()):
    print(f"  pid={pid}: {cnt} escritas", "✅" if cnt==r else "❌")


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
