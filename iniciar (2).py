import subprocess, sys, os, time

# uso: python iniciar.py <n> <r> <k>
n = int(sys.argv[1])
r = sys.argv[2]
k = sys.argv[3]

if os.path.exists("resultado.txt"):
    os.remove("resultado.txt")

procs = []
for i in range(1, n + 1):
    p = subprocess.Popen([sys.executable, "proc.py", str(i), r, k])
    procs.append(p)

for p in procs:
    p.wait()

print(f"Pronto. Verifique resultado.txt — esperado {n*int(r)} linhas.")
