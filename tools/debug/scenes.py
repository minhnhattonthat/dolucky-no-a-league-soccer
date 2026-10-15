"""Debug tool scene list + runner: boot cold and land on any scene with tools/debug/warp.lua.

    python -X utf8 tools/debug/warp.py SCENE [--rom build/dolucky_en.sfc] [--out work/qa/warp_SCENE] [--extra ...]
    python -X utf8 tools/debug/warp.py all            # every scene, one sheet each (regenerates work/qa/warp_*)

Each scene: (lua vars, frames, shot cadence, route string or None, mash every N frames or 0).
"""
SCENES = {
    'title':          (dict(), 800, 60, None, 0),
    'story':          (dict(SCENE="'story'"), 7300, 60, None, 0),
    'profiles':       (dict(SCENE="'profiles'"), 9000, 60, None, 0),
    'attract6':       (dict(SCENE="'attract6'"), 4000, 60, None, 0),
    'options':        (dict(SCENE="'options'"), 1400, 30, None, 0),
    'bonus':          (dict(SCENE="'bonus'"), 1400, 30, None, 0),
    'debug':          (dict(SCENE="'debug'"), 1400, 30, None, 0),
    'match':          (dict(), 3000, 60, '750 -;6 start;200 -;6 a;400 -', 90),
    'ending_easy':    (dict(SCENE="'ending_easy'"), 2600, 30, None, 0),
    'ending_normal':  (dict(SCENE="'ending_normal'"), 9000, 60, None, 0),
    'ending_true':    (dict(SCENE="'ending_true'"), 9000, 60, None, 0),
}
del SCENES['profiles']
for p in range(7):  # 0-3 player teams, 4 Jet Mole Dangerous, 5 referee Curtis, 6 Edward Yamada
    SCENES['profile%d' % p] = (dict(SCENE="'profiles'", PROFILE=str(p)), 3700, 30, None, 0)
for t in range(4):
    SCENES['quotes_team%d' % t] = (dict(SCENE="'ending_easy'", TEAM=str(t)), 2000, 20, None, 0)
