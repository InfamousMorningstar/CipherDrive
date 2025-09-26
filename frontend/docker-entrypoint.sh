#!/bin/sh

# Docker entrypoint script for CipherDrive frontend
# Handles runtime environment variable injection for Vite builds

echo "Starting CipherDrive Frontend..."

# Create env.js with runtime environment variables
cat > /usr/share/nginx/html/env.js << EOF
window.env = {
  VITE_API_BASE_URL: "${VITE_API_BASE_URL:-/api}",
  VITE_APP_NAME: "${VITE_APP_NAME:-CipherDrive}",
  VITE_MAX_FILE_SIZE: "${VITE_MAX_FILE_SIZE:-104857600}",
  VITE_SUPPORTED_FORMATS: "${VITE_SUPPORTED_FORMATS:-jpg,jpeg,png,gif,bmp,webp,svg,pdf,txt,md,doc,docx,xls,xlsx,ppt,pptx,mp4,avi,mkv,mov,wmv,flv,webm,mp3,wav,flac,aac,ogg}",
  VITE_ENABLE_ANALYTICS: "${VITE_ENABLE_ANALYTICS:-false}",
  VITE_ENABLE_NOTIFICATIONS: "${VITE_ENABLE_NOTIFICATIONS:-true}"
};
EOF

# Update index.html to include env.js
if [ -f /usr/share/nginx/html/index.html ]; then
    # Add env.js script tag before closing head tag if not already present
    if ! grep -q "env.js" /usr/share/nginx/html/index.html; then
        sed -i 's|</head>|  <script src="/env.js"></script>\n  </head>|g' /usr/share/nginx/html/index.html
    fi
fi

echo "Environment configuration injected"
echo "API Base URL: ${VITE_API_BASE_URL:-/api}"
echo "App Name: ${VITE_APP_NAME:-CipherDrive}"

# Start nginx
echo "Starting nginx..."
exec "$@"