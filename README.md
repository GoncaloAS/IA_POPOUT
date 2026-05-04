# PopOut + MCTS + ID3 — IA 2025/2026

Trabalho prático de Inteligência Artificial 2025/2026.
Implementação do jogo **PopOut** (variante de Connect-4 com pop moves), do algoritmo **Monte Carlo Tree Search** com UCB1, e de árvores de decisão **ID3** aplicadas a Iris e a um dataset gerado pelo próprio MCTS (behavioural cloning).

**Deadline:** 17 de maio de 2026, 23:59:59 (Lisboa).

---

## Sumário

- **Motor PopOut** completo com regra do duplo-4 por pop e repetição tripla.
- **MCTS standard** com UCB1 (C=√2), validado contra exemplo trabalhado das aulas.
- **4 variações do MCTS:** rollout policies (`random`, `heuristic_win`, `heuristic_block`), N, C, max_children.
- **Tactical lookahead à raiz** (2-ply) que apanha pops com vitória forçada.
- **ID3 from scratch** (sem scikit-learn) com 3 estratégias de discretização.
- **Iris:** 94.7% ± 4% (5-fold CV) com árvore de 8 folhas.
- **Dataset PopOut:** 856 pares gerados pelo MCTS.
- **Tree de PopOut:** 4,300× mais rápida que MCTS-Easy com força equivalente.
- **GUI Pygame** com cliques, modo MCTS-vs-Tree (cumpre §3 do enunciado).

## Estrutura

```
IA_WORK/
├── README.md                  (este ficheiro)
├── RELATORIO_UNIFICADO.md     (todas as decisões de design + resultados)
├── docs/
│   ├── IA_2526_Project.pdf    (enunciado oficial)
│   └── iris (2).csv           (dataset Iris original)
├── codes/                     (código + dados + notebook)
│   ├── popout.py              (motor do jogo)
│   ├── mcts.py                (MCTS + variações + tactical lookahead)
│   ├── decision_tree_builder.py  (ID3 + discretização + tree_strategy)
│   ├── game.py                (CLI + estratégias)
│   ├── gui.py                 (interface Pygame)
│   ├── iris_test.py           (pipeline Iris)
│   ├── generate_dataset.py    (geração do dataset PopOut)
│   ├── train_tree.py          (treino + avaliação da árvore PopOut)
│   ├── evaluation.py          (win-rate matrix + charts)
│   ├── mcts_variations.py     (sweep de variações MCTS)
│   ├── popOut.ipynb           (notebook documentado — entregável)
│   ├── iris.csv
│   ├── popout_dataset.csv
│   ├── decision_tree.pkl
│   ├── iris_tree.pkl
│   └── content/               (PNGs das figuras)
└── ConnectedFour-main/        (projeto-referência do ano passado)
```

## Instalação

```bash
pip install numpy pandas matplotlib pygame jupyter
```

## Como correr

Tudo a partir de `codes/`:

```bash
cd codes
```

### Jogar — interface gráfica

```bash
python gui.py
```

7 modos: Human vs Human, Human vs MCTS (Easy/Medium/Hard), MCTS vs MCTS, Human vs Tree, MCTS vs Tree.

### Jogar — CLI

```bash
python game.py
```

Atalhos do prompt: `0..6` = drop, `d 3`/`p 0` = explícito, `q` = resign, `?` = ajuda.

### Reproduzir as experiências

```bash
# Variações do MCTS — Fase 4
python mcts_variations.py --quick

# Iris — Fase 5
python iris_test.py

# Gerar dataset PopOut — Fase 6 (~10 min)
python generate_dataset.py --games 50

# Treinar árvore PopOut + matches — Fase 7
python train_tree.py --sweep --vs-random 10 --vs-mcts 6

# Avaliação experimental + charts — Fase 8
python evaluation.py --quick
```

### Abrir o notebook

```bash
jupyter notebook codes/popOut.ipynb
```

## Entregáveis para o Moodle

1. **`codes/popOut.ipynb`** — notebook documentado com todas as secções (problema, solução, resultados).
2. **Slides PDF** (a fazer pelo grupo).
3. **Auto-avaliação** — preencher o ficheiro fornecido pelos professores no Moodle.

## Comparação com o projeto-referência (ConnectedFour-main, nota máxima 2024/25)

| Aspecto | Referência | Este trabalho |
|---------|------------|---------------|
| Implementação do jogo | Connect-4 simples (sem pop) | **PopOut completo** (drops + pops + regra duplo-4 + repetição tripla) |
| MCTS — UCB1 | ✅ | ✅ + validação numérica contra exemplo das aulas |
| MCTS — variações | C dinâmico, rollout heurístico | + max_children + tactical lookahead 2-ply |
| ID3 — Iris accuracy | (não reportado) | **94.7% ± 4%** (5-fold CV) |
| ID3 — PopOut accuracy @ depth=10 | 22.23% | **22.7%** |
| Avaliação experimental | Matches qualitativos | Win-rate matrix 4×4 + heatmap + learning curve + charts |
| Interface | CLI texto | CLI + **GUI Pygame** com cliques |

## Referências

- Russell & Norvig — *Artificial Intelligence: A Modern Approach*.
- Allen, J. D. (2010) — *The Complete Book of Connect-4*. Sterling. *(Origem das 3 regras especiais do PopOut.)*
- Browne et al. (2012) — *A Survey of Monte Carlo Tree Search Methods*. IEEE T-CIAIG.
- Auer, Cesa-Bianchi & Fischer (2002) — *Finite-time Analysis of the Multiarmed Bandit Problem*. (Base teórica do UCB1.)
- Quinlan, J. R. (1986) — *Induction of Decision Trees*. Machine Learning 1.
- Slides das aulas IA 2025/2026.
