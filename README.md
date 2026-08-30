# Paper Reading Notes

ChatGPT / Codex との論文読解を蓄積し、最終的に1冊のPDFとして参照できる形にまとめるための研究ノートです。

> AI編集時は、必ず最初に `AGENTS.md` と `papers/_template.tex` を確認してください。

## 基本カード

1論文につき1つの `papers/*.tex` を作り、各論文は次の固定形式をデフォルトとします。

```latex
\subsection{Paper Title --- arXiv:XXXX.XXXXX}

\textbf{Authors:} Author A, Author B, Author C

\paragraph{主な主張}
...

\paragraph{新規性}
...

\paragraph{位置付け}
...
```

デフォルトでは Authors / 主な主張 / 新規性 / 位置付け以外を追加しません。
コメントや補足は、ユーザーがその論文について明示的に追加を指示した場合だけ追記します。
各本文項目は原則1文、長くても2文程度に抑えます。

書誌情報は INSPIRE を基準に `references.bib` に集約し、本文中では `\cite{...}` で参照します。

## 構成

- `papers/`: 1論文1ファイル
- `sections/`: テーマ別に各論文を `\input`
- `references.bib`: 参考文献
- `main.tex`: 全体を1つのPDFへまとめる
- `AGENTS.md`: AI編集時の最優先ルール

## 通常運用

GitHub 上の LaTeX ソースを正本とします。
論文追加・修正時は原則としてリポジトリだけを更新し、PDFは明示的に求められた場合のみ生成します。

## LaTeX

本文は `jsarticle`、pLaTeX + dvipdfmx を使用します。
共通設定・数式マクロは `macro_jsarticle.tex` から読み込み、bibliography style は `yautphys.bst` を使用します。

```bash
platex main.tex
bibtex main
platex main.tex
platex main.tex
dvipdfmx main.dvi
```

生成された `main.pdf` はGit管理しません。
