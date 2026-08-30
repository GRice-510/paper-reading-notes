# Paper Reading Notes

ChatGPT / Codex との論文読解を蓄積し、最終的に1冊のPDFとして参照できる形にまとめるための研究ノートです。

## 方針

- 1論文につき1つの `papers/*.tex` を作る。
- 各論文は `\subsection{論文タイトル --- arXiv:XXXX.XXXXX}` として管理する。
- 基本カードは短く保ち、詳細な議論が生じた論文だけ追記する。
- 書誌情報は INSPIRE を基準に `references.bib` に蓄積する。
- テーマごとの `sections/*.tex` から各論文ファイルを `\input` し、`main.tex` から1つのPDFにまとめる。

## LaTeX

- 本文は `jsarticle` を使用する。
- 共通設定・数式マクロは `macro_jsarticle.tex` を `main.tex` から読み込む。
- `macro.tex` は既存の別用途マクロとして保存しておく。
- bibliography style は `yautphys.bst` を使用する。

## 構成

```text
paper-reading-notes/
├── README.md
├── AGENTS.md
├── main.tex
├── macro_jsarticle.tex
├── macro.tex
├── yautphys.bst
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

pLaTeX + dvipdfmx を用います。

```bash
platex main.tex
bibtex main
platex main.tex
platex main.tex
dvipdfmx main.dvi
```

生成された `main.pdf` はGit管理しません。
