# HTML版ノート

LaTeX/BibTeXを正本のまま、PDFと同じ内容のHTML版を自動生成します。

- 各論文カードと参考文献欄で、BibTeX全文・citation key・`\cite{...}`をコピーできます。
- タイトル、著者、arXiv番号、本文で検索でき、テーマ別の絞り込みもできます。
- 本文中の引用番号は同じページの参考文献欄に移動します。
- 数式はMathJax 3.2.2で表示します。CDN読み込みに失敗してもコピー・検索は使えます。
- ブラウザがクリップボードを許可しない場合は、選択コピーできるテキスト欄を開きます。
- トップページはHTML版です。上部のPDFボタンは内容ハッシュ付きファイルを開き、安定URL `paper-reading-notes.pdf` も維持します。

## 正本と検査

`main.tex` → `sections/*.tex` → `papers/*.tex` を実際にたどり、同じ順序・文面・既存コメントを使います。HTMLのための本文を二重管理しません。
BibTeXは `main.tex` の `\bibliography{...}` に列挙された全ファイルから取得します。`references-extra.bib`も対象です。
クリップボードに入れるentryは元の文字列を保持し、表示用の変換を適用しません。

未接続の論文、重複読み込み、未定義citation、対応するBibTeXが不明なカード、未変換LaTeXはエラーにします。黙って省略しません。
現在の固定形式を変える場合は、変換器とテストも更新してください。

```bash
# Python 3.10+ と Pandoc が必要
python3 scripts/build_html.py --output _site
python3 -m unittest discover -s tests -p test_html.py -v

# 任意のブラウザ検査
python3 -m pip install playwright==1.57.0
python3 -m playwright install chromium
python3 tests/browser_html.py --require-math
```

`Build PDF`が同一コミットからPDFとHTMLを生成し、`paper-reading-notes-site` artifactにまとめます。Pagesはそのrunのartifactを配信します。
`build-info.json`には元コミット、収録論文一覧、PDFハッシュを記録します。配信時に内容の取り違えと古いソースからの配信を検査します。
`.github/workflows/html-preview.yml`でコード変更時とPages配信後に、実際のブラウザでコピー・検索・内部リンク・数式・スマホ幅をテストします。

`noindex`は検索エンジンへの指示であり、アクセス制限ではありません。公開リポジトリと配信データは誰でも閲覧できます。
