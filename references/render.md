# スライドを画像にして確かめる

`scripts/render_pages.py` を使う。PPTX（または PDF）を、ページごとの PNG と、全ページを並べた一覧画像にする。

## 必要なもの

- Python 3 と Pillow（`pip install pillow`）
- LibreOffice（PPTX を PDF にするのに使う。PDF を渡すときは不要）
  - macOS：`brew install --cask libreoffice`
  - Linux：`sudo apt install libreoffice`
- pdftoppm（Poppler に入っている）
  - macOS：`brew install poppler`
  - Linux：`sudo apt install poppler-utils`

## 使い方

```bash
python3 scripts/render_pages.py 資料.pptx --out 作業フォルダ
```

作業フォルダにできるもの：

- `資料.pdf`：PPTX を変換した PDF（PDF を渡したときは作らない）
- `pages/page-01.png` …：各ページの画像（幅1600px）
- `overview.png`：全ページを並べた一覧画像（各ページの左上にページ番号）

オプション：

- `--width 1600`：各ページの画像の幅
- `--cols 4`：一覧画像の列の数

## 見方

1. まず `overview.png` で、資料全体の流れと強弱を見る（同じ構図が続いていないか、山場があるか、色の意味がそろっているか）。
2. 気になるページは `pages/` の画像を原寸で開いて、文字切れ・重なり・小さすぎる文字を見る。
3. 直したら、もう一度スクリプトを動かして見直す。

## 画像にできないとき

LibreOffice や pdftoppm が入っておらず、入れることもできない環境では、画像チェックを飛ばさずに **「画像チェック未実施」** と報告する。PowerPoint や Keynote から PDF に書き出してもらえれば、PDF を渡して画像にできる。

## 注意

- LibreOffice での変換は、PowerPoint と表示が少しずれることがある（フォントの置き換えなど）。文字のはみ出しが見えたら、使われているフォントが入っているか確かめ、利用者の環境での表示も確認してもらう。
