#!/usr/bin/env bash
# generate-icon.sh
# Generates a macOS continuous-curvature squircle icon (.icns) with transparent outer corners.
# Compatible with macOS Big Sur, Monterey, Ventura, Sonoma, and Sequoia.

set -euo pipefail

function show_help {
  cat << 'HELP'
Usage:
  generate-icon.sh --svg <svg_file> --out <output_icns> [options]
  generate-icon.sh --path "<svg_path_d>" --viewbox "<w> <h>" --out <output_icns> [options]
  generate-icon.sh --png <png_file> --out <output_icns> [options]

Options:
  --theme <light|dark>    Background theme (default: light)
  --color <hex>           Symbol fill color (default: #202022 for light, #F5F5F7 for dark)
  --scale <float>         Symbol scaling factor (default: 1.0)
  --name <string>         Icon name for logs
  -h, --help              Show this help message

Examples:
  # From SVG path (e.g., Simple Icons, 24x24 viewBox):
  ./generate-icon.sh --path "M12 0C5.383 0..." --viewbox "24 24" --out ~/dotfiles/nix/icons/light/app.icns

  # From an SVG vector file:
  ./generate-icon.sh --svg ./logo.svg --out ~/dotfiles/nix/icons/light/app.icns
HELP
  exit 0
}

INPUT_SVG=""
INPUT_PATH=""
INPUT_VIEWBOX="24 24"
INPUT_PNG=""
OUTPUT_ICNS=""
THEME="light"
SYMBOL_COLOR=""
SCALE_FACTOR="1.0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --svg)
      INPUT_SVG="$2"; shift 2 ;;
    --path)
      INPUT_PATH="$2"; shift 2 ;;
    --viewbox)
      INPUT_VIEWBOX="$2"; shift 2 ;;
    --png)
      INPUT_PNG="$2"; shift 2 ;;
    --out)
      OUTPUT_ICNS="$2"; shift 2 ;;
    --theme)
      THEME="$2"; shift 2 ;;
    --color)
      SYMBOL_COLOR="$2"; shift 2 ;;
    --scale)
      SCALE_FACTOR="$2"; shift 2 ;;
    -h|--help)
      show_help ;;
    *)
      echo "Unknown option: $1" >&2
      show_help ;;
  esac
done

if [ -z "$OUTPUT_ICNS" ]; then
  echo "Error: --out <output_icns> is required." >&2
  exit 1
fi

if [ -z "$INPUT_SVG" ] && [ -z "$INPUT_PATH" ] && [ -z "$INPUT_PNG" ]; then
  echo "Error: You must provide one of --svg, --path, or --png." >&2
  exit 1
fi

# Set default colors based on theme
if [ -z "$SYMBOL_COLOR" ]; then
  if [ "$THEME" = "dark" ]; then
    SYMBOL_COLOR="#F5F5F7"
  else
    SYMBOL_COLOR="#202022"
  fi
fi

if [ "$THEME" = "dark" ]; then
  BG_TOP="#2A2B2E"
  BG_BOTTOM="#1C1D1F"
  BORDER_COLOR="#38393D"
else
  BG_TOP="#FFFFFF"
  BG_BOTTOM="#EBECEF"
  BORDER_COLOR="#D8D9DC"
fi

TEMP_DIR=$(mktemp -d "/tmp/icon_gen_XXXXXX")
trap 'rm -rf "$TEMP_DIR"' EXIT

# Prepare SVG content
COMPILED_SVG="$TEMP_DIR/composed.svg"

if [ -n "$INPUT_PATH" ]; then
  # Parse viewbox
  VB_W=$(echo "$INPUT_VIEWBOX" | awk '{print $1}')
  VB_H=$(echo "$INPUT_VIEWBOX" | awk '{print $2}')
  VB_CX=$(python3 -c "print($VB_W / 2.0)")
  VB_CY=$(python3 -c "print($VB_H / 2.0)")
  # Calculate scaling to fit within ~480px of 824px tile
  CALC_SCALE=$(python3 -c "print((480.0 / max($VB_W, $VB_H)) * float('$SCALE_FACTOR'))")

  cat << SVG_EOF > "$COMPILED_SVG"
<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="squircle-shadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#000000" flood-opacity="0.22"/>
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.12"/>
    </filter>
    <filter id="symbol-shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.18"/>
      <feDropShadow dx="0" dy="1.5" stdDeviation="2" flood-color="#000000" flood-opacity="0.12"/>
    </filter>
    <linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="$BG_TOP"/>
      <stop offset="100%" stop-color="$BG_BOTTOM"/>
    </linearGradient>
  </defs>

  <rect x="96" y="88" width="832" height="832" rx="185" fill="url(#bg-grad)" filter="url(#squircle-shadow)" stroke="$BORDER_COLOR" stroke-width="1.5"/>

  <g transform="translate(512, 504) scale($CALC_SCALE) translate(-$VB_CX, -$VB_CY)" filter="url(#symbol-shadow)">
    <path fill="$SYMBOL_COLOR" fill-rule="evenodd" d="$INPUT_PATH"/>
  </g>
</svg>
SVG_EOF

elif [ -n "$INPUT_SVG" ]; then
  # Wrap external SVG
  cat << SVG_EOF > "$COMPILED_SVG"
<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <filter id="squircle-shadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#000000" flood-opacity="0.22"/>
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.12"/>
    </filter>
    <linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="$BG_TOP"/>
      <stop offset="100%" stop-color="$BG_BOTTOM"/>
    </linearGradient>
  </defs>

  <rect x="96" y="88" width="832" height="832" rx="185" fill="url(#bg-grad)" filter="url(#squircle-shadow)" stroke="$BORDER_COLOR" stroke-width="1.5"/>

  <g transform="translate(262, 254) scale(0.5)">
    <image xlink:href="$INPUT_SVG" width="1000" height="1000"/>
  </g>
</svg>
SVG_EOF
fi

# Render with QuickLook to 1024x1024
qlmanage -t -s 1024 -o "$TEMP_DIR" "$COMPILED_SVG" >/dev/null 2>&1
RAW_RENDER="$TEMP_DIR/composed.svg.png"

# Mask outer corners to ensure 100% transparency
MASKED_PNG="$TEMP_DIR/masked.png"

cat << 'SWIFT_EOF' > "$TEMP_DIR/mask.swift"
import Cocoa

let srcURL = URL(fileURLWithPath: CommandLine.arguments[1])
let maskURL = URL(fileURLWithPath: CommandLine.arguments[2])
let outURL = URL(fileURLWithPath: CommandLine.arguments[3])

guard let rawImg = NSImage(contentsOf: srcURL) else { fatalError("Raw image load failed") }
var rect = CGRect(x: 0, y: 0, width: 1024, height: 1024)
let rawCG = rawImg.cgImage(forProposedRect: &rect, context: nil, hints: nil)!

let finalImg = NSImage(size: NSSize(width: 1024, height: 1024))
finalImg.lockFocus()

guard let ctx = NSGraphicsContext.current?.cgContext else { fatalError("No graphics context") }

// 1. Draw the composed icon (squircle + symbol + symbol shadow)
ctx.draw(rawCG, in: rect)

// 2. If a reference squircle mask exists (e.g. discord-light.icns), blend with destinationIn to get exact continuous squircle and transparent borders
if FileManager.default.fileExists(atPath: maskURL.path),
   let maskImg = NSImage(contentsOf: maskURL),
   let maskCG = maskImg.cgImage(forProposedRect: &rect, context: nil, hints: nil) {
    ctx.setBlendMode(.destinationIn)
    ctx.draw(maskCG, in: rect)
} else {
    // Fallback: NSBezierPath continuous squircle clip
    let clipPath = NSBezierPath(roundedRect: CGRect(x: 96, y: 88, width: 832, height: 832), xRadius: 185, yRadius: 185)
    ctx.setBlendMode(.destinationIn)
    clipPath.fill()
}

finalImg.unlockFocus()

var r = CGRect(origin: .zero, size: NSSize(width: 1024, height: 1024))
if let finalCG = finalImg.cgImage(forProposedRect: &r, context: nil, hints: nil) {
    let rep = NSBitmapImageRep(cgImage: finalCG)
    let data = rep.representation(using: .png, properties: [:])!
    try! data.write(to: outURL)
}
SWIFT_EOF

REF_MASK="$HOME/dotfiles/nix/icons/light/discord.icns"
swift "$TEMP_DIR/mask.swift" "$RAW_RENDER" "$REF_MASK" "$MASKED_PNG"

# Build iconset
ICONSET="$TEMP_DIR/App.iconset"
mkdir -p "$ICONSET"

sips -z 16 16     "$MASKED_PNG" --out "$ICONSET/icon_16x16.png" >/dev/null
sips -z 32 32     "$MASKED_PNG" --out "$ICONSET/icon_16x16@2x.png" >/dev/null
sips -z 32 32     "$MASKED_PNG" --out "$ICONSET/icon_32x32.png" >/dev/null
sips -z 64 64     "$MASKED_PNG" --out "$ICONSET/icon_32x32@2x.png" >/dev/null
sips -z 128 128   "$MASKED_PNG" --out "$ICONSET/icon_128x128.png" >/dev/null
sips -z 256 256   "$MASKED_PNG" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
sips -z 256 256   "$MASKED_PNG" --out "$ICONSET/icon_256x256.png" >/dev/null
sips -z 512 512   "$MASKED_PNG" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
sips -z 512 512   "$MASKED_PNG" --out "$ICONSET/icon_512x512.png" >/dev/null
sips -z 1024 1024 "$MASKED_PNG" --out "$ICONSET/icon_512x512@2x.png" >/dev/null

mkdir -p "$(dirname "$OUTPUT_ICNS")"
iconutil -c icns "$ICONSET" -o "$OUTPUT_ICNS"

echo "Generated icon successfully at '$OUTPUT_ICNS'."
