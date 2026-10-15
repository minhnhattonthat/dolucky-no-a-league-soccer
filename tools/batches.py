"""Translation batches: split the script into TSV batches, check translator output, merge it into script/*.json.

    python -X utf8 tools/batches.py split            # work/tl/<batch>.tsv + build/terms_<batch>.txt
    python -X utf8 tools/batches.py check <batch>    # validate work/tl/<batch>.out.tsv; prints OK or the errors
    python -X utf8 tools/batches.py merge <batch>    # check, then write `en` into script/*.json (lines centred)

Units (one TSV row each):
  credits_01.NNN  one line of the Japanese staff roll (output may be several lines joined with |)
  story_pN        one page of the intro = 4 slot lines (output exactly 4 lines joined with |, blank lines allowed)
  everything else one string; lines joined with |
Output rows: id<TAB>English, lines separated by `|`. Lines are centred by the merge, so write them without padding.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textio import EN, ROOT, load_group, save_group  # noqa: E402
from textdefs import GROUPS  # noqa: E402

TL = os.path.join(ROOT, 'work', 'tl')
BATCHES = {
    'b1': ['credits'],
    'b2': ['quotes', 'endmsg'],
    'b3': ['story', 'profiles'],
}
LIMIT = {g['id']: g['limit'] for g in GROUPS}
CENTER = {'quotes': 28, 'endmsg': 24, 'story': 24, 'credits': 28}
SPEAKER = {'quotes': 'team members (ending)', 'endmsg': 'narrator to player', 'story': 'narrator',
           'profiles': 'profile card', 'credits': 'staff roll'}


def units(gid):
    """[(unit id, form, limit, jp with ' / ' breaks, notes)]"""
    ents = load_group(gid)
    out = []
    if gid == 'credits':
        for i, ln in enumerate(ents[1]['jp'].split('\n')):
            out.append(('credits_01.%03d' % i, 'credits', LIMIT[gid], ln.strip(), ''))
        return out
    if gid == 'story':
        for p in range(9):
            lines = [ents[4 * p + k]['jp'].strip() for k in range(4)]
            out.append(('story_p%d' % p, 'narration', LIMIT[gid], ' / '.join(lines), '4 lines'))
        return out
    for e in ents:
        form = 'name' if gid == 'profiles' and int(e['id'][-2:]) < 7 else ('dlg' if gid == 'quotes' else 'narration')
        lines = [ln.strip() for ln in e['jp'].split('\n')]
        out.append((e['id'], form, LIMIT[gid], ' / '.join(lines), ''))
    return out


def split():
    os.makedirs(TL, exist_ok=True)
    gl = open(os.path.join(ROOT, 'glossary.md'), encoding='utf-8').read().splitlines()
    for b, gids in BATCHES.items():
        rows = []
        for gid in gids:
            for uid, form, lim, jp, note in units(gid):
                rows.append('\t'.join([uid, SPEAKER[gid], form, '%dch/line' % lim + (' ' + note if note else ''), jp]))
        with open(os.path.join(TL, b + '.tsv'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(rows) + '\n')
        text = '\n'.join(rows)
        terms = [ln for ln in gl if ln.startswith('|') and any(
            k and k in text for k in re.split(r'[|()/ ]+', ln.split('|')[1]) if len(k) >= 2)]
        os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
        with open(os.path.join(ROOT, 'build', 'terms_%s.txt' % b), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(terms) + '\n')
        print(b, len(rows), 'rows')


def read_out(b):
    path = os.path.join(TL, b + '.out.tsv')
    res = {}
    with open(path, encoding='utf-8-sig') as f:
        for n, ln in enumerate(f, 1):
            ln = ln.rstrip('\r\n')
            if not ln.strip():
                continue
            if '\t' not in ln:
                raise SystemExit('%s:%d: no tab' % (path, n))
            k, v = ln.split('\t', 1)
            if k in res:
                raise SystemExit('%s:%d: duplicate id %s' % (path, n, k))
            res[k] = v
    return res


def check(b, quiet=False):
    want = {}
    for gid in BATCHES[b]:
        for u in units(gid):
            want[u[0]] = u
    got = read_out(b)
    errs = []
    for k in want:
        if k not in got:
            errs.append('%s: missing' % k)
    for k in got:
        if k not in want:
            errs.append('%s: unknown id' % k)
    for k, v in got.items():
        if k not in want:
            continue
        lim = want[k][2]
        if '\t' in v or re.search(r'[^\x20-\x7e]', v):
            errs.append('%s: non-ASCII or tab' % k)
            continue
        if re.search(r'\[[0-9A-Fa-f]{2}\]', v):
            errs.append('%s: [XX] is a hex escape, rephrase' % k)
        if re.search(r'(\d)(st|nd|rd|th)\b', v) and False:
            pass
        lines = v.split('|')
        if k.startswith('story_p') and len(lines) != 4:
            errs.append('%s: story page needs exactly 4 lines (has %d)' % (k, len(lines)))
        if k.startswith('profiles_'):
            mx = 2 if int(k[-2:]) < 7 else 4
            if len(lines) > mx:
                errs.append('%s: %d lines, max %d' % (k, len(lines), mx))
        if k.startswith('quotes_') and len(lines) > 2:
            errs.append('%s: %d lines, max 2' % (k, len(lines)))
        for ln in lines:
            if len(ln.strip()) > lim:
                errs.append('%s: line %r is %d chars, limit %d' % (k, ln.strip(), len(ln.strip()), lim))
            try:
                EN.encode(ln)
            except Exception as ex:
                errs.append('%s: unencodable %r (%s)' % (k, ln, ex))
    if not quiet:
        print('\n'.join(errs) if errs else 'OK %s (%d rows)' % (b, len(got)))
    return errs, got


def center(line, width):
    s = line.strip()
    return ' ' * ((width - len(s)) // 2) + s if s else ''


def merge(b):
    errs, got = check(b, quiet=True)
    if errs:
        print('\n'.join(errs)); raise SystemExit('refusing to merge %s' % b)
    for gid in BATCHES[b]:
        ents = load_group(gid)
        w = CENTER.get(gid)
        fmt = (lambda s: '\n'.join(center(x, w) for x in s.split('|'))) if w else \
              (lambda s: '\n'.join(x.strip() for x in s.split('|')))
        if gid == 'credits':
            lines = [fmt(got[u[0]]) for u in units(gid)]
            ents[1]['en'] = '\n'.join(lines); ents[1]['status'] = 'tl'
        elif gid == 'story':
            for p in range(9):
                for k, ln in enumerate(got['story_p%d' % p].split('|')):
                    ents[4 * p + k]['en'] = center(ln, w) or ' '; ents[4 * p + k]['status'] = 'tl'
        else:
            for e in ents:
                e['en'] = fmt(got[e['id']]); e['status'] = 'tl'
        save_group(gid, ents)
    print('merged', b)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'split':
        split()
    elif cmd == 'check':
        sys.exit(1 if check(sys.argv[2])[0] else 0)
    elif cmd == 'merge':
        merge(sys.argv[2])
