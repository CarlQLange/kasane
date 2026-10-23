# Kasane

A browser puzzle game about layering materials. Pieces fall into a wooden frame; a colour that touches both walls clears and scores. Materials react with each other (heat, cold, water, acid and so on), and every two clears you pick a new material for your shelf. Woodblock-print look, silent, playable on desktop and phone.

The whole game is `index.html` (one file of HTML, CSS and JS, no build step) plus `assets/` and `manifest.json`.

## Layout

- `index.html` — the game. Roughly in order: tuning constants, `SHAPES`, `RARITY`, `MATERIALS`, `REACTIONS`, the spatial grid, physics (`substep`), reactions (`react`, `touch`, `transform`), clearing (`findClears`), rendering (`render`, `drawGroup`, `carve`), screens (title, pick, pause, notebook, help, game over), input.
- `assets/` — only files the game loads: `washi.jpg` (backdrop), `waves.webp` (scrolling wave strip), `fx-*.png` (seal, splat, crane, cloud, petal), `app-icon-*.png`, and `icons/<material>.png`.
- `art/` — source material that doesn't ship: generated sheets in `art/raw/`, the four early style concepts in `art/concepts/`, `art/slice_icons.py`, and icons/textures for cut materials in `art/unused/`.
- `scripts/release.sh` — copies the game into the website (see Releasing).

## Running and testing

Serve the folder with the no-cache server from the browser-game skill and open it: `python3 ~/.claude/skills/browser-game/scripts/serve.py 8765 .`. Fonts come from Google Fonts.

The game exposes its state as globals, so the reliable way to test is to drive it from the browser console rather than play by hand: `start()`, set `pool`, set `nextType` and `spawnAt = 0`, call `tick(DT)` in a loop, `moveTo(x)`, `slam()`, then inspect `ps`, `runFound`, `nearMiss`, `clears`. Set `hitstop = 0` inside loops or clears will stall the simulation.

Progress lives in `localStorage` under `walltowall-best` and `walltowall-notebook` (the game's old name; keep the keys so saved progress survives). Testing in the same browser writes to Carl's real notebook, so save both keys before a test run and restore them after.


## Releasing

`./scripts/release.sh [site-repo]` copies `index.html`, `manifest.json` and `assets/` into `~/workspace/personal/web/redfloatplane.lol/public/arcade/kasane/play/` (or the given site repo). Assets go into `assets-<commit>/` and every path is rewritten to match, because the site's nginx caches images for a day. Commit here first so the version is a commit hash; uncommitted changes produce a `-dirty` version.

Then, in the site repo: rebuild to check, commit the release, and deploy with `git push dokku main`. The arcade write-up page is `src/content/arcade/kasane.md` there; its description is Carl's to write.

Source is public at https://github.com/CarlQLange/kasane, and the game is live at https://redfloatplane.lol/arcade/kasane/. Push and deploy only when Carl asks. Keep the site repo's GitHub `main` in step with what's deployed to dokku, because the Scraps blog sync deploys from GitHub `main`. Prose that appears on Carl's website as his (the arcade description, a README for this repo) is his to write; leave placeholders rather than drafting it.

## Design decisions Carl has made

- **Silent.** `sfx` is a no-op proxy and the M key is gone. Don't add sound.
- **Linocut / woodblock style.** Cream washi paper, thick ink outlines, flat muted pigments, carved marks per material (`carve`: stipple for powders, waves for liquids, shine for ice and glass, gouges for solids). New art must match: magenta-backed icon sheets generated in this style, keyed out with the approach in `art/slice_icons.py`.
- **Almost no text.** The only English is the game name, Score, Best, Next, material names and their one-word tags. Everything else is a seal (重 logo, 選 pick, 休 pause, 帳 notebook, 満 game over and the max line, 消 and 二 to 十 for clears and combos) or a glyph button. Reactions are shown as icon equations, never sentences. Any new copy has to be very short and earn its place.
- **Quiet backdrop.** Background animation is close to imperceptible and slows to a fifth of that during play, under a paper-coloured veil (`BACKDROP_*`). Carl found anything livelier distracting.
- **Forgiving.** Touching a wall counts within `TOUCH` px, same-colour pieces link across `LINK_GAP` px, and the next piece waits for the board to settle (`SPAWN_MIN`, `SPAWN_MAX`, `CALM_*`). Difficulty should never come from time pressure.
- **No landing shadow** for now (`SHOW_GHOST = false`); Carl felt it exposed the particle internals.
- **Every pick offers at least one material that reacts with the shelf**, and the board is emptied before the pick doors close.
- **Overlays are shoji doors** that slide shut over the well, with a card dropped on top; seal and button characters are nudged to sit optically centred.

## Adding a material

Add an entry to `MATERIALS` with a `rarity` (pickables only), `shape`, one-word `tag`, `color` (must be visibly distinct from every other material, since clears are by colour), `phase` (`solid`, `soft`, `powder`, `liquid`, `gas`) and its behaviour properties. Add any new reactions to `REACTIONS` as `[input, cause, output]` icon tokens, make sure `reactsWith` knows about it so pick offers treat it as synergistic, and give it an icon at `assets/icons/<key>.png`. Products (no `rarity`) never appear on the shelf, only through reactions.
