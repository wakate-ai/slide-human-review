#!/usr/bin/env python3
"""スライド（PPTX / PDF）を、ページごとの PNG と全ページの一覧画像にする。

使い方:
  python3 render_pages.py 資料.pptx --out 作業フォルダ [--width 1600] [--cols 4]

必要なもの: Python 3 + Pillow, pdftoppm（Poppler）, PPTX のときは LibreOffice（soffice）
"""
import argparse
import glob
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont


def find_soffice():
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    mac = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    return mac if os.path.exists(mac) else None


def to_pdf(src, out_dir):
    """PPTX などを PDF に変換して、そのパスを返す。PDF ならそのまま返す。"""
    if src.lower().endswith(".pdf"):
        return src
    soffice = find_soffice()
    if not soffice:
        sys.exit("LibreOffice（soffice）が見つかりません。入れるか、PDF に書き出したものを渡してください。")
    # 起動中の LibreOffice とぶつからないよう、使い捨てのプロファイルで動かす
    with tempfile.TemporaryDirectory() as profile:
        cmd = [soffice, f"-env:UserInstallation=file://{profile}", "--headless",
               "--convert-to", "pdf", "--outdir", out_dir, src]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(src))[0] + ".pdf")
    if r.returncode != 0 or not os.path.exists(pdf):
        sys.exit(f"PDF への変換に失敗しました。\n{r.stdout}\n{r.stderr}")
    return pdf


def to_pngs(pdf, pages_dir, width):
    if not shutil.which("pdftoppm"):
        sys.exit("pdftoppm が見つかりません。Poppler を入れてください。")
    os.makedirs(pages_dir, exist_ok=True)
    for old in glob.glob(os.path.join(pages_dir, "page-*.png")):
        os.remove(old)
    r = subprocess.run(["pdftoppm", "-png", "-scale-to-x", str(width), "-scale-to-y", "-1",
                        pdf, os.path.join(pages_dir, "page")], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"画像への変換に失敗しました。\n{r.stderr}")
    files = sorted(glob.glob(os.path.join(pages_dir, "page-*.png")),
                   key=lambda p: int(os.path.basename(p).split("-")[-1].split(".")[0]))
    # page-1.png / page-01.png の桁をそろえる
    digits = max(2, len(str(len(files))))
    renamed = []
    for i, f in enumerate(files, 1):
        dst = os.path.join(pages_dir, f"page-{i:0{digits}d}.png")
        if f != dst:
            os.replace(f, dst)
        renamed.append(dst)
    return renamed


def label_font(size):
    for path in ("/System/Library/Fonts/Helvetica.ttc",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    return ImageFont.load_default()


def overview(pngs, out_path, cols, thumb_w=480, gap=16):
    thumbs = []
    for p in pngs:
        im = Image.open(p).convert("RGB")
        h = round(im.height * thumb_w / im.width)
        thumbs.append(im.resize((thumb_w, h), Image.LANCZOS))
    cols = max(1, min(cols, len(thumbs)))
    rows = math.ceil(len(thumbs) / cols)
    label_h = 30  # ページ番号はスライドに重ねず、上の帯に書く
    cell_h = max(t.height for t in thumbs) + label_h
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), (200, 200, 200))
    d = ImageDraw.Draw(sheet)
    f = label_font(20)
    for i, t in enumerate(thumbs):
        x = gap + (i % cols) * (thumb_w + gap)
        y = gap + (i // cols) * (cell_h + gap)
        d.text((x + 2, y + 3), str(i + 1), font=f, fill=(30, 30, 30))
        sheet.paste(t, (x, y + label_h))
    sheet.save(out_path)


def main():
    ap = argparse.ArgumentParser(description="スライドをページ画像と一覧画像にする")
    ap.add_argument("src", help="PPTX / PDF などのファイル")
    ap.add_argument("--out", default="render_out", help="出力フォルダ")
    ap.add_argument("--width", type=int, default=1600, help="各ページの画像の幅（px）")
    ap.add_argument("--cols", type=int, default=4, help="一覧画像の列の数")
    a = ap.parse_args()

    src = os.path.abspath(a.src)
    if not os.path.exists(src):
        sys.exit(f"ファイルが見つかりません: {src}")
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    pdf = to_pdf(src, out)
    pngs = to_pngs(pdf, os.path.join(out, "pages"), a.width)
    if not pngs:
        sys.exit("ページが1枚も画像になりませんでした。")
    ov = os.path.join(out, "overview.png")
    overview(pngs, ov, a.cols)
    print(f"ページ数: {len(pngs)}")
    print(f"各ページ: {os.path.join(out, 'pages')}")
    print(f"一覧画像: {ov}")


if __name__ == "__main__":
    main()
