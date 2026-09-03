# Euro 2024 passing decisions

Every open-play pass at Euro 2024, measured two ways: how many opponents it took out, and how
many the best available option would have taken out. Built from
[StatsBomb Open Data](https://github.com/statsbomb/open-data) 360 freeze frames.

Live: `https://<username>.github.io/<repo>/`

## The idea

Most passing metrics tell you what a player did. A 360 freeze frame records where every visible
player stood at the moment of the pass, which means you can also ask what he *could* have done.

For each pass:

- An opponent is **taken out** if he sits between passer and target, inside a corridor 10 metres
  either side of the pass line.
- The same calculation runs for every visible team-mate at least 5 metres further upfield, minus
  anyone standing in an offside position. The best of those is **what was on offer**.
- The ratio of the two, aggregated over a player's passes, is a read on how consistently he
  picks the incisive option.

The site shows the resulting profile for 239 players, plus seven real passes each, drawn on a
pitch with the opponents he beat, the team-mates he had, and the option he left.

## Scale

43,966 open-play passes, all 51 matches, 237 players with 60 or more passes.

## Does it find the right players?

Sorted by the share of what was available that a player actually took, within position:

| Position | Top of the list |
|---|---|
| Wide attacker | Dennis Man, Cody Gakpo, Nico Williams |
| Centre forward | Memphis Depay, Harry Kane, Álvaro Morata |
| Full back | Andrija Živković, Milos Kerkez, Vladimír Coufal |
| Midfield | Tomáš Souček, Christoph Baumgartner, Timi Elšnik |

Gakpo and Nico Williams among the top three wingers, Depay and Kane leading the forwards. Dani
Olmo and Kevin De Bruyne sit tenth and thirteenth of 87 midfielders, so the metric likes them
without being infatuated. Nothing about the method knows who any of these players are.

The pressure column is a second check. Average distance to the nearest opponent falls
monotonically up the pitch: 6 to 8 metres for centre-backs, around 4 for full-backs, 3 to 4 in
midfield, under 3 for wide players and forwards.

## Limitations, stated plainly

**The camera does not see everything.** 360 frames cover the visible area only, so an option
outside the frame is invisible to this method. The "best available option" is therefore the
best *visible* one, and will sometimes understate what a player could see.

**Congestion inflates the count.** Passes from inside the penalty area take out 5.7 opponents on
average against 3.0 elsewhere, because bodies are packed in there. The metric rewards crosses
and cutbacks. This is a property of any packing-style measure, not a bug, but it matters when
reading a forward's numbers against a midfielder's.

**Offside had to be handled explicitly.** A team-mate in an offside position is not an option.
Before that check was added, one in five of the best options the method found was an offside
player, and the average option on offer was overstated by 9%. Whether a team-mate is offside is
computed from the freeze frame: opponent half, ahead of the ball, and ahead of the second-last
opponent, with goalkeepers included in that count. What this cannot see is a team-mate who was
offside but would have been played onside by a team-mate's run, or the referee's actual call.

**The ratio needs a denominator.** One player, an isolated striker, averaged 1.4 available
options per pass against a typical 3.2, which pushed his ratio to 92% while nobody else cleared
50%. That is the metric breaking down, not a finding, so players offered fewer than 2 options
per pass are excluded.

**Incision is not quality.** A centre-back recycling possession safely is doing his job and will
sit low here. Goalkeepers are excluded entirely: their long distribution clears half a pitch and
is not comparable.

## Build

```bash
# events and 360 frames for competition 55, season 282
python3 analyse.py            # exploration, leaderboards by position
python3 build_euro_data.py    # -> euro_site.json
python3 build_site.py         # -> index.html
```

`index.html` is self-contained, data included, no runtime dependencies.

## Companion piece

[A-League movement profiles](https://nikolavladimirmilicevic.github.io/aleague-movement-profiles/),
built on SkillCorner tracking data. That one asks how a player moves without the ball. This one
asks what he does with it.
