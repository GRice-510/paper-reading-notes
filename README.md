# Paper Reading Notes

ChatGPT / Codex との論文読解を蓄積し、最終的に1冊のPDFとして参照できる形にまとめるための研究ノートです。

## 最新版PDF

**[paper-reading-notes.pdf](./paper-reading-notes.pdf)**

`main` ブランチの LaTeX / BibTeX が更新されると、GitHub Actions が自動でPDFを再生成し、このファイルを最新版へ更新します。

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

## 短い指示での運用

論文が現在の会話から一意に特定できる場合、毎回長いプロンプトを書く必要はありません。

- 「概要を追加して」「ノートに反映して」「これを反映して」 → リポジトリを更新。PDFは GitHub Actions が自動更新する。
- 「概要をPDFに追加して」「PDFにも反映して」「PDFに追加して」 → 同じくリポジトリを更新し、GitHub Actions によるPDF更新までを前提とする。

これらの指示を受けたAIは、明示されていなくても編集前に `AGENTS.md` と `papers/_template.tex` を確認します。

また、論文を追加・更新したときは、実際に保存した Authors / 主な主張 / 新規性 / 位置付けをチャットにも表示します。
単に「更新しました」だけでは終えません。

## 構成

- `papers/`: 1論文1ファイル
- `sections/`: テーマ別に各論文を `\input`
- `references.bib`: 参考文献
- `main.tex`: 全体を1つのPDFへまとめる
- `paper-reading-notes.pdf`: GitHub Actions が更新する閲覧用最新版PDF
- `.github/workflows/build-pdf.yml`: PDF自動ビルド
- `.latexmkrc`: pLaTeX + dvipdfmx 用の latexmk 設定
- `AGENTS.md`: AI編集時の最優先ルール

## 通常運用

GitHub 上の LaTeX ソースを正本とします。
論文追加・修正時はリポジトリのソースを更新すれば、PDFは GitHub Actions により自動更新されます。
レイアウト変更時など、目視確認が必要な場合のみ手元でPDFを再生成して確認します。

## LaTeX

本文は `jsarticle`、pLaTeX + dvipdfmx を使用します。
共通設定・数式マクロは `macro_jsarticle.tex` から読み込み、bibliography style は `yautphys.bst` を使用します。

手元では次の従来手順でもビルドできます。

```bash
platex main.tex
bibtex main
platex main.tex
platex main.tex
dvipdfmx main.dvi
```

または `.latexmkrc` を使って、

```bash
latexmk main.tex
```

でもビルドできます。

`main.pdf` は中間的なローカル生成物としてGit管理せず、公開用の `paper-reading-notes.pdf` のみ GitHub Actions が更新します。
