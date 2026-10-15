"""Dump every text group to script/<group>.json. Never clobbers English: existing files are left alone unless
--force (then `en`, `status` and `notes` are carried over by id).

    python -X utf8 tools/extract.py [--force]
"""
import argparse, os
from textio import JP, ROOT, SCRIPT, dec, load_group, read_rom, save_group, strings_in
from textdefs import GROUPS


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    rom = read_rom()
    os.makedirs(SCRIPT, exist_ok=True)
    for g in GROUPS:
        path = os.path.join(SCRIPT, g['id'] + '.json')
        old = {}
        if os.path.exists(path):
            if not a.force:
                print('keep', path); continue
            old = {e['id']: e for e in load_group(g['id'])}
        entries = []
        for i, (off, raw) in enumerate(strings_in(rom, *g['region'])):
            jp, _ = dec(JP, rom, off)
            eid = '%s_%02d' % (g['id'], i)
            e = dict(id=eid, addr='%06X' % off, form=g['form'], max=g.get('limit'), jp=jp, en='', status='', notes='')
            if eid in old:
                for k in ('en', 'status', 'notes'):
                    e[k] = old[eid].get(k, '')
            entries.append(e)
        save_group(g['id'], entries)
        print('wrote', path, len(entries))


if __name__ == '__main__':
    main()
