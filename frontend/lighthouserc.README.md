# Lighthouse CI Configuration

Lighthouse CI runs automatically on GitHub Actions to ensure code quality on the CrowdIQ PWA. 
It tests pages to maintain minimum thresholds. 

### Understanding the Thresholds:
- **Performance (0.60 minimum - Warn)**: Tracks the overall app load time metrics (FCP, LCP, TBT) without blocking security and correctness CI.
- **Accessibility (0.95 minimum)**: Ensures the app is usable by standard accessibility tools (screen readers). We check WCAG 2.1 AA.
- **Best Practices (0.90 minimum)**: Checks for modern web standards and absence of deprecated APIs.
- **PWA (0.85 minimum)**: Verifies the app is installable, serves over HTTPS, and registers a valid service worker.
- **SEO (0.80 minimum - Warn)**: Basic metadata, this app is accessed directly via QR codes so SEO isn't tightly strict. 

### How to Debug Failure:
- **Performance Drops (< 0.60)**: Check the built bundle size via `npm run build -- --report` to identify large dependencies. Implement code splitting.
- **Accessibility Drops (< 0.95)**: Run axe rules locally using `npm run test:a11y` with vitest. Or use Chrome Lighthouse panel locally to pinpoint the exact DOM element violating rules.
- **PWA Drops (< 0.85)**: Check `public/manifest.json` values and verify the service worker auto-registration. Check the browser's Application tab to inspect Service Worker.
