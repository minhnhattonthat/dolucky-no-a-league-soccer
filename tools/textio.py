"""Shared text helpers: table codecs, script JSON load/save, string listing of a group region."""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# translate-retro-game scripts: $SKILL (the dir holding SKILL.md), else the newest installed plugin copy
SKILL = os.path.join(os.environ['SKILL'], 'scripts') if os.environ.get('SKILL') else max(
    glob.glob(os.path.expanduser('~/.claude/plugins/cache/retro-translation/translate-retro-game/*/skills/'
                                 'translate-retro-game/scripts')), key=os.path.getmtime)
sys.path.insert(0, SKILL)
from tbl import Table  # noqa: E402

ROM = os.path.join(ROOT, 'rom', 'Dolucky no A.League Soccer (Japan).sfc')
SCRIPT = os.path.join(ROOT, 'script')
JP = Table.load(os.path.join(ROOT, 'tbl', 'jp.tbl'))
EN = Table.load(os.path.join(ROOT, 'tbl', 'en.tbl'))


def dec(table, data, pos):
    text, used = table.decode(data, pos)
    return text[:-len('{end}')].replace('{n}', '\n'), used


def enc(table, text):
    return table.encode(text.replace('\n', '{n}')) + b'\x00'


def strings_in(data, start, end):
    """(offset, raw bytes incl. 00) of every 00-terminated string in [start, end)."""
    out, p = [], start
    while p < end:
        e = data.index(b'\x00', p) + 1
        if e > end:
            raise ValueError('string at %X runs past region end %X' % (p, end))
        out.append((p, data[p:e]))
        p = e
    return out


def load_group(gid):
    with open(os.path.join(SCRIPT, gid + '.json'), encoding='utf-8') as f:
        return json.load(f)


def save_group(gid, entries):
    with open(os.path.join(SCRIPT, gid + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
        f.write('\n')


def read_rom():
    with open(ROM, 'rb') as f:
        return f.read()
