"""Release gate + package: check -> build -> smoke -> leftover-Japanese scan -> checksum -> BPS (re-applied and
verified) -> release/dolucky-no-a-league-soccer_en.zip (patch + README only). Never publishes anything.

    python -X utf8 tools/release.py [--no-tour]
--no-tour skips the warp screen tour (tools/debug/warp.py all), which the gate runs by default.
"""
import hashlib, os, shutil, subprocess, sys, zipfile, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from textio import SKILL  # noqa: E402
PY = [sys.executable, '-X', 'utf8']
SLUG = 'dolucky-no-a-league-soccer'
VERSION = '1.0'
# jp_left hits in the text ranges that are code / pointer tables, not text (checked by hand, docs/re/text.md)
KNOWN = {0x012331, 0x012364, 0x01249F, 0x02DE9B, 0x02EE15, 0x02F2A4, 0x0DE123, 0x0DE9D4, 0x0DE9F3, 0x0DEA12,
         0x0DF975}
RANGES = ['12000-12600', '2DE00-30000', 'DE000-E0000', '7E000-80000', '180000-188000', '17C00-18000']


def run(cmd, **kw):
    print('>', ' '.join(os.path.basename(c) if os.sep in c else c for c in cmd[2:6]))
    r = subprocess.run(cmd, cwd=ROOT, **kw)
    if r.returncode:
        raise SystemExit('release gate failed: %s' % ' '.join(cmd))
    return r


def hashes(data):
    return '%08X' % zlib.crc32(data), hashlib.md5(data).hexdigest(), hashlib.sha1(data).hexdigest()


def main():
    tour = '--no-tour' not in sys.argv
    run(PY + [os.path.join(ROOT, 'tools', 'check.py')])
    run(PY + [os.path.join(ROOT, 'build.py')])
    built = os.path.join(ROOT, 'build', 'dolucky_en.sfc')
    run(PY + [os.path.join(SKILL, 'emu.py'), built, '--out', os.path.join(ROOT, 'work', 'qa', 'smoke'),
              '--route', os.path.join(ROOT, 'tools', 'routes', 'boot.txt'), '--smoke'])
    r = subprocess.run(PY + [os.path.join(SKILL, 'jp_left.py'), built, '--tbl', os.path.join(ROOT, 'tbl', 'jp.tbl'),
                             '--min', '6'] + sum((['--range', x] for x in RANGES), []),
                       cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    hits = [int(ln.split()[0], 16) for ln in r.stdout.splitlines() if ln.startswith('0x')]
    new = [h for h in hits if h not in KNOWN]
    if new:
        raise SystemExit('unexpected Japanese runs: %s' % ', '.join('%06X' % h for h in new))
    if tour:
        run(PY + [os.path.join(ROOT, 'tools', 'debug', 'warp.py'), 'all', '--rom', built, '--jobs', '4'])
    orig_path = os.path.join(ROOT, 'rom', 'Dolucky no A.League Soccer (Japan).sfc')
    final = os.path.join(ROOT, 'build', 'dolucky_en_release.sfc')
    run(PY + [os.path.join(SKILL, 'bps.py'), 'snes-checksum', built, '--out', final])
    rel = os.path.join(ROOT, 'release'); os.makedirs(rel, exist_ok=True)
    patch = os.path.join(rel, 'Dolucky_no_A.League_Soccer_EN_v%s.bps' % VERSION)
    run(PY + [os.path.join(SKILL, 'bps.py'), 'make', orig_path, final, patch])
    check = os.path.join(ROOT, 'build', 'reapplied.sfc')
    run(PY + [os.path.join(SKILL, 'bps.py'), 'apply', orig_path, patch, check])
    orig, out, chk = (open(p, 'rb').read() for p in (orig_path, final, check))
    assert out == chk, 'patch does not reproduce the build'
    o, p = hashes(orig), hashes(out)
    readme = open(os.path.join(ROOT, 'docs', 'release-readme.txt'), encoding='utf-8').read().format(
        version=VERSION, crc=o[0], md5=o[1], sha1=o[2], pcrc=p[0], psha1=p[2], size=len(orig))
    rd = os.path.join(rel, 'README.txt')
    with open(rd, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(readme)
    z = os.path.join(rel, '%s_en.zip' % SLUG)
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(patch, os.path.basename(patch)); zf.write(rd, 'README.txt')
    print('release:', z)
    print('patch sha1', hashlib.sha1(open(patch, 'rb').read()).hexdigest(), 'patched ROM crc32', p[0])


if __name__ == '__main__':
    main()
