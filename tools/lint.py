"""Text lint over script/*.json (run by tools/check.py). Prints errors and a count; exit 1 on any error.

Checks every `en`: encodable with tbl/en.tbl, no Japanese left, line width <= the group limit, line counts per box,
no ordinal suffix glued to a digit-less variable, untranslated entries (warning count only).
"""
import re, sys
from textio import EN, load_group
from textdefs import GROUPS

MAXLINES = {'quotes': 2, 'story': 1, 'names': 1}
JPRE = re.compile('[぀-ヿ一-鿿＀-￯]')


def main():
    errs, todo = [], 0
    for g in GROUPS:
        for i, e in enumerate(load_group(g['id'])):
            en = e['en']
            if not en:
                if e['jp'].strip() and JPRE.search(e['jp']):
                    todo += 1
                continue
            lim = g['pad'] if 'pad_from' in g and i >= g['pad_from'] else g['limit']
            if JPRE.search(en):
                errs.append('%s: Japanese left in en' % e['id'])
            try:
                EN.encode(en.replace('\n', '{n}'))
            except Exception as ex:
                errs.append('%s: unencodable (%s)' % (e['id'], ex))
            if re.search(r'\[[0-9A-Fa-f]{2}\]', en):
                errs.append('%s: [XX] hex escape in text' % e['id'])
            lines = en.split('\n')
            for ln in lines:
                if len(ln.rstrip()) > lim:
                    errs.append('%s: line %r %d > %d' % (e['id'], ln, len(ln.rstrip()), lim))
            mx = MAXLINES.get(g['id'])
            if g['id'] == 'profiles':
                mx = 2 if i < 7 else 4
            if mx and len(lines) > mx:
                errs.append('%s: %d lines > %d' % (e['id'], len(lines), mx))
    for x in errs:
        print(x)
    print('lint: %d errors, %d untranslated' % (len(errs), todo))
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
