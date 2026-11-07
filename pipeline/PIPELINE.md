# Hidden Mechanics: daily short runbook

Channel: Hidden Mechanics (@Hidden.Mechanics.Channel), YouTube channel ID UCqTSZ70ZSh30bof-sx5kROQ.
Niche: everyday engineering and tech explained (cars, phones, planes, appliances, buildings, the internet...).
Format: vertical 1080x1920, 30 fps, 45-60 s, animated explainer, AI narration, word-by-word captions, branded outro.
Owner: Bronsin (benyaminbronsin@gmail.com). Claude runs the channel and publishes one short per day.

Home of everything: GitHub repo **bronsinb/hidden-mechanics** (public). Attach it with `add_repo` (owner bronsinb, repo hidden-mechanics, access push) and clone to `/home/claude/hidden-mechanics`.
- `pipeline/` engine (`hm/`), `setup.sh`, this runbook, `episodes.json` (log of every episode)
- `pipeline/episodes/NN_slug/` script.json, scenes.py, meta.json
- `videos/` finished upload-size MP4s (YouTube Studio pulls the file from here)
- `branding/` logo, banner, watermark
A mirror of `videos/` lives on Bronsin's Mac in `~/Movies/Hidden Mechanics/videos/` (nice to have, not required).
Uploading needs Bronsin's Mac to be on, because it happens in his Chrome (Claude in Chrome extension, profile signed into the channel).

## 0. Preflight (stop early, and say why)
- Chrome reachable? `list_connected_browsers` must return a browser (retry a few times over ~2 minutes). If not: **notify** (see 7) "Chrome on your Mac isn't reachable (Mac asleep/off, Chrome closed, or the Claude extension disconnected), so today's short wasn't made" and stop. Check this before spending time on rendering.

## 1. Set up the cloud workspace
- `add_repo` bronsinb/hidden-mechanics (push), then `git clone --depth 1 https://github.com/bronsinb/hidden-mechanics /home/claude/hidden-mechanics`.
- `bash pipeline/setup.sh` (installs packages, downloads the voice model from GitHub ~350 MB).
- Work from `/home/claude/hidden-mechanics/pipeline` (commands are `python3 -m hm.studio ...`). Look at the two most recent `episodes/*/scenes.py` as style references.

## 2. Pick today's topic
- Read `episodes.json`; never repeat a topic or a close variant. Rotate categories (don't do cars twice in a row).
- A good topic is a "wait, how does that work?" question about something people touch every day, with a satisfying mechanism and ideally a twist or surprising fact at the end. Examples of the bar: keyless entry + relay attacks; why plane windows are round + the Comet crashes + the tiny hole.
- Use WebSearch to check what is currently interesting, then research the mechanism. **Every factual claim must be checked against at least one solid source** (manufacturer/engineering/encyclopedic/reputable press). No made-up numbers: if a number can't be sourced, say it qualitatively. Put the sources in `meta.json`.

## 3. Script (`episodes/NN_slug/script.json`)
- 8-9 lines, 105-135 words total, ~50-58 s when voiced. Line ids are short slugs; the **first** line is the hook, the **last** line has id `cta` and text `Follow Hidden Mechanics for more.`
- Hook in the first 3 seconds: a surprising claim or question. One idea per line. Plain words. End on a twist/bonus.
- Voice settings: `{"voice": "am_michael", "speed": 1.08}`.
- `python3 -m hm.studio voice EP` -> writes voice.wav + timeline.json (word timings). Read the timeline to place animation beats on words.

## 4. Animation (`episodes/NN_slug/scenes.py`)
- `from hm.core import *` and `from hm.props import *`. Define `draw(c, t)` (cairo context, seconds) and `SFX()`.
- The engine draws the background, the outro (for the `cta` line) and the captions; scenes draw everything else. Multiply scene alpha by `1 - cta_amount(t)`.
- Timing helpers: `S(id)`/`E(id)` line start/end, `wt(id, "word", nth=0, end=False)` the moment a word is spoken. Easing: `pr(t, start, dur)` progress 0..1, `ease`, `eout`, `eio`, `back` (pop-in). Drawing: `rr` rounded rect, `fill`, `text`, `pill`, `glow`, `check`, `cross`, `lock_icon`, `safe_scale` (use instead of c.scale). Colors: CYAN, AMBER, GREEN, RED, PURPLE, WHITE, MUTED, YEL.
- Helpers: `hook_title(c, t, "LINE ONE", "LINE TWO", S(second_line_id))`, `scene_label(c, t, line_id, "LABEL", color)` for the top pill of each beat.
- Layout (1080x1920): title/labels y 200-345, main stage y 420-1300, captions at y 1470 (keep 1380-1560 clear), outro owns the screen at the end.
- Style: dark navy background, flat shapes with soft glows, one clear visual per line, things pop in exactly on the word that names them, labels as outlined pills, red = danger/problem, green = fix/success, amber = energy/data, cyan = signals/neutral. Every line must have something moving. Props in `hm/props.py` (top-view car, key fob, house, radio bubbles...) can be reused; add new reusable props to props.py when they're generic.
- Gotcha: when drawing a dashed polyline as separate segments, set the dash offset per segment from the cumulative length, or the dashes disappear.
- `SFX()` returns `[(seconds, cue)]`, cue names from `hm.mix.CUES`: pop, blip, ping, wake, ok, success, rumble, warn, low, tick, rise, resolve. Whooshes between lines and the outro chime are automatic.

## 5. Check, then render once
- `python3 -m hm.studio stills EP t1 t2 ...` at ~12 moments (the busiest moment of every line + the outro). Look at `EP/frames/sheet*.jpg` with Read. Fix overlaps, text outside the frame, empty stretches, anything unreadable. Re-check only what changed.
- `python3 -m hm.studio video EP` -> `EP/final.mp4` (~35 s) and `EP/upload.mp4` (same video under 10 MB, which is the Chrome file-attach limit; upload this one). Pull 4 frames from the MP4 with ffmpeg and look once. Check loudness (`volumedetect` max around -1 to -2 dB).
- Name: `hidden_mechanics_NN_slug.mp4`.

## 6. Save and upload
- Copy `EP/upload.mp4` to `/home/claude/hidden-mechanics/videos/hidden_mechanics_NN_slug.mp4`. Commit the video, the episode folder (script.json, scenes.py, meta.json; generated files are gitignored) and any engine changes, then `git push origin main`. Note the commit SHA (`git rev-parse HEAD`).
- Optional mirror: if the Mac is reachable (`get_device_info`), also `device_commit_files` the MP4 to `~/Movies/Hidden Mechanics/videos/`.
- Upload in **Chrome** (Claude in Chrome tools): new tab -> `https://studio.youtube.com/channel/UCqTSZ70ZSh30bof-sx5kROQ/videos/upload?d=ud`. Wait for the upload dialog, then run this in the page with `javascript_tool` (it pulls the video from GitHub and hands it to YouTube's file picker; the Chrome extension's own file attach does not accept files Claude made):
  ```js
  const url = 'https://raw.githubusercontent.com/bronsinb/hidden-mechanics/<SHA>/videos/hidden_mechanics_NN_slug.mp4';
  const blob = await (await fetch(url)).blob();
  const input = document.querySelector('ytcp-uploads-dialog input[type=file], input[type=file]');
  const dt = new DataTransfer(); dt.items.add(new File([blob], 'hidden_mechanics_NN_slug.mp4', {type: 'video/mp4'}));
  input.files = dt.files; input.dispatchEvent(new Event('change', {bubbles: true}));
  blob.size
  ```
  Use the commit SHA in the URL (a branch name can serve a cached old file). If Studio shows "Oops, something went wrong", reload the page once and retry.
- Details: title from meta.json (ends with `#shorts`, under 100 chars), description from meta.json, "No, it's not made for kids" (`tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]`). Under "Show more", add the tags. Altered/synthetic content: "No" (animated explainer, no realistic people or events).
- Next x3 to Visibility. **Schedule** the publish for 10:00 AM America/Los_Angeles on the first day that has no episode yet: the day after the latest `publish_at` in episodes.json, but never earlier than the next 10:00 AM from now. (This keeps a one-day buffer, so one missed run doesn't leave a gap.) Confirm "Checks complete. No issues found." before scheduling. If checks report a copyright or policy issue: do not publish, notify Bronsin.
- Read back the video link from the confirmation dialog. Close the tab.

## 7. Log and notify
- Append to `episodes.json`: `{n, slug, title, topic, category, date, video_url, publish_at, sources}`, commit and push.
- Notify Bronsin with a push notification (PushNotification tool): "Short #N scheduled: <title> - goes live <time>. <link>". If a step failed, say which step and what's needed.
- If push isn't available, or the failure means the short can't go out today, also email benyaminbronsin@gmail.com from the connected Gmail with the same message (subject starts with "Hidden Mechanics:").
