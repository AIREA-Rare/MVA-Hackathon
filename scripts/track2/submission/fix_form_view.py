"""Make the filled Track 2 form open on the Track 2 sheet with readable answers.
- inline strings in B7-B17 -> shared strings (widest viewer compatibility)
- workbook opens on 'Track 2 methods' (activeTab=1, tabSelected moved to sheet2)
- answer rows 7-17 get a height that fits the wrapped text (Excel maximum 409 pt)
Nothing else changes. usage: fix_form_view.py IN.xlsx OUT.xlsx"""
import html
import math
import re
import sys
import zipfile

src, dst = sys.argv[1:3]
z = zipfile.ZipFile(src)
files = {n: z.read(n) for n in z.namelist()}
ss = files["xl/sharedStrings.xml"].decode("utf-8")
items = re.findall(r"<si>.*?</si>", ss, re.S)
n0 = len(items)
s2 = files["xl/worksheets/sheet2.xml"].decode("utf-8")
cells = re.findall(r'<c r="(B\d+)" s="(\d+)" t="inlineStr"><is><t xml:space="preserve">(.*?)</t></is></c>', s2, re.S)
assert len(cells) == 11, len(cells)
new_si = []
heights = {}
for i, (ref, style, text) in enumerate(cells):
    idx = n0 + i
    new_si.append(f'<si><t xml:space="preserve">{text}</t></si>')
    s2 = s2.replace(f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>',
                    f'<c r="{ref}" s="{style}" t="s"><v>{idx}</v></c>', 1)
    plain = html.unescape(text)
    lines = sum(max(1, math.ceil(len(p) / 42)) for p in plain.split("\n"))
    heights[int(ref[1:])] = min(409, max(16, lines * 15))
# rows: set fitted height (keep the original height if it is already larger)
def fix_row(m):
    r = int(m.group(1)); attrs = m.group(2)
    if r not in heights:
        return m.group(0)
    old = re.search(r'ht="([\d.]+)"', attrs)
    h = max(heights[r], float(old.group(1)) if old else 0)
    attrs = re.sub(r'\s(ht|customHeight)="[^"]*"', "", attrs)
    return f'<row r="{r}"{attrs} ht="{h:g}" customHeight="1">'
s2 = re.sub(r'<row r="(\d+)"([^>]*)>', fix_row, s2)
s2 = s2.replace('<sheetView zoomScale', '<sheetView tabSelected="1" zoomScale', 1)
files["xl/worksheets/sheet2.xml"] = s2.encode("utf-8")
s1 = files["xl/worksheets/sheet1.xml"].decode("utf-8")
assert s1.count('tabSelected="1" ') == 1
files["xl/worksheets/sheet1.xml"] = s1.replace('tabSelected="1" ', "", 1).encode("utf-8")
total = int(re.search(r'count="(\d+)"', ss).group(1)) + len(new_si)
ss = re.sub(r'count="\d+"', f'count="{total}"', ss, count=1)
ss = re.sub(r'uniqueCount="\d+"', f'uniqueCount="{n0 + len(new_si)}"', ss, count=1)
ss = ss.replace("</sst>", "".join(new_si) + "</sst>")
files["xl/sharedStrings.xml"] = ss.encode("utf-8")
wb = files["xl/workbook.xml"].decode("utf-8")
assert "activeTab" not in wb
files["xl/workbook.xml"] = wb.replace("<workbookView ", '<workbookView activeTab="1" ', 1).encode("utf-8")
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as out:
    for info in z.infolist():
        out.writestr(info, files[info.filename])
print("fixed:", dst.rsplit("/", 1)[-1], "| shared strings added:", len(new_si), "| row heights:", heights)
