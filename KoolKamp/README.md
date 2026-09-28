# KoolKamp assets

Generated from the supplied logo and brand sheet (`source/`). The K symbol, wordmark and tagline
were vectorised, so the SVGs scale to any size. All PNGs are rendered from those SVGs.

Brand colors: gradient `#6abfde` → `#7840d2` (top-right → bottom-left), wordmark ink `#3c4246`, C1 border navy `#223b73`.

## Where to use what

| Need | File |
|---|---|
| Website header (light bg) | `svg/koolkamp-logo-horizontal.svg` (or `-notagline` for tight navbars) |
| Website header (dark bg) | `svg/koolkamp-logo-horizontal-dark.svg` |
| Splash screen / login / hero | `svg/koolkamp-logo-primary.svg` (`-dark` for dark bg) |
| Symbol only (avatar, loader, watermark) | `svg/koolkamp-mark.svg`, `-black`, `-white` for one-color print/UI |
| Browser favicon | `favicon/` (see `favicon/head-snippet.html`) |
| PWA / web app manifest | `favicon/site.webmanifest`, `android-chrome-*`, `maskable-512x512.png` |
| iOS app icon | `mobile/ios/AppIcon-c2-1024.png` (or `-inverted`), opaque and square: iOS applies the corner mask |
| Android launcher | `mobile/android/mipmap-*/` (legacy, round and adaptive foreground); adaptive background: white or `#ffffff` |
| Play Store listing | `mobile/android/play-store-512.png` |
| Link previews (OG / Twitter) | `social/og-image-1200x630.png` |
| Rounded app-icon artwork (C1 / C2 / Inverted) | `svg/koolkamp-icon-*.svg`, `png/icon/` |

PNG logos are transparent and provided at 256/512/1024/2048 px wide (symbol: 128–1024) in `png/logo/`.

## Notes

- Don't bake shadows into store icons; the platforms add their own.
- The "Ks" monogram from the sheet is not included (its font isn't in the source at usable resolution).
- Wordmark/tagline are traced from a ~380 px source, so edges are clean but minor letter-shape
  differences from the original font are possible. If you have the original vector/font files
  (looks like Montserrat + Roboto Condensed), swap them in for pixel-perfect type.
