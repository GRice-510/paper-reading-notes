# AGENTS.md

このリポジトリは、ChatGPT / Codex との論文読解を研究ノートとして蓄積するためのものです。

## 基本原則

各論文は `papers/` 以下の独立した LaTeX ファイルとして管理する。
ファイル名は原則として arXiv 番号を用いる。

```text
papers/2307.13230.tex
```

各論文ファイルは次の形式とする。

```latex
\subsection{Paper Title --- arXiv:XXXX.XXXXX}

\paragraph{主な主張}
...

\paragraph{新規性}
...

\paragraph{位置付け}
...
```

## 内容

各論文について記載するのは、原則として次の3項目のみとする。

1. 主な主張
2. 新規性
3. 位置付け

各項目は原則 1--2 文とし、できるだけ簡潔にする。
A4 1ページに3--5本程度が収まる密度を目安とする。
著者名、INSPIRE key、DOI、journal、year などの書誌情報は本文カードに重複して書かない。

## 参考文献・citation

- 各論文自身を本文中で `\cite{...}` する。
- 関連先行研究に言及する場合も適切に `\cite{...}` を付ける。
- 書誌情報は `references.bib` に集約する。
- BibTeX key はリポジトリ内部で読みやすい名前を使い、INSPIRE key に合わせる必要はない。
- 書誌情報そのものは可能な限り INSPIRE、arXiv、出版社等で確認する。
- bibliography style は `yautphys.bst` を使用する。

## テーマ分類

各論文は適切な `sections/*.tex` から `\input{papers/<arXiv番号>}` してPDFに含める。
既存テーマで自然に分類できない場合は `sections/uncategorized.tex` に入れ、新しいテーマが十分にまとまった段階で section を新設する。
同じ論文を複数 section から `\input` して重複掲載しない。
新しい section に最初の論文を追加したときは、その section が `main.tex` から読み込まれていることも確認する。

## 編集時のルール

論文を1本追加するときは、原則として次を行う。

1. `papers/<arXiv番号>.tex` を作成する。
2. 適切な `sections/*.tex` に `\input{papers/<arXiv番号>}` を追加する。
3. 論文自身と本文中で引用した先行研究の BibTeX を `references.bib` に追加する。

既存論文を更新するときは、その論文に関係する部分だけを変更する。

## 文章

- 研究ノートとして簡潔かつ具体的に書く。
- 論文の主張と、解釈・推論を混同しない。
- 新規性は既存研究との差が分かるように書く。
- 位置付けでは分野の中での役割を短く述べる。

## LaTeX

- `main.tex` は `jsarticle` を使用し、pLaTeX + dvipdfmx でコンパイルする。
- 共通 package・レイアウト・数式マクロは、ユーザー提供の `macro_jsarticle.tex` を `main.tex` から読み込む。
- `macro.tex` は別用途マクロとして保持し、必要がない限り `main.tex` からは読み込まない。
- 各 paper ファイル単体では document class や package を宣言しない。
- `papers/*.tex` は `main.tex` から読み込まれる本文断片として書く。
