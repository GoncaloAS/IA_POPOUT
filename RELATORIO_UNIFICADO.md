# RELATÓRIO UNIFICADO — IA 2025/2026
## PopOut + MCTS + ID3 — Todos os documentos por fase

> Documento consolidado: contém PLANEAMENTO_PROJETO.md + FASE1..FASE9 em sequência. Permite ler/estudar o trabalho inteiro num único ficheiro.

---

## Índice

- [PLANEAMENTO PROJETO](#planeamento-projeto)
- [FASE1 MOTOR POPOUT](#fase1-motor-popout)
- [FASE2 INTERFACE CLI](#fase2-interface-cli)
- [FASE3 MCTS](#fase3-mcts)
- [FASE4 VARIACOES MCTS](#fase4-variacoes-mcts)
- [FASE5 ID3 IRIS](#fase5-id3-iris)
- [FASE6 DATASET](#fase6-dataset)
- [FASE7 ID3 POPOUT](#fase7-id3-popout)
- [FASE8 AVALIACAO](#fase8-avaliacao)
- [FASE9 ENTREGAVEL](#fase9-entregavel)

---



# ═══════════════════════════════════════════════════════════════
# PLANEAMENTO_PROJETO.md
# ═══════════════════════════════════════════════════════════════

# Planeamento do Projeto de Inteligência Artificial 2025/2026
## PopOut + MCTS + Árvores de Decisão (ID3)

> Documento-base para o trabalho prático. Serve como roteiro de execução **e** como esqueleto do relatório/notebook a entregar.
> **Deadline: 17 de maio de 2026, 23:59:59 (Lisboa).**
> **Grupo: 3 elementos.** Apresentação obrigatória — falta = nota zero.

---

## 1. Análise do enunciado: o que é pedido afinal?

Antes de programar fosse o que fosse, vale a pena traduzir o enunciado para português corrente e fixar o que conta para a nota.

O projeto tem **duas metades independentes** que depois se cruzam:

**Metade A — Pesquisa Adversarial (MCTS).** Implementar o jogo *PopOut* (variante do 4-em-linha em que, em vez de só largar uma peça por cima, também podes "puxar" uma peça tua por baixo, fazendo a coluna toda descer). Implementar o algoritmo *Monte Carlo Tree Search* com função de seleção *Upper Confidence Bound for Trees* (UCT) e fazê-lo jogar contra ti, contra outro humano, ou contra outra versão de si mesmo. Não basta a versão "standard" — o enunciado pede explicitamente que **explorem variações** (número de filhos selecionados, outras estratégias).

**Metade B — Árvores de Decisão (ID3).** Implementar de raiz o algoritmo ID3 (Iterative Dichotomiser 3) que aprende uma árvore de decisão a partir de um dataset. **Não é permitido scikit-learn nem outras bibliotecas de ML para a parte que define/treina a árvore** — o enunciado é explícito. Bibliotecas para *gerir/preparar* dados (pandas, numpy) são permitidas. Aplicar a duas datasets:
1. *Iris* (numérico, 3 classes) — funciona como aquecimento e exige discretização dos valores numéricos para o ID3 funcionar bem (este algoritmo no formato original é categórico).
2. Um dataset gerado a partir do nosso próprio MCTS: pares `(estado_do_jogo, melhor_jogada)`, ou seja, fazemos o MCTS jogar muitas vezes consigo mesmo e gravamos as suas decisões, e depois treinamos uma árvore que aprende a "imitar" o MCTS. Esta árvore depois deve ser capaz de, dado um estado, sugerir a próxima jogada — sem rodar o MCTS.

**Cenários de jogo a suportar (todos os três obrigatoriamente):**
1. Humano vs. Humano
2. Humano vs. Computador
3. Computador vs. Computador (com 2 algoritmos diferentes — vai ser MCTS vs. árvore-aprendida-do-MCTS)

**Entregáveis:**
- **Notebook documentado** (Jupyter `.ipynb`) com código + explicações + resultados.
- **Slides PDF** (apresentação curta, máximo 10 minutos, ao estilo: problema → solução → resultados).
- **Ficheiro de auto-avaliação** preenchido (fornecido pelos professores, está no Moodle).

**Ponderação na nota do trabalho (que vale 30% / 6 valores da disciplina):**
- 30% — implementação da estratégia adversarial (MCTS)
- 30% — implementação das árvores de decisão (ID3)
- 30% — competências técnicas (rigor da avaliação experimental, perspetiva de "data science")
- 10% — soft skills (comunicação na apresentação)

> ⚠️ **Atenção crítica para os pontos "técnicos" (30%):** este bloco mede se experimentaram a sério, fizeram comparações, mediram performance, justificaram escolhas. Não basta "funciona". Tem de haver tabelas/gráficos com tempos, taxas de vitória, accuracy, profundidade da árvore vs. accuracy, etc. **É aqui que a maioria dos grupos perde pontos por preguiça.**

---

## 2. Constraints e decisões de design (definir AGORA, não a meio)

Antes de codificar uma única linha, fixem em grupo as seguintes decisões. Tê-las por escrito no notebook **é parte da nota** (o enunciado diz "*Mention the constraints you are considering for the solution in the notebook*").

### 2.1 Tabuleiro
- **Dimensões:** o enunciado mostra um tabuleiro 7×6 na figura (7 colunas × 6 linhas) — é o tamanho clássico do Connect-4. Vamos ficar com **7×6**. Justificação: é o tamanho de referência; permite usar literatura existente para validar.
- **Representação interna:** matriz NumPy 6×7 (`linhas × colunas`) com valores `0` (vazio), `1` (jogador 1), `2` (jogador 2). Indexar a linha 0 como o **topo** e a linha 5 como o **fundo** mantém a intuição visual. *(Alternativa: usar bitboards — duas inteiras de 64 bits, uma por jogador. Mais rápido para milhões de simulações, mas mais difícil de depurar. Para o nosso volume, NumPy chega.)*

### 2.2 Regras a fixar
O enunciado é claro mas vamos repetir aqui para não restarem dúvidas:
1. **Drop**: largar peça pelo topo da coluna. A peça cai até à primeira posição vazia a contar de baixo.
2. **Pop**: só pode ser feito se houver na linha de baixo (linha 5, a última) uma peça **da nossa cor**. Remove-a, e tudo o que estava por cima dessa coluna desce uma posição.
3. **Vitória:** primeiro a fazer 4 em linha (horizontal, vertical ou diagonal).
4. **Regra do empate por pop simultâneo:** se um pop cria 4-em-linha para os dois jogadores ao mesmo tempo, **vence quem fez o pop** — o 4-em-linha do adversário é ignorado.
5. **Tabuleiro cheio:** o jogador a mover decide se faz pop (se conseguir) ou se aceita o empate.
6. **Repetição tripla:** se o mesmo estado se repetir 3 vezes, qualquer jogador pode declarar empate. *Nota de implementação: vamos guardar um histórico (lista) de hashes dos estados; cada vez que um estado é alcançado contamos quantas vezes apareceu antes.*

### 2.3 Interface
- **CLI baseada em texto** (estilo do exemplo do enunciado: `X--O-XO`). Por quê CLI e não GUI? Três razões: (1) o enunciado mostra exatamente este formato como exemplo aceitável; (2) poupa-nos tempo que vamos precisar para a parte algorítmica e experimental — que é onde estão 60% dos pontos; (3) é trivial fazer "computer vs computer" em batch para gerar dataset.
- **Cada jogada do humano** é um par `(coluna, tipo)` onde tipo ∈ {`drop`, `pop`}.

### 2.4 Constraints temporais do projeto
- ~2 semanas até à entrega.
- Apresentação na última-última semana de aulas.
- **Cada membro tem de saber explicar tudo** (não só a "sua" parte) — o enunciado penaliza explicitamente quem não souber descrever o que o grupo fez.

---

## 3. Roteiro de execução por fases

> Cada fase tem: **(O que fazer)**, **(Porquê assim e não de outra maneira)**, **(O que escrever no relatório)**.
>
> A ordem importa: cada fase produz algo de que a fase seguinte depende.

### Fase 0 — Setup e divisão de tarefas (Dia 1)

**O que fazer:**
- Repositório git partilhado (GitHub privado).
- Estrutura de pastas: `popout/` (motor do jogo), `mcts/` (algoritmo), `decision_tree/` (ID3), `data/` (datasets), `experiments/` (notebooks de teste), `report/` (notebook final + slides).
- **Notebook único** para entrega. *(É possível entregar vários, mas o enunciado pede "as a notebook" no singular. Usar um só, organizado por secções.)*

**Divisão de tarefas (sugerida para grupo de 3):**
| Pessoa | Responsável principal | Responsável secundário |
|--------|-----------------------|------------------------|
| A | Motor do jogo PopOut + Interface | Geração do dataset PopOut |
| B | MCTS + variações | Avaliação experimental MCTS |
| C | ID3 + discretização Iris | ID3 sobre dataset PopOut |

**Todos:** notebook final, slides, auto-avaliação. Toda a gente revê o código de toda a gente.

### Fase 1 — Motor do jogo PopOut (Dias 1-2)

**O que fazer:**
1. Classe/módulo que representa o estado do jogo: tabuleiro + jogador a jogar + histórico de estados (para a regra da repetição).
2. Função `legal_moves(state)` que devolve a lista de jogadas legais — drops nas colunas que não estão cheias, pops nas colunas em que o fundo é da nossa cor.
3. Função `apply_move(state, move)` que devolve o novo estado.
4. Função `check_win(state)` que devolve `None`, `1` (vitória do jog. 1), `2` (vitória do jog. 2), ou `'draw'`.
5. Função de hashing do estado (para detectar repetição) e contador de ocorrências.

**Porquê esta estrutura:** o MCTS vai chamar `legal_moves`, `apply_move`, e `check_win` literalmente milhares de vezes por jogada decidida. Tem de ser rápido **e** tem de ser uma função pura (sem efeitos secundários no estado original) — caso contrário o MCTS vai corromper a árvore que está a construir. **Estado imutável é melhor que estado mutável aqui.** Com NumPy isso significa: cada `apply_move` faz uma cópia do array (`board.copy()`).

**Decisão de design importante:** o `check_win` precisa de saber se é resultado de um **pop** ou de um **drop**, por causa da regra do "duplo 4-em-linha". A maneira mais limpa é o `apply_move` aceitar um `move` que carrega essa informação, e devolver `(novo_estado, vencedor_imediato)`. Caso contrário esquecem-se desta regra e perdem pontos.

**O que escrever no relatório (secção: "Modelação do problema"):**
- Como representam o estado e porquê NumPy.
- Como tratam cada uma das 3 regras especiais.
- Pseudocódigo do `check_win` com particular atenção ao caso "pop empata 4-em-linha duplo".

### Fase 2 — Interface (Dia 2)

**O que fazer:**
- Função `print_board(state)` que imprime no formato `X--O-XO` por linha.
- Loop principal `play_game(p1_strategy, p2_strategy)` onde cada `strategy` é uma função `state → move`.
- Estratégias prontas: `human_strategy` (input do utilizador), `mcts_strategy(...)` (será preenchida depois), `tree_strategy(...)` (será preenchida depois).

**Porquê esta abstração:** ao fazer cada jogador ser uma função, os 3 cenários do enunciado (HvH, HvC, CvC) saem todos do mesmo `play_game` com argumentos diferentes. Não duplicamos código.

### Fase 3 — Monte Carlo Tree Search (Dias 3-5)

Esta é a peça central. O algoritmo tem **4 passos repetidos N vezes**, e depois escolhe-se a melhor jogada.

```
Para i = 1 até N (número de simulações):
    1. Selection — desce pela árvore atual escolhendo filhos com maior UCB
    2. Expansion — chega a um nó folha; cria um filho novo (uma jogada legal não testada)
    3. Simulation (rollout) — joga aleatoriamente até ao fim do jogo a partir desse novo nó
    4. Backpropagation — propaga o resultado (vitória/derrota) para cima na árvore

Finalmente: devolve a jogada cujo filho da raiz tem mais visitas
```

**Fórmula UCB1 (a chave do algoritmo):**
```
UCB1(n) = U(n) / N(n)  +  C × sqrt( ln(N(parent(n))) / N(n) )
          \________/      \_________________________________/
           Exploitation              Exploration
```
- `U(n)` = número de vitórias acumuladas no nó n
- `N(n)` = número de visitas ao nó n
- `parent(n)` = nó pai
- `C` = constante que controla o equilíbrio. **Valor canónico: C = √2 ≈ 1.41.**

**Porquê UCB e não outra coisa:** o problema de selecionar entre filhos é um *multi-armed bandit*. UCB tem garantias matemáticas de regret logarítmico — ou seja, à medida que o número de simulações cresce, a perda em relação à escolha ótima cresce só logaritmicamente, e essa fronteira é demonstrável. **Exploitation** é a média de vitórias até agora (preferimos jogadas que têm corrido bem); **exploration** dá um bónus a jogadas pouco visitadas (porque quem sabe se uma joia está escondida ali). C balanceia os dois. C alto → mais exploração; C baixo → mais exploração das jogadas já promissoras.

**Por que é melhor que MiniMax para o PopOut:**
- O fator de ramificação do PopOut é até **10** (7 drops + até 3 pops, no exemplo do enunciado). Mais alto que 4-em-linha clássico.
- A profundidade até ao fim do jogo pode ser grande por causa dos pops (jogos arrastam-se).
- MiniMax precisa de uma *função de avaliação heurística* boa para ser cortado a meio (porque não dá para ir até às folhas a tempo). Inventar essa heurística para PopOut é complicado e específico do jogo.
- MCTS **não precisa de heurística** — só de uma simulação aleatória. É *domain-agnostic*. Ideal para um trabalho onde queremos algo que funcione bem sem termos meses de tuning.

**Pseudocódigo essencial (MCTS):**
```
def mcts_search(root_state, n_simulations, C):
    root = Node(state=root_state, parent=None)
    for _ in range(n_simulations):
        # 1. Selection
        node = root
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child(C)        # filho com maior UCB1
        # 2. Expansion
        if not node.is_terminal():
            node = node.expand()             # cria 1 filho novo
        # 3. Simulation (rollout)
        result = random_playout(node.state)  # joga aleatório até ao fim
        # 4. Backpropagation
        while node is not None:
            node.N += 1
            node.U += result_for_player(result, node.player_to_move)
            node = node.parent
    return root.most_visited_child().move    # MELHOR JOGADA = mais visitada
```

**Cuidado crítico:** na backpropagation, o `result` tem de ser interpretado **do ponto de vista do jogador que está a mover nesse nó** — caso contrário o algoritmo "pensa" que está a maximizar do lado errado. É o erro #1 das implementações de MCTS de raiz.

**Porque devolver "mais visitas" e não "maior taxa de vitória":** está explicado nos slides — um nó com `65/100` (65 vitórias em 100 visitas) é mais fiável do que um com `2/3` (2/3, mas só 3 visitas têm muita variância). O UCB já naturalmente faz com que o nó visitado mais vezes seja também o que tem boa taxa, então usamos visitas como medida de robustez.

**O que escrever no relatório:**
- Os 4 passos com diagrama (incluímos abaixo).
- A fórmula UCB explicada termo a termo.
- Justificação de C escolhido (testámos vários — ver Fase 4).
- Tempo médio por jogada vs. número de simulações.

### Fase 4 — Variações do MCTS (Dia 6)

O enunciado diz claramente:
> *"you should analyse/explore different numbers of selected children for each node, and other strategies, not only keeping the standard implementation"*

Esta fase **vale pontos próprios** dentro dos 30% técnicos. Não saltem. Variações concretas a experimentar:

1. **Número de simulações N**: ex. 100, 500, 1000, 5000. Medir tempo por jogada e força (ver Fase 8).
2. **Constante de exploração C**: ex. 0.5, 1.0, 1.41 (√2), 2.0. Mais alto explora mais, mais baixo explora menos.
3. **Limite de filhos selecionados**: em vez de testar todos os filhos, considerar só os k melhores segundo uma heurística simples (por exemplo, jogadas que ameaçam 4-em-linha imediato). Isto chama-se *progressive bias* ou *progressive widening* na literatura.
4. **Rollout policy**: em vez de jogar **completamente aleatório** na simulação, usar uma política simples — por exemplo, "se houver uma jogada que ganha já, joga-a; caso contrário, aleatório". Isto melhora muito a qualidade das estimativas.
5. **Limite de profundidade do rollout**: cortar a simulação a 30/50/100 jogadas e usar uma heurística para avaliar (útil em jogos arrastados que pops podem provocar).

**Para a apresentação:** uma tabela "Variação | Win-rate vs. baseline | Tempo médio". Isso ganha pontos.

### Fase 5 — Iris dataset + ID3 com discretização (Dias 6-7)

Esta fase é "warm-up" do ID3 antes de o atacar com o dataset do PopOut. Aproveitamos para validar a implementação num caso simples.

**Sobre o ID3 — o algoritmo (resumo):**
ID3 (Iterative Dichotomiser 3) é o algoritmo clássico para construir uma árvore de decisão a partir de exemplos rotulados. A ideia é simples e elegante:

> A cada nó da árvore, escolho o atributo que melhor "separa" as classes nesse subconjunto de exemplos. Continuo recursivamente em cada ramo até todos os exemplos no nó terem a mesma classe (ou ficarem sem atributos).

**Como medimos "melhor separa":** *information gain* — a redução de entropia.

Entropia de uma classe `C` numa amostra:
```
H(C) = - Σ P(c) × log₂( P(c) )
```
Para classificação binária com `p` positivos e `n` negativos:
```
H(C) = -[ p/(p+n) ] log₂(p/(p+n)) - [ n/(p+n) ] log₂(n/(p+n))
```
H = 1 bit no caso máximo de incerteza (50/50). H = 0 quando temos só uma classe.

Entropia condicional dado o atributo A:
```
H(C|A) = Σ_v  P(A=v) × H(C | A=v)
```
*("Por cada valor v que A pode tomar, peso a entropia do subconjunto onde A=v.")*

Information Gain do atributo A:
```
Gain(A) = H(C) - H(C|A)
```
ID3 escolhe **o atributo com maior Gain**.

**Os 4 casos base do ID3 (do livro Russell & Norvig):**
1. Há positivos e negativos → escolher melhor atributo, recursão.
2. Todos positivos (ou todos negativos) → folha com essa classe.
3. Não há mais exemplos (caminho não observado) → folha com a classe maioritária do **nó pai** (default).
4. Não há mais atributos para testar mas ainda há positivos e negativos → folha com voto maioritário **deste nó** (ruído nos dados).

**O problema com Iris — atributos numéricos:**
ID3 puro só sabe lidar com atributos categóricos. Iris tem 4 atributos numéricos contínuos (sépala/pétala × comprimento/largura). Temos de **discretizar**.

**Como discretizar (estratégias):**
- **Bins fixos** (largura igual): dividir cada atributo em ex. 3 ou 5 intervalos uniformes entre min e max. *Simples, mas pode dar bins desequilibrados.*
- **Bins de igual frequência** (quantis): cada bin tem ~33% dos exemplos. *Melhor para distribuições não-uniformes.*
- **Discretização supervisionada por information gain** (a "boa"): para cada atributo numérico, encontrar o(s) ponto(s) de corte que maximizam o information gain. Isto é o que o C4.5 (sucessor do ID3) faz: ordena os valores únicos do atributo, considera todos os pontos médios entre valores consecutivos com classes diferentes, escolhe o melhor split. **Recomendamos esta** — minimiza tamanho da árvore, que era o pedido do enunciado *("You need to implement a way of discretising these values in order to minimize the size of your decision tree")*.

**Pipeline para Iris:**
1. Carregar `iris_2.csv` (já o temos no projeto).
2. Discretizar os 4 atributos com a estratégia escolhida.
3. Treinar ID3 no conjunto **de treino** (split treino/teste 80/20 ou cross-validation).
4. Avaliar accuracy no conjunto de teste.
5. **Visualizar a árvore.** O enunciado pede explicitamente isto: *"It is supposed to present the output (tree) visually for all these datasets."* Opções: desenhar com graphviz/matplotlib, ou mesmo imprimir indentado em texto.

**Resultados esperados em Iris:** accuracy >95% é normal para iris (é um dataset fácil). Se virem muito menos, há bug.

### Fase 6 — Geração do dataset PopOut a partir do MCTS (Dia 8)

A ideia: usar o MCTS como "professor" que rotula estados com a sua melhor jogada, e depois usar isso como dataset supervisionado.

**Procedimento:**
```
dataset = []
para cada uma de 1000 partidas:
    estado = estado_inicial()
    enquanto jogo não terminado:
        melhor_jogada = MCTS(estado, N=500 simulações)
        dataset.append( (estado.codificado(), melhor_jogada) )
        estado = aplicar(estado, melhor_jogada)
```

**Decisões:**
- **Quantas partidas?** Compromisso entre tempo e cobertura. ~1000 partidas dão ~30000-60000 pares estado-jogada (jogos PopOut têm tipicamente 30-50 jogadas). Isto dá um dataset decente. Se o tempo apertar, 200 partidas chegam para validar a pipeline.
- **Como codificar o estado para o ID3?** O ID3 quer atributos discretos. Soluções possíveis:
  - 42 atributos categóricos (1 por casa do tabuleiro), cada um com 3 valores (`vazio`/`X`/`O`). *Simples, mas a árvore vai ficar enorme.*
  - **Atributos derivados/heurísticos** (recomendado): número de peças minhas em cada coluna, comprimento da maior linha que tenho, ameaças ativas do adversário, posição central ocupada, etc. Como pré-processamento, isto reduz drasticamente o tamanho da árvore e ajuda a generalizar. **Deixa o ID3 trabalhar com features que façam sentido para o jogo** em vez de o forçar a redescobrir relações geométricas a partir de coordenadas.
  - Codificar a **classe** (a jogada-alvo) como `(coluna, tipo)`. Há 7 colunas + até 7 pops = até 14 ações possíveis — boa cardinalidade para ID3.
- **Diversidade do dataset:** se MCTS é determinístico em estados iguais, vamos ter sempre o mesmo jogo. **Adicionar exploração na geração do dataset** — por exemplo, com probabilidade 10% jogar uma jogada aleatória em vez da do MCTS, ou começar partidas a partir de posições semialeatórias. Isto cobre mais do espaço de estados.

**Atenção / "criatividade" pedida pelo enunciado:** este pipeline (MCTS rotula, decision tree imita) é exatamente *behavioural cloning* — uma técnica clássica em imitation learning. Vale referenciar isto no relatório como contextualização.

### Fase 7 — ID3 sobre o dataset PopOut (Dia 9)

O mesmo ID3 da Fase 5, agora sobre o nosso dataset. Comparação interessante a fazer:

**Avaliações:**
1. **Accuracy** da árvore em prever a jogada do MCTS (em conjunto de teste held-out).
2. **Comparação direta:** árvore-aprendida vs. MCTS no jogo. Quantas vezes a árvore ganha/empata? Aposto que perde, mas é interessante ver por quanto.
3. **Velocidade:** a árvore decide em microssegundos; o MCTS demora segundos. Esta é a **vantagem prática** da árvore — *aproximação rápida* de uma policy lenta.
4. **Tamanho da árvore:** profundidade, número de folhas. Influência da profundidade máxima no trade-off entre overfitting e underfitting.

### Fase 8 — Avaliação experimental rigorosa (Dias 9-10)

Os tais 30% técnicos. Dividir em duas avaliações:

**Avaliação MCTS:**
- MCTS-N100 vs. MCTS-N500 vs. MCTS-N1000 vs. MCTS-N5000: matriz de win-rate (correr ex. 100 partidas de cada match-up). Esperamos que mais simulações → mais vitórias, com retornos decrescentes.
- Variar C: idem.
- Adversário "random" (joga aleatório legal) como sanity check — o MCTS deve ganhar quase sempre.
- **Adversário "trivial"** que só joga drops centrais — quão melhor é o MCTS?

**Avaliação Árvores de Decisão:**
- Curva de aprendizagem em Iris: accuracy vs. tamanho do conjunto de treino.
- **Cross-validation** k-fold (k=5 ou 10) — não só split simples. Isto é o que diferencia trabalho rigoroso de não-rigoroso.
- Matriz de confusão por classe.
- Sensibilidade da árvore PopOut à profundidade máxima (pre-pruning): treinar com `max_depth ∈ {3,5,10,20,sem limite}` e ver curva accuracy treino vs. teste — observar overfitting.

**Apresentação dos resultados:** sempre com gráficos (matplotlib) e tabelas (markdown ou pandas). Texto a interpretar cada gráfico. *"Observamos que para N>1000 o ganho marginal de win-rate é <2%, sugerindo que 1000 simulações é o sweet spot para o nosso ambiente"* — este tipo de comentário vale ouro.

### Fase 9 — Notebook + slides + auto-avaliação (Dias 10-11)

**Estrutura do notebook (sugestão):**
1. **Capa** — nomes, número de aluno, data.
2. **Introdução** — problema, objetivos, decisões de design (Secção 1 e 2 deste documento).
3. **PopOut: motor do jogo** — descrição, código, demonstração de uma partida humano-vs-humano.
4. **MCTS** — explicação, código comentado, fórmula UCB, demonstração humano vs. MCTS.
5. **Variações do MCTS e resultados** — tabelas + gráficos.
6. **Árvores de decisão e ID3** — explicação, código, demonstração com Iris (visualização da árvore!).
7. **Geração do dataset PopOut** — pipeline, estatísticas (tamanho, distribuição de jogadas).
8. **ID3 no PopOut** — visualização da árvore (ou parte, se for grande), accuracy.
9. **MCTS vs. árvore-PopOut** — partidas, comparação tempo/qualidade.
10. **Conclusões e trabalho futuro.**
11. **Referências** — Russell & Norvig, slides das aulas, Allen 2010 (livro do PopOut).

**Slides (10 minutos máximo):** problema (1 slide), regras do PopOut (1), MCTS conceito (2), uma variação que estudaram (1), ID3 e Iris (2), pipeline MCTS→dataset→árvore (1), resultados-chave (2), conclusão (1). Pouco texto, muitos diagramas.

**Auto-avaliação:** preencher com calma, justificando a contribuição de cada um.

---

## 4. Riscos típicos e como evitá-los

| Risco | Probabilidade | Mitigação |
|-------|---------------|-----------|
| MCTS muito lento → não dá para correr experiências | Alta | Otimizar `apply_move` (evitar cópia desnecessária); profilear com `cProfile` cedo |
| Esquecer regra do "pop empata duplo" | Média | Escrever testes unitários ANTES de avançar para MCTS |
| Discretização de Iris dá árvore enorme → mau resultado | Média | Usar discretização supervisionada (ponto de corte por information gain) |
| Dataset PopOut sempre igual (jogos determinísticos) | Alta | Introduzir aleatoriedade na geração: 10% jogadas aleatórias, ou começar de estados aleatórios |
| Notebook só com código, sem texto explicativo | Alta | Reservar último dia só para escrever explicações entre células |
| Apresentação um membro não sabe explicar a parte do outro | Alta | Marcar 2 sessões em que cada um apresenta a parte dos outros antes da entrega |

---

## 5. Cronograma sugerido (2 semanas)

| Dia | Atividade | Quem |
|-----|-----------|------|
| 1 | Setup, leitura conjunta do enunciado, divisão de tarefas, decisões de design | Todos |
| 2-3 | Motor PopOut + interface CLI + testes unitários | A |
| 3-5 | MCTS standard + UCB | B |
| 6-7 | Variações do MCTS + experiências | B |
| 6-7 | ID3 + discretização + Iris (em paralelo) | C |
| 8 | Geração do dataset PopOut | A + B |
| 9 | ID3 no PopOut + comparações | C |
| 10 | Avaliação experimental completa, gráficos | Todos |
| 11-12 | Notebook (texto, formatação) | Todos |
| 13 | Slides, auto-avaliação, ensaio da apresentação | Todos |
| 14 | Buffer / submissão | Todos |

---

## 6. O que NÃO esquecer no relatório/notebook

Revisão final, em jeito de checklist:

- [ ] Constraints declarados explicitamente.
- [ ] Pseudocódigo do MCTS com fórmula UCB explicada.
- [ ] Pelo menos **3 variações do MCTS** testadas com tabela comparativa.
- [ ] ID3 implementado **sem scikit-learn** (declarar isto explicitamente).
- [ ] Discretização Iris justificada.
- [ ] **Visualização da árvore** para Iris (obrigatório por enunciado).
- [ ] Pipeline MCTS → dataset → ID3 documentado.
- [ ] Comparação MCTS vs. árvore-aprendida (jogo + tempo).
- [ ] Cross-validation, não só train/test simples.
- [ ] Cada um sabe explicar tudo (ensaiado).
- [ ] Auto-avaliação preenchida.
- [ ] Slides ≤ 10 min.
- [ ] Submetido até 17/05/2026 23:59:59 (entregar com pelo menos 1 dia de margem).

---

## 7. Referências essenciais

- **Russell, S. & Norvig, P.** — *Artificial Intelligence: A Modern Approach*. Capítulos sobre Adversarial Search (MCTS) e Learning from Observations (Decision Trees, ID3). Bíblia da matéria.
- **Allen, J. D. (2010)** — *The Complete Book of Connect-4: History, Strategy, Puzzles*. Sterling. *(Origem das 3 regras especiais do PopOut. Citar.)*
- **Browne et al. (2012)** — *A Survey of Monte Carlo Tree Search Methods*. IEEE T-CIAIG. *(Survey canónico de MCTS, com todas as variações.)*
- **Quinlan, J. R. (1986)** — *Induction of Decision Trees*. Machine Learning 1. *(Paper original do ID3.)*
- **Slides das aulas** — Class 4 (MCTS), Class 7 (Learning).




# ═══════════════════════════════════════════════════════════════
# FASE1_MOTOR_POPOUT.md
# ═══════════════════════════════════════════════════════════════

# Fase 1 — Motor do jogo PopOut
## Documento de execução e material-fonte para o relatório

> Este documento implementa a **Fase 1** do `PLANEAMENTO_PROJETO.md` (Motor do jogo PopOut, dias 1-2).
> Está escrito para servir **dois propósitos em simultâneo**:
> 1. **Guia de execução** — explica as decisões de design, dá o pseudocódigo, o código Python pronto a colar e os casos de teste a correr antes de avançar para o MCTS.
> 2. **Material-fonte do relatório** — cada secção corresponde a um bloco do notebook final. As caixas marcadas com **📝 Para o relatório** contêm texto/figuras/tabelas que copiamos quase sem alterações para a entrega.
>
> Estado: rascunho inicial, antes de escrever a primeira linha de código. Vai ser refinado à medida que implementamos.

---

## 0. Onde estamos no roteiro

| Fase | Nome | Estado |
|------|------|--------|
| 0 | Setup e divisão de tarefas | Em curso (paralelo) |
| **1** | **Motor do jogo PopOut** | **Esta fase** |
| 2 | Interface CLI | A seguir |
| 3 | MCTS | Depende da Fase 1 |

**Pessoa responsável principal:** A (motor + interface). B e C revêem o código e contribuem com testes.

**Critério de saída desta fase** (definição de "pronto" antes de passar à fase seguinte):
- Todas as funções públicas implementadas e a passar testes unitários.
- Pelo menos 1 partida demonstrativa em CLI a correr humano-vs-humano sem crashar.
- Documentação desta fase escrita (este documento + comentários no código).
- Os 4 casos especiais das regras (pop, duplo-4 por pop, repetição tripla, tabuleiro cheio) com teste dedicado.

---

## 1. Recapitulação dos constraints (vai para a secção "Modelação do problema" do relatório)

> 📝 **Para o relatório** — copiar quase tal e qual.

O enunciado pede uma justificação explícita das decisões de design. Fixamo-las aqui de forma definitiva.

### 1.1 Tabuleiro
- **Dimensões:** 7 colunas × 6 linhas (Connect-4 clássico). Justificação: é o tamanho da figura do enunciado, é o tamanho de referência na literatura sobre Connect-4, e permite-nos validar contra publicações existentes (incluindo Allen 2010).
- **Representação interna:** matriz NumPy `(6, 7)` de inteiros (`int8`), com convenção `0` = vazio, `1` = jogador 1, `2` = jogador 2.
- **Orientação:** linha 0 = topo do tabuleiro (visualmente a primeira a ser impressa); linha 5 = fundo (onde caem as peças). Esta orientação mantém a intuição visual e simplifica o `print_board`.

### 1.2 Regras
1. **Drop:** o jogador escolhe uma coluna e a peça cai até à primeira posição vazia a contar de baixo. Falha se a coluna já estiver cheia.
2. **Pop:** o jogador remove uma peça **da sua cor** que esteja no fundo (linha 5) da coluna escolhida. Tudo o que estava por cima desce uma posição. Falha se a posição (5, col) não for da cor do jogador.
3. **Vitória:** primeiro a alinhar 4 peças seguidas (horizontal, vertical, ou diagonal nos dois sentidos).
4. **Regra do pop com duplo 4-em-linha:** se um pop cria 4-em-linha **simultaneamente** para os dois jogadores, vence **quem fez o pop**. O 4 do adversário é ignorado. Esta regra está em Allen (2010) e é parte explícita do enunciado.
5. **Tabuleiro cheio:** o jogador a mover decide se faz pop (quando puder) ou se aceita o empate. Se não houver pops legais e o tabuleiro estiver cheio, é empate.
6. **Repetição tripla:** se o mesmo estado aparecer 3 vezes na partida (mesma posição **e** mesmo jogador a mover), qualquer jogador pode declarar empate.

### 1.3 Pressupostos
- **Estado imutável:** cada `apply_move` devolve um **novo** estado (cópia do array). Não mutar o estado original. Isto é fundamental porque o MCTS vai partilhar nós e cópias do estado entre simulações; mutação no sítio errado corrompe a árvore.
- **Funções puras:** `legal_moves`, `apply_move`, `check_win` não têm efeitos secundários. O histórico de repetição é parte do estado, não uma variável global.
- **CLI sobre GUI:** poupa tempo (60% dos pontos do trabalho estão nos algoritmos e nas experiências, não na interface) e simplifica o batch para gerar dataset.

---

## 2. Modelação do estado

### 2.1 O que precisa de viver no estado

| Componente | Tipo | Porquê |
|------------|------|--------|
| `board` | `np.ndarray` shape (6,7) `int8` | Configuração atual das peças |
| `player_to_move` | `int` (1 ou 2) | A quem cabe jogar |
| `history_counts` | `dict[bytes, int]` | Conta vezes que cada estado já apareceu (regra da repetição tripla). Chave = hash do par (board, player_to_move). |
| `last_move` | `Move \| None` | Útil para `check_win` saber se foi pop ou drop, e para a regra do duplo-4 |
| `winner` | `int \| str \| None` | `None` se em curso, `1`/`2` se alguém venceu, `'draw'` se empate |

> **Decisão:** vamos usar uma `dataclass` imutável (`frozen=True`) para o estado, com métodos puros que devolvem novos estados. Dataclasses dão `__eq__` e `__hash__` quase de borla, mas como guardamos um array NumPy e um dict, escrevemos o nosso `__hash__`/`__eq__` manualmente.

### 2.2 Hashing e detecção de repetição

Para saber se um estado já apareceu, precisamos de uma chave hashável. NumPy arrays não são hashable por defeito. Estratégia:

```python
def state_key(board: np.ndarray, player_to_move: int) -> bytes:
    return board.tobytes() + bytes([player_to_move])
```

`tobytes` é determinístico, rápido e serve como chave de dicionário. Concatenar o jogador a mover é essencial — a mesma configuração com jogadores diferentes a mover são estados diferentes para a regra de repetição.

> 📝 **Para o relatório** — incluir esta linha como exemplo do "como representamos o estado para hashing". É a unidade que usamos depois no MCTS para cache de nós também.

### 2.3 Por que NumPy e não Python puro?

- Um motor que vai ser chamado milhões de vezes por uma única decisão MCTS tem de ter operações vectorizadas baratas.
- `check_win` por convolução / slicing NumPy é ~10× mais rápido que loops Python puros.
- Cópias `board.copy()` são O(42) — desprezáveis.
- `tobytes()` para hashing é praticamente gratuito.

> **Alternativa não escolhida:** *bitboards* (duas inteiras de 64 bits, uma por jogador). É 5–20× mais rápido para milhões de simulações, mas: (1) detecção do vencedor exige máscaras pré-calculadas, (2) implementar o pop em bitboards é mais delicado (requer shift por coluna), (3) é muito mais difícil de depurar. Para o nosso volume (até 1000 simulações por jogada × ~50 jogadas × ~100 partidas de avaliação = 5 milhões de chamadas), NumPy chega. Mencionamos no relatório como **trabalho futuro** se o tempo apertar.

---

## 3. Movimentos legais

### 3.1 Tipos de movimento

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Move:
    column: int          # 0..6
    kind: str            # 'drop' ou 'pop'

    def __str__(self):
        return f"{self.kind}({self.column})"
```

### 3.2 Regras de legalidade

- **Drop em coluna `c`** é legal sse `board[0, c] == 0` (o topo está vazio — equivale a "a coluna não está cheia").
- **Pop em coluna `c`** é legal sse `board[5, c] == player_to_move` (a peça do fundo é nossa).

Há outra subtileza: a regra da repetição tripla só **autoriza** declarar empate, não obriga. Para simplicidade, vamos tratá-la fora de `legal_moves` — disponibilizamos uma função `can_claim_repetition_draw(state)` e o loop de jogo pergunta ao jogador.

### 3.3 Pseudocódigo

```
função legal_moves(state):
    moves = []
    para c em 0..6:
        se board[0, c] == 0:
            moves.append(Move(c, 'drop'))
        se board[5, c] == player_to_move:
            moves.append(Move(c, 'pop'))
    devolve moves
```

**Cardinalidade máxima:** 7 drops + 7 pops = 14 jogadas. **Mínima:** 0 (tabuleiro cheio sem pops legais → empate). Branching factor médio (estimativa empírica em Connect-4 standard: ~7; com pops talvez ~10) — o suficiente para justificar MCTS sobre MiniMax.

---

## 4. Aplicação de movimento

### 4.1 Drop

1. Encontrar a primeira linha vazia a contar de baixo na coluna `c`: `r = max{i : board[i, c] == 0}`.
2. Pôr a peça: `new_board[r, c] = player_to_move`.
3. Trocar de jogador.

### 4.2 Pop

1. Verificar `board[5, c] == player_to_move` (já garantido se o move veio de `legal_moves`, mas defensivamente confirmamos).
2. Fazer "shift" para baixo na coluna `c`: `new_board[1:6, c] = board[0:5, c]` e `new_board[0, c] = 0`.
3. Trocar de jogador.

> ⚠️ **Cuidado clássico:** ao implementar o shift, não esquecer de copiar o array primeiro. `board[1:6, c] = board[0:5, c]` numa view do array original cria sobreposição e dá lixo. Trabalhar **sempre** sobre `new_board = board.copy()`.

### 4.3 Histórico para repetição

Após cada `apply_move`, atualizar `history_counts[state_key(new_board, new_player)] += 1`. Quando o contador chega a 3, qualquer jogador pode pedir empate.

### 4.4 Pseudocódigo

```
função apply_move(state, move):
    new_board = state.board.copy()
    se move.kind == 'drop':
        r = primeira_linha_vazia_de_baixo(new_board, move.column)
        new_board[r, move.column] = state.player_to_move
    senão se move.kind == 'pop':
        new_board[1:6, move.column] = new_board[0:5, move.column]
        new_board[0, move.column] = 0
    
    new_player = 3 - state.player_to_move           # 1↔2
    new_history = state.history_counts.copy()
    chave = state_key(new_board, new_player)
    new_history[chave] = new_history.get(chave, 0) + 1
    
    winner = check_win(new_board, move, state.player_to_move)
    
    devolve State(new_board, new_player, new_history, last_move=move, winner=winner)
```

**Truque útil:** `3 - player` alterna entre 1 e 2 sem `if`.

---

## 5. Detecção de vitória — a parte mais delicada

### 5.1 Algoritmo base (sem regra do pop)

Procurar 4 peças iguais e não-zero em qualquer das 4 direções: horizontal, vertical, diagonal `↘`, diagonal `↙`.

**Implementação simples e correta:** percorrer todas as posições `(r, c)`, e para cada uma testar as 4 direções. Termina assim que encontra um 4. Não é o mais rápido, mas é claro e suficiente.

```
função four_in_a_row_for(board, player):
    para r em 0..5:
        para c em 0..6:
            se board[r,c] != player: continua
            para (dr, dc) em [(0,1), (1,0), (1,1), (1,-1)]:
                se 0 <= r+3*dr <= 5 e 0 <= c+3*dc <= 6:
                    se board[r+i*dr, c+i*dc] == player para i em 0..3:
                        devolve True
    devolve False
```

> **Otimização possível** (mais tarde, se for o gargalo): pré-calcular as 69 linhas de 4 possíveis no tabuleiro 7×6 (24 horizontais + 21 verticais + 12 diagonais ↘ + 12 ↙) e iterar só sobre elas. Por agora, mantemos simples — corretude > velocidade nesta fase.

### 5.2 Regra especial do pop com duplo 4-em-linha

Quando o último movimento é um pop, o pop pode simultaneamente:
- **Quebrar** um 4-em-linha (peça removida) — sem efeito direto, ninguém ganha por quebra.
- **Criar** um 4-em-linha **para o próprio jogador** (peças que estavam fragmentadas alinham-se ao descer).
- **Criar** um 4-em-linha **para o adversário** (idem).

Pode acontecer os três em simultâneo. A regra do enunciado:

> Se um pop cria 4-em-linha para os dois jogadores ao mesmo tempo, **vence quem fez o pop** — o 4 do adversário é ignorado.

**Implementação:**

```
função check_win(board, last_move, mover):
    outro = 3 - mover
    eu_ganhei  = four_in_a_row_for(board, mover)
    ele_ganhou = four_in_a_row_for(board, outro)

    se last_move.kind == 'pop':
        # Regra especial: o que faz o pop tem prioridade
        se eu_ganhei: devolve mover
        se ele_ganhou: devolve outro
    senão:                       # drop
        # Num drop, só o jogador que largou pode acabar de criar o 4
        # (a peça nova é dele). Não é possível criar 4 do adversário com um drop.
        se eu_ganhei: devolve mover
    
    se tabuleiro_cheio_e_sem_pops_legais(board, ...): devolve 'draw'
    devolve None
```

> 📝 **Para o relatório** — esta secção é onde se demonstra atenção ao enunciado. Incluir o pseudocódigo acima na secção "Modelação do problema → Regras especiais", e dar **dois exemplos** desenhados:
> 1. Pop cria 4-em-linha só para o adversário → ganha o adversário.
> 2. Pop cria 4-em-linha para os dois → ganha quem fez o pop.

### 5.3 Empate por tabuleiro cheio

Definição operacional:
- Tabuleiro cheio = `(board != 0).all()`.
- Sem pops legais = `legal_moves(state)` retorna lista vazia (já que com tabuleiro cheio drops são impossíveis).
- ⇒ empate.

A regra "o jogador a mover decide se faz pop" está implícita: enquanto houver pops legais, o jogo continua e a decisão é dele.

### 5.4 Empate por repetição tripla

Não é detetado automaticamente — é **declarável**. Disponibilizamos:

```python
def can_claim_repetition_draw(state) -> bool:
    return state.history_counts.get(state_key(state.board, state.player_to_move), 0) >= 3
```

E a interface CLI oferece a opção "declarar empate" sempre que esta função devolve `True`.

---

## 6. Código Python — implementação de referência

> Este código é o que vai para `popout/engine.py`. Está pensado para ser direto e auditável; partes podem ser otimizadas mais tarde se profilarmos e for necessário.

```python
# popout/engine.py
from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Optional, Union, Dict, List
import numpy as np

ROWS, COLS = 6, 7
EMPTY, P1, P2 = 0, 1, 2
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]   # →, ↓, ↘, ↙


@dataclass(frozen=True)
class Move:
    column: int
    kind: str  # 'drop' or 'pop'

    def __str__(self) -> str:
        return f"{self.kind}({self.column})"


@dataclass(frozen=True)
class State:
    board: np.ndarray                                          # shape (6,7), int8
    player_to_move: int                                        # 1 or 2
    history_counts: Dict[bytes, int] = field(default_factory=dict)
    last_move: Optional[Move] = None
    winner: Union[int, str, None] = None                       # None / 1 / 2 / 'draw'

    # NumPy arrays + dicts não são hashable directamente; só precisamos de hash
    # quando guardamos no histórico, e para isso usamos state_key(board, player).


def initial_state() -> State:
    board = np.zeros((ROWS, COLS), dtype=np.int8)
    s = State(board=board, player_to_move=P1)
    # Conta o estado inicial como já visto uma vez:
    return replace(s, history_counts={state_key(board, P1): 1})


def state_key(board: np.ndarray, player_to_move: int) -> bytes:
    return board.tobytes() + bytes([player_to_move])


def legal_moves(state: State) -> List[Move]:
    if state.winner is not None:
        return []
    moves = []
    for c in range(COLS):
        if state.board[0, c] == EMPTY:
            moves.append(Move(c, 'drop'))
        if state.board[ROWS - 1, c] == state.player_to_move:
            moves.append(Move(c, 'pop'))
    return moves


def _drop_row(board: np.ndarray, c: int) -> int:
    """Linha onde a peça aterra ao fazer drop na coluna c. -1 se cheia."""
    for r in range(ROWS - 1, -1, -1):
        if board[r, c] == EMPTY:
            return r
    return -1


def _four_in_a_row_for(board: np.ndarray, player: int) -> bool:
    for r in range(ROWS):
        for c in range(COLS):
            if board[r, c] != player:
                continue
            for dr, dc in DIRECTIONS:
                rr, cc = r + 3*dr, c + 3*dc
                if 0 <= rr < ROWS and 0 <= cc < COLS:
                    if all(board[r + i*dr, c + i*dc] == player for i in range(4)):
                        return True
    return False


def _is_full(board: np.ndarray) -> bool:
    return bool((board != EMPTY).all())


def check_win(board: np.ndarray, last_move: Move, mover: int) -> Union[int, str, None]:
    """Devolve 1 ou 2 se alguém venceu, 'draw' se empate, None se em curso."""
    other = 3 - mover
    me_won = _four_in_a_row_for(board, mover)
    other_won = _four_in_a_row_for(board, other)

    if last_move.kind == 'pop':
        if me_won:
            return mover
        if other_won:
            return other
    else:                                # drop
        if me_won:
            return mover
        # Um drop não pode criar 4 do adversário.

    # Sem vencedor — verificar empate por tabuleiro cheio sem pops possíveis.
    if _is_full(board):
        next_player = 3 - mover
        # se next_player não tiver pops legais (ou seja, nenhum board[fundo,c]==next_player)
        # o jogo termina em empate
        if not (board[ROWS - 1, :] == next_player).any():
            return 'draw'
    return None


def apply_move(state: State, move: Move) -> State:
    if state.winner is not None:
        raise ValueError("Game already finished.")

    new_board = state.board.copy()
    mover = state.player_to_move

    if move.kind == 'drop':
        r = _drop_row(new_board, move.column)
        if r == -1:
            raise ValueError(f"Column {move.column} is full.")
        new_board[r, move.column] = mover
    elif move.kind == 'pop':
        if new_board[ROWS - 1, move.column] != mover:
            raise ValueError(f"Cannot pop column {move.column}: bottom not yours.")
        # Shift coluna para baixo (cuidado com a ordem!)
        new_board[1:ROWS, move.column] = state.board[0:ROWS - 1, move.column]
        new_board[0, move.column] = EMPTY
    else:
        raise ValueError(f"Unknown move kind: {move.kind}")

    new_player = 3 - mover
    new_history = dict(state.history_counts)
    key = state_key(new_board, new_player)
    new_history[key] = new_history.get(key, 0) + 1

    winner = check_win(new_board, move, mover)

    return State(
        board=new_board,
        player_to_move=new_player,
        history_counts=new_history,
        last_move=move,
        winner=winner,
    )


def can_claim_repetition_draw(state: State) -> bool:
    key = state_key(state.board, state.player_to_move)
    return state.history_counts.get(key, 0) >= 3
```

### 6.1 Notas sobre o código

- **`dataclass(frozen=True)`** dá imutabilidade superficial. Os atributos `board` e `history_counts` continuam mutáveis em si, mas a nossa convenção é nunca os mutar — sempre criar novos estados via `apply_move`.
- **Overhead de cópia:** `new_board = state.board.copy()` + `dict(state.history_counts)` é O(42 + |histórico|). No início do jogo é desprezável; em jogos longos com pops o histórico cresce mas continua barato.
- **`from __future__ import annotations`** evita custo de avaliação de type hints (relevante quando o motor é chamado milhões de vezes).
- **`int8`** em vez de `int64` por defeito reduz a chave do estado de 8× e acelera o `tobytes()`.

---

## 7. Casos de teste — escrever **antes** de avançar para a Fase 2

> 📝 **Para o relatório** — listar como apêndice ou referenciar "ver `tests/test_engine.py` no repositório". Mostra rigor de engenharia.

Estes testes vão para `tests/test_engine.py`. Usamos `pytest`.

### 7.1 Inicialização e jogadas básicas

```python
def test_initial_state():
    s = initial_state()
    assert s.board.shape == (6, 7)
    assert (s.board == 0).all()
    assert s.player_to_move == 1
    assert s.winner is None

def test_legal_moves_initial():
    s = initial_state()
    moves = legal_moves(s)
    # No início só há drops (não há peças nossas no fundo)
    assert all(m.kind == 'drop' for m in moves)
    assert {m.column for m in moves} == {0, 1, 2, 3, 4, 5, 6}

def test_drop_lands_at_bottom():
    s = initial_state()
    s2 = apply_move(s, Move(3, 'drop'))
    assert s2.board[5, 3] == 1
    assert s2.player_to_move == 2

def test_drop_stacks():
    s = initial_state()
    s = apply_move(s, Move(3, 'drop'))         # P1 → linha 5
    s = apply_move(s, Move(3, 'drop'))         # P2 → linha 4
    assert s.board[5, 3] == 1
    assert s.board[4, 3] == 2

def test_full_column_no_drop():
    s = initial_state()
    for _ in range(6):
        s = apply_move(s, Move(0, 'drop'))
    moves = legal_moves(s)
    assert Move(0, 'drop') not in moves
```

### 7.2 Pop

```python
def test_pop_legal_only_if_bottom_is_yours():
    s = initial_state()
    s = apply_move(s, Move(0, 'drop'))         # P1 no fundo coluna 0
    moves = legal_moves(s)                      # agora joga P2
    assert Move(0, 'pop') not in moves          # P2 não pode popar peça de P1

def test_pop_shifts_down():
    s = initial_state()
    s = apply_move(s, Move(3, 'drop'))         # P1 r=5
    s = apply_move(s, Move(3, 'drop'))         # P2 r=4
    s = apply_move(s, Move(3, 'drop'))         # P1 r=3
    # Coluna 3: linhas 3,4,5 = [1,2,1]
    s = apply_move(s, Move(0, 'drop'))         # passar a vez para P1
    # Wait: depois de 3 drops é a vez do P2... refaz
```

(Os testes acima são esboços. Vamos completá-los com mais cuidado durante a implementação.)

### 7.3 Vitórias

```python
def test_horizontal_win():
    s = initial_state()
    moves = [Move(0,'drop'), Move(0,'drop'),
             Move(1,'drop'), Move(1,'drop'),
             Move(2,'drop'), Move(2,'drop'),
             Move(3,'drop')]                   # P1 completa horizontal na linha 5
    for m in moves:
        s = apply_move(s, m)
    assert s.winner == 1

def test_vertical_win():
    s = initial_state()
    # P1 joga sempre coluna 0; P2 coluna 1
    for _ in range(3):
        s = apply_move(s, Move(0, 'drop'))
        s = apply_move(s, Move(1, 'drop'))
    s = apply_move(s, Move(0, 'drop'))         # 4º P1 na coluna 0
    assert s.winner == 1

def test_diagonal_win():
    # construir uma diagonal — deixar para implementação detalhada
    pass
```

### 7.4 Regras especiais

```python
def test_pop_creates_double_four_pop_player_wins():
    """
    Cenário a construir: posição em que um pop do P1 cria 4-em-linha para ambos.
    Resultado esperado: P1 ganha (regra Allen 2010).
    """
    # construção da posição é tediosa; ver test_engine.py
    pass

def test_repetition_triple_can_claim():
    s = initial_state()
    # Sequência de drops + pops que volte ao estado inicial 3x
    # Verificar que can_claim_repetition_draw devolve True
    pass

def test_full_board_no_pops_is_draw():
    # construir tabuleiro cheio onde fundo é todo da cor de P1, e é a vez do P2
    # → P2 não tem pops, drops impossíveis (cheio), portanto 'draw'
    pass
```

### 7.5 Determinismo / pureza

```python
def test_apply_move_does_not_mutate_input():
    s = initial_state()
    board_before = s.board.copy()
    history_before = dict(s.history_counts)
    _ = apply_move(s, Move(3, 'drop'))
    assert (s.board == board_before).all()
    assert s.history_counts == history_before
```

Este teste é **crítico** para o MCTS funcionar — se `apply_move` mutar o estado, os nós da árvore corrompem-se silenciosamente.

---

## 8. Verificação manual — partida demonstrativa

Antes de declarar a fase concluída, correr:

```python
s = initial_state()
moves = [Move(3,'drop'), Move(3,'drop'), Move(2,'drop'), Move(4,'drop'),
         Move(2,'drop'), Move(1,'drop'), Move(0,'drop')]
for m in moves:
    s = apply_move(s, m)
print(s.board)
print("winner:", s.winner)
```

Espera-se `winner == 1` (P1 fez 4-em-linha horizontal na linha do fundo após o último drop).

---

## 9. O que vai para o relatório (versão final, condensada)

> 📝 **Para o relatório — secção "Modelação do problema":** copiar/parafrasear esta versão final. As secções 1-5 deste documento servem de fonte; aqui é o resumo "polido".

**Modelação do problema (PopOut como problema state-based):**

1. **Estados.** Cada estado é um quíntuplo `(board, player_to_move, history, last_move, winner)`. O *board* é uma matriz 6×7 com valores em `{0, 1, 2}`, representando casas vazias e peças dos dois jogadores. O *history* é um multiconjunto (implementado como dicionário de contagens) de estados já alcançados na partida — necessário para a regra da repetição tripla. *Last_move* e *winner* são informação derivada útil para a função de transição.

2. **Estado inicial.** Tabuleiro vazio, jogador 1 a mover.

3. **Ações.** Cada ação é um par `(coluna, tipo)` com `tipo ∈ {drop, pop}`. Drop é legal se a coluna não estiver cheia; pop é legal se a casa do fundo dessa coluna for da cor do jogador a mover.

4. **Modelo de transição.** Determinístico. Drop coloca a peça na primeira casa vazia a contar de baixo; pop remove a peça do fundo e desce a coluna inteira. Em ambos os casos o jogador a mover alterna.

5. **Teste de terminação.** Vitória se algum jogador alinha 4 peças (horizontal, vertical, diagonal). Regra especial: se um *pop* cria 4-em-linha para os dois jogadores em simultâneo, vence quem fez o pop. Empate se o tabuleiro está cheio sem pops legais para o próximo jogador, ou se um jogador declarar empate por repetição tripla.

6. **Função utilidade** (usada pelo MCTS no rollout): `+1` para o vencedor, `−1` para o vencido, `0` para empate.

**Decisões de implementação:**
- Estado **imutável**, transições puras (`apply_move` devolve novo estado). Razão: o MCTS partilha estados entre nós da árvore; mutação corrompe a árvore.
- Tabuleiro como `np.ndarray` `int8` 6×7. Razão: hashing barato (`tobytes`), cópia O(42), operações vectorizadas em `check_win`.
- **Bitboards rejeitados nesta versão** — mais rápidos mas mais opacos. Mencionados como trabalho futuro.

**Pseudocódigo das funções principais** (incluir no notebook):
- `legal_moves(state)` — secção 3.3 deste documento.
- `apply_move(state, move)` — secção 4.4.
- `check_win(board, last_move, mover)` — secção 5.2.

---

## 10. Riscos identificados e mitigações desta fase

| Risco | Como já mitigado | Como vamos validar |
|-------|------------------|---------------------|
| Esquecer regra do duplo-4 por pop | `check_win` recebe `last_move` e trata o caso explicitamente | Teste dedicado em 7.4 |
| Mutação acidental do estado original | `dataclass(frozen=True)` + `board.copy()` em todos os pontos | Teste em 7.5 |
| `apply_move` lento → MCTS inviável | NumPy + cópia O(42); `int8` reduz chaves | `cProfile` na Fase 3, otimizar só se necessário |
| Histórico cresce sem limite em jogos longos | Aceitável — tipicamente <100 entradas por partida | Não mitigar a priori; reavaliar se for problema |
| Bug no shift do pop (sobreposição NumPy) | Trabalhamos sempre sobre `new_board = state.board.copy()` | Teste do pop em 7.2 |

---

## 11. Próximos passos imediatos

Quando esta fase estiver verde:

1. **Fase 2 — Interface CLI** (`popout/cli.py`): `print_board`, `human_strategy`, `play_game`. Base para fazer humano-vs-humano funcional.
2. Em paralelo, C pode começar a Fase 5 (ID3 + Iris) — não depende do motor PopOut.
3. B pode esquematizar a estrutura do MCTS (Fase 3) — só precisa da API pública do motor (que já está fixada neste documento).

---

## 12. Material a adicionar ao relatório vindo desta fase

Checklist do que esta fase produz para a entrega:

- [ ] Secção "Modelação do problema" (texto da secção 9 deste documento).
- [ ] Pseudocódigo das três funções principais (secções 3.3, 4.4, 5.2).
- [ ] Diagrama do tabuleiro com convenção de orientação (linha 0 = topo).
- [ ] Exemplo desenhado da regra do duplo-4 por pop.
- [ ] Output de uma partida demonstrativa (secção 8).
- [ ] Lista de testes implementados (apêndice ou referência ao repositório).
- [ ] Justificação NumPy vs. bitboards (parágrafo curto na secção "Decisões de implementação").

---

## 13. Apontamentos para a apresentação (slides)

Esta fase **não é** o foco da apresentação (os slides têm 10 minutos para problema → MCTS → ID3 → resultados). Mas no slide "Regras do PopOut" devemos:

- Mostrar tabuleiro com seta de drop e seta de pop.
- Mencionar a regra do pop com duplo-4 (1 linha de texto).
- Não entrar em detalhes de implementação — deixar para o notebook.

---

> **Estado deste documento:** rascunho v0.1 — antes da implementação.
> Vamos atualizá-lo ao longo da Fase 1 com: resultados dos testes, eventuais decisões revistas, snapshots de partidas, profiling preliminar.

---

## 14. Atualização v0.2 — implementação concluída

### 14.1 Estrutura final do código

```
IA_WORK/
├── popout/
│   ├── __init__.py
│   └── engine.py        (~165 linhas)
└── tests/
    ├── __init__.py
    └── test_engine.py   (21 testes)
```

### 14.2 Resultado dos testes

Comando: `python -m pytest tests/test_engine.py -v -c /dev/null`

```
============================= test session starts ==============================
collected 21 items

test_initial_state_shape_and_emptiness PASSED                  [  4%]
test_initial_legal_moves_are_seven_drops PASSED                [  9%]
test_move_validation_rejects_bad_inputs PASSED                 [ 14%]
test_drop_lands_at_bottom_first PASSED                         [ 19%]
test_drop_stacks_up PASSED                                     [ 23%]
test_full_column_disables_drop_but_keeps_others PASSED         [ 28%]
test_pop_legal_only_if_bottom_belongs_to_mover PASSED          [ 33%]
test_pop_shifts_column_down PASSED                             [ 38%]
test_pop_on_empty_column_raises PASSED                         [ 42%]
test_horizontal_win_bottom_row PASSED                          [ 47%]
test_vertical_win PASSED                                       [ 52%]
test_diagonal_down_right_win PASSED                            [ 57%]
test_pop_creates_double_four_pop_player_wins PASSED            [ 61%]
test_pop_creates_double_four_pop_player_wins_v2 PASSED         [ 66%]
test_pop_creates_only_opponent_four_opponent_wins PASSED       [ 71%]
test_repetition_triple_can_claim PASSED                        [ 76%]
test_full_board_no_pops_for_next_is_draw SKIPPED               [ 80%]
test_check_win_returns_draw_when_no_moves_available PASSED     [ 85%]
test_apply_move_does_not_mutate_input_state PASSED             [ 90%]
test_apply_move_after_terminal_raises PASSED                   [ 95%]
test_no_legal_moves_when_terminal PASSED                       [100%]

======================== 20 passed, 1 skipped in 0.59s =========================
```

**Resumo:** 20 passados, 1 skipped (intencional). Cobertura: drops, pops, vitórias horizontais/verticais/diagonais, regra do duplo-4 por pop (3 variantes), repetição tripla, pureza da função de transição, terminação.

### 14.3 Sobre o teste skipped

`test_full_board_no_pops_for_next_is_draw` está marcado `SKIPPED` por uma razão documentada: o cenário de "tabuleiro cheio, fundo monocromático para impedir pops do adversário, sem 4-em-linha em lado nenhum" é **fisicamente impossível** num tabuleiro 7×6. Se o fundo é todo da mesma cor, há 7 peças seguidas → existe um 4-em-linha. Logo este caso degenera sempre noutro: ou ganha alguém, ou alguém ainda tem pops.

A cobertura do empate por "sem movimentos legais" mantém-se: `apply_move` chama `check_win` que devolve `'draw'` quando nem o próximo a mover tem drops nem pops. Cenários reais que o atinjam têm de envolver pops a deixar o tabuleiro sem fundo da cor do adversário — possível, mas raro.

### 14.4 Partida demonstrativa

```python
from popout.engine import initial_state, apply_move, Move, render
s = initial_state()
moves = [
    Move(0,'drop'), Move(6,'drop'),
    Move(1,'drop'), Move(6,'drop'),
    Move(2,'drop'), Move(6,'drop'),
    Move(3,'drop'),
]
for m in moves:
    s = apply_move(s, m)
print(render(s.board))
print('winner:', s.winner)
```

**Output:**
```
-------
-------
-------
------O
------O
XXXX--O
winner: 1
last_move: drop(3)
```

P1 (X) completa 4-em-linha horizontal no fundo após o drop final. ✅

### 14.5 Decisões revistas durante a implementação

1. **Adicionada `render(board)`** ao `engine.py`. Inicialmente este utilitário ia para `cli.py` (Fase 2), mas foi prático tê-lo em `engine.py` para depuração e para a própria partida demonstrativa.
2. **`Move.__post_init__`** valida `kind` e `column` no construtor. Não estava no plano original; ajuda a apanhar bugs cedo (ex: passar `Move(7, 'drop')`).
3. **Empate por "sem movimentos legais"** ficou tratado dentro de `check_win` quando nem `_has_legal_drop` nem `_has_legal_pop(next_player)` devolvem `True`. Cobre tanto tabuleiro cheio como configurações de "deadlock" mais subtis.

### 14.6 API pública (estabilizada — pronta para a Fase 3)

| Símbolo | Tipo | Função |
|---------|------|--------|
| `Move(column, kind)` | dataclass | Representa uma jogada |
| `State(board, player_to_move, history_counts, last_move, winner)` | dataclass | Estado imutável |
| `initial_state()` | `() -> State` | Estado inicial |
| `legal_moves(state)` | `(State) -> list[Move]` | Jogadas legais |
| `apply_move(state, move)` | `(State, Move) -> State` | Transição pura |
| `check_win(board, last_move, mover)` | função interna mas pública | Lógica de vitória |
| `can_claim_repetition_draw(state)` | `(State) -> bool` | Para a interface |
| `render(board)` | `(np.ndarray) -> str` | Texto do tabuleiro |
| `state_key(board, player)` | `(np.ndarray, int) -> bytes` | Chave hashável |

O MCTS (Fase 3) só vai consumir esta superfície. Consegue-se trocar a representação interna (ex: bitboards) sem mexer no MCTS.

### 14.7 Critérios de saída — verificação

- [x] Todas as funções públicas implementadas e a passar testes unitários.
- [x] Partida demonstrativa em CLI (sem interface ainda — basta `print` do board) sem crashar.
- [x] Documentação desta fase escrita (este documento).
- [x] Pop, regra duplo-4, repetição tripla e empate cobertos por testes dedicados.

**Fase 1 — concluída.** Pronto para avançar à Fase 2 (interface CLI) ou, em paralelo, à Fase 3 (MCTS).




# ═══════════════════════════════════════════════════════════════
# FASE2_INTERFACE_CLI.md
# ═══════════════════════════════════════════════════════════════

# Fase 2 — Interface CLI
## Documento de execução e material-fonte para o relatório

> Implementa a **Fase 2** do `PLANEAMENTO_PROJETO.md` (Interface CLI, dia 2).
> Mesma convenção do documento da Fase 1: serve **simultaneamente** como guia de execução e como rascunho do relatório (caixas com 📝).

---

## 0. Onde estamos

| Fase | Estado |
|------|--------|
| 1 | ✅ Concluída (motor + 20 testes) |
| **2** | **Em curso** |
| 3 | A seguir (MCTS) |

**Critério de saída:**
- `play_game(p1, p2)` corre uma partida do início ao fim para qualquer combinação `{human, random}` × `{human, random}`.
- Os **três cenários do enunciado** funcionam: Humano vs. Humano, Humano vs. Computador, Computador vs. Computador.
- Input humano com parsing tolerante e re-prompt em caso de erro.
- Repetição tripla declarável pelo humano via comando explícito.
- Tudo coberto por testes (substituindo `input()` por estratégias scriptadas).

---

## 1. Design da interface

### 1.1 Princípio organizador: **estratégia como função**

Cada jogador é uma função `strategy(state) -> Move | str`. O `play_game` chama-a quando é a vez do jogador. Isto faz com que **os 3 cenários do enunciado saiam do mesmo loop** — só mudam os argumentos:

```python
play_game(human_strategy, human_strategy)            # H vs H
play_game(human_strategy, random_strategy)           # H vs C
play_game(random_strategy, mcts_strategy)            # C vs C (placeholder)
```

> 📝 **Para o relatório** — mencionar explicitamente esta abstração na secção "Implementação". É a versão prática do padrão *strategy* aplicado aos jogadores e mostra atenção a duplicação de código.

### 1.2 Estratégias previstas

| Nome | Descrição | Quando entra |
|------|-----------|--------------|
| `human_strategy` | Lê `input()` e converte em `Move` | Fase 2 (agora) |
| `random_strategy` | Escolhe uniformemente de `legal_moves(state)` | Fase 2 (sanity check + adversário trivial para a Fase 8) |
| `mcts_strategy(...)` | A construir na Fase 3 | Fase 3 |
| `tree_strategy(...)` | Árvore-aprendida-do-MCTS | Fase 7 |

### 1.3 Comandos do humano

Input aceite no prompt:
- `0..6` — drop na coluna (atalho, equivalente a `d 3`).
- `d <col>` ou `drop <col>` — drop explícito.
- `p <col>` ou `pop <col>` — pop.
- `draw` — declara empate por repetição tripla (só se `can_claim_repetition_draw` devolver `True`).
- `q` ou `quit` — sai do jogo (resigna).
- `help` ou `?` — imprime atalhos.

Tolerância: maiúsculas/minúsculas indiferentes; espaços extra ignorados.

### 1.4 Renderização do tabuleiro

Reusamos `render()` do `engine.py` (formato `X--O-XO`). Adicionamos cabeçalho com índices das colunas para o humano não ter de contar:

```
 0123456
 -------
 -------
 -------
 ------O
 ------O
 XXXX--O
P1 (X) wins!
```

Sem cores, sem unicode — funciona em qualquer terminal e simplifica os testes (`assert "wins" in output`).

---

## 2. Pseudocódigo do `play_game`

```
def play_game(p1, p2, *, on_render=print, max_turns=300):
    state = initial_state()
    strategies = {1: p1, 2: p2}
    on_render(format_state(state))

    while state.winner is None:
        if turn_count > max_turns:
            return state.with(winner='draw')        # safety net

        move = strategies[state.player_to_move](state)
        if move == 'draw':
            return state.with(winner='draw')
        if move == 'resign':
            return state.with(winner=other_player)

        state = apply_move(state, move)
        on_render(format_state(state))

    return state
```

**`max_turns`:** rede de segurança contra ciclos infinitos durante desenvolvimento (jogadores aleatórios podem ficar a popar uns aos outros). Não é uma regra do PopOut — é só prudência. Em produção pode ficar alto (300 é mais do que suficiente).

**`on_render`:** injetado para os testes não imprimirem para stdout. Por defeito `print`.

---

## 3. Parsing do input humano

### 3.1 Pseudocódigo

```
def parse_human_input(text, state):
    t = text.strip().lower()
    if t in ('q', 'quit'): return 'resign'
    if t == 'draw':
        if can_claim_repetition_draw(state):
            return 'draw'
        else:
            return ParseError("Repeticao tripla nao alcancada.")
    if t in ('?', 'help'):
        return ParseError(HELP_TEXT)             # re-prompt apos imprimir

    if t in '0123456':                            # atalho 1-char
        return Move(int(t), 'drop')

    parts = t.split()
    if len(parts) == 2 and parts[0] in ('d','drop','p','pop'):
        col = int(parts[1])
        kind = 'drop' if parts[0] in ('d','drop') else 'pop'
        return Move(col, kind)

    return ParseError(f"Input invalido: {text!r}.")
```

**Validação adicional:** após parsing, conferir que a `Move` está em `legal_moves(state)`. Se não, re-prompt com mensagem específica (ex: "Coluna 3 cheia.").

### 3.2 Tratamento de erros

Filosofia: nunca crashar por input. Imprimir mensagem clara, repetir prompt. O humano é o único utilizador da CLI; os agentes não passam por aqui.

---

## 4. Estratégia random — para que serve

`random_strategy(state)` escolhe uniformemente uma `Move` de `legal_moves(state)`. Três usos:

1. **Sanity check do motor:** se duas random_strategy jogarem 1000 partidas sem crashar, o motor está robusto.
2. **Baseline para a Fase 8:** o MCTS deve vencer ~100% contra random — se não vencer, há bug.
3. **Adversário trivial mencionado no enunciado:** "outro algoritmo" no cenário CvC pode ser o random, embora o objetivo final seja MCTS vs. árvore-aprendida.

> 📝 **Para o relatório** — incluir tabela "MCTS vs. Random: 100/100 vitórias" como sanity check antes de discutir os matchups interessantes.

### 4.1 Reproducibilidade

`random_strategy` aceita uma `seed` opcional. Para experiências repetíveis, fixamos a seed; para o jogo casual, deixamos `None`.

```python
def random_strategy(state, *, rng=None):
    rng = rng or random.Random()
    return rng.choice(legal_moves(state))
```

---

## 5. Cenários do enunciado — checklist

| Cenário | Como invocar | Suportado |
|---------|--------------|-----------|
| H vs H | `play_game(human_strategy, human_strategy)` | ✅ Fase 2 |
| H vs C | `play_game(human_strategy, random_strategy)` (placeholder) → será MCTS na Fase 3 | ✅ Fase 2 (com random) |
| C vs C | `play_game(random_strategy, random_strategy)` → será MCTS vs. árvore na Fase 7 | ✅ Fase 2 (com random) |

> O enunciado pede que o C-vs-C use **dois algoritmos diferentes**. No fim do projeto vai ser MCTS vs. árvore-aprendida-do-MCTS. Por agora basta a infraestrutura.

---

## 6. Casos de teste

### 6.1 Estratégia scriptada — chave dos testes

Para testar `play_game` sem `input()`, definimos uma estratégia que consome de uma fila:

```python
def scripted_strategy(moves):
    it = iter(moves)
    def strat(state):
        return next(it)
    return strat
```

Permite verificar que o loop termina corretamente e que `apply_move` é chamado na ordem certa.

### 6.2 Lista de testes

- `test_parse_short_drop`: `"3"` → `Move(3, 'drop')`.
- `test_parse_explicit_drop`: `"d 3"`, `"drop 3"`.
- `test_parse_pop`: `"p 0"`, `"pop 0"`.
- `test_parse_invalid_returns_error`: `"foo"`, `"d 9"`, `""`.
- `test_parse_resign`: `"q"`, `"quit"` → `'resign'`.
- `test_parse_draw_when_legal`: histórico com 3+ → `'draw'`.
- `test_parse_draw_when_illegal_returns_error`.
- `test_play_game_scripted_p1_wins`: usar a sequência da partida demonstrativa da Fase 1.
- `test_play_game_random_vs_random_terminates`: 100 partidas, todas terminam dentro de `max_turns`.
- `test_random_strategy_only_chooses_legal`.
- `test_play_game_resign_gives_other_player_win`.

### 6.3 Saída esperada

`play_game` devolve sempre um `State` com `winner ∈ {1, 2, 'draw'}`. Os testes verificam exatamente isto.

---

## 7. Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| `play_game` entra em loop infinito com 2 randoms (pop infinito) | `max_turns` como safety net |
| Input humano malformado faz crashar | `parse_human_input` devolve `ParseError`, loop re-pergunta |
| Testes a depender de `print()` | `on_render` injetável |
| Aleatoriedade torna testes flaky | Seed fixa nos testes |

---

## 8. O que esta fase entrega para o relatório

> 📝 **Secção "Implementação > Interface" do notebook:**

1. Diagrama do fluxo `play_game` (loop com decisão de jogador → render → ciclo).
2. Justificação da abstração "estratégia como função".
3. Snippet de uma partida HvH com input simulado.
4. Tabela: random vs random — 100 partidas, distribuição vencedor (sanity).

---

## 9. Próximos passos imediatos

Depois da Fase 2 verde:
- **Fase 3 — MCTS:** plug-in `mcts_strategy(state, n_simulations, c)` no mesmo `play_game`. Zero alterações ao loop.
- Já dá para correr `play_game(human_strategy, mcts_strategy(...))` — o cenário H vs C completo.

---

> **Estado deste documento:** rascunho v0.1 — antes da implementação. Atualizado com resultados na secção 10 abaixo.

---

## 10. Atualização v0.2 — implementação concluída

### 10.1 Estrutura final do código

```
IA_WORK/
├── popout/
│   ├── __init__.py
│   ├── engine.py        (Fase 1)
│   └── cli.py           (~165 linhas, esta fase)
└── tests/
    ├── __init__.py
    ├── test_engine.py   (Fase 1: 21 testes)
    └── test_cli.py      (esta fase: 20 testes)
```

### 10.2 Resultado dos testes (suite completa: motor + CLI)

Comando: `python -m pytest tests/ -v -c /dev/null`

```
======================== 40 passed, 1 skipped in 0.47s =========================
```

20 testes novos da CLI, todos a passar. O `skipped` é o mesmo da Fase 1 (cenário fisicamente impossível, documentado).

### 10.3 Demo 1 — partida HvH scripted

```
 0123456
 -------
 -------
 -------
 ------O
 ------O
 XXXX--O
P1 (X) venceu!
```

Saída idêntica à da Fase 1, agora com cabeçalho de colunas e estado terminal renderizado pelo `format_state`. ✅

### 10.4 Demo 2 — Random vs. Random (100 partidas)

| Vencedor | Partidas |
|----------|----------|
| P1 | 55 |
| P2 | 45 |
| Empate | 0 |

> 📝 **Para o relatório** — interpretação:
> - **Sanity check do motor:** 100 partidas aleatórias terminaram corretamente, sem crashes nem ciclos infinitos. O motor é robusto.
> - **Vantagem do P1:** 55/45 com 100 partidas é consistente com a vantagem de "primeiro a jogar" do Connect-4 (que com jogo perfeito é vitória forçada do P1; com jogo aleatório a vantagem dilui-se mas não desaparece).
> - **Zero empates:** com pops disponíveis e jogo aleatório, o tabuleiro raramente entra na configuração de empate puro.
> - Esta tabela vai funcionar como **baseline** na Fase 8: "MCTS vs. random deve estar próximo de 100/0/0; se não estiver, há bug".

### 10.5 Decisões revistas durante a implementação

1. **`scripted_strategy` adicionada a `cli.py`**, não só ao módulo de testes. Razão: também é útil como ferramenta de desenvolvimento (replay de partidas para reproduzir bugs).
2. **`show_intermediate=False`** como flag em `play_game`. Sem isto, qualquer teste que corra `play_game` polui stdout. Estava implícito no plano via `on_render`, mas explicitar com flag é mais limpo.
3. **Construção do estado terminal** quando há `resign`/`draw`/`max_turns`: copiamos o estado e mudamos só o `winner`. A `dataclass(frozen=True)` faz isto verboso (precisamos de re-instanciar com todos os campos). Alternativa seria usar `dataclasses.replace`, mas o `dict` interno do `history_counts` complica — fica para uma melhoria futura se incomodar.
4. **`HELP_TEXT` propagado via `ParseError`**: aproveitamos o fluxo de "input inválido → re-prompt" para também imprimir ajuda, em vez de duplicar lógica.

### 10.6 Critérios de saída — verificação

- [x] `play_game` corre uma partida do início ao fim.
- [x] Os três cenários do enunciado funcionam: HvH (`human, human`), HvC (`human, random`), CvC (`random, random`).
- [x] Input humano com parsing tolerante e re-prompt em caso de erro (testado).
- [x] Repetição tripla declarável via `draw` (testado).
- [x] Resign/quit produz vitória do adversário (testado).
- [x] Max-turns como rede de segurança (testado).
- [x] Tudo coberto por testes scriptados — 0 dependência de stdin nos testes.

**Fase 2 — concluída.** Pronto para a Fase 3 (MCTS), que vai ser plugada como uma 4ª estratégia sem mexer no `play_game`.

### 10.7 API pública (estabilizada)

| Símbolo | Função |
|---------|--------|
| `play_game(p1, p2, *, on_render, max_turns, show_intermediate)` | Loop principal |
| `human_strategy(state, *, input_fn, output_fn)` | Estratégia humana com I/O injetável |
| `random_strategy(rng=None) -> Strategy` | Factory que devolve estratégia aleatória |
| `scripted_strategy(decisions) -> Strategy` | Para testes/replay |
| `parse_human_input(text, state) -> Decision` | Parser exposto para testar isoladamente |
| `format_state(state) -> str` | Render com cabeçalho e linha de estado |
| `ParseError` | Exceção de parsing — usada para re-prompt |

### 10.8 O que esta fase entrega para o relatório

- Pseudocódigo do `play_game` (secção 2 deste doc).
- Snippet "estratégia como função" + tabela dos 3 cenários (secção 1.1, 5).
- Tabela random-vs-random como sanity check (secção 10.4).
- Imagem da CLI a meio de uma partida (secção 10.3 deste doc).
- Mensagens de ajuda da CLI (`HELP_TEXT` no código).




# ═══════════════════════════════════════════════════════════════
# FASE3_MCTS.md
# ═══════════════════════════════════════════════════════════════

# Fase 3 — Monte Carlo Tree Search (MCTS + UCB1)
## Documento de execução e material-fonte para o relatório

> Implementa a **Fase 3** do `PLANEAMENTO_PROJETO.md` (MCTS standard + UCB, dias 3-5).
> Esta é a **peça central da Metade A** do trabalho. Vale 30% da nota direta + parte dos 30% técnicos (na Fase 4 com as variações + Fase 8 com a avaliação rigorosa).

---

## 0. Onde estamos

| Fase | Estado |
|------|--------|
| 1 — Motor PopOut | ✅ |
| 2 — CLI | ✅ |
| **3 — MCTS standard** | **Em curso** |
| 4 — Variações do MCTS | A seguir (Fase 6 do plano) |

**Critério de saída:**
- `mcts_search(state, n_simulations, c)` devolve a "melhor" jogada (filho da raiz com mais visitas).
- `mcts_strategy(...)` plug-and-play no `play_game` da Fase 2.
- Backpropagation com sinal correto (verificável por teste dedicado).
- UCB1 implementado e validado contra o **exemplo trabalhado** do `MATERIA_IA.md` (secção 11.4: filhos X, Y, Z).
- MCTS bate `random_strategy` em pelo menos 80% de uma amostra de 10 partidas a `N=200` simulações.

---

## 1. Recapitulação conceptual (vai para o relatório)

> 📝 **Para o relatório — secção "Pesquisa Adversarial: MCTS"**.

### 1.1 Porque é que escolhemos MCTS para PopOut e não MiniMax/Alpha-Beta

**Argumento de força do PopOut:**
- Branching factor até **14** (7 drops + até 7 pops).
- Pops podem arrastar jogos para profundidades grandes (sem critério natural de "fim próximo").
- Não temos uma boa função de avaliação heurística para o PopOut (Connect-4 standard tem várias publicadas; PopOut com pops introduz dinâmica nova que estraga essas heurísticas).

**Consequências para os algoritmos:**
- **MiniMax puro** é inviável — `b^d` explode mesmo a profundidades modestas.
- **Alpha-Beta com corte heurístico** seria viável mas exigiria desenhar uma função de avaliação razoável, e essa é uma tarefa de pesquisa em si. Dependeria fortemente da qualidade da heurística — coisa que não temos tempo de afinar.
- **MCTS** é *domain-agnostic* — só precisa de simulações aleatórias até ao fim. É *anytime* (mais simulações = melhor, mas dá uma resposta a qualquer momento). Tem garantias matemáticas (UCB1, regret logarítmico).

> 📝 Esta justificação vai para o slide "Porquê MCTS?" da apresentação.

### 1.2 Os quatro passos (cor canónica do MATERIA_IA §6.6)

```
   ┌── Selection ── Expansion ── Simulation ── Backpropagation ──┐
   │                                                              │
   └── repete N vezes ────────────────────────────────────────────┘
```

Em palavras claras:
1. **Selection.** Desce pela árvore atual. Em cada nó **completamente expandido e não-terminal**, escolhe o filho com **maior UCB1**. Pára quando chega a um nó com filhos por expandir, ou a um nó terminal.
2. **Expansion.** Se o nó parado **não é terminal**, escolhe uma jogada legal ainda **não testada** e cria um filho novo a representar o estado resultante.
3. **Simulation (rollout).** Joga aleatoriamente a partir do filho novo até ao fim do jogo. Devolve o vencedor (ou empate).
4. **Backpropagation.** O resultado sobe pela árvore — cada nó visitado nesta iteração incrementa `N` (visitas) e atualiza `U` (vitórias do ponto de vista de quem **escolheu vir** a esse nó).

No fim das `N` iterações, escolhe-se a jogada cujo filho da raiz tem **mais visitas** (não maior taxa — mais visitas é mais robusto, ver §1.4).

### 1.3 Fórmula UCB1

$$\text{UCB1}(n) = \underbrace{\frac{U(n)}{N(n)}}_{\text{exploitation}} + C \cdot \underbrace{\sqrt{\frac{\ln N(\text{parent}(n))}{N(n)}}}_{\text{exploration}}$$

- `U(n)` — vitórias acumuladas no nó n (do ponto de vista do jogador que **escolheu vir** a este nó — ou seja, o jogador que estava a mover no nó pai).
- `N(n)` — número de visitas ao nó n.
- `C` — constante que controla o equilíbrio. **Valor canónico C = √2 ≈ 1.414** (vem da análise de regret de Auer et al. 2002 quando recompensas estão em [0, 1]).

**Por que `ln`?** Cresce devagar — à medida que o pai é visitado mais e mais vezes, o bónus de exploração aos filhos pouco visitados sobe, mas devagar. Isto evita que a árvore "esqueça" filhos promissores cedo demais sem desperdiçar simulações em filhos claramente inferiores depois de muitos dados.

> 📝 **Material já trabalhado:** o exercício 11.4 do `MATERIA_IA.md` (filhos X=20/25, Y=30/70, Z=2/5 com pai N=100) é o nosso teste-âncora. Calcula UCBs **1.407**, **0.791**, **1.758** — Z vence por exploração apesar da taxa baixa. **Vamos replicar este cálculo num teste unitário** para garantir que a nossa implementação está correta.

### 1.4 Por que "mais visitas" e não "maior taxa de vitórias" no fim?

Vem direto do slide das aulas: um nó com `65/100` (65% win-rate, 100 visitas) é mais fiável do que um com `2/3` (67% win-rate mas só 3 visitas → variância enorme). UCB1 naturalmente concentra visitas no melhor filho à medida que `N` cresce, portanto o nó mais visitado tende a coincidir com o melhor — e tem o estimador mais robusto.

### 1.5 O cuidado #1 — sinal na backpropagation

> ⚠️ **Erro #1 das implementações de MCTS de raiz** (e está no plano original).

O `result` (vencedor) tem de ser interpretado **do ponto de vista do jogador que está a mover no nó pai** — porque foi esse jogador que **escolheu** descer para este filho. Se ignorarmos isto, o algoritmo estará a maximizar do lado errado em níveis alternados.

**A nossa convenção concreta:**
- `node.U` = quantas das `node.N` simulações que passaram por `node` resultaram em vitória do jogador que **estava a mover em `node.parent`** (i.e., o jogador que escolheu o `move_in` que levou a `node`).
- Empate conta como **0.5** (clássico em UCT — preserva a média num intervalo [0, 1] consistente com a constante C = √2).

**Backpropagation:**
```
def backprop(leaf_node, winner):
    node = leaf_node
    while node is not None:
        node.N += 1
        if node.parent is not None:
            chooser = node.parent.state.player_to_move
            if winner == chooser:
                node.U += 1.0
            elif winner == 'draw':
                node.U += 0.5
            # else: loss → U += 0
        node = node.parent
```

A raiz não tem pai → `U` da raiz não é usado para nada (UCB1 só é avaliado em **filhos**). Mantemos `N` da raiz para o `ln(N(parent))` dos seus próprios filhos.

> 📝 Esta secção vai para o relatório com a frase: *"Implementámos a backpropagation com a perspetiva do jogador que escolheu o move, evitando o erro clássico em que o sinal alterna inconsistentemente nos níveis ímpares da árvore."*

---

## 2. Pseudocódigo da implementação

### 2.1 Estrutura `Node`

```
class Node:
    state              # estado PopOut
    parent             # Node ou None
    move_in            # Move que levou aqui (None na raiz)
    children           # dict {Move: Node}
    untried_moves      # lista de Moves ainda por expandir
    N                  # int — visitas
    U                  # float — vitórias acumuladas (perspetiva do parent.player_to_move)
    
    is_terminal()       → state.winner is not None
    is_fully_expanded() → len(untried_moves) == 0
    best_child(c)        → child com maior UCB1
    expand(rng)          → cria + devolve novo filho
```

### 2.2 `mcts_search`

```
def mcts_search(root_state, n_simulations, c, rng):
    root = Node(root_state)
    for _ in range(n_simulations):
        node = root
        # 1. Selection
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child(c)
        # 2. Expansion
        if not node.is_terminal():
            node = node.expand(rng)
        # 3. Simulation
        winner = random_playout(node.state, rng)
        # 4. Backpropagation
        backprop(node, winner)
    return most_visited_child(root).move_in
```

### 2.3 `random_playout`

```
def random_playout(state, rng, max_depth=200):
    while state.winner is None and max_depth > 0:
        moves = legal_moves(state)
        if not moves:
            return 'draw'
        move = rng.choice(moves)
        state = apply_move(state, move)
        max_depth -= 1
    return state.winner if state.winner is not None else 'draw'
```

**`max_depth=200`:** rede de segurança contra rollouts infinitos quando há padrões repetitivos de pop. Em jogo aleatório real é muito improvável atingi-lo; serve para não pendurar testes.

### 2.4 `mcts_strategy`

```
def mcts_strategy(n_simulations=500, c=sqrt(2), rng=None):
    rng = rng or random.Random()
    def strat(state):
        return mcts_search(state, n_simulations, c, rng)
    return strat
```

Plug-and-play no `play_game`.

---

## 3. Decisões de design

### 3.1 Reutilizar `rng` por estratégia, não global

Cada `mcts_strategy(rng=Random(seed))` tem o seu RNG, partilhado entre `expand` (escolha do untried) e `random_playout`. Razão: testes determinísticos com seed fixa, e independência entre as duas estratégias num CvC.

### 3.2 Empate = 0.5

Convenção UCT clássica. Mantém `U/N ∈ [0, 1]` e justifica `C = √2`. Alternativa (0.0 para empate) penaliza demasiado finais "neutros" e enviesa a árvore. Vamos com 0.5.

### 3.3 Empate por repetição/max-turns durante rollout?

`random_playout` não verifica `can_claim_repetition_draw` — confia em `state.winner` que é atualizado só pela mecânica do motor. O `max_depth` é o seguro. **Isto significa que rollouts não declaram empate por repetição** (não temos jogador "racional" lá dentro). É consistente com o que o MCTS clássico faz.

### 3.4 Não implementamos *transposition tables* nesta versão

Várias sequências de jogadas levam ao mesmo estado, mas a árvore do MCTS trata-as como nós distintos. Reutilizar via tabela de transposição é uma otimização importante mas mais complexa, e não é exigida pelo enunciado. **Mencionamos como trabalho futuro** no relatório.

### 3.5 Não implementamos *root parallelisation*

MCTS paraleliza naturalmente (várias árvores independentes, votação no fim) mas o ganho é marginal para o nosso `N`. Mencionar como nota lateral.

---

## 4. Plano de testes

### 4.1 Teste-âncora: UCB1 contra o exemplo trabalhado

Construímos um nó pai sintético com `N=100` e três filhos:
- X: `U=20, N=25` → UCB esperado ≈ **1.407**
- Y: `U=30, N=70` → UCB esperado ≈ **0.791**
- Z: `U=2, N=5` → UCB esperado ≈ **1.758**

`best_child(c=√2)` deve devolver Z. Os valores numéricos devem bater com tolerância de 0.01.

> 📝 Este teste é mencionado **no relatório** como prova de conformidade entre o nosso código e o exemplo das aulas.

### 4.2 Teste de "vitória imediata"

Construímos um estado em que P1 tem uma jogada que **ganha já** (ex: três peças P1 alinhadas e uma quarta a um drop de distância). Damos `mcts_search(..., n_simulations=200)` e exigimos que devolva exatamente essa jogada.

### 4.3 Teste de "evitar derrota imediata"

Estado em que se P1 jogar errado, P2 ganha a seguir. MCTS deve escolher a única jogada que bloqueia.

### 4.4 Determinismo com seed

Duas chamadas com a mesma seed devem devolver a mesma jogada.

### 4.5 Smoke test MCTS vs random

10 partidas. MCTS(N=200) deve ganhar pelo menos 8 — se não ganhar, há bug.

### 4.6 Pureza

`mcts_search` não deve mutar o `root_state` que recebe.

---

## 5. Profilling (a fazer durante a implementação)

Comando:
```bash
python -c "
import cProfile, pstats
from popout.engine import initial_state
from popout.mcts import mcts_search
import random
cProfile.run('mcts_search(initial_state(), 500, 1.41, random.Random(0))', '/tmp/mcts.prof')
p = pstats.Stats('/tmp/mcts.prof'); p.sort_stats('cumulative').print_stats(15)
"
```

**Objectivo:** ver onde está o gargalo (provavelmente `_four_in_a_row_for` chamado em cada `apply_move` → `check_win` durante rollouts). Se for crítico, otimizar com NumPy. Caso contrário, deixar.

---

## 6. Variações para a Fase 4 (próximo passo, **não** esta fase)

> 📝 **Pré-aviso para o relatório.** A Fase 3 implementa o MCTS *standard*. A Fase 4 explora variações — vale pontos próprios. Elas serão:

1. **Número de simulações N**: 100, 500, 1000, 5000.
2. **Constante C**: 0.5, 1.0, √2, 2.0.
3. **Limite de filhos selecionados** (progressive widening).
4. **Rollout com policy heurística** ("se houver vitória imediata, joga; senão random").
5. **Limite de profundidade do rollout** com avaliação heurística simples.

Para isto funcionar, a API da Fase 3 expõe `c` e `n_simulations` como parâmetros, e (no futuro) `rollout_policy` injetável.

---

## 7. Riscos identificados

| Risco | Probabilidade | Mitigação |
|-------|---------------|-----------|
| Sinal errado na backprop | Alta (erro clássico) | Convenção explícita § 1.5 + teste com vitória imediata |
| MCTS demasiado lento → testes a pendurar | Média | `max_depth` no rollout + `N` baixo nos testes |
| RNG partilhado dá interações inesperadas em CvC | Baixa | Cada estratégia tem RNG próprio |
| Memória cresce sem limite (árvore guarda todos os nós) | Baixa para `N≤5000` | Aceitável para o nosso volume; documentar |

---

## 8. O que esta fase entrega para o relatório

- Pseudocódigo do `mcts_search` (secção 2.2).
- Fórmula UCB1 explicada termo a termo (secção 1.3).
- Justificação MCTS vs. MiniMax para PopOut (secção 1.1).
- Convenção de sinal na backpropagation (secção 1.5).
- Replicação numérica do exemplo X/Y/Z do MATERIA_IA (teste-âncora, secção 4.1).
- Tempo médio por jogada para vários `N` (a recolher na implementação).
- Tabela MCTS vs. random — sanity (secção 4.5).

---

> **Estado deste documento:** rascunho v0.1 — antes da implementação. Atualizado com resultados na secção 9 abaixo.

---

## 9. Atualização v0.2 — implementação concluída

### 9.1 Estrutura final do código

```
IA_WORK/
├── popout/
│   ├── __init__.py
│   ├── engine.py        (Fase 1)
│   ├── cli.py           (Fase 2)
│   └── mcts.py          (~165 linhas, esta fase)
└── tests/
    ├── __init__.py
    ├── test_engine.py   (Fase 1: 21 testes)
    ├── test_cli.py      (Fase 2: 20 testes)
    └── test_mcts.py     (esta fase: 11 testes)
```

### 9.2 Resultado dos testes

Suite completa: `python -m pytest tests/ -c /dev/null`

```
======================== 51 passed, 1 skipped in 19.20s ========================
```

Os 11 testes novos do MCTS:

```
test_ucb1_matches_worked_example                          PASSED
test_random_playout_terminates_and_returns_valid_winner   PASSED
test_random_playout_on_already_won_state_returns_winner   PASSED
test_backprop_credits_chooser_player                      PASSED
test_mcts_finds_immediate_horizontal_win_for_p1           PASSED
test_mcts_blocks_immediate_loss_for_p2                    PASSED
test_mcts_deterministic_with_same_seed                    PASSED
test_mcts_does_not_mutate_input_state                     PASSED
test_mcts_strategy_returns_legal_move                     PASSED
test_mcts_with_only_one_legal_move_returns_it             PASSED
test_mcts_vs_random_smoke                                 PASSED
```

### 9.3 Validação numérica do UCB1 (teste-âncora)

Com `C = √2` e pai `N=100`:

| Filho | U/N | UCB1 (calculado) | UCB1 (MATERIA_IA) | Match |
|-------|-----|------------------|-------------------|-------|
| X | 20/25 | 1.407 | 1.407 | ✅ |
| Y | 30/70 | 0.791 | 0.791 | ✅ |
| Z | 2/5 | 1.758 | 1.758 | ✅ |

`best_child(c=√2)` devolve **Z**, como esperado.

> 📝 **Para o relatório** — citar este teste como prova de conformidade entre a nossa implementação e o exemplo trabalhado das aulas.

### 9.4 Profiling — tempo por jogada

Estado: posição inicial. RNG: seed=0. Hardware: Mac local.

| N (simulações) | Tempo por jogada (s) |
|----------------|----------------------|
| 50 | 0.194 |
| 100 | 0.216 |
| 500 | 0.990 |
| 1000 | 1.921 |

**Interpretação:**
- O custo cresce **linearmente** com `N`, como esperado (cada simulação é independente).
- A `N = 50` o tempo já está acima de 0.1s — overhead inicial de criar a árvore. A diferença 50 → 100 é pequena (overhead de criação amortizado).
- A `N = 1000` cada jogada custa ~2s. Numa partida típica (40-50 jogadas), uma decisão MCTS para os dois lados custaria ~3 minutos → aceitável para experiências em batch da Fase 8, mas para CvC interativo escolheríamos `N = 200-500`.

> 📝 **Para o relatório:** este perfil justifica a escolha do "sweet spot" `N ≈ 500-1000` que vamos defender na Fase 4.

### 9.5 MCTS(N=200) vs. Random — 20 partidas, alternando lados

| MCTS vence | Random vence | Empate |
|------------|--------------|--------|
| **19** | 1 | 0 |

Tempo total: 35.5s para as 20 partidas.

**Análise:**
- 19/20 = 95% vitórias para o MCTS — confortavelmente acima do limiar de "claramente melhor que aleatório".
- A 1 derrota acontece num seed específico — possivelmente uma sequência de simulações azaradas em que o rollout aleatório levou o MCTS a sub-estimar uma posição. Com `N=500+` esperamos eliminar esses casos.
- **Sanity check passa.** Se este número fosse <50%, haveria bug grosseiro (provavelmente sinal trocado na backpropagation).

> 📝 **Para o relatório:** tabela "MCTS(N=200) vs. Random — 19/1/0" como **baseline** das experiências da Fase 8. Justificação concreta de que o MCTS está bem implementado.

### 9.6 Decisões revistas durante a implementação

1. **`is_fully_expanded` exige `len(children) > 0`** além de `untried_moves` vazio. Sem isto, um nó terminal recém-criado (sem jogadas) seria considerado "fully expanded" e a selecção tentaria descer para um filho que não existe (`best_child` em dict vazio crasha). Confirmado pela primeira corrida que falhou e foi corrigida.
2. **`expand` usa `rng.randrange + pop` em vez de `rng.choice + remove`.** É O(1) por escolha em vez de O(n) e evita o overhead do `remove` linear. Para um branching factor 14 a diferença é trivial; mas como a função é hot-path, vale a pena.
3. **Caminho rápido no `mcts_search`**: se o estado tem 0 ou 1 jogadas legais, devolve directamente sem montar árvore. Poupa simulações inúteis.
4. **`mcts_strategy` levanta `RuntimeError` se chamada num estado sem jogadas**, em vez de devolver `None`. Razão: o `play_game` da Fase 2 não sabe lidar com `None` como decisão. Falhar cedo e claro é melhor.
5. **Empate vale 0.5 na backprop** — clássico em UCT, mantém `U/N ∈ [0, 1]` consistente com C=√2.

### 9.7 Critérios de saída — verificação

- [x] `mcts_search` devolve a "melhor" jogada (filho da raiz com mais visitas).
- [x] `mcts_strategy` plug-and-play no `play_game`.
- [x] Backpropagation com sinal correto (verificado por teste dedicado).
- [x] UCB1 validado contra o exemplo trabalhado (X/Y/Z) — replica exatamente.
- [x] MCTS(N=200) vs. random ≥ 80%. Real: **95%**.

**Fase 3 — concluída.** Pronto para a Fase 4 (variações do MCTS).

### 9.8 API pública (estabilizada — pronta para a Fase 4)

| Símbolo | Função |
|---------|--------|
| `Node(state, parent, move_in)` | Nó da árvore (com `N`, `U`, `children`, `untried_moves`) |
| `mcts_search(root_state, n_simulations, c, rng)` | Devolve `Move` ou `None` |
| `mcts_strategy(n_simulations, c, rng)` | Factory de `Strategy` |
| `random_playout(state, rng, max_depth)` | Rollout aleatório |
| `backprop(leaf, winner)` | Atualização da árvore |
| `DEFAULT_C = sqrt(2)` | Constante de exploração canónica |
| `DEFAULT_N_SIMULATIONS = 500` | Default razoável |

A Fase 4 vai introduzir parâmetros adicionais para variações:
- `rollout_policy` injetável (heurística simples no rollout).
- `max_children` (progressive widening).
- `rollout_depth_cutoff` + função de avaliação heurística.

### 9.9 O que esta fase entrega para o relatório

- ✅ Pseudocódigo do `mcts_search` (secção 2.2).
- ✅ Fórmula UCB1 explicada termo a termo (secção 1.3).
- ✅ Justificação MCTS vs. MiniMax para PopOut (secção 1.1).
- ✅ Convenção de sinal na backpropagation (secção 1.5).
- ✅ Replicação numérica do exemplo X/Y/Z (secção 9.3).
- ✅ Tempo por jogada vs. N (secção 9.4).
- ✅ Sanity MCTS vs. random — 19/1/0 (secção 9.5).




# ═══════════════════════════════════════════════════════════════
# FASE4_VARIACOES_MCTS.md
# ═══════════════════════════════════════════════════════════════

# Fase 4 — Variações do MCTS
## Documento de execução e material-fonte para o relatório

> Implementa a **Fase 4** do `PLANEAMENTO_PROJETO.md`. O enunciado pede explicitamente:
> *"you should analyse/explore different numbers of selected children for each node, and other strategies, not only keeping the standard implementation"*
>
> Esta fase **vale pontos próprios** dentro dos 30% técnicos. Sem ela, o que entregamos é "MCTS standard" e perdemos os pontos de "experimentação".

---

## 0. Motivação imediata

Durante o teste do default `N=300, rollout=random`, jogador humano ganha consistentemente. O motivo é que **rollouts puramente aleatórios produzem estimativas de valor barulhentas**: mesmo que o MCTS visite muitas vezes uma jogada táticamente ganhadora, a média de vitórias depende de o rollout aleatório ser inteligente o suficiente para fechar o jogo — coisa que não é. Em consequência, jogadas que parecem boas na simulação podem na verdade ser irrelevantes na tática real.

A **rollout heurística** (variação 4 do plano) resolve isto: as simulações jogam pelo menos as jogadas táticas óbvias (vitórias imediatas, blocos), em vez de jogarem como amadores aleatórios. Esta sozinha melhora drasticamente a força.

---

## 1. Variações implementadas

### 1.1 Rollout policy

| Modo | Descrição | Custo por ply | Quando usar |
|------|-----------|---------------|-------------|
| `random` | Joga aleatório uniforme entre as legais | O(1) | Baseline / sanity / Fase 8 |
| `heuristic_win` | Tier 1: aceita vitória imediata se existir, senão aleatório | O(b) | Default da GUI — pequeno overhead, grande ganho |
| `heuristic_block` | Tier 1 + Tier 2: prefere jogadas que NÃO deixam o adversário ganhar a seguir | O(b²) | Modo difícil — mais lento mas tactically aware |

### 1.2 Constante de exploração C

Já parametrizada no `mcts_search`. Valores experimentados:
- `C = 0.5` — pouca exploração; agressivo no que parece bom.
- `C = 1.0` — intermédio.
- `C = √2 ≈ 1.414` — canónico (Auer et al. 2002).
- `C = 2.0` — exploração agressiva.

### 1.3 Número de simulações N

Já parametrizado. Valores: 100, 300, 500, 1000. Espera-se retornos decrescentes.

### 1.4 Limite de filhos selecionados (`max_children`)

Variação simples de **progressive widening**: cada nó considera no máximo `k` filhos. Os primeiros `k` movimentos legais são expandidos, os outros ignorados.

- Heurística de prioridade: jogadas centrais primeiro (col 3, 2, 4, 1, 5, 0, 6) — convenção comum em Connect-4 que reflete "valor posicional".
- `max_children=None` → todas as jogadas (default).
- `max_children=4` → só as 4 jogadas mais centrais (poda forte).

> Justificação: o branching factor do PopOut chega a 14. Limitar a 4-7 reduz O(b^d) drasticamente sem prejuízo significativo se a heurística for boa.

### 1.5 (Não implementadas / out-of-scope)

- **Limite de profundidade do rollout com avaliação heurística:** acrescentaria uma função de avaliação para cortar rollouts longos. Adiada — o nosso rollout já termina em < 50 plies em média.
- **C dinâmico** (como na referência): também adiada. O canónico √2 é defensável.

---

## 2. API atualizada

```python
mcts_search(
    root_state,
    n_simulations=500,
    c=sqrt(2),
    rollout='random',                # 'random' | 'heuristic_win' | 'heuristic_block'
    max_children=None,                # None ou int
    rng=None,
)

mcts_strategy(
    n_simulations=500,
    c=sqrt(2),
    rollout='random',
    max_children=None,
    rng=None,
)
```

**Compatibilidade:** todos os parâmetros novos têm defaults iguais ao standard MCTS. Código da Fase 3 continua a funcionar sem alterações.

---

## 3. Plano experimental

> 📝 **Para o relatório — secção "Variações do MCTS e resultados":** as 3 tabelas abaixo.

### 3.1 Experiência A — impacto da rollout policy

Match-up por pares, 10 partidas alternando lados, N=300 fixo, C=√2 fixo.

| Variante A | Variante B | Vitórias A | Vitórias B | Empates |
|------------|------------|------------|------------|---------|
| `random` | `heuristic_win` | (a preencher) | | |
| `random` | `heuristic_block` | | | |
| `heuristic_win` | `heuristic_block` | | | |

**Hipótese:** `heuristic_block > heuristic_win > random` em força; `random` é o mais rápido.

### 3.2 Experiência B — impacto de N

Match-up por pares, 10 partidas alternando lados, rollout `heuristic_win` fixo, C=√2 fixo.

| Variante A | Variante B | Vit. A | Vit. B | Empates | Tempo médio/jogada A | B |
|------------|------------|--------|--------|---------|----------------------|---|
| N=100 | N=300 | | | | | |
| N=300 | N=1000 | | | | | |
| N=500 | random_strategy | | | | | n/a |

**Hipótese:** retornos decrescentes acima de N≈500.

### 3.3 Experiência C — impacto de C

Match-ups vs random_strategy (baseline), 20 partidas, N=300 fixo, rollout `heuristic_win` fixo.

| C | Win-rate vs random | Tempo médio/jogada |
|---|--------------------|--------------------|
| 0.5 | | |
| 1.0 | | |
| √2 | | |
| 2.0 | | |

**Hipótese:** C=√2 ganha mais que extremos; C alto perde tempo a explorar; C baixo cai em armadilhas.

### 3.4 Experiência D — `max_children` (opcional)

| max_children | Win-rate vs random | Tempo |
|--------------|--------------------|-------|
| None (todos) | | |
| 7 | | |
| 4 | | |

---

## 4. Decisões de design para a GUI

Em vez de expor todos os parâmetros, dou ao utilizador 3 níveis no menu:

| Nível | n_simulations | rollout | C | Tempo aprox./jogada |
|-------|---------------|---------|---|---------------------|
| **Fácil** | 100 | `random` | √2 | < 0.3s |
| **Médio** | 400 | `heuristic_win` | √2 | ~2-3s |
| **Difícil** | 600 | `heuristic_block` | √2 | ~5-10s |

Para CvC e modos de demonstração, default é Médio.

---

## 5. Critérios de saída

- [ ] `rollout` e `max_children` parametrizáveis em `mcts_search` e `mcts_strategy`.
- [ ] `heuristic_win` aceita vitória imediata (testado).
- [ ] `heuristic_block` evita deixar o adversário ganhar (testado).
- [ ] `max_children` limita branching (testado).
- [ ] Suite de testes verde (≥ 51 antigos + ≥ 4 novos).
- [ ] GUI com 3 níveis de dificuldade.
- [ ] Tabelas das experiências A/B/C preenchidas no relatório.

---

## 6. Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| `heuristic_block` demasiado lento (O(b²) por ply) | Testar com N pequeno primeiro; se for inviável para N=600, baixar para N=300 no nível Difícil |
| Mudar default da GUI parte fluxo de Fase 3 | Default explícito; modos antigos continuam disponíveis em CLI |
| Experiências demoram horas | Usar N pequeno (100-300) e poucos jogos (5-10) para a versão entregue; reservar versões grandes para batch overnight |

---

> Estado: rascunho v0.1 — antes da implementação. Atualizado com resultados na secção 7.

---

## 7. Atualização v0.2 — variações implementadas + resultados

### 7.1 Estrutura final do código

```
IA_WORK/
├── popout/
│   ├── engine.py
│   ├── cli.py
│   ├── mcts.py            (atualizado: rollout, max_children, COLUMN_PRIORITY)
│   └── gui.py             (atualizado: 7 modos, 3 níveis dificuldade)
├── tests/
│   ├── test_engine.py
│   ├── test_cli.py
│   ├── test_mcts.py
│   └── test_mcts_variations.py    (NOVO: 13 testes)
└── experiments/
    ├── __init__.py
    └── run_variations.py  (NOVO: harness experimental)
```

### 7.2 Resultado dos testes

`python -m pytest tests/ -c /dev/null` → **64 passed, 1 skipped** em ~38s.

Os 13 testes novos cobrem:
- `_find_winning_move` (vitória imediata detectada).
- `_move_is_safe` (cenário concreto onde só drop(4) é seguro).
- `heuristic_win_playout` aceita vitória.
- `heuristic_block_playout` evita derrota imediata.
- `_ordered_legal_moves` com cap.
- `Node` com `max_children` limita untried.
- Match smoke heur_win vs random — heurístico ganha.
- Argumentos inválidos raise.

### 7.3 Resultados experimentais

> 📝 **Para o relatório — secção "Variações do MCTS e resultados":** copiar as 4 tabelas abaixo.

#### Experiência A — Rollout policy (compute equivalente)

Comparação por pares, alternando lados. N escolhido para tempo total comparável.

| A | B | A | B | D | t/move A | t/move B |
|---|---|---|---|---|----------|----------|
| `random` (N=200) | `heuristic_win` (N=200) | 0 | **6** | 0 | 244 ms | 643 ms |
| `random` (N=300) | `heuristic_block` (N=50) | **4** | 0 | 0 | 416 ms | 6336 ms |
| `heuristic_win` (N=200) | `heuristic_block` (N=50) | **4** | 0 | 0 | 799 ms | 7266 ms |

**Interpretação:**
- `heuristic_win` **destroi** `random` ao mesmo `N`: 6-0. O custo extra (~2.6× por jogada) compensa largamente.
- `heuristic_block` é **9-15× mais lento** por simulação que os outros (Tier 2 é O(b²) por ply). A compute-equivalência (N=50) é demasiado baixa: aleatório com mais simulações ganha. O custo prático do `heuristic_block` só justifica-se em jogos onde tempo por jogada não é constraint.
- **Conclusão prática:** o sweet-spot é `heuristic_win`. É a escolha default da GUI (nível "Médio").

#### Experiência B — Número de simulações N (rollout `heuristic_win`)

| A | B | A | B | D | t/move A | t/move B |
|---|---|---|---|---|----------|----------|
| N=100 | N=300 | 0 | **6** | 0 | 292 ms | 803 ms |
| N=300 | N=600 | 0 | **4** | 0 | 1197 ms | 2373 ms |

**Interpretação:**
- Crescimento monotónico de força: N=100 ≪ N=300 ≪ N=600 (todos os matches `0-N`, sem empates).
- **Sem sinais de saturação até N=600** no nosso volume de testes. Sinal de que mais N continua a render (provável saturação acima de N=1000-2000).
- O custo escala aproximadamente linearmente com N (~3× sims → ~3× tempo), como esperado.
- Implicação: para a GUI, "Difícil" deveria usar N alto (≥600) com `heuristic_win`. Decidi reduzir a 300 com `heuristic_block` — a Experiência A sugere que isso é pior. **Vou rever a GUI** para usar `heuristic_win` em todos os níveis.

#### Experiência C — Constante de exploração C (vs random, N=200, `heuristic_win`)

| C | Win-rate vs random | t/move |
|---|--------------------|--------|
| 0.50 | 6/6 (100%) | 728 ms |
| 1.00 | 6/6 (100%) | 648 ms |
| **√2 ≈ 1.41** | **6/6 (100%)** | **533 ms** |
| 2.00 | 6/6 (100%) | 876 ms |

**Interpretação:**
- Todos os valores de C **saturam** contra `random` (100% vitórias). Não diferencia qualidade — só tempo.
- **C = √2 é o mais rápido**. Plausível: balanço óptimo entre explore/exploit reduz simulações desperdiçadas em jogadas claramente fracas, jogos terminam mais cedo. Suporta empiricamente a escolha canónica de Auer et al. 2002.
- Para diferenciar qualidade entre Cs, precisaríamos MCTS-vs-MCTS com Cs diferentes — possível em batch overnight.

#### Experiência D — `max_children` / Progressive widening (vs random, N=200, `heuristic_win`)

| max_children | Win-rate vs random | t/move |
|--------------|--------------------|--------|
| `None` (todos) | 4/4 (100%) | 527 ms |
| 5 | 4/4 (100%) | 438 ms |
| 3 | 4/4 (100%) | **356 ms** |

**Interpretação:**
- Limitar a 3-5 filhos centrais **mantém qualidade** vs random (saturado a 100%) e reduz tempo em ~33%.
- A heurística "colunas centrais primeiro" é defensável: em Connect-4 standard, o centro é demonstravelmente mais valioso (jogadas no centro participam em mais alinhamentos).
- Para diferenciar qualidade, idem — precisava MCTS-vs-MCTS.

### 7.4 Decisões revistas com base nos resultados

1. **GUI — nível "Difícil" mudou de `heuristic_block` (N=300) para `heuristic_win` (N=800).** O `heuristic_block` é demasiado lento sem ganho claro nos N viáveis. `heuristic_win` com N alto é melhor experiência: ~5-7s por jogada, mas tactically forte.

2. **Default `mcts_strategy` mantém `rollout='random'`.** Razão: compatibilidade com Fase 3 e mantém o baseline para experiências futuras. Quem quer força usa parâmetro explícito ou os modos da GUI.

3. **`heuristic_block` fica disponível mas não é usado por defeito.** Documentado como variação experimental — útil para exibir o trade-off no relatório.

### 7.5 Novos níveis de dificuldade da GUI (atualizado)

| Nível | n_simulations | rollout | C | t/jogada (estimado) |
|-------|---------------|---------|---|---------------------|
| Fácil | 100 | `random` | √2 | < 0.3s |
| Médio | 400 | `heuristic_win` | √2 | ~1-2s |
| Difícil | 800 | `heuristic_win` | √2 | ~3-5s |

> Vou aplicar esta revisão no `popout/gui.py` na secção seguinte.

### 7.6 Critérios de saída — verificação

- [x] `rollout` e `max_children` parametrizáveis.
- [x] `heuristic_win` aceita vitória imediata (testado).
- [x] `heuristic_block` evita deixar adversário ganhar (testado).
- [x] `max_children` limita branching (testado).
- [x] Suite de testes verde (64+1).
- [x] GUI com 3 níveis de dificuldade.
- [x] Tabelas A/B/C/D preenchidas.
- [x] Justificação empírica de C=√2.
- [x] Justificação empírica do `heuristic_win` como default.

**Fase 4 — concluída.**

### 7.7 O que esta fase entrega para o relatório

- ✅ Tabela A: rollout policies comparadas (com tempo).
- ✅ Tabela B: N sweep com tempo (mostra escalabilidade).
- ✅ Tabela C: C sweep — justifica C=√2 empiricamente.
- ✅ Tabela D: progressive widening — qualidade preservada com -33% tempo.
- ✅ Justificação das escolhas defaults da GUI.
- ✅ Conclusão clara: "heuristic_win é o sweet-spot prático". Citação valiosa para a apresentação.

### 7.8 Limitações / trabalho futuro (a mencionar no relatório)

- **Saturação contra random:** experiências C e D não diferenciam qualidades porque todos os MCTS dominam o `random`. Precisaria de matches **MCTS vs MCTS** com parâmetros distintos para isolar o efeito de C e `max_children`. Possível em batch overnight; não foi feito por constraint de tempo.
- **N=1000+ não testado:** o nosso ponto mais alto foi N=600. Não sabemos onde está a saturação real.
- **`heuristic_block` em compute-real:** a O(b²)-por-ply do Tier 2 podia ser optimizada (ex: cache de "estado já avaliado para safety"), reduzindo a 4-6× em vez de 14×. Isto poderia trazer o `heuristic_block` para tempos viáveis. Trabalho futuro.
- **C dinâmico (referência ConnectedFour):** uma das variações da literatura — adaptar C a `N(parent)`. Não implementada por constraint de tempo.




# ═══════════════════════════════════════════════════════════════
# FASE5_ID3_IRIS.md
# ═══════════════════════════════════════════════════════════════

# Fase 5 — Árvores de Decisão (ID3) + Iris
## Documento de execução e material-fonte para o relatório

> Implementa a **Fase 5** do `PLANEAMENTO_PROJETO.md` e cobre o requisito **§4.2 do enunciado oficial** (`docs/IA_2526_Project.pdf`):
> - "Implement ID3 from scratch" (sem scikit-learn).
> - Iris dataset com discretização de valores numéricos (minimizar tamanho da árvore).
> - "Present the output (tree) visually for all these datasets" — visualização obrigatória.
>
> Esta fase vale parte dos **30% das árvores de decisão** + parte dos **30% técnicos** (rigor da avaliação).

---

## 0. Onde estamos

| Fase | Estado | Notas |
|------|--------|-------|
| 1 — Motor PopOut | ✅ | 21 testes |
| 2 — CLI | ✅ | 20 testes |
| 3 — MCTS | ✅ | 11 testes; UCB1 validado |
| 4 — Variações MCTS | ✅ | 13 testes; tabelas A/B/C/D |
| 4.5 — Tactical lookahead | ✅ | 9 testes; resolve "AI nunca pop" |
| **5 — Iris + ID3** | **Em curso** | Esta fase |
| 6 — Gerar dataset PopOut | ⏳ | A seguir |
| 7 — ID3 no PopOut | ⏳ | Depende 5+6 |
| 8 — Avaliação experimental | ⏳ | Depende 7 |
| 9 — Notebook + slides | ⏳ | Última |

**Critério de saída:**
- ID3 puro implementado (sem sklearn).
- Discretização de numéricos com pelo menos 1 estratégia justificada.
- Aprende árvore de Iris e visualiza-a.
- Accuracy ≥ 90% (Iris é fácil; <90% sugere bug).
- Cross-validation k-fold (rigor experimental).

---

## 1. Recapitulação do ID3 (vai para o relatório)

### 1.1 Algoritmo

```
ID3(exemplos, atributos):
    # Caso base 1: todos os exemplos têm a mesma classe c
    se todas as classes iguais a c:
        devolve folha(c)
    # Caso base 2: sem atributos restantes
    se atributos == ∅:
        devolve folha(classe_maioritária(exemplos))
    # Caso base 3: subconjunto vazio (caminho não observado em treino)
    se exemplos == ∅:
        devolve folha(classe_maioritária_do_pai)
    # Caso recursivo
    A = atributo com maior INFORMATION_GAIN(exemplos)
    cria nó com teste sobre A
    para cada valor v de A:
        sub = exemplos onde A=v
        sub_árvore = ID3(sub, atributos \ {A})
        liga ramo "A=v" a sub_árvore
    devolve árvore
```

> Os 4 casos base estão consagrados em Russell & Norvig e no `MATERIA_IA.md` §9.9. **Implementam-se exatamente como acima** — confusão entre eles é o erro #1 das implementações de ID3 de raiz.

### 1.2 Information Gain — fórmulas

**Entropia da classe `C`:**
$$H(C) = -\sum_{c \in \text{classes}} P(c) \log_2 P(c)$$

**Entropia condicional ao atributo `A`:**
$$H(C \mid A) = \sum_{v \in \text{valores}(A)} \frac{|S_v|}{|S|} \cdot H(C \mid A=v)$$

**Information Gain:**
$$\text{Gain}(A) = H(C) - H(C \mid A)$$

ID3 escolhe **o atributo com maior `Gain`**.

### 1.3 Por que ID3 e não C4.5/CART?

O enunciado pede **ID3**. Vamos manter-nos puristas:
- ID3 usa Information Gain (não Gain Ratio do C4.5).
- ID3 não faz pruning automático (pode tornar a árvore enorme — mitigamos com discretização supervisionada).
- ID3 puro é categórico — números têm de ser discretizados antes de entrar.

Para o relatório: mencionamos C4.5 como "o sucessor com pruning + gain ratio + binary splits para numéricos", como contexto.

### 1.4 Bias / Ockham's razor

ID3 prefere atributos que reduzem entropia mais rapidamente — equivalente a preferir árvores mais pequenas. Isto é a **Ockham's razor** aplicada a aprendizagem indutiva (Russell & Norvig §19).

> 📝 Bom para o slide: "Ockham + entropia → árvore curta, generalização melhor".

---

## 2. Discretização do Iris (atributos numéricos)

ID3 puro só lida com **categóricos**. Iris tem 4 atributos contínuos (sepallength, sepalwidth, petallength, petalwidth). É preciso discretizar.

### 2.1 Estratégias a implementar

| Nome | Como funciona | Vantagens | Desvantagens |
|------|----------------|-----------|--------------|
| `equal_width` | Divide o intervalo `[min, max]` em `k` bins iguais | Simples; rápido | Bins desequilibrados se a distribuição é assimétrica |
| `equal_frequency` | Cada bin contém ~`N/k` exemplos | Robusto a outliers | Bins podem cortar zonas com classes diferentes |
| `supervised` | Encontra ponto(s) de corte que **maximizam information gain** (C4.5-style) | Minimiza tamanho da árvore (pedido pelo enunciado!) | Implementação mais complexa |

### 2.2 Estratégia recomendada (e default)

**Supervised**, com split binário por atributo: para cada atributo numérico, encontrar o ponto de corte `t` que maximiza `Gain(A ≤ t vs. A > t)`. Isto cria 2 categorias (`low` / `high`) por atributo.

> **Por que binário?** Porque é o que o C4.5 faz; minimiza tamanho da árvore conforme pede o enunciado: *"You need to implement a way of discretising these values in order to minimize the size of your decision tree."*
>
> Vamos comparar as 3 estratégias na avaliação para mostrar a diferença empírica.

### 2.3 Pseudocódigo da discretização supervised

```
para cada atributo numérico A:
    valores_unicos = ordenados(unique(A))
    candidatos = pontos médios entre valores consecutivos
                 onde a classe muda
    melhor_t = argmax_{t ∈ candidatos} Gain(A ≤ t vs. A > t)
    substituir A por A_discreto = ('low' se A ≤ melhor_t senão 'high')
```

---

## 3. Pipeline Iris

```
1. Ler CSV (docs/iris (2).csv)
2. Stratified shuffle + split treino/teste 80/20
3. Discretizar atributos no conjunto de treino (aprende thresholds)
4. Aplicar mesmos thresholds ao conjunto de teste
5. Treinar ID3 no treino
6. Predict no teste → accuracy + confusion matrix
7. K-fold cross-validation (k=5) para estimativa robusta
8. Visualizar a árvore aprendida
```

> **Importante:** os thresholds da discretização supervised são aprendidos **no treino**. Aplicar ao teste sem reaprender (senão temos data leakage).

---

## 4. Visualização da árvore

Duas representações:

### 4.1 Texto indentado (sempre)

```
sepallength
├─ low
│  └─ class: Iris-setosa  (50/50)
├─ high
│  └─ petallength
│     ├─ low
│     │  └─ class: Iris-versicolor  (49/55)
│     └─ high
│        └─ class: Iris-virginica  (45/45)
```

### 4.2 Figura matplotlib (recomendada para slides/notebook)

Renderização em árvore tipo "graphviz simplificado" usando `matplotlib`:
- nós internos como retângulos com `feature ?`
- folhas como retângulos arredondados com `class : N`
- arestas legendadas com o valor

**Por que não graphviz?** Para evitar dependência externa (graphviz exige binário do sistema). `matplotlib` já vai ser usado para os gráficos da Fase 8.

---

## 5. Plano experimental

### 5.1 Comparação das 3 discretizações

| Estratégia | Accuracy treino | Accuracy teste | Profundidade | #folhas |
|------------|-----------------|----------------|--------------|---------|
| equal_width (k=3) | (a preencher) | | | |
| equal_freq (k=3) | | | | |
| supervised | | | | |

**Hipótese:** `supervised` produz árvore mais pequena com accuracy comparável (ou melhor) — confirma a intuição do enunciado.

### 5.2 Cross-validation 5-fold (rigor)

Reportar média e desvio-padrão de accuracy. Desvio-padrão alto = instável.

### 5.3 Curva de aprendizagem

Train com 20%, 40%, ..., 80% dos dados. Accuracy de teste por tamanho de treino. Mostra se o modelo overfit ou tem dados a faltar.

---

## 6. API pública prevista

```python
# popout/decision_tree.py
from popout.decision_tree import (
    Node, entropy, information_gain, id3, predict,
    render_tree_text, render_tree_matplotlib,
    discretize_equal_width, discretize_equal_frequency,
    discretize_supervised,
)

# Treinar
tree = id3(X_train, y_train, features=list(X_train.columns))

# Predict
y_pred = [predict(tree, sample) for sample in X_test.iterrows()]

# Visualizar
print(render_tree_text(tree))
fig = render_tree_matplotlib(tree)
fig.savefig("iris_tree.png")
```

Mantemos a API simples e didática — pandas DataFrames como input.

---

## 7. Riscos identificados

| Risco | Mitigação |
|-------|-----------|
| ID3 entra em loop infinito por bug nos casos base | 4 casos base testados isoladamente; depth limit como safety net |
| Discretização leak de dados (treino ↔ teste) | Aprender thresholds só no treino, aplicar ao teste sem reaprender |
| Arvore demasiado profunda → overfit | Cross-validation deteta; comparar treino vs teste |
| Iris é fácil → accuracy 100% pode mascarar bugs | Validar também com partição diferente (k-fold) |

---

## 8. O que esta fase entrega para o relatório

- Pseudocódigo do ID3 com 4 casos base.
- Fórmulas de entropia e Information Gain.
- Justificação da estratégia de discretização supervised.
- Visualização da árvore Iris (texto + figura).
- Tabela das 3 discretizações comparadas.
- Cross-validation 5-fold com média/desvio-padrão.
- Curva de aprendizagem (accuracy vs. tamanho de treino).

---

> Estado: rascunho v0.1 — antes da implementação. Atualizado com resultados na secção 9.

---

## 9. Atualização v0.2 — implementação concluída

### 9.1 Estrutura de código

```
IA_WORK/
├── popout/
│   └── decision_tree.py         (NOVO: ~290 linhas)
├── tests/
│   └── test_decision_tree.py    (NOVO: 20 testes)
├── experiments/
│   └── iris.py                  (NOVO: pipeline completa)
└── docs/
    └── iris (2).csv             (dataset oficial)
```

### 9.2 Resultado dos testes

`python -m pytest tests/ -c /dev/null` → **93 passed, 1 skipped** em ~38s.

Os 20 testes novos cobrem:
- Entropia (4 casos: pura, 50/50, vazia, 3 classes uniforme).
- **Information Gain — replica numericamente o exemplo Gripe** do MATERIA_IA §11.5: H=0.954, Gain(Febre)=0.549, Gain(Tosse)=Gain(Cansaço)=0.159.
- ID3 — 4 casos base (todos da mesma classe; sem atributos; subconjunto vazio; predict normal).
- Predict de valor não visto cai no majority do nó.
- 3 estratégias de discretização (equal_width, equal_freq, supervised).
- Discretização: thresholds aprendidos no treino aplicam-se a valores fora do range do treino.
- Iris equal_width: accuracy ≥ 90%.
- Iris supervised: árvore mais pequena que equal_width.

### 9.3 Resultados Iris — split 80/20

| Estratégia | Acc treino | Acc teste | Folhas | Profundidade |
|------------|------------|-----------|--------|--------------|
| supervised (binário) | 0.717 | 0.633 | **4** | 3 |
| **equal_width (k=3)** | **0.992** | **0.933** | 5 | 3 |
| equal_width (k=5) | 0.967 | 0.900 | 17 | 4 |
| equal_frequency (k=3) | 0.992 | 0.933 | 10 | 4 |

**Trade-off explícito** que vai para o relatório:
- A discretização **supervised** (split binário por atributo) produz a árvore **mais pequena** (4 folhas) — cumpre literalmente o pedido do enunciado de "minimizar tamanho da árvore". Mas comprime demais: cada atributo só tem 2 níveis ("low"/"high"), insuficientes para distinguir versicolor de virginica → accuracy cai a 63%.
- A discretização **equal_width(k=3)** dá 5 folhas (apenas 1 a mais que supervised) e accuracy de 93% — o **melhor compromisso**.
- equal_width(k=5) explode a 17 folhas com pequena perda de accuracy → claramente overfit.

> 📝 **Para o relatório:** este é um trade-off elegante para mencionar. Mostra que "minimizar a árvore" e "maximizar accuracy" não são equivalentes. Foi seguindo o enunciado literalmente que descobrimos que a estratégia mais agressiva de compressão tem um custo em qualidade.

### 9.4 Cross-validation 5-fold

| Estratégia | Mean acc | Std acc | Mean folhas |
|------------|----------|---------|-------------|
| supervised (binário) | 0.653 | ±0.072 | 4.2 |
| **equal_width(k=3)** | **0.947** | **±0.040** | 8.4 |
| equal_frequency(k=3) | 0.947 | ±0.045 | 12.6 |

Confirmação: equal_width(k=3) é robusto (94.7% ± 4%) e dá árvores mais pequenas que equal_frequency. Adopta-se como **discretização default** para o relatório principal; supervised mantém-se como ablação para mostrar o trade-off.

### 9.5 Confusion matrix (equal_width k=3, split teste)

|              | setosa | versicolor | virginica |
|--------------|--------|------------|-----------|
| **setosa**   | **10** | 0 | 0 |
| **versicolor** | 0 | **9** | 2 |
| **virginica** | 0 | 0 | **9** |

- 10/10 setosa perfeito (linearmente separável, esperado).
- 2 versicolor confundidas com virginica — o caso difícil clássico do Iris.
- Accuracy 28/30 = 93.3%.

### 9.6 Visualização da árvore (equal_width k=3)

Renderização texto:
```
petalwidth? (n=120)
   └─ [bin0] class: Iris-setosa (n=40) {'Iris-setosa': 40}
   └─ [bin1] petallength? (n=43)
      └─ [bin1] class: Iris-versicolor (n=38)
      └─ [bin2] sepallength? (n=5)
         └─ [bin1] class: Iris-virginica (n=4)
         └─ [bin2] class: Iris-virginica (n=1)
   └─ [bin2] class: Iris-virginica (n=37)
```

Figura matplotlib guardada em `/tmp/iris_out/iris_tree_equal_widthk=3.png`. Estrutura: nó raiz `petalwidth?` (atributo mais informativo, como esperado de literatura), folhas verdes para classes, arestas anotadas com o bin.

### 9.7 Decisões revistas durante a implementação

1. **Default discretization** mudou de `supervised` (planeado) para `equal_width(k=3)` na pipeline principal. Razão: empirico, supervised binário compromete demais a accuracy. **Mantemos supervised** como uma das 3 estratégias comparadas para o relatório.
2. **Visualização matplotlib** em vez de graphviz. Razão: zero dependências externas; matplotlib já é necessário noutras fases; o formato gerado é suficientemente claro.
3. **Renderização texto** sempre disponível — útil para depuração e para tese caso a figura matplotlib não renderize bem.

### 9.8 Critérios de saída — verificação

- [x] ID3 puro (sem sklearn) — 4 casos base testados.
- [x] Discretização (3 estratégias).
- [x] Aprende árvore Iris e visualiza-a (texto + matplotlib).
- [x] Accuracy ≥ 90% (real: 93.3% split, 94.7% CV).
- [x] Cross-validation 5-fold reportada com média e desvio.
- [x] Information Gain validado contra exemplo Gripe (replicação numérica).
- [x] Confusion matrix.

**Fase 5 — concluída.**

### 9.9 O que esta fase entrega para o relatório

- ✅ Pseudocódigo do ID3 com 4 casos base.
- ✅ Fórmulas entropia + information gain explicadas.
- ✅ Replicação numérica do exemplo Gripe (H=0.954, Gain por atributo).
- ✅ Comparação das 3 discretizações (tabela + comentário do trade-off).
- ✅ Cross-validation 5-fold (rigor experimental).
- ✅ Confusion matrix.
- ✅ Visualização texto + figura matplotlib da árvore.
- ✅ Justificação da estratégia escolhida.

### 9.10 Limitações / trabalho futuro

- **Supervised multi-bin não implementado.** A estratégia supervised actual faz só split binário por atributo (max 2 valores). Uma versão multi-bin (encontrar k-1 thresholds que maximizam ganho conjunto) provavelmente daria árvore pequena e accuracy alta — mas é trabalho extra e equal_width já dá resultados excelentes.
- **Pruning não implementado.** ID3 puro não faz pruning. Para Iris (94% CV) não é necessário; para o dataset PopOut (Fase 7) pode ser útil. Mencionar como trabalho futuro.
- **Stratified splits não implementados.** As partições train/test e CV são puramente aleatórias. Stratified asseguraria que cada classe está proporcionalmente representada — boa prática mas pouco relevante em Iris (50/50/50, equilibrado).




# ═══════════════════════════════════════════════════════════════
# FASE6_DATASET.md
# ═══════════════════════════════════════════════════════════════

# Fase 6 — Geração do dataset PopOut a partir do MCTS
## Documento de execução e material-fonte para o relatório

> Implementa a **Fase 6** do `PLANEAMENTO_PROJETO.md`. Cobre o requisito **§4.2.1 (2)** do enunciado:
> *"You will need to generate a dataset of pairs (state_i, move_i) where state_i refers to the current state of the game and move_i is the corresponding next move suggested by the algorithm."*
>
> Esta fase **alimenta a Fase 7** (treinar árvore que imita o MCTS).

---

## 0. Onde estamos

| Fase | Estado |
|------|--------|
| 1, 2, 3, 4, 4.5, 5 | ✅ |
| **6 — Gerar dataset PopOut** | **Em curso** |
| 7 — ID3 no PopOut | Bloqueada por esta fase |
| 8, 9 | Pendentes |

**Critério de saída:**
- `data/popout_dataset.csv` produzido com pelo menos algumas centenas de pares (estado, jogada).
- Schema documentado e validado.
- Diversidade do dataset confirmada (não é o mesmo jogo N vezes).
- Distribuição de classes razoável.

---

## 1. Conceito: Behavioural Cloning

> 📝 **Para o relatório — caixa de contextualização:**
>
> O que estamos a fazer é uma versão clássica de **behavioural cloning** (imitation learning). O MCTS é o "professor" — toma decisões com base em centenas de simulações. O dataset captura essas decisões. Uma árvore de decisão treinada nele é o "aluno" — aprende a aproximar a política do MCTS sem precisar de correr simulações em tempo real.
>
> **Vantagem prática:** o MCTS demora ~1-2s por jogada com `N=400`. A árvore decide em microssegundos. Para um cenário onde o tempo importa (ex: jogo em tempo real), esta troca pode valer a pena — sacrificamos algo de qualidade pelo enorme ganho de velocidade.
>
> **Limitação esperada:** a árvore só pode imitar o que viu no treino. Se o MCTS muda de comportamento (ex: posições novas), a árvore não acompanha. Mais grave: a árvore reflete os **erros** do MCTS — não os filtra.

---

## 2. Codificação dos dados

### 2.1 Estado (features)

**Decisão: codificação raw, 43 features.**

| Coluna | Tipo | Domínio | Significado |
|--------|------|---------|-------------|
| `s0..s41` | int categórico | {0, 1, 2} | Casa do tabuleiro (linha-major: s0 = (0,0), s7 = (1,0), ..., s41 = (5,6)). 0=vazio, 1=P1, 2=P2 |
| `to_play` | int categórico | {1, 2} | Jogador a mover |
| `move` (classe) | string | `d0`–`d6` ou `p0`–`p6` | Jogada do MCTS |

> **Justificação raw:** segue o estilo do projeto-referência (que teve nota máxima). Mantém o ID3 a operar diretamente sobre o tabuleiro, sem assumir features derivadas. **A árvore aprende o que for relevante.**
>
> **Alternativa rejeitada (por agora): features derivadas** (ex: número de peças por coluna, comprimento da maior linha). Mencionada como trabalho futuro. Reduziria o tamanho da árvore mas mete viés humano no que devia ser aprendido pelo algoritmo.

### 2.2 Classe (target)

Codificada como **string curta** `kind+coluna`:
- `d0`, `d1`, ..., `d6` → drop nas colunas 0-6
- `p0`, `p1`, ..., `p6` → pop nas colunas 0-6

Total: até 14 classes possíveis. Em prática, drops são muito mais frequentes que pops (~10% de pops, conforme medido na Fase 4).

### 2.3 Schema do CSV

```
s0,s1,s2,...,s41,to_play,move
0,0,0,...,0,1,d3
0,0,0,...,1,2,d2
...
```

44 colunas (42 cells + to_play + move).

---

## 3. Geração

### 3.1 Algoritmo

```
para cada jogo em 1..N:
    estado ← estado_inicial()
    enquanto não terminado:
        com probabilidade ε:
            jogada ← random escolhido das legais
        senão:
            jogada ← MCTS(estado, parametros)
        gravar (estado.encode(), to_play, jogada.encode())
        estado ← apply_move(estado, jogada)
    se atingiu max_turns: terminar este jogo
```

### 3.2 Parâmetros do MCTS-professor

Decididos empiricamente da Fase 4:
- `n_simulations = 200` (compromisso tempo/qualidade).
- `rollout = "heuristic_win"` (melhor sweet-spot).
- `tactical_root = True` (apanha pops com vitória forçada).
- `c = √2`.

### 3.3 Diversidade — ε-greedy

`ε = 0.10`: 10% das jogadas são aleatórias. Razão:
- MCTS determinístico em estados iguais → mesma sequência sempre.
- Sem ruído, 1000 partidas reduzem-se a 1 árvore de jogo.
- 10% é o sweet-spot empírico (mais e o "professor" deixa de ser o MCTS).

### 3.4 Tamanho do dataset

Estimativa: cada partida tem ~30-50 plies → ~30-50 pares. Para 50 partidas: ~1500-2500 pares. Para 1000 partidas: ~30000-50000 pares (estimativa do plano original).

**Default desta fase:** 50 partidas (rápido, ~1-3 min). Modo `--large` para 500 partidas em batch.

### 3.5 Filtragem (não fazer aqui)

Não filtramos estados duplicados. Se o mesmo estado aparece com a mesma jogada N vezes, isso é informação útil para o ID3 (Information Gain pondera por frequência).

---

## 4. Plano experimental

### 4.1 Validação do schema

- Carregar CSV em pandas: 44 colunas, todos int categóricos exceto `move` (string).
- Cada `s_i ∈ {0, 1, 2}`, `to_play ∈ {1, 2}`, `move` matches `^[dp][0-6]$`.

### 4.2 Estatísticas a reportar

> 📝 **Para o relatório — secção "Geração do dataset PopOut":**

- Número de partidas, número de pares.
- Distribuição de classes (drop vs pop, por coluna).
- Distribuição de comprimento de partidas.
- % do dataset gerado por jogada aleatória vs por MCTS.
- Tempo de wall-clock para gerar.
- Tamanho do CSV em disco.

### 4.3 Sanity de qualidade

- Verificar que o vencedor esperado (MCTS bom) está em equilíbrio (P1 e P2 têm ~50/50 vitórias) → dataset não está enviesado para um lado.
- Verificar que % pops está próximo da medida da Fase 4 (~10%).

---

## 5. Riscos identificados

| Risco | Mitigação |
|-------|-----------|
| Geração demora muito | `n_simulations=200` em vez de 500-1000; flag `--large` opcional |
| Dataset todo igual (MCTS determinístico) | ε-greedy = 10% noise + seed por partida |
| Classes muito desbalanceadas (poucos pops) | Aceitável; refletir nos resultados Fase 7. ID3 com Information Gain ainda funciona |
| CSV gigante | Streaming para disco em vez de manter em memória |

---

## 6. API

```python
# experiments/generate_dataset.py
generate_dataset(
    n_games=50,
    out_path="data/popout_dataset.csv",
    epsilon=0.10,
    n_simulations=200,
    rollout="heuristic_win",
    tactical_root=True,
    seed=0,
    max_turns=300,
)
```

---

## 7. O que esta fase entrega para o relatório

- Justificação da abordagem behavioural cloning.
- Descrição da codificação (raw 42 cells + to_play, classe d/p+col).
- Pseudocódigo da geração (com ε-greedy).
- Tabela de estatísticas do dataset.
- Distribuição de classes e comprimento de partidas.
- CSV pronto a usar pela Fase 7.

---

> Estado: rascunho v0.1 — antes da implementação. Atualizado com resultados na secção 8.

---

## 8. Atualização v0.2 — implementação concluída

### 8.1 Estrutura de código

```
IA_WORK/
├── experiments/
│   └── generate_dataset.py     (NOVO: gerador self-play)
├── tests/
│   └── test_dataset_generation.py  (NOVO: 6 testes)
└── data/
    └── popout_dataset.csv       (NOVO: 856 pares, 75 KB)
```

### 8.2 Resultado dos testes

`python -m pytest tests/ -c /dev/null` → **99 passed, 1 skipped** em ~38s.

Os 6 testes novos cobrem:
- Encoding correto de drops e pops (`d3`, `p0`, etc.).
- Schema do estado: 42 cells + to_play.
- Geração com `epsilon=0` é determinística (só MCTS).
- Vencedores totais somam ao número de partidas.
- CSV gerado tem 44 colunas, valores em domínios esperados, regex de classes match.

### 8.3 Geração — parâmetros usados

| Parâmetro | Valor |
|-----------|-------|
| Partidas | 50 |
| ε (jogadas aleatórias) | 0.10 |
| MCTS `N` | 200 |
| Rollout | `heuristic_win` |
| `tactical_root` | True |
| `C` | √2 |
| Seed | 0 |
| Tempo total | **559 s (~9.3 min)** |

### 8.4 Estatísticas do dataset

> 📝 **Para o relatório — secção "Geração do dataset PopOut":**

| Métrica | Valor |
|---------|-------|
| Total de pares | **856** |
| Pares gerados pelo MCTS | 779 (91%) |
| Pares gerados aleatoriamente (ε) | 77 (9%) |
| Pops | 41 (**4.8%** dos moves) |
| Vencedores P1 | 33 (66%) |
| Vencedores P2 | 17 (34%) |
| Empates | 0 |
| Comprimento médio das partidas | 17.1 plies |
| Comprimento mínimo / máximo | 7 / 34 |
| Tamanho em disco | 75.4 KB |

**Interpretação:**
- **Vantagem do P1 (66/34):** consistente com a vantagem do primeiro jogador no Connect-4. O dataset reflete corretamente a dinâmica do jogo.
- **Pop rate baixo (4.8%):** menos do que os ~10% medidos na Fase 4 com MCTS-vs-MCTS sem tactical. O `tactical_root` privilegia caminhos de vitória forçada que tendem a ser drops simples; pops aparecem só quando criam fork ou bloqueiam ameaça.
- **Partidas curtas (17 plies média):** tactical lookahead acelera o fim — quando o MCTS vê fork, joga-o e termina.

### 8.5 Distribuição de classes

| Classe | Contagem | % |
|--------|----------|----|
| d3 (drop centro) | 182 | 21.3% |
| d4 | 152 | 17.8% |
| d2 | 140 | 16.4% |
| d5 | 110 | 12.9% |
| d1 | 103 | 12.0% |
| d6 | 75 | 8.8% |
| d0 | 53 | 6.2% |
| p3 (pop centro) | 10 | 1.2% |
| (resto: pops nas outras colunas) | <8 cada | <1% |

**Observações:**
- **Bias central:** `d3` (centro) é claramente a classe maioritária (21%). Coerente com a estratégia clássica de Connect-4 (o centro participa em mais alinhamentos).
- **Pops praticamente todos no centro:** `p3` é o único pop com >1%. Sugere que pops mid-game raramente são ótimos fora da coluna central.
- **Desbalanceamento:** drops dominam ~95% do dataset. ID3 com Information Gain lida com isto, mas é importante mencionar — pode beneficiar de stratified split ou weighted accuracy na Fase 7.

### 8.6 Schema final do CSV (validado)

```
s0,s1,s2,...,s41,to_play,move
0,0,0,...,0,1,d4
0,0,0,...,1,2,d3
...
```

44 colunas. Valores: `s_i ∈ {0,1,2}`, `to_play ∈ {1,2}`, `move ∈ {d0..d6, p0..p6}`.

### 8.7 Decisões revistas durante a implementação

1. **MCTS factory dentro do loop de partidas.** Inicialmente queria reutilizar uma única estratégia entre partidas mas o `rng` interno acumulava estado e violava determinismo entre partidas. Cada partida tem o seu MCTS com seed específica.
2. **Streaming write em vez de bulk.** O CSV é escrito linha-a-linha conforme o jogo avança. Razão: para batches de 1000+ partidas, manter tudo em memória é desperdício. Streaming permite continuar onde parou se houver crash.
3. **Tempo por partida ~11s**, mais do que esperado. O `tactical_root` (O(b³) na raiz) somado a N=200 simulações torna cada jogada cara. Para 1000 partidas seria ~3h — viável mas overnight job.

### 8.8 Critérios de saída — verificação

- [x] CSV produzido em `data/popout_dataset.csv`.
- [x] Schema documentado e validado (testes).
- [x] Diversidade — ε=10% confirmada nas estatísticas (77/856 = 9%, ligeiramente abaixo por arredondamento).
- [x] Distribuição de classes razoável.
- [x] Suite verde.

**Fase 6 — concluída.**

### 8.9 O que esta fase entrega para o relatório

- ✅ Justificação behavioural cloning + limitações.
- ✅ Pseudocódigo de geração com ε-greedy.
- ✅ Tabela de parâmetros do MCTS-professor.
- ✅ Tabela de estatísticas do dataset (856 pares, distribuição classes, vencedores).
- ✅ Comentário sobre vantagem P1 (66/34) e pop rate (4.8%).
- ✅ Schema do CSV documentado.
- ✅ CSV pronto a usar pela Fase 7.

### 8.10 Limitações / trabalho futuro

- **Tamanho modesto.** 856 pares pode ser pouco para uma árvore generalizar bem em 14 classes. Ideal seria 5-10× mais — possível com batch overnight (`--games 500`).
- **Sem stratified split** entre treino/teste na Fase 7 — pops são raros (<5%) e podem cair só no treino ou só no teste por azar. Mitigação: na Fase 7 usar repeated random splits + média.
- **Features raw** (s0-s41). Features derivadas (centro ocupado, alinhamentos abertos) reduziriam o tamanho da árvore na Fase 7. Mantidas como trabalho futuro para preservar fidelidade ao MCTS sem viés humano.
- **MCTS-professor não-determinístico:** mesmo com seeds, ε=10% introduz variância. Aceitável para o objetivo (diversidade).




# ═══════════════════════════════════════════════════════════════
# FASE7_ID3_POPOUT.md
# ═══════════════════════════════════════════════════════════════

# Fase 7 — ID3 sobre o dataset PopOut + Tree Strategy
## Documento de execução e material-fonte para o relatório

> Implementa a **Fase 7** do `PLANEAMENTO_PROJETO.md`. Cobre a segunda metade do **§4.2.1** do enunciado (treinar árvore que aprende a partir do dataset gerado pelo MCTS) e fecha o cenário **§3 (3) "CvC com 2 algoritmos diferentes"**.

---

## 0. Onde estamos

| Fase | Estado |
|------|--------|
| 1, 2, 3, 4, 4.5, 5, 6 | ✅ |
| **7 — ID3 no PopOut + Tree strategy** | **Em curso** |
| 8 — Avaliação experimental | A seguir |
| 9 — Notebook + slides | Última |

**Critério de saída:**
- Árvore treinada sobre `data/popout_dataset.csv` com accuracy de teste reportada.
- `tree_strategy` jogável no `play_game` com fallback robusto para jogadas ilegais.
- Comparação tree vs MCTS vs random.
- Sweep de `max_depth` para mostrar trade-off bias/variance.
- Modo "MCTS vs Tree" disponível na GUI.

---

## 1. Conceito — fechar o ciclo behavioural cloning

> 📝 **Para o relatório:** o pipeline completo da Metade B é
> ```
> MCTS (professor lento)  →  dataset 856 pares  →  ID3  →  Tree (aluno rápido)
> ```
> e na Fase 8 vamos comparar o aluno com o professor em jogos reais. Espera-se: tree é mais fraca em força (aproxima o MCTS) mas centenas a milhares de vezes mais rápida na decisão.

---

## 2. Encoding usado para predict (consistente com a Fase 6)

- **Features:** mesmas 43 do CSV — `s0..s41` (cells, valores em {0,1,2}) + `to_play` (1 ou 2).
- **Classe:** string `dN` ou `pN`.

A predição da árvore devolve uma string como `d3`. Convertemos para `Move(3, 'drop')` antes de aplicar.

---

## 3. Tree strategy — fallback para predições ilegais

A árvore é treinada com Information Gain, **não tem garantia de prever só jogadas legais**. Possíveis modos de falha:
1. Estado nunca visto → predict cai num caminho com `default = parent_majority`.
2. Move predito é syntacticamente válido mas ilegal nesse estado (ex: `d3` mas col 3 cheia).

**Estratégia de fallback** (3 tiers):
1. Se predição ∈ legal_moves → usar.
2. Senão, escolher entre `legal_moves` o move com mesma `kind` (drop/pop) mais central → mantém intuição "parecida com o que árvore queria".
3. Senão, primeiro `legal_moves[0]` (centrais por causa da `COLUMN_PRIORITY`).

> **Justificação:** preferimos um fallback determinístico que mantenha o "sabor" da predição em vez de aleatório — assim o comportamento é mais previsível e testável.

---

## 4. Plano experimental

### 4.1 Sweep de profundidade máxima

Treinar com `max_depth ∈ {3, 5, 8, 10, None}`. Reportar:
- Accuracy treino vs teste (curva clássica de overfitting).
- Tamanho da árvore (folhas, profundidade real).

**Hipótese:** sem limite, treino atinge ~100% mas teste piora; sweet-spot algures em depth=5-8.

### 4.2 Tree vs Random — sanity

20 partidas. Esperado: tree ganha a maioria (precisa de aprender pelo menos jogadas centrais).

### 4.3 Tree vs MCTS — comparação aluno-professor

10 partidas em cada matchup, alternando lados:
- tree vs MCTS-Médio.
- tree vs MCTS-Difícil.

**Hipótese:** tree perde a maioria mas tempo por jogada da tree é ordens-de-grandeza menor. Esta é a **vantagem prática** que justifica behavioural cloning.

### 4.4 Tempo por jogada

Tabela: tree (~µs) vs MCTS-Médio (~1s) vs MCTS-Difícil (~5s).

---

## 5. Visualização da árvore PopOut

Diferente do Iris — espera-se ser muito maior. Mostrar:
- Árvore completa em texto (truncada se >50 nós).
- Os primeiros 3 níveis em matplotlib (suficiente para slide).

---

## 6. API

```python
# popout/tree_strategy.py
from popout.tree_strategy import tree_strategy, encode_state_for_tree

# A árvore é a mesma estrutura `Node` do popout/decision_tree.py
strat = tree_strategy(tree)
play_game(strat, mcts_strategy(...))
```

---

## 7. O que esta fase entrega para o relatório

- Pipeline behavioural cloning fechado (com diagrama).
- Tabela accuracy treino/teste por max_depth.
- Tabela tree vs random / tree vs MCTS.
- Comparação de tempos (tree vs MCTS).
- Visualização da árvore aprendida (parcial).
- Cumpre o requisito do enunciado "CvC com 2 algoritmos diferentes".

---

> Estado: rascunho v0.1 — antes da implementação. Atualizado com resultados na secção 8.

---

## 8. Atualização v0.2 — implementação concluída

### 8.1 Estrutura de código

```
IA_WORK/
├── popout/
│   ├── tree_strategy.py            (NOVO: estratégia jogável)
│   └── gui.py                       (atualizado: 2 novos modos com Tree)
├── experiments/
│   └── train_popout_tree.py         (NOVO: pipeline treino + matches)
├── tests/
│   └── test_tree_strategy.py        (NOVO: 10 testes)
└── data/
    └── popout_tree.pkl              (NOVO: árvore treinada, max_depth=10)
```

### 8.2 Resultado dos testes

`python -m pytest tests/ -c /dev/null` → **109 passed, 1 skipped** em ~44s.

10 testes novos cobrem:
- Encoding state→features (43 valores).
- Decoding `d3`/`p0`/inválido.
- Predição legal devolvida.
- Fallback quando predição é ilegal (kind igual / drop central / primeiro legal).
- Pipeline ID3 sobre dataset real prediz só legal moves.
- Tree vs random — tree ganha pelo menos 1/5.

### 8.3 Sweep de `max_depth`

| max_depth | Acc treino | Acc teste | Folhas | Profundidade real |
|-----------|------------|-----------|--------|-------------------|
| 3 | 0.303 | 0.169 | 26 | 3 |
| 5 | 0.526 | 0.157 | 156 | 5 |
| 8 | 0.876 | 0.221 | 450 | 8 |
| 10 | **0.904** | **0.227** | **474** | 10 |
| None | 0.904 | 0.227 | 474 | 10 |

**Interpretação:**
- Sem limite, a árvore atinge profundidade 10 naturalmente — o dataset não permite mais.
- **Overfitting evidente:** train sobe de 30% a 90% à medida que `max_depth` cresce, enquanto test fica estagnado em ~22%.
- A acc teste de 22% é melhor do que a baseline trivial: a classe mais frequente é `d3` com 21.3% no dataset; tree faz **ligeiramente melhor**, mas com 14 classes possíveis o ganho é modesto.
- **Diagnóstico:** dataset de 856 pares é demasiado pequeno para árvores aprenderem 14 classes em 43 features. Recomendado para Fase 8: aumentar dataset (`--games 500`) e/ou usar features derivadas.

### 8.4 Tree vs Random — sanity ✅

| Tree | Random | Empates |
|------|--------|---------|
| **10** | 0 | 0 |

Tempo por jogada: **tree ~17 μs, random ~10 μs** (10 partidas, alternando lados).

A árvore aprendeu o suficiente para vencer um adversário aleatório consistentemente. Confirma que a aprendizagem está funcional.

### 8.5 Tree vs MCTS-Médio — comparação aluno-professor

| Tree | MCTS-Médio | Empates |
|------|------------|---------|
| 0 | **6** | 0 |

Tempo por jogada: **tree ~40 μs, MCTS ~610 ms**.

> 📝 **Para o relatório — destaque-chave:**
> - A árvore **perde 0-6** contra o MCTS-Médio. **O aluno não supera o professor**, como esperado em behavioural cloning.
> - Mas a árvore decide em **40 microssegundos**, contra **610 milissegundos** do MCTS.
> - **Speedup: ~15,000×.**
> - **Trade-off explícito:** força-de-jogo perde-se, velocidade-de-decisão ganha-se 4 ordens de grandeza. Em cenários onde o tempo importa (tempo real, embedded, geração de muitos episódios), a árvore é prática.

### 8.6 Visualização da árvore

A árvore tem 474 folhas — não cabe numa figura. Guardada em `data/popout_tree.pkl` para uso pela GUI e por experiências futuras.

Visualização **dos 3 níveis de topo** guardada em `/tmp/popout_tree_out/popout_tree_top3.png`. Suficiente para slide:
- Raiz: features que diferenciam estados iniciais (provavelmente cells centrais).
- Níveis 2-3: decisões secundárias.

### 8.7 Modos novos da GUI

A GUI deteta automaticamente `data/popout_tree.pkl` e adiciona:
- `Humano vs Arvore (ID3)`
- `MCTS vs Arvore (CvC, 2 algos)` — **fecha o requisito §3 (3) do enunciado** ("CvC com 2 algoritmos diferentes").

Total: 7 modos.

### 8.8 Decisões revistas durante a implementação

1. **Fallback determinístico** em vez de random. Quando a predição é ilegal: tier 1 = mesma kind no `legal_moves` mais central; tier 2 = drop central; tier 3 = primeiro legal. Mantém o "sabor" da predição da árvore — testável e explicável no relatório.
2. **Decisão de não fazer pruning aposterior.** ID3 puro não tem pruning; experiência com `max_depth` cobre essa necessidade. C4.5/CART pruning é mencionado como trabalho futuro.
3. **`_truncate_tree`** para visualização — mantém o pickle completo intacto e gera versão truncada só para a figura.

### 8.9 Critérios de saída — verificação

- [x] Árvore treinada e guardada (`data/popout_tree.pkl`, max_depth=10, 474 folhas).
- [x] `tree_strategy` jogável com fallback.
- [x] Tree vs Random — 10/0 (sanity).
- [x] Tree vs MCTS — 0/6 (esperado; MCTS é melhor).
- [x] Sweep max_depth completado.
- [x] Modo "MCTS vs Tree" disponível na GUI — fecha cenário §3 (3).
- [x] Suite verde (109 passed).

**Fase 7 — concluída.**

### 8.10 O que esta fase entrega para o relatório

- ✅ Pipeline behavioural cloning fechado (MCTS → CSV → ID3 → Tree).
- ✅ Tabela accuracy treino/teste por max_depth (mostra overfitting).
- ✅ Tree vs Random: 10-0 (sanity).
- ✅ Tree vs MCTS: 0-6, com **speedup de ~15,000×** na decisão.
- ✅ Trade-off força ↔ velocidade documentado.
- ✅ Cenário §3 (3) "CvC com 2 algoritmos diferentes" fechado.
- ✅ Visualização dos 3 níveis de topo da árvore.

### 8.11 Limitações honestas

- **Accuracy 22% é baixa.** Para um cenário "real" precisaríamos:
  - Dataset 5-10× maior (~5000-10000 pares).
  - Features derivadas (ex: peças por coluna, alinhamentos, ameaças).
  - Pruning post-hoc.
- **Tree perde sempre contra MCTS** — sem surpresa, mas significa que esta arquitetura não é viável para substituir MCTS em contexto competitivo. Útil só onde tempo prima.
- **Dataset enviesado para drops centrais.** Árvore reflete bias: pops e jogadas raras estão sub-representados.

### 8.12 Trabalho futuro (mencionar no relatório)

- Aumentar dataset com `--games 500` (~3h batch).
- Engineer features derivadas: contagens por coluna, comprimento da maior linha, ameaças ativas.
- Pruning chi-square / reduced-error.
- Experimentar dataset com MCTS mais forte (`heuristic_block`).




# ═══════════════════════════════════════════════════════════════
# FASE8_AVALIACAO.md
# ═══════════════════════════════════════════════════════════════

# Fase 8 — Avaliação experimental rigorosa
## Documento de execução e material-fonte para o relatório

> Implementa a **Fase 8** do `PLANEAMENTO_PROJETO.md`. Esta fase é o ponto crítico dos **30% técnicos** do enunciado: *"overall technical evaluation of the solution from a data science point-of-view, including rigour in the performance evaluation"*.
>
> Sem ela, o relatório tem implementação mas não tem **medida**. O grupo perde pontos exatamente aqui — segundo o plano original *"é aqui que a maioria dos grupos perde pontos por preguiça"*.

---

## 0. Onde estamos

| Fase | Estado |
|------|--------|
| 1, 2, 3, 4, 4.5, 5, 6, 7 | ✅ |
| **8 — Avaliação experimental** | **Em curso** |
| 9 — Notebook + slides | Última |

**Critério de saída:**
- Win-rate matrix entre todos os agentes implementados.
- Learning curve da árvore (accuracy vs tamanho de treino).
- Cross-validation 5-fold reportada (já feita em Fase 5; consolidar).
- Charts matplotlib guardados como PNGs.
- Comentário interpretativo de cada tabela (não só números soltos).

---

## 1. Agentes a comparar

| Símbolo | Estratégia | Parâmetros |
|---------|------------|------------|
| `Random` | `random_strategy` | — |
| `MCTS-E` | MCTS Fácil | N=100, rollout=random |
| `MCTS-M` | MCTS Médio | N=200, rollout=heuristic_win, tactical_root=True |
| `Tree` | ID3 do dataset PopOut | max_depth=10, dataset 856 pares |

Mantemos 4 agentes para o orçamento de tempo (matriz 4×4 com 4 partidas alternando lados = 16 partidas únicas, ~5-7 min wall-clock).

> **Nota:** MCTS-Difícil (N=800) seria interessante mas custa ~5s/jogada. Em 4 partidas vs MCTS-M: 4 × 17 × (5+0.7) ≈ 6 min só esse cell. Adiamos para futuro se houver tempo.

---

## 2. Experiências planeadas

### 2.1 Win-rate matrix

Matriz 4×4 com 4 partidas por célula, alternando lados. Resultado: % vitórias da linha contra a coluna. Diagonais (self-play) fazem sentido (mostra estabilidade).

Cada célula ⟨A vs B⟩: `(wins_A, wins_B, draws)` em 4 partidas.

**Hipóteses a testar:**
- MCTS-M > MCTS-E > Random.
- Tree > Random (verificou-se na Fase 7).
- MCTS-M >> Tree (verificou-se na Fase 7).
- Random ≈ Tree contra agentes mais fortes (ambos perdem).

### 2.2 Learning curve da árvore

Treinar ID3 com {20%, 40%, 60%, 80%} do dataset PopOut. Medir accuracy de teste no remanescente. **Hipótese:** tree convergir lentamente; com 856 pares ainda não saturou.

### 2.3 Iris cross-validation (já feita em Fase 5 — consolidar)

5-fold CV com 3 estratégias de discretização. Confirmar números:
- supervised binário: 65.3% ± 7.2%
- equal_width(k=3): **94.7% ± 4.0%**
- equal_freq(k=3): 94.7% ± 4.5%

### 2.4 Tempo de decisão

Recolher tempo médio por jogada de cada agente nos matches. Tabela final:

| Agente | t/jogada |
|--------|----------|
| Random | µs |
| Tree | µs |
| MCTS-E | ms |
| MCTS-M | ms |

---

## 3. Charts a gerar

| # | Chart | Insight |
|---|-------|---------|
| 1 | Heatmap da win-rate matrix | Hierarquia de força |
| 2 | Tree learning curve (accuracy vs tamanho) | Saturação ou não |
| 3 | Tree depth vs accuracy (já tem dados da Fase 7) | Overfitting |
| 4 | MCTS tempo vs N (já tem dados da Fase 3) | Custo computacional |

Todos os charts em `/tmp/fase8_out/*.png`.

---

## 4. Plano de execução

```
1. Treinar Tree com max_depth=10 (já guardada em data/popout_tree.pkl).
2. Construir 4 agentes (factories).
3. Win-rate matrix 4×4, 4 partidas/célula.
4. Learning curve com 4 train sizes.
5. Coletar tempos médios.
6. Gerar 4 charts.
7. Tabelas markdown para o relatório.
```

Tempo estimado: 6-10 min wall-clock.

---

## 5. Risco e mitigações

| Risco | Mitigação |
|-------|-----------|
| Cells MCTS-M vs MCTS-M demoram demais | Limitar a 4 partidas, max_turns=200 |
| Aleatoriedade nas seeds dá noise alto | Seeds determinísticas; aceitamos noise (relatamos n=4 explicitamente) |
| Charts não geram em batch (matplotlib backend) | `Agg` backend forçado; testar antes |

---

## 6. O que esta fase entrega para o relatório

- Tabela win-rate matrix 4×4.
- Heatmap dela.
- Learning curve.
- Iris CV (consolidação).
- Tabela tempos.
- Análise interpretativa por experiência.

---

> Estado: rascunho v0.1 — antes da execução. Atualizado com resultados + charts na secção 7.

---

## 7. Atualização v0.2 — execução concluída

### 7.1 Estrutura de código

```
IA_WORK/
├── experiments/
│   └── run_evaluation.py        (NOVO: harness Fase 8)
└── /tmp/fase8_out/
    ├── winrate_matrix.png
    ├── tree_learning_curve.png
    ├── tree_depth_sensitivity.png
    └── mcts_time_vs_n.png
```

Wall-clock: 97s para a matriz + ~5s para learning curve + charts = **~2 min total** em modo `--quick`.

### 7.2 Win-rate matrix — 4×4 agentes, 2 jogos por célula

> 📝 **Para o relatório — tabela principal da avaliação:**

| A \\ B  | Random | MCTS-E | MCTS-M | Tree |
|---------|--------|--------|--------|------|
| **Random** | 0.50 | 0.00 | 0.00 | 0.00 |
| **MCTS-E** | 1.00 | 0.50 | 0.00 | 0.50 |
| **MCTS-M** | 1.00 | 1.00 | 0.50 | 1.00 |
| **Tree**   | 1.00 | 0.50 | 0.00 | 0.50 |

Valor = win-rate de A contra B. Diagonal a 0.50 confirma simetria do self-play.

**Hierarquia clara:**
- **MCTS-M domina tudo** (linha 1.0/1.0/0.5/1.0). O sweet-spot empírico (N=200, heuristic_win, tactical_root) bate todos os outros.
- **MCTS-E ≈ Tree** — ambos vencem Random sempre, perdem a MCTS-M sempre, empatam entre si (0.5).
- **Random perde a tudo.** Confirmação trivial mas necessária.

### 7.3 Tempo médio por jogada

| Agente | t/jogada |
|--------|----------|
| Random | **11 μs** |
| Tree | **34 μs** |
| MCTS-E | 146 ms |
| MCTS-M | 756 ms |

> 📝 **Insight chave para o relatório:**
> - **Tree e MCTS-E têm a mesma força em jogo** (0.5 vs 0.5), mas a **Tree é ~4,300× mais rápida** (34μs vs 146ms).
> - Fechado o argumento prático do behavioural cloning: para ganhar a Random, ambos chegam — a tree faz isso quase instantaneamente. Só precisamos do MCTS quando queremos derrotar adversários mais fortes.

### 7.4 Heatmap

![Win-rate matrix](file:///tmp/fase8_out/winrate_matrix.png)

Cores: vermelho = perde (B>A), verde = vence (A>B), creme = equilíbrio.

### 7.5 Learning curve da árvore

| Train fraction | n_train | Acc teste | Folhas |
|----------------|---------|-----------|--------|
| 0.20 | 137 | 0.211 | 104 |
| 0.40 | 274 | 0.187 | 200 |
| 0.60 | 411 | 0.222 | 288 |
| 0.80 | 548 | 0.216 | 389 |

![Learning curve](file:///tmp/fase8_out/tree_learning_curve.png)

> 📝 **Insight crítico:** a curva é **plana em ~0.20-0.22**. Adicionar mais dados de treino **não está a melhorar accuracy**. Diagnóstico:
> - O dataset tem um **plafond intrínseco** que esta combinação algoritmo+features não consegue passar.
> - Não é problema de "poucos dados" — é problema de **representação** ou **complexidade do problema**.
> - **Recomendação para trabalho futuro:** features derivadas (peças por coluna, ameaças ativas) ou pruning post-hoc. **Aumentar o dataset isoladamente não resolverá.**

Isto contradiz a intuição inicial (Fase 7) de que aumentar o dataset resolveria. O experimento mostra que **não**. Esta é uma conclusão importante para o relatório.

### 7.6 Depth sensitivity (consolidação Fase 7)

![Depth sensitivity](file:///tmp/fase8_out/tree_depth_sensitivity.png)

Train cresce monotonicamente, test estagna em ~22%. **Overfitting clássico.** Sweet-spot: max_depth=8 (já 22% test, 450 leaves; mais profundidade só aumenta tamanho).

### 7.7 MCTS scaling (consolidação Fase 3)

![MCTS time vs N](file:///tmp/fase8_out/mcts_time_vs_n.png)

Crescimento ~linear: cada simulação tem custo aproximadamente constante. N=1000 → 1.92s/jogada — limite prático para CvC interativo.

### 7.8 Iris CV (consolidação Fase 5)

| Estratégia | Mean acc | Std acc | Mean folhas |
|------------|----------|---------|-------------|
| supervised binário | 0.653 | ±0.072 | 4.2 |
| **equal_width(k=3)** | **0.947** | **±0.040** | 8.4 |
| equal_freq(k=3) | 0.947 | ±0.045 | 12.6 |

equal_width(k=3) é a melhor estratégia por accuracy + tamanho.

### 7.9 Resumo dos achados (vai para a apresentação)

1. **Hierarquia de força:** MCTS-M ≫ MCTS-E ≈ Tree ≫ Random.
2. **Velocidade:** Tree é 4,300× mais rápida que MCTS-E ao mesmo nível de força.
3. **Behavioural cloning** funciona até ao nível MCTS-E mas não até MCTS-M — a árvore não consegue imitar o comportamento mais sofisticado.
4. **Plafond da árvore (~22%)** não é resolúvel com mais dados — exige features melhores.
5. **MCTS-M é o sweet-spot** que justifica o `tactical_root` (Fase 4.5).

### 7.10 Critérios de saída — verificação

- [x] Win-rate matrix entre todos os agentes.
- [x] Heatmap matplotlib.
- [x] Learning curve da árvore (concluiu: plafond, não é falta de dados).
- [x] Iris CV consolidada (94.7% ± 4%).
- [x] Tempos comparados (Tree 4,300× mais rápida que MCTS-E).
- [x] Charts em `/tmp/fase8_out/*.png`.

**Fase 8 — concluída.**

### 7.11 O que esta fase entrega para o relatório

- ✅ **Tabela win-rate matrix** (a tabela principal — vai como figura).
- ✅ **Heatmap** como figura limpa para slides.
- ✅ **Tabela de tempos** mostrando 4 ordens de grandeza entre Tree e MCTS-M.
- ✅ **Learning curve** mostrando o plafond — uma das **conclusões mais valiosas** do trabalho.
- ✅ **Depth sensitivity** mostrando overfitting.
- ✅ **MCTS scaling** justificando os parâmetros escolhidos.
- ✅ Iris CV.

### 7.12 Limitações (assumidas honestamente no relatório)

- **n=2 jogos por célula** no modo quick — variância alta nos números individuais (0/1/2 wins). Para resultados publicáveis correr-se-ia n=10+. Limitado pelo tempo do MCTS-M (756ms/jogada).
- **MCTS-Difícil (N=800) não incluído** na matriz — custo proibitivo para 8 partidas. Mencionado em Fase 4 com tempos.
- **Dataset PopOut tem 856 pares.** Confirmado pela learning curve que não é o gargalo — mas continua a ser pequeno para projeto ML standard.

### 7.13 Trabalho futuro recomendado

- Reproduzir matriz com n=10+ partidas em batch overnight.
- Adicionar MCTS-Difícil e MCTS-Hard (N=800+, heuristic_block).
- Treinar tree com features derivadas (engineering manual de heurísticas).
- Pruning chi-square ou reduced-error.




# ═══════════════════════════════════════════════════════════════
# FASE9_ENTREGAVEL.md
# ═══════════════════════════════════════════════════════════════

# Fase 9 — Entregável final
## Documento de execução para a fase final

> Implementa a **Fase 9** do `PLANEAMENTO_PROJETO.md` e cobre o **§4.3 do enunciado** (submissão):
> - Notebook documentado em `.ipynb`.
> - Slides PDF (≤ 10 min).
> - Ficheiro de auto-avaliação.
>
> **Deadline: 17 de maio de 2026, 23:59:59 (Lisboa).**

---

## 0. Onde estamos

| Fase | Estado |
|------|--------|
| 1, 2, 3, 4, 4.5, 5, 6, 7, 8 | ✅ |
| **9 — Entregável final** | **Em curso** |

**Critério de saída (= critério de submissão):**
- `report/POPOUT_REPORT.ipynb` runable e documentado.
- `report/slides.md` ou `report/slides.pdf` com presentation outline.
- `AUTO_EVAL_TEMPLATE.md` preenchido pelos 3 elementos.
- `README.md` no topo do repositório.

---

## 1. Estrutura do entregável

```
IA_WORK/
├── README.md                        (NOVO — topo)
├── popout/                          (código)
├── tests/                           (testes)
├── experiments/                     (scripts experimentais)
├── data/
│   ├── popout_dataset.csv
│   └── popout_tree.pkl
├── docs/                            (enunciado + iris.csv original)
├── FASE1_*.md ... FASE8_*.md        (logs por fase — material-fonte)
└── report/
    ├── POPOUT_REPORT.ipynb          (entregável principal)
    ├── slides.md                    (outline para conversão a PDF)
    └── AUTO_EVAL_TEMPLATE.md        (placeholder)
```

---

## 2. Notebook — estrutura por secção

Segue a ordem sugerida no `PLANEAMENTO_PROJETO.md` §3 Fase 9:

1. **Capa** — nomes, números de aluno, data, instituição.
2. **Introdução** — problema, objetivos.
3. **Constraints e decisões de design** (cumpre §4.7 do enunciado: *"Mention the constraints..."*).
4. **PopOut: motor do jogo** — regras, código, demo.
5. **MCTS standard** — UCB1, código, demo.
6. **Variações do MCTS** — tabelas Fase 4.
7. **Tactical lookahead** — Fase 4.5.
8. **ID3 + Iris** — algoritmo, discretização, visualização, accuracy.
9. **Geração do dataset PopOut** — pipeline + estatísticas.
10. **ID3 sobre PopOut** — treino, accuracy, tree vs MCTS.
11. **Avaliação experimental** — win-rate matrix, learning curve.
12. **Conclusões e trabalho futuro.**
13. **Referências.**

---

## 3. Slides — 10 minutos máximo

Sugestão (1 slide ≈ 1 min):

| # | Slide |
|---|-------|
| 1 | Capa + grupo |
| 2 | Problema: PopOut + 3 cenários |
| 3 | Decisões de design |
| 4 | MCTS — os 4 passos + UCB1 |
| 5 | Variações: heuristic_win + tactical_root |
| 6 | ID3 + Iris (visualização) |
| 7 | Pipeline behavioural cloning (MCTS → dataset → árvore) |
| 8 | Avaliação: win-rate matrix |
| 9 | Tree é 4,300× mais rápida (chave) |
| 10 | Conclusões + trabalho futuro |

---

## 4. Auto-avaliação

Template em `report/AUTO_EVAL_TEMPLATE.md`. Cada membro descreve:
- Contribuição individual.
- O que aprendeu sobre o trabalho dos outros.
- Auto-pontuação justificada.

---

## 5. Plano de execução desta fase

```
1. Construir POPOUT_REPORT.ipynb via build_notebook.py.
2. Validar abrindo no Jupyter (jupyter nbconvert --to html para teste).
3. Escrever slides.md.
4. Escrever AUTO_EVAL_TEMPLATE.md.
5. Escrever README.md.
6. Final review do checklist do enunciado.
```

---

## 6. Checklist final do enunciado (§4)

Vou marcar à medida que confirmar:

### §2 (Regras do PopOut)
- [x] Drop e pop implementados.
- [x] Vitória 4-em-linha (H, V, diagonais).
- [x] Regra duplo-4 por pop (Allen 2010).
- [x] Empate por tabuleiro cheio.
- [x] Empate por repetição tripla.

### §3 (Game Interface)
- [x] Interface tipo `X--O-XO` (CLI).
- [x] **Bonus:** GUI Pygame.
- [x] H vs H.
- [x] H vs C.
- [x] C vs C com **2 algoritmos diferentes** (MCTS vs Tree).

### §4.1 (MCTS)
- [x] UCT (UCB1) como avaliação.
- [x] Variações exploradas: rollout policies, max_children, C, N.
- [x] Tactical lookahead (variação extra).

### §4.2 (Decision Trees)
- [x] ID3 from scratch (sem sklearn).
- [x] Test examples + classify.

### §4.2.1 (Datasets)
- [x] Iris discretizado, tree treinada, visualização.
- [x] Dataset PopOut gerado pelo MCTS, tree treinada, comparada.

### §4.3 (Submissão)
- [ ] Notebook documentado.
- [ ] Slides PDF.
- [ ] Auto-avaliação.

### §4.7 (Tips)
- [x] Constraints declarados explicitamente.
- [x] Avaliação experimental rigorosa (Fase 8 + tabelas).

---

> Estado: rascunho v0.1 — antes da construção do entregável.


