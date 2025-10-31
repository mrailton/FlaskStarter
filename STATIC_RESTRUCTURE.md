# Static Files Restructure

## Summary

The static files have been reorganized into a cleaner, more maintainable structure with proper subdirectories for different asset types.

## Changes Made

### Directory Structure

**Before:**
```
static/
├── src/
│   ├── input.css
│   └── app.js
└── dist/
    ├── output.css
    └── alpine.min.js
```

**After:**
```
static/
├── src/              # Source files
│   ├── css/
│   │   └── app.css   # Renamed from input.css
│   └── js/
│       └── app.js    # Organized into js/ subdirectory
└── dist/             # Built files (gitignored)
    ├── css/
    │   └── app.css   # Renamed from output.css
    └── js/
        └── app.js    # Renamed from alpine.min.js
```

### File Renames

| Old Path | New Path | Reason |
|----------|----------|--------|
| `static/src/input.css` | `static/src/css/app.css` | More descriptive, matches app.js naming |
| `static/dist/output.css` | `static/dist/css/app.css` | Consistent naming convention |
| `static/dist/alpine.min.js` | `static/dist/js/app.js` | Generic name, easier to reference |

### Updated Files

1. **package.json**
   - Updated all build paths to new structure
   - Added `npm run dev` alias for `watch:css`

2. **templates/base.html**
   - Updated asset references:
     - `dist/output.css` → `dist/css/app.css`
     - `dist/alpine.min.js` → `dist/js/app.js`

3. **tailwind.config.js**
   - Updated content paths to `static/src/js/**/*.js`

4. **.gitignore**
   - Updated to ignore `static/dist/` directory

5. **Documentation**
   - Updated DOCKER_BUILD.md
   - Updated PRODUCTION_READY.md
   - Created static/README.md

## Benefits

### 1. Better Organization
- CSS and JS are clearly separated
- Easier to find and manage files
- Scalable structure for future additions

### 2. Consistent Naming
- All files use `app.*` naming convention
- Source and dist files have matching names
- Clearer what each file contains

### 3. Professional Structure
- Follows industry standards
- Similar to modern frameworks (Next.js, Vite, etc.)
- Easier for new developers to understand

### 4. Future-Proof
- Easy to add more CSS files (e.g., `components.css`)
- Room for multiple JS files if needed
- Clear separation of concerns

## Build Commands

```bash
# Build all assets
npm run build

# Watch CSS for changes
npm run watch:css

# Development mode (alias for watch:css)
npm run dev
```

## File Sizes

- **app.css**: ~32 KB (minified)
- **app.js**: ~44 KB (Alpine.js minified)

## Migration Guide

If you have existing projects based on the old structure:

1. **Move source files:**
   ```bash
   mkdir -p static/src/css static/src/js
   mv static/src/input.css static/src/css/app.css
   mv static/src/app.js static/src/js/app.js
   ```

2. **Update package.json** with new paths

3. **Update templates** to reference new asset paths

4. **Rebuild:**
   ```bash
   npm run build
   ```

## Environment Detection

The application automatically uses the appropriate assets:

**Development (`FLASK_ENV=development`):**
- Loads Tailwind and Alpine from CDN
- No build step required
- Hot reload friendly

**Production (`FLASK_ENV=production`):**
- Uses built files from `static/dist/`
- No CDN dependencies
- Optimized and minified

## Testing

All 231 tests pass with the new structure:

```bash
uv run manage.py test -n auto
# ===== 231 passed in ~10s =====
```

## Compatibility

✅ Works with Docker builds
✅ Works with GitHub Actions CI/CD  
✅ Works with Coolify deployment
✅ Backward compatible via environment variables

## Notes

### Tailwind Version

Now using **Tailwind CSS v4.1** (latest stable).

The CSS file uses Tailwind v4 syntax:
```css
@import "tailwindcss";
@plugin "@tailwindcss/forms";

@theme {
  --color-primary-500: #3b82f6;
  /* ... */
}
```

Benefits of v4:
- CSS-first configuration (no JS config required)
- Faster builds with Rust-based engine
- Better performance and smaller output
- Native CSS variable system

### Alpine.js

Alpine.js is copied directly from node_modules as a pre-built bundle.

For custom JavaScript bundling, consider adding:
- esbuild
- Vite
- Rollup

## Questions?

See `static/README.md` for detailed documentation on the static assets structure.
