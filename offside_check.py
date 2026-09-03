import json, math, glob, os

CORRIDOR, MIN_PROG = 10.0, 5.0
SET_PIECE = {'Corner', 'Free Kick', 'Throw-in', 'Kick Off', 'Goal Kick'}

def nbypass(src, dst, opps):
    dx, dy = dst[0]-src[0], dst[1]-src[1]
    L = math.hypot(dx, dy)
    if L < 1e-6 or dx <= 0: return 0
    return sum(1 for ox0, oy0 in opps
               if 0 < ((ox0-src[0])*dx + (oy0-src[1])*dy)/(L*L) < 1
               and abs((ox0-src[0])*dy - (oy0-src[1])*dx)/L < CORRIDOR)

def offside(m, src, all_opp):
    """A team-mate is in an offside position if he is in the opponent half,
    ahead of the ball, and ahead of the second-last opponent."""
    if m[0] <= 60 or m[0] <= src[0]:
        return False
    return sum(1 for o in all_opp if o[0] >= m[0]) < 2

tot = off = 0
d_old = d_new = 0.0
n = 0
for path in sorted(glob.glob('/home/claude/euro/ev/*.json')):
    mid = int(os.path.basename(path)[:-5])
    try:
        FR = {f['event_uuid']: f['freeze_frame']
              for f in json.load(open(f'/home/claude/euro/f360/{mid}.json'))}
    except Exception:
        continue
    for ev in json.load(open(path)):
        if ev['type']['name'] != 'Pass': continue
        p = ev['pass']
        if p.get('type', {}).get('name') in SET_PIECE: continue
        ff = FR.get(ev['id'])
        if not ff: continue
        src = ev['location']
        opps    = [q['location'] for q in ff if not q['teammate'] and not q['keeper']]
        all_opp = [q['location'] for q in ff if not q['teammate']]
        mates   = [q['location'] for q in ff if q['teammate'] and not q['actor']]
        if not opps or not mates: continue

        cands = [m for m in mates if m[0] - src[0] >= MIN_PROG]
        if not cands: continue
        old = max((nbypass(src, m, opps) for m in cands), default=0)
        legal = [m for m in cands if not offside(m, src, all_opp)]
        new = max((nbypass(src, m, opps) for m in legal), default=0)

        # was the old best an offside player?
        best_m = max(cands, key=lambda m: nbypass(src, m, opps))
        tot += 1
        if offside(best_m, src, all_opp): off += 1
        d_old += old; d_new += new; n += 1

print(f"passes with at least one forward option: {tot:,}")
print(f"best option was offside: {off:,}  ({100*off/tot:.1f}%)\n")
print(f"average best option offered  before: {d_old/n:.3f}")
print(f"                              after: {d_new/n:.3f}")
print(f"                             change: {100*(d_new-d_old)/d_old:+.1f}%")
