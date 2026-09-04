import json

DATA = json.dumps(json.load(open('/home/claude/euro_site.json')),
                  ensure_ascii=False, separators=(',', ':'))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Euro 2024 passing decisions</title>
<meta name="description" content="Who picked the incisive pass at Euro 2024. Built from StatsBomb 360 freeze frames: for every open-play pass, how many opponents it took out and what was on offer instead." />
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ctext y=%22.9em%22 font-size=%2290%22%3E%E2%9A%BD%3C/text%3E%3C/svg%3E" />
<meta property="og:title" content="Euro 2024 passing decisions" />
<meta property="og:description" content="For every open-play pass at Euro 2024: how many opponents it took out, and what the player could have played instead." />
<meta property="og:type" content="website" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --pitch:#0F1A15; --pitch-2:#16241D; --line:#2A3A32;
  --chalk:#E9EFE8; --chalk-dim:#8FA096; --chalk-faint:#6B7C72;
  --signal:#E0A33E;      /* the player and his pass */
  --alt:#5FB6C4;         /* the option he did not take */
  --opp:#D2685C;         /* opponents */
  --grass:#12201A;
}
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--pitch);color:var(--chalk);font-family:Barlow,system-ui,sans-serif;
     font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:"Barlow Condensed",Barlow,system-ui,sans-serif;font-weight:600}
a{color:var(--alt)}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 64px}
header{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}
h1{font-size:34px;margin:0 0 4px;line-height:1.05}
.sub{color:var(--chalk-dim);max-width:64ch;margin:0}
.sub b{color:var(--chalk);font-weight:600}
.cols{display:grid;grid-template-columns:250px 1fr;gap:24px;align-items:stretch}
@media(max-width:880px){
  .cols{grid-template-columns:1fr}
  .rail{position:static;min-height:0}
  .panel{position:static}
}
.rail{position:relative;min-height:460px}
.panel{position:absolute;inset:0;background:var(--pitch-2);border:1px solid var(--line);
  border-radius:4px;display:flex;flex-direction:column;min-height:0}
.controls{padding:12px}
input[type=search],select{width:100%;background:var(--pitch);color:var(--chalk);
  border:1px solid var(--line);border-radius:3px;padding:8px 10px;font-family:inherit;
  font-size:14px;margin-bottom:8px}
input:focus-visible,select:focus-visible,button:focus-visible,li:focus-visible{
  outline:2px solid var(--signal);outline-offset:2px}
ul.list{list-style:none;margin:0;padding:0;flex:1 1 auto;min-height:0;overflow-y:auto}
@media(max-width:880px){ul.list{flex:none;max-height:260px}}
ul.list li{padding:7px 12px;cursor:pointer;border-top:1px solid var(--line);
  display:flex;justify-content:space-between;gap:8px;align-items:baseline}
ul.list li:hover{background:#1D2E25}
ul.list li[aria-selected=true]{background:#243A2E;box-shadow:inset 3px 0 0 var(--signal)}
.li-meta{color:var(--chalk-dim);font-size:12.5px;white-space:nowrap}
.count{color:var(--chalk-dim);font-size:13px;padding:8px 12px 10px;
  border-top:1px solid var(--line);flex:none}
.who{display:flex;flex-wrap:wrap;align-items:baseline;gap:10px 14px}
.who h2{font-size:30px;margin:0;line-height:1}
.who .team{color:var(--chalk-dim)}
.facts{color:var(--chalk-dim);font-size:14px;margin:2px 0 18px}
.metric{padding:9px 0 10px;border-bottom:1px solid #1E2C25}
.metric:last-of-type{border-bottom:0}
.why{margin:3px 0 0;font-size:12px;color:var(--chalk-faint);
  max-width:78ch;line-height:1.5}
@media(max-width:560px){.why{margin-bottom:14px}}
.bar-row{display:grid;grid-template-columns:190px 1fr 96px;gap:10px;align-items:center;padding:3px 0}
@media(max-width:560px){.bar-row{grid-template-columns:140px 1fr 84px}}
.bar-lab{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:16.5px;
  font-weight:600;color:var(--chalk);line-height:1.15;letter-spacing:.01em}
.track{display:block;background:#0C1410;border:1px solid var(--line);height:14px;
  border-radius:2px;overflow:hidden}
.fill{display:block;height:100%;background:var(--signal);opacity:.9}
.bar-val{text-align:right;font-variant-numeric:tabular-nums;font-size:13.5px}
.raw{color:var(--chalk-dim);font-size:12px}
h3{font-size:20px;margin:26px 0 4px}
.hint{color:var(--chalk-dim);font-size:13.5px;margin:0 0 14px;max-width:74ch}
.hint b{color:var(--chalk);font-weight:600}
.viewer{display:grid;grid-template-columns:1fr 210px;gap:18px;align-items:start}
@media(max-width:760px){.viewer{grid-template-columns:1fr}}
svg.pitch{width:100%;height:auto;display:block;background:var(--grass);
  border:1px solid var(--line);border-radius:3px}
.nav{display:flex;gap:8px;align-items:center;margin-top:10px;flex-wrap:wrap}
button.nb{background:none;border:1px solid var(--line);color:var(--chalk);font:inherit;
  border-radius:3px;padding:4px 12px;cursor:pointer}
button.nb:hover{border-color:var(--signal);color:var(--signal)}
button.nb[disabled]{opacity:.35;cursor:default}
.pager{color:var(--chalk-dim);font-size:13.5px;font-variant-numeric:tabular-nums}
.tag{font-size:12.5px;border:1px solid var(--line);border-radius:99px;padding:1px 10px;color:var(--chalk-dim)}
.tag.good{border-color:var(--signal);color:var(--signal)}
.tag.miss{border-color:var(--alt);color:var(--alt)}
.side dl{margin:0}
.side dt{font-family:"Barlow Condensed";font-size:13px;color:var(--chalk-dim);
  text-transform:none;margin-top:10px}
.side dd{margin:0;font-size:22px;font-variant-numeric:tabular-nums}
.side .legend{margin-top:16px;font-size:13px;color:var(--chalk-dim);line-height:1.9}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block;vertical-align:-1px;margin-right:7px}
footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);
  color:var(--chalk-dim);font-size:13.5px;max-width:74ch}
details summary{cursor:pointer;color:var(--chalk);margin-top:10px}
details p{margin:8px 0}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Euro 2024 passing decisions</h1>
  <p class="sub">Every open-play pass at the tournament, measured two ways: how many opponents
  it actually took out, and how many the <b>best available option</b> would have taken out.
  The gap between those is a read on decision making. Built from
  <b>43,818 passes</b> across all 51 matches, using StatsBomb 360 freeze frames.
  Offside team-mates are not counted as options.</p>
</header>

<div class="cols">
  <div class="rail"><div class="panel">
    <div class="controls">
      <input id="q" type="search" placeholder="Search player or country" autocomplete="off">
      <select id="pos"><option value="">All positions</option></select>
      <select id="sort">
        <option value="took">Sort: took the option</option>
        <option value="byp">Sort: opponents bypassed</option>
        <option value="press">Sort: pressure faced</option>
        <option value="name">Sort: name</option>
      </select>
    </div>
    <ul class="list" id="list" role="listbox" aria-label="Players"></ul>
    <p class="count" id="count"></p>
  </div></div>
  <main id="detail"></main>
</div>

<footer>
  <p>Data: <a href="https://github.com/statsbomb/open-data">StatsBomb Open Data</a>, UEFA Euro 2024,
     including 360 freeze frames. Built by Nikola Milićević.
     Companion piece to <a href="https://nikolavladimirmilicevic.github.io/aleague-movement-profiles/">A-League movement profiles</a>.</p>
  <details>
    <summary>How a pass is scored</summary>
    <p>A 360 freeze frame records where every visible player stood at the moment of the event.
       An opponent counts as taken out if he sits between the passer and the target, inside a
       corridor 10 metres either side of the pass line. The same calculation is then run for
       every visible team-mate who was at least 5 metres further upfield, and the best of those
       is what was on offer.</p>
    <p>A team-mate standing in an offside position is not an option, so he is not counted.
       Without that check one in five of the best options found was an offside player, which
       inflated what everyone appeared to be missing by roughly a tenth.</p>
    <p>Passes the referee called back, 147 ruled offside and 56 injury clearances, are dropped:
       a pass that did not stand did not beat anyone. Set pieces are excluded, as are goalkeepers, whose long distribution clears half a pitch
       and would not be comparable. Players need at least 60 open-play passes. Percentiles are
       within position group, because a centre-back and a winger are not solving the same problem.</p>
    <p>Two honest limitations. The camera does not see the whole pitch, so options outside the
       frame are invisible to this method and the true best option may have been missed. And
       passes from inside the penalty area take out 5.7 opponents on average against 3.0
       elsewhere, simply because bodies are packed in there, so the metric rewards crosses and
       cutbacks. Both are properties of the approach, not bugs, but they shape how the numbers
       should be read.</p>
    <p>This measures incision, not quality. A centre-back recycling possession safely is doing
       his job, and will sit low here.</p>
  </details>
</footer>
</div>

<script>
const DB = __DATA__, P = DB.players;
const METRICS = [
  ['byp',  'Opponents bypassed', ' per pass',
   'How many opponents his average pass leaves behind the ball.'],
  ['avail','Best option offered', ' per pass',
   'What the most incisive visible team-mate would have been worth. High means his team kept offering him forward options.'],
  ['took', 'Took the option', '%',
   'The share of what was on offer that he actually played. This is the decision reading: two players can face the same picture and choose differently.'],
  ['press','Nearest opponent', ' m',
   'His space at the moment of the pass. Low means he was playing in tight areas, which makes everything above harder.'],
  ['prog', 'Ball moved upfield', ' m',
   'How far towards the opponent goal his average pass moved the ball. Negative territory would mean he mostly played backwards.'],
  ['comp', 'Completion', '%',
   'Share of passes that reached a team-mate. Incision costs completion, so read this against the rows above rather than on its own.'],
];
let sel = P[0], fi = 0;

/* ---------------- pitch ---------------- */
function pitch(f){
  const W=120,H=80,PAD=2,S=`0 0 ${W+PAD*2} ${H+PAD*2}`;
  const X=x=>x+PAD, Y=y=>y+PAD;
  let s=`<svg class="pitch" viewBox="${S}" role="img" aria-label="Pass at ${f.v}">`;
  const ln='stroke="#2F4438" stroke-width=".5" fill="none"';
  s+=`<rect x="${PAD}" y="${PAD}" width="${W}" height="${H}" ${ln}/>`;
  s+=`<line x1="${X(60)}" y1="${Y(0)}" x2="${X(60)}" y2="${Y(80)}" ${ln}/>`;
  s+=`<circle cx="${X(60)}" cy="${Y(40)}" r="10" ${ln}/>`;
  s+=`<rect x="${X(0)}" y="${Y(18)}" width="18" height="44" ${ln}/>`;
  s+=`<rect x="${X(102)}" y="${Y(18)}" width="18" height="44" ${ln}/>`;
  s+=`<rect x="${X(0)}" y="${Y(30)}" width="6" height="20" ${ln}/>`;
  s+=`<rect x="${X(114)}" y="${Y(30)}" width="6" height="20" ${ln}/>`;
  // opponents
  f.o.forEach((o,i)=>{
    const hit=f.k.includes(i);
    s+=`<circle cx="${X(o[0])}" cy="${Y(o[1])}" r="${hit?2.1:1.7}" fill="var(--opp)"
        opacity="${hit?1:.45}"${hit?' stroke="#F2B4AC" stroke-width=".5"':''}/>`;
  });
  // team-mates
  f.m.forEach(m=>{ s+=`<circle cx="${X(m[0])}" cy="${Y(m[1])}" r="1.5" fill="#7D9187" opacity=".8"/>`; });
  // the option not taken
  if(f.b && f.a>f.n){
    s+=`<line x1="${X(f.s[0])}" y1="${Y(f.s[1])}" x2="${X(f.b[0])}" y2="${Y(f.b[1])}"
        stroke="var(--alt)" stroke-width=".7" stroke-dasharray="2 1.6" opacity=".9"/>`;
    s+=`<circle cx="${X(f.b[0])}" cy="${Y(f.b[1])}" r="2.4" fill="none" stroke="var(--alt)" stroke-width=".7"/>`;
  }
  // the pass
  s+=`<line x1="${X(f.s[0])}" y1="${Y(f.s[1])}" x2="${X(f.e[0])}" y2="${Y(f.e[1])}"
      stroke="var(--signal)" stroke-width="1" stroke-linecap="round"/>`;
  s+=`<circle cx="${X(f.e[0])}" cy="${Y(f.e[1])}" r="1.4" fill="var(--signal)" opacity=".8"/>`;
  s+=`<circle cx="${X(f.s[0])}" cy="${Y(f.s[1])}" r="2.6" fill="var(--signal)"/>`;
  return s+`</svg>`;
}

/* ---------------- detail ---------------- */
function render(){
  const p=sel, f=p.frames[fi];
  const bars=METRICS.map(([k,lab,unit,why])=>`
    <div class="metric">
      <div class="bar-row">
        <span class="bar-lab">${lab}</span>
        <span class="track"><span class="fill" style="width:${p.pct[k]}%"></span></span>
        <span class="bar-val">${Math.round(p.pct[k])}<span class="raw"> / ${p[k]}${unit}</span></span>
      </div>
      <p class="why">${why}</p>
    </div>`).join("");

  const missed=f.a>f.n;
  document.getElementById("detail").innerHTML=`
    <div class="who"><h2>${p.name}</h2><span class="team">${p.team}</span>${p.full&&p.full!==p.name?`<span class="raw">${p.full}</span>`:""}</div>
    <p class="facts">${p.pos} · ${p.passes} open-play passes · ${p.min} minutes</p>
    <p class="hint">Two numbers on every row: his <b>percentile against other ${p.pos.toLowerCase()}s</b>
       at this tournament, then the raw value. The bar shows the percentile.</p>
    ${bars}
    <h3>What he saw</h3>
    <p class="hint">His four most incisive passes and his three biggest missed options, where he had them.
       Each frame is one real pass. Red is an opponent, brighter red if the pass
       took him out of the game. Grey is a team-mate. Gold is the pass he played. A dashed blue
       line is the option that would have taken out more.</p>
    <div class="viewer">
      <div>
        ${pitch(f)}
        <div class="nav">
          <button class="nb" id="prev" ${fi===0?"disabled":""}>Previous</button>
          <button class="nb" id="next" ${fi===p.frames.length-1?"disabled":""}>Next</button>
          <span class="pager">${fi+1} of ${p.frames.length}</span>
          <span class="tag ${missed?'miss':'good'}">${missed?'left a better option':'took the best option'}</span>
          ${f.c?'':'<span class="tag">incomplete</span>'}
        </div>
      </div>
      <div class="side">
        <dl>
          <dt>${f.v}</dt>
          <dd>${f.n} <span class="raw" style="font-size:14px">taken out</span></dd>
          <dt>best option available</dt>
          <dd>${f.a}</dd>
        </dl>
        <div class="legend">
          <span class="dot" style="background:var(--signal)"></span>the player<br>
          <span class="dot" style="background:var(--opp)"></span>opponent<br>
          <span class="dot" style="background:#7D9187"></span>team-mate<br>
          <span class="dot" style="background:var(--alt)"></span>option not taken
        </div>
      </div>
    </div>`;
  const pv=document.getElementById("prev"), nx=document.getElementById("next");
  if(pv) pv.onclick=()=>{ if(fi>0){fi--;render();} };
  if(nx) nx.onclick=()=>{ if(fi<p.frames.length-1){fi++;render();} };
}

/* ---------------- list ---------------- */
function paint(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const pos=document.getElementById("pos").value, by=document.getElementById("sort").value;
  let rows=P.filter(p=>(!pos||p.pos===pos)&&(!q||p.name.toLowerCase().includes(q)||p.team.toLowerCase().includes(q)));
  rows.sort(by==="name"?(a,b)=>a.name.localeCompare(b.name):(a,b)=>b[by]-a[by]);
  document.getElementById("list").innerHTML=rows.map(p=>
    `<li role="option" tabindex="0" data-id="${p.id}" aria-selected="${p.id===sel.id}">
      <span>${p.name}</span><span class="li-meta">${p.team}</span></li>`).join("")
    || `<li style="color:var(--chalk-dim)">Nobody matches that search.</li>`;
  document.getElementById("count").textContent=rows.length+(rows.length===1?" player":" players");
  document.querySelectorAll("#list li[data-id]").forEach(li=>{
    const pick=()=>{ sel=P.find(x=>x.id==li.dataset.id); fi=0; paint(); render(); };
    li.onclick=pick;
    li.onkeydown=e=>{ if(e.key==="Enter"||e.key===" "){e.preventDefault();pick();} };
  });
}
[...new Set(P.map(p=>p.pos))].sort().forEach(v=>{
  const o=document.createElement("option"); o.value=o.textContent=v;
  document.getElementById("pos").appendChild(o);
});
document.getElementById("q").oninput=paint;
document.getElementById("pos").onchange=paint;
document.getElementById("sort").onchange=paint;
document.getElementById("sort").value="took";
sel=[...P].sort((a,b)=>b.took-a.took)[0];
paint(); render();
</script>
</body>
</html>
"""

open('/home/claude/euro2024.html', 'w', encoding='utf-8').write(HTML.replace('__DATA__', DATA))
print("%.1f KB" % (len(HTML.replace('__DATA__', DATA))/1024))
