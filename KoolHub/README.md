# KoolHub assets

Generated from the supplied logo (`source/original-logo.png`, 526×601). Rebuild everything with `python3 source/build_assets.py` (needs pillow, numpy, scipy, opencv-python-headless, fonttools, playwright + Chromium).

Brand colors: mark gradient blue `#4f6fe0` → purple `#7a45c8` / green `#4fb98a`; wordmark ink `#3f4152`; manifest theme color `#5b57d1`.

## Where to use what

| Need | File |
|---|---|
| Website header (light bg) | `svg/koolhub-logo-horizontal.svg` (or `-notagline` for tight navbars) |
| Website header (dark bg) | `svg/koolhub-logo-horizontal-dark.svg` |
| Splash screen / login / hero | `svg/koolhub-logo-primary.svg` (`-dark` for dark bg) |
| Symbol only | `svg/koolhub-mark.svg`; `-white` / `-black` are one-color silhouettes |
| Browser favicon | `favicon/` (see `favicon/head-snippet.html`) |
| PWA / web app manifest | `favicon/site.webmanifest`, `android-chrome-*`, `maskable-512x512.png` |
| iOS app icon | `mobile/ios/AppIcon-1024.png` (or `-dark`), opaque square: iOS applies the corner mask |
| Android launcher | `mobile/android/mipmap-*/` (legacy, round and adaptive foreground); adaptive background: white `#ffffff` |
| Play Store listing | `mobile/android/play-store-512.png` |
| Link previews (OG / Twitter) | `social/og-image-1200x630.png` |
| Rounded app-icon artwork | `svg/koolhub-icon*.svg`, `png/icon/` |

PNG logos are transparent, at 256/512/1024/2048 px wide (symbol: 128–1024) in `png/logo/`.

## Notes

- **The mark is not a true vector.** It is a 3D-shaded, translucent render, so it is a background-removed raster
  (upscaled 4× from the source) embedded in the SVGs.
  It stays sharp to roughly 1000 px wide; beyond that, supply a higher-resolution source or vector file.
- **Typography:** wordmark is Poppins Bold, tagline Poppins Regular, both converted to true vector outlines (fonts in `source/fonts/`, SIL OFL). Poppins was chosen over Montserrat because its proportions match the supplied logo (width/cap-height 6.17 vs 6.17; Montserrat is ~5% wider). To use Montserrat instead, swap the font files and `outline()` in `source/build_assets.py`.
- Dark variants change only the text color; the mark is used as-is on dark backgrounds.
- Don't bake shadows into store icons; the platforms add their own.
