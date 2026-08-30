# Paper Reading Notes

ChatGPT / Codex との論文読解を蓄積し、最終的に1冊のPDFとして参照できる形にまとめるための研究ノートです。

## 方針

- 1論文につき1つの `papers/*.tex` を作る。
- 各論文は `\subsection{論文タイトル --- arXiv:XXXX.XXXXX}` として管理する。
- 基本カードは短く保ち、詳細な議論が生じた論文だけ追記する。
- 書誌情報は INSPIRE を基準に `references.bib` に蓄積する。
- テーマごとの `sections/*.tex` から各論文ファイルを `\input` し、`main.tex` から1つのPDFにまとめる。

## 構成

```text
paper-reading-notes/
├── README.md
├── AGENTS.md
├── main.tex
├── references.bib
├── .gitignore
├── sections/
│   ├── moduli-dynamics.tex
│   ├── modular-cosmology.tex
│   ├── inflation.tex
│   ├── string-phenomenology.tex
│   └── uncategorized.tex
└── papers/
    └── _template.tex
```

## ビルド

LuaLaTeX を用います。

```bash
latexmk -lualatex main.tex
```

生成された `main.pdf` はGit管理しません。
