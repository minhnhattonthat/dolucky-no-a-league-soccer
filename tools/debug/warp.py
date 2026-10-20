"""Run a debug-tool scene (tools/debug/scenes.py) from a cold boot and make its contact sheet.

    python -X utf8 tools/debug/warp.py SCENE|all [--rom ROM] [--out DIR] [--log] [--jobs 3]
--log adds tools/lua/printlog.lua (every printed string in log.txt).
"""
import argparse, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [HERE, os.path.join(ROOT, 'tools')]
from scenes import SCENES  # noqa: E402
from textio import SKILL  # noqa: E402

EMU = os.path.join(SKILL, 'emu.py')


def run(scene, rom, out, log):
    vars_, frames, every, route, mash = SCENES[scene]
    cmd = [sys.executable, '-X', 'utf8', EMU, rom, '--out', out, '--frames', str(frames), '--shot-every', str(every),
           '--timeout', '400', '--script', os.path.join(HERE, 'warp.lua'), '--sheet']
    for k, v in vars_.items():
        cmd += ['--var', '%s=%s' % (k, v)]
    if route:
        cmd += ['--route-str', route]
    if mash:
        cmd += ['--mash', str(mash)]
    if log:
        cmd += ['--script', os.path.join(ROOT, 'tools', 'lua', 'printlog.lua')]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return scene, r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scene'); ap.add_argument('--rom', default=os.path.join(ROOT, 'build', 'dolucky_en.sfc'))
    ap.add_argument('--out'); ap.add_argument('--log', action='store_true'); ap.add_argument('--jobs', type=int, default=3)
    a = ap.parse_args()
    names = list(SCENES) if a.scene == 'all' else [a.scene]
    tag = os.path.splitext(os.path.basename(a.rom))[0]
    with ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(run, s, a.rom, a.out or os.path.join(ROOT, 'work', 'qa', '%s_%s' % (tag, s)), a.log)
                for s in names]
        bad = 0
        for f in futs:
            s, rc, last = f.result()
            print(s, rc, *last)
            bad += rc != 0
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
