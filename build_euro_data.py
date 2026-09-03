"""Euro 2024 decision quality -> site data (profiles + selected pass frames)."""
import json, math, glob, os, collections

CORRIDOR = 10.0
MIN_PROG = 5.0
SET_PIECE = {'Corner', 'Free Kick', 'Throw-in', 'Kick Off', 'Goal Kick'}
MIN_PASSES = 60
MIN_AVAIL = 2.0     # took% is unstable when almost nothing was on offer
MIN_BYPASS = 4      # a pass worth showing takes out at least this many
MIN_GAP = 3         # a miss worth showing left at least this many on the table
MAX_BEST, MAX_MISS = 4, 3

def bypass_list(src, dst, opps):
    """Indices of opponents taken out by a pass from src to dst."""
    dx, dy = dst[0]-src[0], dst[1]-src[1]
    L = math.hypot(dx, dy)
    if L < 1e-6 or dx <= 0:
        return []
    out = []
    for i, (ox0, oy0) in enumerate(opps):
        ox, oy = ox0-src[0], oy0-src[1]
        t = (ox*dx + oy*dy)/(L*L)
        if 0 < t < 1 and abs(ox*dy - oy*dx)/L < CORRIDOR:
            out.append(i)
    return out

def group(name):
    if name in ('Right Back', 'Left Back'): return 'Full Back'
    if 'Goalkeeper' in name: return 'Goalkeeper'
    if 'Wing Back' in name: return 'Full Back'
    if 'Back' in name: return 'Central Defender'
    if 'Wing' in name or name in ('Left Midfield', 'Right Midfield'): return 'Wide Attacker'
    if 'Forward' in name: return 'Center Forward'
    return 'Midfield'

matches = json.load(open('/home/claude/euro/matches.json'))
MI = {m['match_id']: m for m in matches}

posc = collections.defaultdict(collections.Counter)
mins = collections.defaultdict(float)
passes = collections.defaultdict(list)      # player -> list of pass records
frames = collections.defaultdict(list)      # player -> list of full frames

for path in sorted(glob.glob('/home/claude/euro/ev/*.json')):
    mid = int(os.path.basename(path)[:-5])
    E = json.load(open(path))
    try:
        FR = {f['event_uuid']: f['freeze_frame']
              for f in json.load(open(f'/home/claude/euro/f360/{mid}.json'))}
    except Exception:
        continue
    end = max((e['minute'] for e in E), default=90)
    m = MI[mid]
    home, away = m['home_team']['home_team_name'], m['away_team']['away_team_name']

    for ev in E:
        t = ev['type']['name']
        if t == 'Starting XI':
            for pl in ev['tactics']['lineup']:
                posc[pl['player']['id']][group(pl['position']['name'])] += 1
                mins[pl['player']['id']] += end
        elif t == 'Substitution':
            mins[ev['player']['id']] -= (end - ev['minute'])
            mins[ev['substitution']['replacement']['id']] += (end - ev['minute'])
        elif t == 'Pass':
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

            chosen = bypass_list(src, dst, opps)
            best_n, best_t = 0, None
            for mm in mates:
                if mm[0] - src[0] < MIN_PROG:
                    continue
                b = len(bypass_list(src, mm, opps))
                if b > best_n:
                    best_n, best_t = b, mm

            pid = ev['player']['id']
            passes[pid].append((len(chosen), best_n,
                                min(math.dist(src, o) for o in opps),
                                dst[0]-src[0], 'outcome' not in p))
            frames[pid].append({
                'n': len(chosen), 'a': best_n,
                's': [round(v,1) for v in src], 'e': [round(v,1) for v in dst],
                'o': [[round(v,1) for v in q] for q in opps],
                'm': [[round(v,1) for v in q] for q in mates],
                'k': chosen,
                'b': [round(v,1) for v in best_t] if best_t else None,
                'v': f"{ev['minute']}' v {away if ev['team']['name']==home else home}",
                'c': 'outcome' not in p,
            })

POS = {k: v.most_common(1)[0][0] for k, v in posc.items()}

# official short names from the line-up files, with a fallback rule
NICK = {}
for path in glob.glob('/home/claude/euro/lu/*.json'):
    for t in json.load(open(path)):
        for pl in t['lineup']:
            NICK[pl['player_id']] = pl.get('player_nickname') or None

PARTICLE = {'van','von','de','del','della','di','da','dos','das','du','le','la',
            'el','al','ben','bin','mac','mc',"o'",'ter','ten','op'}
def short(full):
    parts = full.split()
    if len(parts) <= 2:
        return full
    for i in range(1, len(parts)):
        if parts[i].lower() in PARTICLE:
            return parts[0] + ' ' + ' '.join(parts[i:i+2])
        return parts[0] + ' ' + parts[i]
    return full
NAME, TEAM = {}, {}
for path in sorted(glob.glob('/home/claude/euro/ev/*.json'))[:1]:
    pass
for path in sorted(glob.glob('/home/claude/euro/ev/*.json')):
    for ev in json.load(open(path)):
        if ev.get('player'):
            NAME[ev['player']['id']] = ev['player']['name']
            TEAM.setdefault(ev['player']['id'], ev['team']['name'])

players = []
for pid, rs in passes.items():
    if len(rs) < MIN_PASSES or POS.get(pid) in (None, 'Goalkeeper'):
        continue
    n = len(rs)
    ch = sum(r[0] for r in rs); be = sum(r[1] for r in rs)
    fs = frames[pid]
    best = [f for f in fs if f['n'] >= MIN_BYPASS]
    best = sorted(best, key=lambda f: (-f['n'], -f['a']))[:MAX_BEST]
    miss = [f for f in fs if f['b'] and (f['a'] - f['n']) >= MIN_GAP]
    miss = sorted(miss, key=lambda f: -(f['a'] - f['n']))[:MAX_MISS]
    seen, sel = set(), []
    for f in best + miss:
        k = (f['v'], tuple(f['s']))
        if k not in seen:
            seen.add(k); sel.append(f)
    if len(sel) < 2:   # nothing notable: show his two most incisive anyway
        sel = sorted(fs, key=lambda f: -f['n'])[:2]
    players.append({
        'id': pid,
        'name': NICK.get(pid) or short(NAME.get(pid, str(pid))),
        'full': NAME.get(pid, str(pid)),
        'team': TEAM.get(pid, ''),
        'pos': POS[pid], 'passes': n, 'min': round(mins.get(pid, 0)),
        'byp': round(ch/n, 3), 'avail': round(be/n, 3),
        'took': round(100*ch/be, 1) if be else 0,
        'press': round(sum(r[2] for r in rs)/n, 2),
        'prog': round(sum(r[3] for r in rs)/n, 2),
        'comp': round(100*sum(r[4] for r in rs)/n, 1),
        'frames': sel,
    })

dropped = [p['name'] for p in players if p['avail'] < MIN_AVAIL]
players = [p for p in players if p['avail'] >= MIN_AVAIL]
if dropped:
    print("dropped for too few options offered:", ", ".join(dropped))

# percentile within position group (after filtering)
KEYS = ['byp', 'avail', 'took', 'press', 'prog', 'comp']
for g in set(p['pos'] for p in players):
    grp = [p for p in players if p['pos'] == g]
    for k in KEYS:
        vals = sorted(p[k] for p in grp)
        for p in grp:
            p.setdefault('pct', {})[k] = round(
                100*sum(1 for v in vals if v < p[k])/max(len(vals)-1, 1), 1)

players.sort(key=lambda p: p['name'])
out = {'meta': {'competition': 'UEFA Euro 2024', 'source': 'StatsBomb Open Data (360)',
                'matches': 51, 'passes_analysed': sum(len(v) for v in passes.values()),
                'min_passes': MIN_PASSES, 'corridor_m': CORRIDOR},
       'players': players}
json.dump(out, open('/home/claude/euro_site.json', 'w'), ensure_ascii=False,
          separators=(',', ':'))

print(f"{len(players)} players, {out['meta']['passes_analysed']:,} passes analysed")
print("by position:", collections.Counter(p['pos'] for p in players).most_common())
print("frames per player:", sorted(collections.Counter(len(p['frames']) for p in players).items()))
print("frames with 0 bypassed:", sum(1 for p in players for f in p['frames'] if f['n'] == 0))
print("size: %.1f MB" % (os.path.getsize('/home/claude/euro_site.json')/1e6))
