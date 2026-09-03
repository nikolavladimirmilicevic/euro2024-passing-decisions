"""
Euro 2024 - pass decision quality from StatsBomb 360.
For every open-play pass: how many opponents did the chosen pass take out,
and what was on offer?
"""
import json, math, glob, os, collections, csv

CORRIDOR = 10.0   # metres either side of the pass line
MIN_PROG = 5.0    # an option must move the ball 5m upfield
SET_PIECE = {'Corner', 'Free Kick', 'Throw-in', 'Kick Off', 'Goal Kick', 'Interception', 'Recovery'}

def bypassed(src, dst, opps):
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    L = math.hypot(dx, dy)
    if L < 1e-6 or dx <= 0:
        return 0
    n = 0
    for ox0, oy0 in opps:
        ox, oy = ox0 - src[0], oy0 - src[1]
        t = (ox*dx + oy*dy) / (L*L)
        if 0 < t < 1 and abs(ox*dy - oy*dx) / L < CORRIDOR:
            n += 1
    return n

matches = json.load(open('/home/claude/euro/matches.json'))
MINFO = {m['match_id']: m for m in matches}

rows = []
for path in sorted(glob.glob('/home/claude/euro/ev/*.json')):
    mid = int(os.path.basename(path)[:-5])
    E = json.load(open(path))
    try:
        FR = {f['event_uuid']: f['freeze_frame']
              for f in json.load(open(f'/home/claude/euro/f360/{mid}.json'))}
    except Exception:
        continue

    for ev in E:
        if ev['type']['name'] != 'Pass':
            continue
        p = ev['pass']
        if p.get('type', {}).get('name') in SET_PIECE:
            continue
        ff = FR.get(ev['id'])
        if not ff:
            continue
        src, dst = ev['location'], p['end_location'][:2]
        opps  = [q['location'] for q in ff if not q['teammate'] and not q['keeper']]
        mates = [q['location'] for q in ff if q['teammate'] and not q['actor']]
        if not opps or not mates:
            continue

        opts = [bypassed(src, m, opps) for m in mates if m[0] - src[0] >= MIN_PROG]
        rows.append((
            ev['player']['id'], ev['player']['name'], ev['team']['name'],
            bypassed(src, dst, opps),
            max(opts) if opts else 0,
            min(math.dist(src, o) for o in opps),
            dst[0] - src[0],
            'outcome' not in p,
            mid,
        ))

print(f"{len(rows):,} open-play passes with a 360 frame, {len(set(r[8] for r in rows))} matches")

# minutes played, for a per-90 view and a sample floor
mins = collections.defaultdict(float)
for path in sorted(glob.glob('/home/claude/euro/ev/*.json')):
    E = json.load(open(path))
    end = max((e['minute'] for e in E), default=90)
    for ev in E:
        if ev['type']['name'] == 'Starting XI':
            for pl in ev['tactics']['lineup']:
                mins[pl['player']['id']] += end
        elif ev['type']['name'] == 'Substitution':
            mins[ev['player']['id']] -= (end - ev['minute'])
            mins[ev['substitution']['replacement']['id']] += (end - ev['minute'])


# --- position groups, from starting line-ups ------------------------------
POSMAP = [
    ('Goalkeeper',       'Goalkeeper'),
    ('Wing Back',        'Full Back'),
    ('Back',             'Central Defender'),   # after Wing Back
    ('Defensive Midfield','Midfield'),
    ('Center Midfield',  'Midfield'),
    ('Attacking Midfield','Midfield'),
    ('Wing',             'Wide Attacker'),
    ('Midfield',         'Wide Attacker'),      # Left/Right Midfield
    ('Forward',          'Center Forward'),
]
def group(name):
    if name in ('Right Back', 'Left Back'):
        return 'Full Back'
    for key, g in POSMAP:
        if key in name:
            return g
    return 'Midfield'

posc = collections.defaultdict(collections.Counter)
for path in sorted(glob.glob('/home/claude/euro/ev/*.json')):
    for ev in json.load(open(path)):
        if ev['type']['name'] == 'Starting XI':
            for pl in ev['tactics']['lineup']:
                posc[pl['player']['id']][group(pl['position']['name'])] += 1
POS = {k: v.most_common(1)[0][0] for k, v in posc.items()}

agg = collections.defaultdict(list)
for r in rows:
    agg[(r[0], r[1], r[2])].append(r)

out = []
for (pid, name, team), rs in agg.items():
    n = len(rs)
    if n < 100:
        continue
    ch = sum(r[3] for r in rs)
    be = sum(r[4] for r in rs)
    out.append({
        'player_id': pid, 'player': name, 'team': team,
        'position': POS.get(pid, 'Unknown'),
        'passes': n,
        'minutes': round(mins.get(pid, 0)),
        'bypassed_per_pass': round(ch / n, 3),
        'available_per_pass': round(be / n, 3),
        'took_pct': round(100 * ch / be, 1) if be else 0,
        'pressure_m': round(sum(r[5] for r in rs) / n, 2),
        'progression_m': round(sum(r[6] for r in rs) / n, 2),
        'completion_pct': round(100 * sum(r[7] for r in rs) / n, 1),
    })

with open('/home/claude/euro/decisions.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader(); w.writerows(out)

print(f"{len(out)} players with 100+ passes\n")

byp = collections.defaultdict(list)
for o in out: byp[o['position']].append(o)
for g in ['Central Defender','Full Back','Midfield','Wide Attacker','Center Forward']:
    rs = sorted(byp.get(g, []), key=lambda x: -x['took_pct'])[:5]
    if not rs: continue
    print(f"--- {g} ({len(byp[g])} players) " + "-"*(46-len(g)))
    print("%-26s %-13s %5s %6s %6s %6s" % ('player','team','pass','bypass','took%','press'))
    for o in rs:
        print("%-26s %-13s %5d %6.2f %6.0f %6.1f" %
              (o['player'][:26], o['team'][:13], o['passes'],
               o['bypassed_per_pass'], o['took_pct'], o['pressure_m']))
    print()
