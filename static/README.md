# Static Assets

This directory contains the frontend assets for the application.

## Directory Structure

```
static/
├── src/              # Source files (edit these)
│   ├── css/
│   │   └── app.css   # Main CSS with Tailwind directives
│   └── js/
│       └── app.js    # Main JavaScript (Alpine.js)
└── dist/             # Built files (auto-generated, don't edit)
    ├── css/
    │   └── app.css   # Compiled & minified CSS
    └── js/
        └── app.js    # Bundled Alpine.js
```

## Development Workflow

### First Time Setup

```bash
# Install Node dependencies
npm install
```

### Building Assets

```bash
# Build for production (minified)
npm run build

# Watch for changes (development)
npm run watch:css
# or
npm run dev
```

### What Gets Built

1. **CSS (`src/css/app.css` → `dist/css/app.css`)**
   - Tailwind CSS is processed
   - Custom components are applied
   - Output is minified for production

2. **JavaScript (`node_modules` → `dist/js/app.js`)**
   - Alpine.js is copied from node_modules
   - Already minified from source

## Environment Modes

### Development (FLASK_ENV=development)
- Uses CDN versions of Tailwind and Alpine
- No build step required
- Easier to debug
- Hot reload friendly

### Production (FLASK_ENV=production)
- Uses built assets from `dist/`
- No external CDN dependencies
- Optimized and minified
- Better performance

## File Sizes

- **app.css**: ~30-35 KB (minified)
- **app.js**: ~44 KB (Alpine.js minified)

## Adding Custom Styles

Edit `src/css/app.css`:

```css
@layer components {
  .my-component {
    @apply bg-blue-500 text-white px-4 py-2;
  }
}
```

Then rebuild:

```bash
npm run build
```

## Adding Custom JavaScript

Edit `src/js/app.js`:

```javascript
// Import Alpine.js
import Alpine from 'alpinejs';

// Add custom Alpine components here
Alpine.data('myComponent', () => ({
    // component logic
}));

window.Alpine = Alpine;
Alpine.start();
```

Note: Currently, Alpine is just copied from node_modules. 
To use custom JavaScript, you'd need to add a bundler like esbuild or Vite.

## Tailwind Configuration

**Tailwind CSS v4** uses CSS-first configuration.

Custom theme settings are defined in `src/css/app.css`:

```css
@theme {
  --color-primary-500: #3b82f6;
  --font-sans: 'Inter', system-ui, sans-serif;
}
```

The `tailwind.config.js` file is optional and mainly used for content scanning.

## Don't Commit

The `dist/` directory is in `.gitignore` and should not be committed.
These files are built:
- During Docker image builds
- By CI/CD pipelines
- Locally when you run `npm run build`

## Troubleshooting

### CSS not updating
```bash
# Clean and rebuild
rm -rf static/dist/
npm run build
```

### Build errors
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Production assets not loading
- Check `FLASK_ENV=production` is set
- Verify files exist in `static/dist/`
- Check browser console for 404 errors
