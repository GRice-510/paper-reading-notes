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

各論文について記載するのは、デフォルトでは次の3項目のみとする。

1. 主な主張
2. 新規性
3. 位置付け

各項目は原則 1--2 文とし、できるだけ簡潔にする。
A4 1ページに3--5本程度が収まる密度を目安とする。
著者名、INSPIRE key、DOI、journal、year などの書誌情報は本文カードに重複して書かない。

### 追加コメント

- デフォルト状態では上記3項目以外を追加しない。
- ユーザーから明示的に指示された場合にのみ、その論文の subsection 内へコメント・補足・式の解釈・研究上の注意点などを追加する。
- 追加コメントは既存の3項目を置き換えず、その後ろに追記する。
- 追加内容も研究ノートとして必要最小限にし、基本カードとの重複を避ける。
- PDFを生成する場合も、この簡潔な3項目形式を標準とし、指示された論文だけ追加コメントを含める。

## 参考文献・citation

- 各論文自身を本文中で `\cite{...}` する。
- 関連先行研究に言及する場合も適切に `\cite{...}` を付ける。
- 書誌情報は `references.bib` に集約する。
- BibTeX は原則として INSPIRE が出力する形式をそのまま使用する。citation key も、取得できる場合は `Abe:2026cmt` のような INSPIRE の key を使用する。
- INSPIRE の BibTeX を直接取得できない場合は、arXiv・出版社等で書誌情報を確認した上で、INSPIRE 出力に近い形式の `@article` entry を作成する。その場合の key は `Surname:YearKeyword` のようなローカルな識別可能な形式でよい。
- 未出版論文では原則として `author`, `title`, `eprint`, `archivePrefix`, `primaryClass`, `reportNumber`（存在する場合）, `month`, `year` を保持する。
- 出版済み論文では上記に加えて `doi`, `journal`, `volume`, `number`（存在する場合）, `pages`, `year` を保持する。
- 書誌情報を推測で埋めない。不明な field は省略する。
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

## 通常運用

- GitHub 上の LaTeX ソースを正本とする。
- 論文の追加・修正時は、原則としてリポジトリのみ更新する。
- PDF は閲覧用スナップショットとして扱い、ユーザーから明示的に求められた場合のみ生成する。

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
