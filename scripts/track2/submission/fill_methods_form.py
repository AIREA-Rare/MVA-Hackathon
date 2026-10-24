"""Fill the official Track 2 methods form (sheet2, B7-B17) from the report's Annex A and abstract.
Only the B7-B17 cell elements change; every other zip member is copied byte-for-byte.
usage: fill_methods_form.py TEMPLATE.xlsx REPORT.md OUT.xlsx"""
import html
import re
import sys
import zipfile

tpl, report, out = sys.argv[1:4]
md = open(report, encoding="utf-8").read()


def plain(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = s.replace("`", "")
    return s.strip()


annex = md.split("## Annex A.")[1].split("## Annex B.")[0]
answers = {}
for line in annex.splitlines():
    m = re.match(r"^\| (A\d+) \| [^|]+ \| (.+) \|$", line)
    if m:
        answers["B" + m.group(1)[1:]] = plain(m.group(2))
abstract = md.split("## 2. Abstract")[1].split("## 3.")[0]
abstract = "\n".join(l for l in abstract.splitlines() if not l.startswith("*("))
abstract = re.sub(r"\n{2,}", "\n\n", plain(abstract)).strip()
abstract = re.sub(r"^- ", "• ", abstract, flags=re.M)
answers["B17"] = abstract
assert sorted(answers) == sorted(f"B{i}" for i in range(7, 18)), sorted(answers)

zin = zipfile.ZipFile(tpl)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "xl/worksheets/sheet2.xml":
            x = data.decode("utf-8")
            for ref, val in answers.items():
                pat = re.compile(r'<c r="' + ref + r'"( s="\d+")?/>')
                assert len(pat.findall(x)) == 1, ref
                x = pat.sub(lambda m: f'<c r="{ref}"{m.group(1) or ""} t="inlineStr"><is><t xml:space="preserve">'
                                      f'{html.escape(val, quote=False)}</t></is></c>', x)
            data = x.encode("utf-8")
        zout.writestr(item, data)
words = len(re.findall(r"\S+", re.sub(r"^• ", "", answers["B17"], flags=re.M)))
print("filled:", ", ".join(sorted(answers, key=lambda k: int(k[1:]))), "| B17 words:", words)
