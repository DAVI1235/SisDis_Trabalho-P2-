import subprocess, sys, os, time

# uso: python iniciar.py <n> <r> <k>
"""
quando rodar esse script, ele vai criar n processos, cada um com r repeticoes de entrar na rc, com k tempo dentro dela
"""
n = int(sys.argv[1])
r = sys.argv[2]
k = sys.argv[3]

if os.path.exists("resultado.txt"): #antes de comecar o teste verifica se o arquivo resultado.txt existe, se existir ele deleta para comecar do zero
    os.remove("resultado.txt")

procs = [] #dispara processos em massa
for i in range(1, n + 1):
    p = subprocess.Popen([sys.executable, "proc.py", str(i), r, k]) #dispara o processo proc.py passando como argumento o pid (i), a quantidade de vezes que ele vai tentar entrar na rc (r) e o tempo que ele vai ficar dentro da rc (k)
    procs.append(p) #quarda a referencia do processo disparado em uma lista 

for p in procs: 
    p.wait() #espera todos os processos terminarem antes de encerrar o script principal

print(f"Pronto. Verifique resultado.txt — esperado {n*int(r)} linhas.")
