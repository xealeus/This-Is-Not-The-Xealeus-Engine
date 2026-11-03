# This Is Not The Xealeus Engine

A deliberately accessible guided demonstration of the computational experiments behind the Xealeus Voynich project.

> **The Xealeus Engine does not solve the Voynich Manuscript.**
>
> The lute remains under investigation.

## What this is

This repository packages a small graphical companion to the original Xealeus Voynich experiments. It is meant to let curious readers inspect the project without first having to become comfortable with Python, terminals, file paths, or corpus-processing scripts.

The interface is intentionally theatrical: faux late-1990s Windows chrome, oversized buttons, unnecessary mechanical click sounds, fake menu options, epistemic banana peels, and a Forbidden Lute. The calculations underneath are ordinary Python and are included in source form.

The central research question is narrower than a Voynich "solution":

> **How much of the unusual surface structure of EVA-transcribed Voynichese can be reproduced by compact local state-transition mechanisms?**

## Download the Windows build

The compiled Windows application is distributed from the repository's **Releases** page.

Look for:

`This_Is_Not_The_Xealeus_Engine.exe`

The Windows build is a terminal-free single-file executable. No Python installation is required to run that compiled release.

Because the executable is independently built and not code-signed, Windows SmartScreen may identify it as an unknown publisher. The complete Python source and build script are provided here so the executable can be independently rebuilt and inspected.

## Guided Demo mode

The default mode works immediately. It uses project-derived aggregate data stored in `data/demo_data.json`.

The bundled package contains reference measurements and trained count/transition tables used by the demonstration. It does **not** contain the original IVTFF transcription.

The guided tests cover:

- parser / corpus sanity checks;
- Prefix / Core / Suffix coupling;
- Currier A / B Core transfer;
- Compiler V1;
- Compiler V2 and cross-word state;
- a simple two-dimensional paragraph-geometry probe.

The compiler buttons can generate fresh synthetic lines from the bundled transition tables.

## Full Reproduction mode

The application also contains an optional full-reproduction path. A researcher may independently obtain a compatible IVTFF transcription and select it using the application's faux file browser.

The program then parses that source and recomputes the tests directly rather than relying on the bundled reference summaries.

This is the audit path: obtain the source independently, inspect the implementation, change the assumptions, rerun the measurements, and try to make the model fail.

## Run from Python

Python 3 with Tkinter is sufficient for the application itself; the runtime otherwise uses the Python standard library.

```bash
python voynich_guided_demo.py
```

On some Linux distributions, Tkinter may need to be installed separately through the system package manager.

## Build the Windows executable

A Windows build helper is included:

`build_windows.bat`

It checks for Python and PyInstaller, installs PyInstaller when necessary, and builds a single-file GUI executable without a terminal window.

The finished file is written to:

```text
dist\This_Is_Not_The_Xealeus_Engine.exe
```

The executable bundles the guided-demo data and project audio assets. It does not bundle the IVTFF source transcription.

For a reproducible build environment, the PyInstaller dependency is also listed in `requirements-build.txt`.

## Repository layout

```text
.
├── README.md
├── LICENSE
├── LICENSE-CONTENT.md
├── CITATION.cff
├── DATA_PROVENANCE.md
├── EASTER_EGGS.md
├── THIRD_PARTY_NOTICES.md
├── requirements-build.txt
├── build_windows.bat
├── run_linux.sh
├── voynich_guided_demo.py
├── assets/
│   ├── click.wav
│   └── voynich_lute_tempus_perfectum.wav
└── data/
    └── demo_data.json
```

Build products such as `build/`, `dist/`, `*.spec`, and `__pycache__/` are intentionally excluded from normal repository history.

## Data provenance

The reference analysis was produced from the Landini–Stolfi Interlinear IVTFF archive using the Takeshi Takahashi `;H` EVA stream and archive metadata used by the project.

The original transcription is **not redistributed** here. The self-contained demo contains project-derived aggregate measurements, transition/count tables, reference statistics, and synthetic compiler output.

See [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## The Easter eggs

The original project contains deliberate epistemic traps: a microscopic broken test, prose produced across nearby experimental iterations, intentionally seductive medieval framing, an absurd Renaissance-computer image, and an entirely unreasonable amount of lute.

They are jokes about the distinction between:

**source → measurement → model → representation → interpretation → historical claim**

They are not hidden changes to the corpus and are not evidence that the manuscript encodes lute music.

See [`EASTER_EGGS.md`](EASTER_EGGS.md).

## What this project does not claim

This project does not claim to translate the Voynich Manuscript.

It does not establish the manuscript's language, cipher, authorship, historical purpose, or exact production mechanism.

It tests whether compact computational mechanisms can reproduce selected measurable properties of a transcription of its surface text.

If you disagree with the model, excellent: change the segmentation, change the source transcription, build a better null model, find a bug, find a confound, or show that a simpler mechanism reproduces the same behavior.

**Disagreement can become another program.**

## Citation

Machine-readable citation metadata is provided in [`CITATION.cff`](CITATION.cff). GitHub can use this file to expose a **Cite this repository** control.

For scholarly use, prefer citing a fixed tagged release (and its DOI, if/when an archived DOI is assigned) rather than the moving `main` branch.

## Licensing

- **Software source code:** MIT License. See [`LICENSE`](LICENSE).
- **Project-authored documentation, interface text, audio/visual assets, and derived demonstration data:** CC BY 4.0 unless otherwise noted. See [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md).
- **Third-party source materials:** not relicensed by this repository. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

No Voynich Manuscripts were solved during the execution of this program.

The lute remains under investigation.
