from dataclasses import dataclass
from typing import List, Tuple


Coord = Tuple[int, int]  # (row, col) with 0-based indices


@dataclass(frozen=True)
class Pattern:
    name: str
    coords: List[Coord]
    weight: int


def winning_patterns() -> List[Pattern]:
    """Returns the five patterns as per DS-HomeWork.md.

    First four patterns pay 1x symbol multiplier (weight=1).
    Fifth pattern pays 5x symbol multiplier (weight=5).
    """
    p: List[Pattern] = []
    # 4.1: top-left 2x2
    p.append(Pattern(
        name="top_left_2x2",
        coords=[(0, 0), (0, 1), (1, 0), (1, 1)],
        weight=1,
    ))
    # 4.2: top-right 2x2
    p.append(Pattern(
        name="top_right_2x2",
        coords=[(0, 1), (0, 2), (1, 1), (1, 2)],
        weight=1,
    ))
    # 4.3: bottom-left 2x2
    p.append(Pattern(
        name="bottom_left_2x2",
        coords=[(1, 0), (1, 1), (2, 0), (2, 1)],
        weight=1,
    ))
    # 4.4: bottom-right 2x2
    p.append(Pattern(
        name="bottom_right_2x2",
        coords=[(1, 1), (1, 2), (2, 1), (2, 2)],
        weight=1,
    ))
    # 4.5: full 3x3
    p.append(Pattern(
        name="full_3x3",
        coords=[(r, c) for r in range(3) for c in range(3)],
        weight=5,
    ))
    return p

