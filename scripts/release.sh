#!/bin/bash
# HymnFlow Release Script
# Builds three release artifacts and a git tag:
#   hymnflow-vX-lite.zip  — plugin + default KJV + default hymnal (nnbh)
#   hymnflow-vX-full.zip  — plugin + all Bibles + all hymn collections
#   hymnflow-vX-data.zip  — importable Bibles + hymn collections only (drop into data/)

set -e

# Get version from package.json
VERSION=$(grep '"version"' package.json | grep -o '"[^"]*"' | sed 's/"//g' | tail -1)
if [ -z "$VERSION" ]; then
    echo "Error: Could not read version from package.json"
    exit 1
fi

echo "🚀 Creating HymnFlow v$VERSION release (lite / full / data)..."

# Abort if there are uncommitted changes - tag must point to a clean commit
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: You have uncommitted changes. Commit everything before releasing."
    exit 1
fi

# ── Importable data sources ────────────────────────────────────────────────
# Bibles live in public/data (large files, git-ignored — generate or import).
# Hymn collections live in hymn-bundle/.
BIBLES="public/data/en_kjv.json public/data/en_bbe.json public/data/bible-yor.js"
HYMNS="hymn-bundle/cac_ghb.json hymn-bundle/cac_yhb.json hymn-bundle/fws.json \
       hymn-bundle/nnbh.json hymn-bundle/umh.json hymn-bundle/ybh.json hymn-bundle/metadata.json"

# Stage the shared plugin (code/UI + core data code) into $1
stage_plugin() {
    local d="$1"
    rm -rf "$d"; mkdir -p "$d/data" "$d/scripts"
    cp -r public/obs-dock    "$d/"
    cp -r public/obs-overlay "$d/"
    cp -r public/parsers     "$d/"
    cp -r public/i18n        "$d/"
    cp public/obs-setup.html "$d/"
    cp public/validation.js  "$d/"
    # Core data code (always required): lookup engine + default hymns
    cp public/data/bible-lookup.js "$d/data/"
    cp public/data/hymns-data.js   "$d/data/"
    # Scripts: OBS hotkey bridge + Bible converters
    cp scripts/hymnflow-obs-hotkeys.py "$d/scripts/"
    cp scripts/convert_bible_txt.py    "$d/scripts/"
    cp scripts/convert_yoruba_bible.py "$d/scripts/"
    # Documentation
    cp README.md "$d/"; cp doc/SETUP.md "$d/"
    cp doc/TROUBLESHOOTING.md "$d/"; cp doc/SECURITY.md "$d/"
    [ -f "doc/RELEASE_NOTES_v$VERSION.md" ] && cp "doc/RELEASE_NOTES_v$VERSION.md" "$d/" || true
}

make_zip() { # make_zip <dir> <zipfile>
    rm -f "$2"
    zip -r "$2" "$1" > /dev/null
    echo "   $(du -h "$2" | cut -f1)  $2"
}

echo "📦 Building lite bundle (KJV + nnbh)..."
LITE="hymnflow-v$VERSION-lite"
stage_plugin "$LITE"
cp public/data/en_kjv.json "$LITE/data/"
cp hymn-bundle/nnbh.json   "$LITE/data/"
make_zip "$LITE" "hymnflow-v$VERSION-lite.zip"

echo "📦 Building full bundle (all Bibles + all hymn collections)..."
FULL="hymnflow-v$VERSION-full"
stage_plugin "$FULL"
cp $BIBLES "$FULL/data/"
cp $HYMNS  "$FULL/data/"
make_zip "$FULL" "hymnflow-v$VERSION-full.zip"

echo "📦 Building data bundle (importable Bibles + hymn collections)..."
DATA="hymnflow-v$VERSION-data"
rm -rf "$DATA"; mkdir -p "$DATA/data"
cp $BIBLES "$DATA/data/"
cp $HYMNS  "$DATA/data/"
make_zip "$DATA" "hymnflow-v$VERSION-data.zip"

# Create git tag (skip if it already exists)
echo "🏷️  Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION - HymnFlow OBS Plugin" 2>/dev/null \
    || echo "   (tag v$VERSION already exists — left unchanged)"

echo ""
echo "✅ Release artifacts created for v$VERSION:"
echo "   hymnflow-v$VERSION-lite.zip   (plugin + KJV + nnbh)"
echo "   hymnflow-v$VERSION-full.zip   (plugin + all Bibles + all hymns)"
echo "   hymnflow-v$VERSION-data.zip   (importable Bibles + hymns)"
echo ""
echo "📤 Next steps:"
echo "   1. Review the ZIP contents"
echo "   2. Push tag: git push origin v$VERSION"
echo "   3. Create the GitHub release and attach all three ZIPs"
