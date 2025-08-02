# Curses Minesweeper

*(yet)* another Minesweeper implementation, cuz why not?

## Features
- Minesweeper
- Lightweight
- 3 control schemes (WASD, arrow keys, numpad)
- Customizable grid size
- Deterministic mine placement with seeeding
- Runs in most terminals
- Oh, and also Minesweeper

## Installation

```bash
pip install curses-minesweeper
```

## Usage

To play the game in terminal
```bash
minesweeper
```
use minesweeper --help for more information

To start the game from a python script
```python
import curses_minesweeper
curses_minesweeper.launch()
```
use help(curses_minesweeper) for more information