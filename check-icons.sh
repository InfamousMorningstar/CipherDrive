#!/bin/bash
# Icon compatibility check script

echo "🔍 Checking for potential Heroicons v2 compatibility issues..."

# Known problematic icons that don't exist in v2
PROBLEMATIC_ICONS=(
  "MusicIcon"
  "DownloadIcon" 
  "LogoutIcon"
  "CogIcon"
  "MenuIcon"
  "RefreshIcon"
  "SaveIcon"
  "EditIcon"
  "DeleteIcon"
  "SettingsIcon"
  "SearchIcon"
  "CloseIcon"
  "UploadIcon"
)

FOUND_ISSUES=0

for icon in "${PROBLEMATIC_ICONS[@]}"; do
  if grep -r "$icon" frontend/src/ --include="*.jsx" --include="*.js"; then
    echo "⚠️  Found potentially problematic icon: $icon"
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
  fi
done

if [ $FOUND_ISSUES -eq 0 ]; then
  echo "✅ No problematic icon imports found!"
  echo "🚀 Frontend should build successfully now."
else
  echo "❌ Found $FOUND_ISSUES potential icon issues that need fixing."
fi