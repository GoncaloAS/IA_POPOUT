"""PopOut game engine — variant of Connect-4 with pop moves.

Rules implemented (Allen 2010):
- Pop creating four-in-row for both players: pop player wins.
- Full board with no legal pops: draw.
- Triple state repetition: either player may declare draw.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

import numpy as np

ROWS, COLS = 6, 7
EMPTY, P1, P2 = 0, 1, 2
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]
WINNER_DRAW = "draw"


@dataclass(frozen=True)
class Move:
    column: int
    kind: str  # 'drop' or 'pop'

    def __post_init__(self) -> None:
        if self.kind not in ("drop", "pop"):
            raise ValueError(f"invalid kind: {self.kind!r}")
        if not 0 <= self.column < COLS:
            raise ValueError(f"column out of [0,{COLS-1}]: {self.column}")

    def __str__(self) -> str:
        return f"{self.kind}({self.column})"


@dataclass(frozen=True)
class State:
    board: np.ndarray
    player_to_move: int
    history_counts: Dict[bytes, int] = field(default_factory=dict)
    last_move: Optional[Move] = None
    winner: Union[int, str, None] = None


def state_key(board: np.ndarray, player_to_move: int) -> bytes:
    return board.tobytes() + bytes([player_to_move])


def initial_state() -> State:
    board = np.zeros((ROWS, COLS), dtype=np.int8)
    history = {state_key(board, P1): 1}
    return State(board=board, player_to_move=P1, history_counts=history)


def legal_moves(state: State) -> List[Move]:
    if state.winner is not None:
        return []
    moves: List[Move] = []
    for c in range(COLS):
        if state.board[0, c] == EMPTY:
            moves.append(Move(c, "drop"))
        if state.board[ROWS - 1, c] == state.player_to_move:
            moves.append(Move(c, "pop"))
    return moves


def _drop_row(board: np.ndarray, c: int) -> int:
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
                rr, cc = r + 3 * dr, c + 3 * dc
                if 0 <= rr < ROWS and 0 <= cc < COLS:
                    if all(board[r + i * dr, c + i * dc] == player for i in range(4)):
                        return True
    return False


def _has_legal_pop(board: np.ndarray, player: int) -> bool:
    return bool((board[ROWS - 1, :] == player).any())


def _has_legal_drop(board: np.ndarray) -> bool:
    return bool((board[0, :] == EMPTY).any())


def check_win(
    board: np.ndarray, last_move: Move, mover: int
) -> Union[int, str, None]:
    """Return winning player (1 or 2), 'draw', or None."""
    other = 3 - mover
    me_won = _four_in_a_row_for(board, mover)
    other_won = _four_in_a_row_for(board, other)

    if last_move.kind == "pop":
        # Allen 2010 rule: simultaneous four-in-row by pop favours pop player.
        if me_won:
            return mover
        if other_won:
            return other
    else:  # drop — only the dropping player can complete a four
        if me_won:
            return mover

    next_player = 3 - mover
    if not _has_legal_drop(board) and not _has_legal_pop(board, next_player):
        return WINNER_DRAW
    return None


def apply_move(state: State, move: Move) -> State:
    if state.winner is not None:
        raise ValueError("Game already finished.")

    new_board = state.board.copy()
    mover = state.player_to_move

    if move.kind == "drop":
        r = _drop_row(new_board, move.column)
        if r == -1:
            raise ValueError(f"Column {move.column} is full.")
        new_board[r, move.column] = mover
    else:  # pop
        if new_board[ROWS - 1, move.column] != mover:
            raise ValueError(
                f"Illegal pop on column {move.column}: bottom not player {mover}."
            )
        # Shift column down by one; top becomes empty.
        new_board[1:ROWS, move.column] = state.board[0 : ROWS - 1, move.column]
        new_board[0, move.column] = EMPTY

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


def render(board: np.ndarray) -> str:
    glyph = {EMPTY: "-", P1: "X", P2: "O"}
    lines = ["".join(glyph[int(v)] for v in row) for row in board]
    return "\n".join(lines)
