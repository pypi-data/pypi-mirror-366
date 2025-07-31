# pddl2hoa

**pddl2hoa** is a Python tool that converts PDDL (Planning Domain Definition Language) planning problems into [HOA (Hanoi Omega Automata)](https://adl.github.io/hoaf/) format. This enables downstream analysis with formal methods tools and automata-based verification frameworks.

---

## Features

- Parse and analyze PDDL domain and problem files
- Convert planning goals into equivalent HOA automata
- Generate [Strategy Templates](https://arxiv.org/abs/2305.14026) for PDDL domains and problems (must install [Pestel](https://github.com/satya2009rta/pestel) seperately)
- Compatible with tools that support HOA format (e.g., Spot, Pestel)
- Designed for integration into formal methods pipelines

---

## Installation

Install via [`uv`](https://github.com/astral-sh/uv) (recommended):

```bash
uv pip install pddl2hoa
```

Or from source:
```bash
git clone https://github.com/yourusername/pddl2hoa.git
cd pddl2hoa
uv pip install .
```

---

## Usage
After installation, use the CLI tool:
```bash
pddl2hoa domain.pddl problem.pddl > edge_labeled_HOA.hoa
```

Or use it as a Python library:
```python
from pddl2hoa import convert_pddl_to_hoa

convert_pddl_to_hoa("domain.pddl", "problem.pddl")
```

---


## Converting from other formats to HOA
This library is designed to be extensible. You can convert almost any domain with a graph-based structure into an HOA representation by subclassing the `TurnBasedGame` abstract base class in [game.py](./pddl2hoa/game.py). Once your game format is implemented, you can call the `format_hoa` method from [generate_hoa.py](./pddl2hoa/generate_hoa.py) to produce a corresponding HOA graph.

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## Links

- [Github](https://github.com/OzGitelson/pddl2hoa)
- [PyPi](https://pypi.org/project/pddl2hoa/)
- [PDDLGym](https://github.com/tomsilver/pddlgym), the PDDL utility that this package uses under the hood
- [HOA Format Spec](https://adl.github.io/hoaf/)



