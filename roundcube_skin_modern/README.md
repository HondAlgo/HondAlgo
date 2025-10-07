# Modern Roundcube Skin

This skin delivers a redesigned Roundcube experience with a modernized interface, flexible layout, and refreshed styling. It is built to be responsive, accessible, and easy to customize.

## Features
- **Responsive three-pane layout** with collapsible folders sidebar and flexible message preview pane.
- **Clean typography and color system** based on CSS custom properties for quick theming.
- **Improved message list interactions** featuring subtle hover states, quick actions, and visual density controls.
- **Accessible contrasts** that respect WCAG AA guidelines for text and interactive elements.
- **Modular structure** separating layout, color, and component styles to simplify maintenance.

## Installation
1. Copy the `roundcube_skin_modern` directory into `skins/` inside your Roundcube installation.
2. Update `config/config.inc.php` and set:
   ```php
   $config['skin'] = 'roundcube_skin_modern';
   ```
3. Clear compiled templates (if caching is enabled) by removing `temp/cache/*`.
4. Reload Roundcube in the browser.

## Customization
- Adjust global design tokens inside `styles/_tokens.css` to tweak fonts, spacing, or colors.
- Extend or override component styles within `styles/components/*.css`.
- Modify structural layout in `templates/mail.html` and `templates/includes/*.html` as needed.

## File Structure
```
roundcube_skin_modern/
├── README.md
├── config.json
├── styles/
│   ├── _tokens.css
│   ├── layout.css
│   ├── components.css
│   └── overrides.css
└── templates/
    └── mail.html
```

## Build Notes
- The skin uses vanilla CSS; no preprocessing is required.
- If you prefer SCSS/LESS, convert `_tokens.css` into variables and import them where needed.
- Minify the CSS for production deployments if desired.
