# README embed snippet

Add this to your GitHub profile repository `README.md` after you copy the files into the repo:

```md
<p align="center">
  <img src="./assets/worldline-card.svg" alt="Worldline Status Card" width="980" />
</p>
```

If you want to use the raw GitHub URL instead:

```md
![Worldline Status Card](https://raw.githubusercontent.com/<YOUR_USERNAME>/<YOUR_PROFILE_REPO>/main/assets/worldline-card.svg)
```

Expected repo layout:

```text
.github/workflows/update-worldline-card.yml
scripts/generate-worldline-card.mjs
assets/worldline-card.svg
data/worldline.json
```
