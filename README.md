# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Teazel-lab/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Teazel-lab/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A single 1024x1024 front page summing up the world news of Thursday 19 November 2026: a dated masthead, a region colour bar and a UTC timeline, four illustrated lead stories and twelve smaller illustrated cards (each tagged CONFIRMED with its source or CLAIM with who said it), a "Where it happened" world map with numbered pins, a date check listing what was left out because it broke earlier or is still to come, and 27 one-line briefs. `build.py` turns `data/stories.json` into an HTML/CSS page with hand-drawn inline SVG illustrations (`illus*.py`) and a hand-made SVG world map, then renders it to `entry.png` with headless Chrome using locally installed fonts; `main.py` simply copies the committed `entry.png` to the output.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=68mq8j14&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
