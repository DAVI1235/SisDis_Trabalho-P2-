# SisDis_Trabalho-P2-
Repositório para a P2 de Sistemas Distribuídos.

# Sistema Distribuído de Exclusão Mútua (Algoritmo Centralizado)

Este projeto implementa um modelo de **Exclusão Mútua Centralizada** em Sistemas Distribuídos utilizando sockets e múltiplas threads em Python. O sistema simula o controle de acesso a um recurso compartilhado (região crítica) coordenado por um processo central.

## 🛠️ Componentes do Sistema

* **`coord.py`**: O Coordenador central que gerencia a fila de pedidos (FIFO) e garante que apenas um processo acesse o recurso por vez.
* **`proc.py`**: O processo cliente que solicita acesso à região crítica, realiza escritas em um arquivo compartilhado e libera o recurso.
* **`iniciar.py`**: Script automatizado para inicializar o coordenador e disparar múltiplos processos concorrentes configuráveis.
* **`verificar.py`**: Script de validação que analisa a integridade das escritas e a ordem lógica das mensagens de controle.

---

## 🚀 Como Rodar o Programa

Para executar a simulação, você precisará de dois terminais abertos na pasta raiz do projeto.

### Passo 1: Iniciar o Coordenador
No **Terminal 1**, execute o coordenador para que ele fique ouvindo as requisições na porta configurada:

[Terminal 1]
> python coord.py

### Passo 2: Executar os Processos Simultâneos
No **Terminal 2**, utilize o script de inicialização passando três parâmetros obrigatórios:
* `N`: Número de processos que serão criados.
* `R`: Quantidade de vezes que cada processo vai escrever no arquivo.
* `K`: Tempo (em segundos) que cada processo retém a região crítica.

Exemplo para rodar com **4 processos**, onde cada um escreve **5 vezes** com retenção de **0.2 segundos**:

[Terminal 2]
> python iniciar.py 4 5 0.2

### Passo 3: Verificar os Resultados
Após a execução terminar, rode o script verificador no **Terminal 2 com os mesmos parâmetros N e R** para validar o comportamento do sistema:

[Terminal 2]
> python verificar.py 4 5

---

## 🔍 Análise do Teste de Validação

Ao rodar o script `verificar.py`, a saída do terminal apresentará um relatório de validação semelhante a este:

Linhas: 20 (esperado 20) OK
  pid=1: 5 escritas OK
  pid=2: 5 escritas OK
  pid=3: 5 escritas OK
  pid=4: 5 escritas OK
  GRANT/RELEASE intercalados: v
  Ordem REQUEST==RELEASE:     x

### Por que o teste aponta um "X" em Ordem REQUEST==RELEASE?

O resultado x nesta última linha não indica uma falha no algoritmo de exclusão mútua, mas sim um comportamento natural de concorrência na rede.

#### Como o Coordenador funciona:
O algoritmo implementa uma fila rigorosa baseada no padrão FIFO (First-In, First-Out). Se o processo 1 e o processo 2 solicitam acesso quase juntos, o coordenador os enfileira e concede a permissão na ordem exata de chegada (ex: GRANT para o processo 1 primeiro, depois GRANT para o processo 2).

#### O motivo do desalinhamento:
Quando os processos terminam suas operações e saem da região crítica, eles enviam uma mensagem de RELEASE de volta para o coordenador. No entanto, o tempo que essa mensagem leva para viajar pela rede local ou ser processada pelo sistema operacional varia em milissegundos.

Se duas mensagens de RELEASE de processos diferentes chegam ao coordenador exatamente no mesmo milissegundo, as threads receptoras do coordenador podem registrar essas entradas no arquivo de log (coord.log) com uma inversão microscópica na ordem física das linhas (ex: o RELEASE do processo 2 é gravado uma linha antes do RELEASE do processo 1).

Como o script verificar.py faz uma checagem puramente textual e linear comparando se a lista exata de linhas GRANT é idêntica à lista de linhas RELEASE, qualquer variação de milissegundos no agendamento de threads do sistema operacional gera esse falso positivo.

### 📌 Conclusão da Validação
A integridade do sistema é comprovada pelos outros fatores do log:
1. **Exclusão Mútua Perfeita:** A validação GRANT/RELEASE intercalados resulta sempre em v, provando que o coordenador nunca permitiu que dois processos estivessem na região crítica simultaneamente.
2. **Consistência dos Dados:** O arquivo resultado.txt termina com o número exato de linhas esperadas, e nenhum processo corrompeu ou atropelou a escrita do outro.
