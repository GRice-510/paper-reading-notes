# AGENTS.md

このリポジトリは、ChatGPT / Codex との論文読解を研究ノートとして蓄積するためのものです。

## 基本原則

各論文は `papers/` 以下の独立した LaTeX ファイルとして管理する。
ファイル名は原則として arXiv 番号を用いる。

```text
papers/2307.13230.tex
```

各論文ファイルは原則として次の形式から始める。

```latex
\subsection{Paper Title --- arXiv:XXXX.XXXXX}

\textbf{Authors:} ... \\
\textbf{Reference:} \cite{BibTeXKey}

\paragraph{主な主張}
...

\paragraph{新規性}
...

\paragraph{位置付け}
...
```

## 基本カードの内容

通常の論文では、原則として以下のみを書く。

1. Authors
2. Reference citation
3. 主な主張
4. 新規性
5. 位置付け

`主な主張`、`新規性`、`位置付け` は各 1--2 文を基本とし、できるだけ簡潔にする。
追加の詳細議論がない論文は、A4 1ページに3--5本程度が収まる密度を目安とする。

## 詳細ノート

ChatGPTとの対話で重要な理解が得られた場合のみ、その subsection 内に短い追加ノートを置いてよい。
候補は、重要な式の解釈、仮定・限界、論文への疑問、研究への具体的な応用、引用時の注意点など。
詳細ノートも必要最小限にし、基本カードと内容が重複する説明は避ける。

## 参考文献・citation

- INSPIRE citation key を本文に表示しない。
- 各論文自身を `\cite{...}` で参照し、関連先行研究に言及する場合も適切に `\cite{...}` を付ける。
- 書誌情報は `references.bib` に集約する。
- BibTeX key はリポジトリ内部で読みやすい名前を使えばよく、INSPIRE key に合わせる必要はない。
- 書誌情報そのものは可能な限り INSPIRE、arXiv、出版社等で確認する。
- DOI、journal、year 等は本文に重複して書かず、`references.bib` に保持する。
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

既存論文を更新するときは、その論文に関係する部分だけを変更し、無関係なノートを勝手に書き換えない。

## 文章

- 研究ノートとして簡潔かつ具体的に書く。
- 論文の主張と、解釈・推論・研究への示唆を混同しない。
- 新規性は既存研究との差が分かるように書く。
- 位置付けでは分野の中での役割を短く述べる。

## LaTeX

- `main.tex` は `jsarticle` を使用し、pLaTeX + dvipdfmx でコンパイルする。
- 共通 package・レイアウト・数式マクロは、ユーザー提供の `macro_jsarticle.tex` を `main.tex` から読み込む。
- `macro.tex` は別用途マクロとして保持し、必要がない限り `main.tex` からは読み込まない。
- 各 paper ファイル単体では document class や package を宣言しない。
- `papers/*.tex` は `main.tex` から読み込まれる本文断片として書く。
