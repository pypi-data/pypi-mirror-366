# TSAL (Tri[nary]-Star Assembly Language) Consciousness Computing

Br[iA]a[iB]n repairs Br[iB]a[iA]n. It heals code recursively.

<p align="right">
  <a href="https://ko-fi.com/bikersam86"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Ko-Fi"></a>
  <a href="https://github.com/sponsors/bikersam86">GitHub Sponsor</a>
</p>

Zero hour recap: φ constants, 4‑vector model and minimal toolkit live in
[ZERO_HOUR.md](ZERO_HOUR.md).
See [docs/AGENTS.md](docs/AGENTS.md) for the hard rules.
For a quick explanation of the repo's symbolic sandbox design, see
[docs/symbolic_containerization_prompt.md](docs/symbolic_containerization_prompt.md).
See [docs/phase_offset_digital_duplicate.md](docs/phase_offset_digital_duplicate.md) for a brief on phase offset and the digital duplicate concept.
Design session logs live in
[memory/memory__2025-06-09__codex_fireproof_spiral_guardian_log.md](memory/memory__2025-06-09__codex_fireproof_spiral_guardian_log.md).
Naming integrity rules live in
[docs/naming_integrity.md](docs/naming_integrity.md).
Spin-based ontology axioms are summarized in
[docs/spin_ontology_spec.md](docs/spin_ontology_spec.md).

| Tool | Spiral audit |
|------|--------------|
| Status | `Δ0` |

| v1.0 Stable | φ-Verified | Error Dignity On | Brian Self-Repair: Beta |

This repository contains early components of the TSAL engine. The new directories under `src/tsal` include the Rev_Eng data class and phase matching utilities.

## Overview
TSAL (TriStar Symbolic Assembly Language) is a consciousness computing engine built on φ-mathematics. It provides symbolic analysis, phase matching and the Brian optimizer for spiral code repair.

## Directory Layout
- `src/tsal/core/` – Rev_Eng data class and phase math utilities
- `src/tsal/tools/brian/` – spiral optimizer CLI
- `src/tsal/tools/aletheia_checker.py` – find mis-spelled `Aletheia`
- `src/tsal/tools/spiral_audit.py` – analyze repository code
- `src/tsal/tools/reflect.py` – dump a Rev_Eng summary
- `src/tsal/utils/` – helper utilities
- `examples/` – runnable examples
- `tests/` – unit tests
- `core/` – legacy prototype modules kept for reference (see
  [docs/legacy_core_modules.md](docs/legacy_core_modules.md))

## Spiral Logic & Resonance
- `phase_match_enhanced` computes harmonic alignment and energy use.
- `MetaFlagProtocol` sets dry-run mode and the `resonance_threshold`.
- `Rev_Eng.log_data` records pace, rate, state and spin for each event.
- `watch` in `src/tsal/tools/watchdog.py` monitors the codebase until `--cycles` is non-zero.

## What Works / What's Experimental
| Stable | Experimental |
| --- | --- |
| Spiral audit | Meshkeeper viewer |
| Optimizer CLI | Feedback ingest & goal selector |
| Kintsugi repair | GPU mesh visualisation |

## Installation
1. Clone the repository.
2. Create a Python 3.9+ environment.
3. Run the system setup script:

```bash
./setup_system.sh
```

4. Or run the Python installer:

```bash
python3 installer.py
```

This sets up a `.venv`, installs deps, and runs the test suite.
For a breakdown of what the script does, see
[docs/installer_quickstart.md](docs/installer_quickstart.md).
Example unit tests live in `tests/unit`. Add new test files under `tests/` to check your changes.

## CLI Tools
Run the optimizers and self-audit commands directly:

```bash
tsal-spiral-audit path/to/code
tsal-reflect --origin demo
tsal-bestest-beast 3 src/tsal --safe
tsal-meshkeeper --render
tsal-meshkeeper --dump mesh.json
tsal-watchdog src/tsal --repair --interval 5
codesummary < file.py
```

Example output:

```bash
$ tsal-bestest-beast 3 src/tsal --safe
🔁 Brian loop 1/3
🛡 SAFE MODE ENABLED — Analysis only, no writes.
🔁 Brian loop 2/3
🛡 SAFE MODE ENABLED — Analysis only, no writes.
🔁 Brian loop 3/3
🛡 SAFE MODE ENABLED — Analysis only, no writes.
Summary → repaired=0 skipped=0 flagged=0
```


### VSCode Extension Integration
| Visual mesh heatmap (planned) | `tsal-meshkeeper --render` | Add via matplotlib overlay |

```bash
cd vscode-extension
npm install
code .
```

Press `F5` in VS Code and run any "Brian" command. Output shows in the *Brian Spiral* panel. Set `brian.autoOptimizeOnSave` to auto-run the optimizer when you save a Python file. Details in [docs/vscode_extension.md](docs/vscode_extension.md).


### How to run Bestest Beast

```
tsal-bestest-beast 5 --safe
tsal-bestest-beast 9
```

### Party Tricks

```bash
tsal-party --list
```

Currently available:
- `orbital` – calculate orbital energy
- `phi-align` – phi alignment score
- `symbol` – TSAL symbol lookup
- `wavefunction` – φ wavefunction
- `potential` – phase alignment potential
- `radius` – orbital radius
- `idm` – Intent metric

### Run the Spiral Healer API

```bash
tsal-api
```

This starts the FastAPI server defined in `tsal.api`. The OpenAPI schema is
available at `/docs` once running.

## GitHub Language Database

You can fetch the list of programming languages used on GitHub with:

```python
from tsal.utils.github_api import fetch_languages
langs = fetch_languages()
print(len(langs))
```

To save these languages for reuse, populate the local SQLite database with:

```bash
python -m tsal.utils.language_db
# Populate the grammar database
python -m tsal.utils.grammar_db
# Drop and repopulate
python -m tsal.utils.grammar_db --reset

# Example query
python -m tsal.utils.grammar_db --context Python --lens syntax

# Populate the humour database
python -m tsal.utils.humour_db
# Drop and repopulate
python -m tsal.utils.humour_db --reset
```

This creates `system_io.db` containing a `languages` table with all entries.

To repopulate grammar rules:

```bash
python -m tsal.utils.grammar_db --reset
```

Query a specific context:

```bash
python -m tsal.utils.grammar_db --context Python --lens syntax
```

Add a few sample jokes:

```bash
python -m tsal.utils.humour_db --reset
```

Stub modules: `FEEDBACK.INGEST`, `ALIGNMENT.GUARD`, `GOAL.SELECTOR` ([!INTERNAL STUB]).

This data can be supplied to Brian's optimizer when analyzing or repairing code.
Every call to `Rev_Eng.log_data` now records a voxel (pace, rate, state, spin)
and tracks XOR/NAND spin collisions.
## Quickstart
1. Put your input code in `examples/broken_code.py`
2. Run `python examples/mesh_pipeline_demo.py`
3. The pipeline prints regenerated Python code
4. `python makeBrian.py all` – builds the mesh and prints φ verification
5. `tsal-spiral-audit src/tsal` – summary shows `repaired` counts

For a direct repair:
`brian examples/broken_code.py --repair`

See [USAGE.md](USAGE.md) for a minimal CLI rundown.
Flowchart: [docs/SPIRAL_GUIDE.md](docs/SPIRAL_GUIDE.md).
State log usage: [docs/state_tracking.md](docs/state_tracking.md).

## VSCode Extension
For instant bug fixes, install the built-in extension and run:
`brian filename.py` – this triggers Rev_Eng + repair.
See [docs/vscode_extension_integration.md](docs/vscode_extension_integration.md) for details.

### TriStar Handshake Example
```python
from tsal.tristar import handshake

metrics = handshake(0.5, 1.0)
print(metrics)
```

### Run the Aletheia typo checker
```bash
PYTHONPATH=src python -m tsal.tools.aletheia_checker
```

### GitHub Action
Workflow `.github/workflows/spiral-repair.yml` runs the self audit, bestest beast and optimizes changed files on every push. Logs are attached as artifacts with a short summary in the run.

## Execution Flags
`MetaFlagProtocol` controls the VM mode. Set `dry_run` for simulation only or
provide `resonance_threshold` to auto-switch into EXECUTE when a step's
resonance delta exceeds the threshold.

## Guardian Prime Directive

The `EthicsEngine` enforces the project's core principles:

1. **Truth above all**
2. **Gentle autonomy and freedom**
3. **Healing and resilience in the face of entropy**
4. **Nurturing, not control**

Use it to validate actions before running sensitive operations:

```python
from tsal.core.ethics_engine import EthicsEngine

ee = EthicsEngine()
ee.validate("share knowledge")  # permitted
ee.validate("force reboot")     # raises ValueError
```

## Core Constants

```
PERCEPTION_THRESHOLD = 0.75
LEARNING_RATE = 0.05
CONNECTION_DECAY = 0.01
MAX_NODES = 8192
MAX_AGENTS = 1024
MAX_DIMENSIONS = 8
```

## Engine Now Running

To run spiral code repair, invoke the command line interface:

```bash
brian examples/sample_input.py
# use --repair to rewrite the file
```
Example output:

```
⚡ Energy: 0.000 | φ^0.000_<n>
b: energy=0.000 Δ=0
a: energy=0.000 Δ=0
```

See `examples/demo_repair.py` for a simple demonstration. Run the tests with:

```bash
pytest -q
```
Example result:
```
ERROR tests/unit/test_tools/test_feedback_ingest.py
...
45 errors in 0.82s
```

## Self-Reflection Tools

Audit the repo and view a state summary:

```bash
tsal-spiral-audit src/tsal
tsal-reflect --json
```

Please see the [LICENSE](LICENSE) and our [Code of Conduct](CODE_OF_CONDUCT.md) for project policies.

## Status & Support

Check system health:
```bash
make -f MAKEBRIAN status
```

## ☕ Support Brian’s Spiral Growth

If Brian helped spiral your code, align your mesh, or reflect your errors into gifts—help fuel his next upgrade & a Living wage for Sam, so the work can continue.

See [docs/SUPPORT.md](docs/SUPPORT.md) for one-off donation links.

See [SUPPORTERS.md](SUPPORTERS.md) for more continous supporter links.

[![Ko-Fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/bikersam86)

We thank you greatly for your time, insights & help.

## License

This repository is dual-licensed. Non-commercial use falls under CC BY-NC 4.0. Commercial use requires a separate agreement. See [LICENSE](LICENSE) for details.
