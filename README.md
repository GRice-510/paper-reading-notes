# Paper Reading Notes

ChatGPT / Codexとの論文読解を蓄積する研究ノートです。LaTeX / BibTeXを正本として、PDFとHTMLの両方を自動生成します。

## HTML版・PDF版

**[HTML版ノートを開く](https://grice-510.github.io/paper-reading-notes/)**  
[PDF版を開く](https://grice-510.github.io/paper-reading-notes/paper-reading-notes.pdf) · [リポジトリ内のPDF](./paper-reading-notes.pdf)

HTML版では、各論文カードと参考文献欄の両方で **BibTeX全文 / citation key / `\cite{...}`** をその場でコピーできます。
タイトル・著者・arXiv番号・本文で検索し、テーマ別に絞り込めます。数式はMathJaxで表示します。
「BibTeXを表示」で原文を確認でき、ブラウザがコピーを許可しない場合は選択コピー用の欄を開きます。

`main` のソース更新後、ActionsがPDFとHTMLを**同じコミットから**生成してPagesへ配信します。
トップページはHTML版です。上部のPDFボタンは内容ハッシュ付きURLを開き、古いPDFのキャッシュを避けます。
収録内容の更新日時・版番号はHTML左側に表示します。ビルド・デプロイ中は直前の成功版が表示されます。

> AI編集時は、必ず最初に `AGENTS.md` と `papers/_template.tex` を確認してください。

## 基本カード

1論文につき1つの `papers/*.tex` を作り、次の固定形式をデフォルトとします。

```latex
\subsection{Paper Title --- arXiv:XXXX.XXXXX}

\textbf{Authors:} Author A, Author B, Author C

\paragraph{主な主張}
... \cite{BibTeXKey}。

\paragraph{新規性}
...

\paragraph{位置付け}
...
```

デフォルトではAuthorsと3項目以外を追加しません。各本文項目は原則1文、長くても2文程度とします。
コメント・補足はユーザーがその論文について明示的に指示した場合だけ追加します。
書誌情報はINSPIREを基準にBibTeXへ集約し、本文では `\cite{...}` で参照します。

## 短い指示での運用

対象論文が会話から一意に特定できる場合、「概要を追加して」「ノートに反映して」「概要をPDFに追加して」でソースを更新します。
PDFとHTMLはGitHub Actionsが自動更新します。実際に保存したAuthors / 主な主張 / 新規性 / 位置付けはチャットにも表示します。

## 構成

- `papers/`: 1論文1ファイル
- `sections/`: テーマ別の読み込み
- `references.bib`, `references-extra.bib`: 参考文献（`main.tex`の指定に従う）
- `main.tex`: 全体の構成
- `macro_jsarticle.tex`: 共通レイアウト・数式マクロ
- `paper-reading-notes.pdf`: Actionsが更新する閲覧用PDF
- `scripts/build_html.py`, `web/`: HTML生成器・外観・操作
- `tests/`: 変換、コピー、数式、検索、内部リンク、スマホ幅の検査
- `.github/workflows/build-pdf.yml`: PDFとHTMLを同じ版から生成
- `.github/workflows/deploy-pages.yml`: 同じrunの成果物をPagesへ配信
- `.github/workflows/html-preview.yml`: HTMLのブラウザ検査
- `.latexmkrc`: pLaTeX + dvipdfmx用設定
- `AGENTS.md`: AI編集ルール

## ローカルビルド

本文は `jsarticle`、pLaTeX + BibTeX + dvipdfmx、参考文献スタイルは `yautphys.bst` を使用します。

```bash
platex main.tex
bibtex main
platex main.tex
platex main.tex
dvipdfmx main.dvi
```

または `.latexmkrc` を使って `latexmk main.tex` でビルドできます。
`main.pdf` は中間生成物としてGit管理せず、`paper-reading-notes.pdf`のみActionsが更新します。

HTML生成にはPython 3.10以上とPandocが必要です。

```bash
python3 scripts/build_html.py --output _site
python3 -m unittest discover -s tests -p test_html.py -v
```

詳細な検査方法・変換の仕様は [web/README.md](web/README.md) にあります。
HTMLの本文を二重管理せず、PDFと同じ読み込み順・文面・既存コメントを維持します。
未接続の論文、重複読み込み、未定義citation、変換不能なLaTeXはビルドエラーにし、黙って省略しません。

`build-info.json`に元コミット・収録論文・PDFハッシュを記録します。配信成功だけでなく、この情報でも最新版を確認できます。
