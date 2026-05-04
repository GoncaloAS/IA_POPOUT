"""CLI game loop and built-in strategies (human, random, scripted).

`play_game(p1, p2)` is the central abstraction: each player is a callable
state -> Move|str ('resign'|'draw'). Same loop serves all three game scenarios
(HvH, HvC, CvC) only by changing the arguments.
"""

from __future__ import annotations

import random
from typing import Callable, Optional, Union

from popout import (
    COLS, EMPTY, Move, P1, P2, State,
    apply_move, can_claim_repetition_draw, initial_state, legal_moves, render,
)

Decision = Union[Move, str]
Strategy = Callable[[State], Decision]
Renderer = Callable[[str], None]


HELP_TEXT = """\
Commands:
  0..6           drop in column (shortcut)
  d <col>        explicit drop  (e.g. d 3)
  p <col>        pop            (e.g. p 0)
  draw           claim draw by triple repetition (when applicable)
  q | quit       resign
  ? | help       show this help
"""


class ParseError(Exception):
    """Raised on invalid input; the CLI re-prompts without crashing."""


def format_state(state: State) -> str:
    header = " " + "".join(str(c) for c in range(COLS))
    body = "\n".join(" " + line for line in render(state.board).split("\n"))
    glyph = {P1: "X", P2: "O"}
    if state.winner is None:
        footer = f"P{state.player_to_move} ({glyph[state.player_to_move]}) to move."
    elif state.winner == "draw":
        footer = "Draw."
    else:
        footer = f"P{state.winner} ({glyph[state.winner]}) wins!"
    return f"{header}\n{body}\n{footer}"


def parse_human_input(text: str, state: State) -> Decision:
    t = text.strip().lower()
    if t == "":
        raise ParseError("Empty input. Type '?' for help.")
    if t in ("q", "quit"):
        return "resign"
    if t == "draw":
        if can_claim_repetition_draw(state):
            return "draw"
        raise ParseError("Triple repetition not reached — cannot claim draw.")
    if t in ("?", "help"):
        raise ParseError(HELP_TEXT)
    if len(t) == 1 and t.isdigit():
        return Move(int(t), "drop")
    parts = t.split()
    if len(parts) == 2 and parts[0] in ("d", "drop", "p", "pop"):
        if not parts[1].isdigit():
            raise ParseError(f"Column is not a number: {parts[1]!r}.")
        col = int(parts[1])
        if not 0 <= col < COLS:
            raise ParseError(f"Column out of [0,{COLS-1}]: {col}.")
        kind = "drop" if parts[0] in ("d", "drop") else "pop"
        return Move(col, kind)
    raise ParseError(f"Invalid input: {text!r}. Type '?' for help.")


def human_strategy(
    state: State,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Renderer = print,
) -> Decision:
    while True:
        try:
            raw = input_fn(f"P{state.player_to_move}> ")
        except EOFError:
            return "resign"
        try:
            decision = parse_human_input(raw, state)
        except ParseError as exc:
            output_fn(str(exc))
            continue
        if isinstance(decision, str):
            return decision
        if decision not in legal_moves(state):
            output_fn(f"Illegal move: {decision}. Try another.")
            continue
        return decision


def random_strategy(rng: Optional[random.Random] = None) -> Strategy:
    rng = rng or random.Random()

    def strat(state: State) -> Decision:
        moves = legal_moves(state)
        if not moves:
            return "resign"
        return rng.choice(moves)

    return strat


def scripted_strategy(decisions) -> Strategy:
    it = iter(decisions)

    def strat(state: State) -> Decision:
        return next(it)

    return strat


def play_game(
    p1: Strategy,
    p2: Strategy,
    *,
    on_render: Renderer = print,
    max_turns: int = 300,
    show_intermediate: bool = True,
) -> State:
    state = initial_state()
    strategies = {P1: p1, P2: p2}
    if show_intermediate:
        on_render(format_state(state))

    turns = 0
    while state.winner is None:
        if turns >= max_turns:
            return State(
                board=state.board,
                player_to_move=state.player_to_move,
                history_counts=state.history_counts,
                last_move=state.last_move,
                winner="draw",
            )
        mover = state.player_to_move
        decision = strategies[mover](state)

        if decision == "resign":
            other = 3 - mover
            return State(
                board=state.board,
                player_to_move=state.player_to_move,
                history_counts=state.history_counts,
                last_move=state.last_move,
                winner=other,
            )
        if decision == "draw":
            return State(
                board=state.board,
                player_to_move=state.player_to_move,
                history_counts=state.history_counts,
                last_move=state.last_move,
                winner="draw",
            )

        state = apply_move(state, decision)
        turns += 1
        if show_intermediate:
            on_render(format_state(state))

    return state


def main() -> None:  # pragma: no cover
    print("PopOut CLI — Human vs Human")
    print(HELP_TEXT)
    final = play_game(human_strategy, human_strategy)
    print(format_state(final))


if __name__ == "__main__":  # pragma: no cover
    main()
