# AGENTS.md

このリポジトリは、ChatGPT / Codexとの論文読解を研究ノートとして蓄積するためのものです。

## 最重要ルール

**このリポジトリを編集する前に、毎回この `AGENTS.md` と `papers/_template.tex` を読むこと。**

既存ファイルや過去会話に異なる形式が存在しても、このファイルのルールを優先する。
「有用そうだから」「過去に詳しく議論したから」という理由だけで、項目や説明を追加してはいけない。

## 自然言語の短縮指示

ユーザーは毎回リポジトリ名や詳細ルールを書かなくてよい。
論文が現在の会話から一意に特定できる場合、次のような短い指示をこのリポジトリへの編集指示として扱う。

- 「概要を追加して」
- 「ノートに反映して」
- 「これを反映して」
- 「概要をPDFに追加して」
- 「PDFにも反映して」
- 「PDFに追加して」

これらを受けたら、明示されていなくても **編集前に必ず `AGENTS.md` と `papers/_template.tex` を読み、以下の全ルールに従う。**

- 「追加して」「ノートに反映して」「これを反映して」: GitHub上のLaTeX / BibTeXを更新する。PDFとHTMLはGitHub Actionsが自動更新する。
- 「PDFに追加して」「PDFにも反映して」: 同様にソースを更新し、ActionsによるPDF・HTML自動更新を前提とする。
- 「PDF見せて」「最新版PDF」: 可能なら生成済みの `paper-reading-notes.pdf` を使い、通常はゼロから再コンパイルしない。ソース更新直後で自動ビルドが未完了、またはレイアウト検証が必要な場合のみ手元で再生成する。

現在の会話だけでは対象論文を一意に特定できない場合のみ確認する。

## チャットへの出力

論文を新規追加・更新するときは、リポジトリを編集するだけで終わらない。
**実際に保存する内容をチャットにも必ず表示する。**

通常はAuthors / 主な主張 / 新規性 / 位置付けを読みやすいMarkdownで示す。
ユーザーの明示指示でコメント等を追加した場合は、その追加内容もチャットに示す。
「更新しました」「反映しました」だけで終えてはいけない。
ただし、単に「PDF見せて」など既存内容のPDF表示だけを求めた場合は、本文カードを繰り返さずPDFのみ返してよい。

## 基本原則

各論文は `papers/` 以下の独立したLaTeXファイルとして管理する。ファイル名は原則としてarXiv番号を用いる。

```text
papers/2307.13230.tex
```

各論文のデフォルト形式は必ず次の形とする。

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

## 本文カードの固定フォーマット

デフォルトの本文カードは **Authors + 主な主張 / 新規性 / 位置付け** のみ。
Authors以外の書誌情報（INSPIRE key、DOI、journal、volume、pages、year、report number等）は本文カードに書かず、BibTeXと参考文献欄に集約する。

### 分量と役割

- 各本文項目は原則1文。必要な場合でも最大2文程度。A4 1ページに3--5本程度を目安とする。
- 詳細な背景説明、手法の細部、式の解説を基本カードに持ち込まない。
- 主な主張: その論文が最終的に何を示したかを書く。
- 新規性: 既存研究に対して何が新しいかを書く。単なる作業内容の列挙にしない。
- 位置付け: 分野の中での役割を短く述べる。必要ならユーザーの研究との関係を短く含めてよい。

## 追加コメントは例外

コメント、補足、仮定、研究への関係、重要な式、注意点などの追加項目は、**ユーザーがその論文について明示的に追加を指示した場合にのみ**作成してよい。
過去の会話に詳しい議論が存在すること自体は追加の理由にならない。AIの独自判断で第4の本文項目を増やしてはいけない。
追加コメントを許可された場合は3項目の後ろに追記する。
既にユーザーの指示で追加されたコメントは、指示なしに削除・要約・拡張しない。
PDF・HTMLも同じルールを適用する。

## 参考文献・citation

- 各論文自身を本文中で `\cite{...}` する。
- 関連先行研究に具体的に言及する場合も適切に `\cite{...}` を付ける。
- 書誌情報は原則 `references.bib` に集約する。分割されている場合は `main.tex` の `\bibliography{...}` に含める。
- BibTeXは原則INSPIREの出力形式をそのまま使用し、取得できる場合は `Abe:2026cmt` のようなINSPIRE keyを使う。
- INSPIREのBibTeXを直接取得できない場合は、arXiv・出版社等で書誌情報を確認してINSPIREに近い `@article` entryを作成する。
- INSPIRE keyを確認できない場合は `Surname:YearKeyword` のような識別可能なローカルkeyでよい。
- 未出版論文では原則 `author`, `title`, `eprint`, `archivePrefix`, `primaryClass`, `reportNumber`（存在する場合）, `month`, `year` を保持する。
- 出版済み論文では上記に加えて `doi`, `journal`, `volume`, `number`（存在する場合）, `pages`, `year` を保持する。
- 書誌情報を推測で埋めない。不明なfieldは省略する。
- bibliography styleは `yautphys.bst` を使用する。

## PDF・レイアウト

- 論文タイトルである `\subsection` 見出しは `RuriIro` で表示する。
- `section` 見出しは通常の黒色のままにする。
- **各sectionは必ず新しいページから開始する。** `main.tex`では先頭sectionを除き、各 `\input{sections/...}` の直前に `\clearpage` を置く。
- **参考文献も必ず新しいページから開始する。** `\bibliographystyle` / `\bibliography` の直前に `\clearpage` を置く。
- 新しいsectionを追加するときも改ページ規則を維持する。
- レイアウトを変更したときは、タイトルの色、sectionごとの改ページ、参考文献前の改ページを目視確認する。

### PDF自動生成

- GitHub上のLaTeX / BibTeXを正本とする。
- `.github/workflows/build-pdf.yml`で `main` のLaTeX / BibTeX / bibliography style / build設定変更時にPDFを自動ビルドする。
- `.latexmkrc`を使いpLaTeX + BibTeX + dvipdfmxを維持する。
- 自動生成された閲覧用PDFはリポジトリ直下の `paper-reading-notes.pdf` とする。
- `main.pdf`はローカル・CIの中間生成物としてGit管理しない。
- PDFは閲覧用スナップショットであり、PDF側を直接編集しない。
- 通常の論文追加では毎回ローカルで全ページをレンダリング確認しない。レイアウト変更時、ビルド失敗時、ユーザーが明示的に確認を求めた場合に目視確認する。

## HTML版

- PagesトップはHTML版ノートとする。PDFへの自動転送に戻さない。上部にPDFを開くリンクを残す。
- 正本は引き続きLaTeXとBibTeX。HTML用の本文を手編集・再要約して二重管理しない。
- HTMLはPDFと同じ `main.tex` の読み込み順、同じ論文本文・既存コメントを使う。
- 各カードと参考文献欄に「BibTeX をコピー」「Key」「\cite{…}」を配置する。
- コピーするBibTeXは元entryを保持し、表示用Unicode化・数式変換をコピー文字列に適用しない。
- `\bibliography{...}`の全ファイルを読む。`references-extra.bib`を取りこぼさない。
- PDFとHTMLを同じBuild PDF runで生成し、Pagesはそのrunの `paper-reading-notes-site` artifactを配信する。別コミットの本文とPDFを混在させない。
- 全 `.bib`、HTML生成器、テンプレート、CSS、JavaScriptの変更も自動ビルド対象とする。
- 未接続論文、重複読み込み、未定義citation、対応BibTeX不明、未変換LaTeXを検査で検出する。黙って省略しない。
- HTML生成器・外観・操作を変更したら、`tests/test_html.py` とブラウザ検査でコピー文字列・内部リンク・数式・スマホ幅を確認する。
- 配信成功だけで「最新版」と断定しない。必要に応じて `build-info.json` の元コミット・収録論文・PDFハッシュを確認する。
- 実装とローカル検査の詳細は `web/README.md` を参照する。

## テーマ分類

各論文は適切な `sections/*.tex` から `\input{papers/<arXiv番号>}` する。
既存テーマで自然に分類できない場合は `sections/uncategorized.tex` に入れ、新しいテーマがまとまった段階でsectionを新設する。
同じ論文を複数sectionから読み込んで重複掲載しない。
sectionに最初の論文を追加したときは、そのsectionが `main.tex` から読み込まれていることも確認する。

## 編集時の手順

1. この `AGENTS.md` と `papers/_template.tex` を確認する。
2. `papers/<arXiv番号>.tex` を作成する。
3. 適切なsectionへ読み込みを追加し、`main.tex`から到達できることを確認する。
4. 本人の論文と引用した先行研究のBibTeXを登録する。
5. Authors + 3項目のみであることを確認する。新規追加項目に明示指示がないものは作らない。既存の許可済みコメントは維持する。
6. 実際に保存したAuthors + 3項目（許可された追加内容も）をチャットに表示する。
7. PDF・HTMLの生成はActionsに任せ、必要のないローカル再生成は省略する。

既存論文を更新するときは、その論文に関係する部分だけを変更する。

## 通常運用と文章

- ソースの追加・修正をGitHubへ反映すると、PDF・HTMLはActionsが更新する。
- 閲覧・引用の取得はPagesのHTML版を利用できる。PDF単体を求められた場合は可能なら生成済みの最新版を再利用する。
- 研究ノートとして簡潔かつ具体的に書く。論文の主張と解釈・推論を混同しない。
- 新規性は既存研究との差が分かるように、位置付けは分野での役割を短く書く。

## LaTeX

- `main.tex`は `jsarticle` を使用し、pLaTeX + dvipdfmxでコンパイルする。
- 共通package・レイアウト・数式マクロは `macro_jsarticle.tex` を読み込む。
- `macro.tex`は別用途として保持し、必要がない限り `main.tex` から読み込まない。
- `papers/*.tex`は本文断片とし、document classやpackageを個別に宣言しない。
