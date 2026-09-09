#!/usr/bin/python3
"""
icon_tool.py - macOS Custom Application Icon Generator & Manager

Generates Apple continuous-curvature squircle icons (.icns) with transparent
corners, custom background gradients/colors, customizable symbol colors,
drop shadow toggles, and one-step application to macOS .app bundles.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import urllib.error

# Standard Apple Big Sur/Sonoma icon grid dimensions
CANVAS_SIZE = 1024
TILE_SIZE = 832
TILE_X = 96
TILE_Y = 88
CORNER_RADIUS = 185
DEFAULT_SYMBOL_SIZE = 480.0

THEME_PRESETS = {
    "light": {
        "bg_top": "#FFFFFF",
        "bg_bottom": "#EBECEF",
        "border": "#D8D9DC",
        "symbol": "#202022",
    },
    "dark": {
        "bg_top": "#2C2D31",
        "bg_bottom": "#1C1D20",
        "border": "#3A3B40",
        "symbol": "#F5F5F7",
    },
    "white": {
        "bg_top": "#FFFFFF",
        "bg_bottom": "#FFFFFF",
        "border": "#E5E5EA",
        "symbol": "#1C1C1E",
    },
    "black": {
        "bg_top": "#161618",
        "bg_bottom": "#0D0D0E",
        "border": "#28282C",
        "symbol": "#FFFFFF",
    },
    "slate": {
        "bg_top": "#F1F5F9",
        "bg_bottom": "#E2E8F0",
        "border": "#CBD5E1",
        "symbol": "#0F172A",
    },
}

COLOR_SHORTCUTS = {
    "white": ("#FFFFFF", "#EBECEF"),
    "pure-white": ("#FFFFFF", "#FFFFFF"),
    "light": ("#FFFFFF", "#EBECEF"),
    "dark": ("#2C2D31", "#1C1D20"),
    "black": ("#161618", "#0D0D0E"),
    "slate": ("#F1F5F9", "#E2E8F0"),
    "gray": ("#F2F2F7", "#E5E5EA"),
}

SYMBOL_SHORTCUTS = {
    "black": "#202022",
    "dark": "#202022",
    "charcoal": "#202022",
    "white": "#FFFFFF",
    "light": "#FFFFFF",
    "blue": "#007AFF",
    "gray": "#8E8E93",
    "red": "#FF3B30",
    "green": "#34C759",
    "purple": "#AF52DE",
}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate and apply custom macOS squircle icons (.icns) with full styling controls."
    )
    # Source options
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--query", "-q",
        help="Search term or link from Simple Icons (e.g. 'slack', 'https://simpleicons.org/?q=warp', or direct SVG link)"
    )
    source_group.add_argument(
        "--svg", "-s",
        help="Path to a local SVG file"
    )
    source_group.add_argument(
        "--path", "-p",
        help="Direct SVG path string d='...'"
    )
    source_group.add_argument(
        "--letter", "-l",
        help="Generate an Apple-style typography lettermark monogram (e.g. 'S', 'G', 'AI')"
    )

    parser.add_argument(
        "--fallback-letter",
        action="store_true",
        help="If --query is not found online, automatically fall back to an Apple lettermark monogram"
    )

    # Style options
    parser.add_argument(
        "--theme", "-t",
        choices=list(THEME_PRESETS.keys()),
        default="light",
        help="Base theme preset (default: light)"
    )
    parser.add_argument(
        "--bg", "-b",
        help="Background color/gradient: 'white', 'dark', '#FFFFFF', or gradient '#FFFFFF,#EBECEF' (default: theme default)"
    )
    parser.add_argument(
        "--color", "-c",
        help="Symbol color: 'black', 'white', hex '#202022', etc. (default: theme default)"
    )
    parser.add_argument(
        "--border-color",
        help="Custom tile border color (hex)"
    )
    parser.add_argument(
        "--shadow",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable or disable drop shadow on the symbol (default: --shadow, use --no-shadow for flat)"
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.25,
        help="Scale multiplier for the symbol (default: 1.25, ideal for macOS Dock)"
    )
    parser.add_argument(
        "--viewbox", "-v",
        default="0 0 24 24",
        help="SVG viewBox when using --path (default: '0 0 24 24')"
    )

    # Output & Action options
    parser.add_argument(
        "--out", "-o",
        help="Destination path for .icns (optional: auto-generated based on app name or query)"
    )
    parser.add_argument(
        "--preview",
        nargs="?",
        const=True,
        default=None,
        help="Generate a 1024x1024 PNG preview (optional custom path, or auto /tmp/<name>-preview.png)"
    )
    parser.add_argument(
        "--apply", "-a",
        help="Target .app bundle path to immediately apply the icon to"
    )
    parser.add_argument(
        "--no-dock-restart",
        action="store_true",
        help="Do not restart the Dock after applying the icon"
    )

    return parser.parse_args()

def extract_path_from_svg(svg_content):
    vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', svg_content)
    if vb_match:
        viewbox = vb_match.group(1)
    else:
        w_match = re.search(r'<svg[^>]*\bwidth=["\']([0-9.]+)["\']', svg_content)
        h_match = re.search(r'<svg[^>]*\bheight=["\']([0-9.]+)["\']', svg_content)
        if w_match and h_match:
            viewbox = f"0 0 {w_match.group(1)} {h_match.group(1)}"
        else:
            viewbox = "0 0 24 24"

    fr_match = re.search(r'\bfill-rule=["\']([^"\']+)["\']', svg_content)
    fill_rule = fr_match.group(1) if fr_match else "evenodd"

    paths = re.findall(r'<path[^>]*\bd=["\']([^"\']+)["\']', svg_content)
    if not paths:
        sys.exit("Error: No <path d=\"...\"> found in the SVG.")
    return " ".join(paths), viewbox, fill_rule

def fetch_icon_or_create(query, fallback_letter=False):
    query_str = query.strip()

    # Check if user provided a URL
    if query_str.startswith("http://") or query_str.startswith("https://"):
        parsed = urllib.parse.urlparse(query_str)
        qs = urllib.parse.parse_qs(parsed.query)

        # Handle search link e.g. https://simpleicons.org/?q=warp
        if "q" in qs and qs["q"]:
            query_str = qs["q"][0]
        elif parsed.path.endswith(".svg") or "cdn.simpleicons.org" in parsed.netloc or "jsdelivr.net" in parsed.netloc:
            # Direct SVG link
            try:
                req = urllib.request.Request(query_str, headers={"User-Agent": "macOS-Custom-Icons-Tool"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    print(f"Fetched SVG from URL: {query_str}")
                    content = resp.read().decode("utf-8")
                    path_d, viewbox, fill_rule = extract_path_from_svg(content)
                    stem = os.path.splitext(os.path.basename(parsed.path))[0] or "custom"
                    return {"type": "path", "path_d": path_d, "viewbox": viewbox, "fill_rule": fill_rule, "name": stem}
            except Exception as e:
                sys.exit(f"Error fetching SVG from URL '{query_str}': {e}")
        else:
            # URL like https://simpleicons.org/icons/slack -> slack
            path_parts = [p for p in parsed.path.split("/") if p and p != "icons"]
            if path_parts:
                query_str = path_parts[-1].replace(".svg", "")

    COMMON_ALIASES = {
        "zed": "zedindustries",
        "gemini": "googlegemini",
        "vscode": "visualstudiocode",
        "sublime": "sublimetext",
    }

    slug = query_str.lower().strip().replace(" ", "").replace("-", "").replace("_", "")
    candidate_slugs = [slug]
    if slug in COMMON_ALIASES and COMMON_ALIASES[slug] not in candidate_slugs:
        candidate_slugs.append(COMMON_ALIASES[slug])
    for s in [f"{slug}industries", f"{slug}editor", f"{slug}app"]:
        if s not in candidate_slugs:
            candidate_slugs.append(s)

    for cand in candidate_slugs:
        sources = [
            ("Simple Icons", f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{cand}.svg"),
            ("Dashboard Icons", f"https://raw.githubusercontent.com/homarr-labs/dashboard-icons/main/svg/{cand}.svg"),
        ]
        for source_name, url in sources:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "macOS-Custom-Icons-Tool"})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    print(f"Found icon on {source_name}: {url}")
                    content = resp.read().decode("utf-8")
                    path_d, viewbox, fill_rule = extract_path_from_svg(content)
                    return {"type": "path", "path_d": path_d, "viewbox": viewbox, "fill_rule": fill_rule, "name": slug}
            except (urllib.error.HTTPError, urllib.error.URLError):
                continue

    if fallback_letter:
        letter = query_str[:2].upper() if len(query_str) <= 2 else query_str[0].upper()
        print(f"Icon '{query_str}' not found online. Generating Apple-style lettermark '{letter}'...")
        return {"type": "letter", "letter": letter, "name": f"letter-{letter.lower()}"}

    sys.exit(
        f"Error: Could not find icon '{query_str}' on Simple Icons or Dashboard Icons.\n\n"
        f"Recommended solutions:\n"
        f"  1. Check https://simpleicons.org for the exact slug (e.g. 'googlegemini' instead of 'gemini').\n"
        f"  2. Provide the direct simpleicons link (e.g. https://simpleicons.org/?q={query_str}).\n"
        f"  3. Use --fallback-letter to auto-create a clean Apple lettermark icon.\n"
        f"  4. Provide a local vector file with --svg <path>."
    )

def is_color_dark(hex_color):
    """Returns True if the hex color has a dark perceived luminance."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return False
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 100
    except ValueError:
        return False

def compute_styling(args):
    # Detect if a dark theme was requested or implied
    preset = THEME_PRESETS[args.theme]
    bg_top = preset["bg_top"]
    bg_bottom = preset["bg_bottom"]
    border = preset["border"]
    symbol_color = preset["symbol"]

    if args.bg:
        raw_bg = args.bg.strip()
        lowered = raw_bg.lower()
        if lowered in COLOR_SHORTCUTS:
            bg_top, bg_bottom = COLOR_SHORTCUTS[lowered]
        else:
            parts = [p.strip() for p in raw_bg.split(",")]
            if len(parts) == 1:
                bg_top = parts[0]
                bg_bottom = parts[0]
            elif len(parts) >= 2:
                bg_top = parts[0]
                bg_bottom = parts[1]

    if args.border_color:
        border = args.border_color
    else:
        # Determine border based on background luminance
        if is_color_dark(bg_top) or is_color_dark(bg_bottom):
            if bg_top.lower() in ("#161618", "#000000", "#0d0d0e") or args.theme == "black":
                border = "#28282C"
            else:
                border = "#3A3B40"
        elif args.bg and bg_top == bg_bottom:
            border = bg_top

    if args.color:
        raw_color = args.color.strip()
        lowered = raw_color.lower()
        if lowered in SYMBOL_SHORTCUTS:
            symbol_color = SYMBOL_SHORTCUTS[lowered]
        else:
            symbol_color = raw_color

    return bg_top, bg_bottom, border, symbol_color

def build_svg(path_d, viewbox, bg_top, bg_bottom, border, symbol_color, scale, fill_rule="evenodd", shadow=True):
    vb_parts = [float(x) for x in viewbox.replace(",", " ").split() if x]
    if len(vb_parts) == 4:
        min_x, min_y, vb_w, vb_h = vb_parts
    elif len(vb_parts) == 2:
        min_x, min_y, vb_w, vb_h = 0.0, 0.0, vb_parts[0], vb_parts[1]
    else:
        min_x, min_y, vb_w, vb_h = 0.0, 0.0, 24.0, 24.0

    center_x = min_x + (vb_w / 2.0)
    center_y = min_y + (vb_h / 2.0)
    max_dim = max(vb_w, vb_h)
    calc_scale = (DEFAULT_SYMBOL_SIZE / max_dim) * scale

    filter_attr = ' filter="url(#symbol-shadow)"' if shadow else ""

    svg = f"""<svg width="{CANVAS_SIZE}" height="{CANVAS_SIZE}" viewBox="0 0 {CANVAS_SIZE} {CANVAS_SIZE}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="symbol-shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.18"/>
      <feDropShadow dx="0" dy="1.5" stdDeviation="2" flood-color="#000000" flood-opacity="0.12"/>
    </filter>
    <linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{bg_top}"/>
      <stop offset="100%" stop-color="{bg_bottom}"/>
    </linearGradient>
  </defs>

  <!-- Base Squircle -->
  <rect x="{TILE_X}" y="{TILE_Y}" width="{TILE_SIZE}" height="{TILE_SIZE}" rx="{CORNER_RADIUS}" fill="url(#bg-grad)" stroke="{border}" stroke-width="1.5"/>

  <!-- Centered Symbol -->
  <g transform="translate(512, 504) scale({calc_scale}) translate({-center_x}, {-center_y})"{filter_attr}>
    <path fill="{symbol_color}" fill-rule="{fill_rule}" d="{path_d}"/>
  </g>
</svg>"""
    return svg

def build_letter_svg(letter, bg_top, bg_bottom, border, symbol_color, scale, shadow=True):
    font_size = int(400 * scale) if len(letter) == 1 else int(280 * scale)
    y_pos = 635 if len(letter) == 1 else 600
    filter_attr = ' filter="url(#symbol-shadow)"' if shadow else ""

    svg = f"""<svg width="{CANVAS_SIZE}" height="{CANVAS_SIZE}" viewBox="0 0 {CANVAS_SIZE} {CANVAS_SIZE}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="symbol-shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.18"/>
      <feDropShadow dx="0" dy="1.5" stdDeviation="2" flood-color="#000000" flood-opacity="0.12"/>
    </filter>
    <linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{bg_top}"/>
      <stop offset="100%" stop-color="{bg_bottom}"/>
    </linearGradient>
  </defs>

  <!-- Base Squircle -->
  <rect x="{TILE_X}" y="{TILE_Y}" width="{TILE_SIZE}" height="{TILE_SIZE}" rx="{CORNER_RADIUS}" fill="url(#bg-grad)" stroke="{border}" stroke-width="1.5"/>

  <!-- Centered Lettermark -->
  <text x="512" y="{y_pos}" font-family="-apple-system, 'SF Pro Display', system-ui, sans-serif" font-size="{font_size}" font-weight="800" text-anchor="middle" fill="{symbol_color}"{filter_attr}>{letter}</text>
</svg>"""
    return svg

def render_and_mask(svg_path, temp_dir, mask_ref_path, shadow=True, is_dark=False):
    subprocess.run(["qlmanage", "-t", "-s", "1024", "-o", temp_dir, svg_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rendered_png = os.path.join(temp_dir, f"{os.path.basename(svg_path)}.png")
    masked_png = os.path.join(temp_dir, "masked.png")

    swift_script = os.path.join(temp_dir, "mask.swift")
    with open(swift_script, "w") as f:
        f.write("""import Cocoa

let srcURL = URL(fileURLWithPath: CommandLine.arguments[1])
let maskURL = URL(fileURLWithPath: CommandLine.arguments[2])
let outURL = URL(fileURLWithPath: CommandLine.arguments[3])
let hasShadow = (CommandLine.arguments.count > 4 && CommandLine.arguments[4] == "1")

guard let rawImg = NSImage(contentsOf: srcURL) else { fatalError("Raw image load failed") }

let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: 1024,
    pixelsHigh: 1024,
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: NSColorSpaceName.deviceRGB,
    bytesPerRow: 0,
    bitsPerPixel: 0
)!

let gCtx = NSGraphicsContext(bitmapImageRep: rep)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = gCtx
let ctx = gCtx.cgContext
ctx.clear(CGRect(x: 0, y: 0, width: 1024, height: 1024))

// In standard Cocoa coordinates (origin at bottom-left):
// The squircle top margin in SVG is 88px, height is 832px.
// Thus in Cocoa coordinates: y = 1024 - 88 - 832 = 104.
let squircleRect = CGRect(x: 96, y: 104, width: 832, height: 832)

if hasShadow {
    ctx.saveGState()
    ctx.setShadow(offset: CGSize(width: 0, height: -16), blur: 18, color: CGColor(red: 0, green: 0, blue: 0, alpha: 0.24))
    let shadowPath = CGPath(roundedRect: squircleRect, cornerWidth: 185, cornerHeight: 185, transform: nil)
    ctx.addPath(shadowPath)
    ctx.fillPath()
    ctx.restoreGState()
}

// Clip strictly to squircle to eliminate any QuickLook white background
ctx.saveGState()
let clipPath = CGPath(roundedRect: squircleRect, cornerWidth: 185, cornerHeight: 185, transform: nil)
ctx.addPath(clipPath)
ctx.clip()

rawImg.draw(in: NSRect(x: 0, y: 0, width: 1024, height: 1024))
ctx.restoreGState()

NSGraphicsContext.restoreGraphicsState()

let data = rep.representation(using: NSBitmapImageRep.FileType.png, properties: [:])!
try! data.write(to: outURL)
""")
    shadow_arg = "1" if shadow else "0"
    subprocess.run(["swift", swift_script, rendered_png, mask_ref_path, masked_png, shadow_arg], check=True)
    return masked_png

def compile_icns(masked_png, out_icns, temp_dir):
    iconset_dir = os.path.join(temp_dir, "App.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    for sz, filename in sizes:
        dest = os.path.join(iconset_dir, filename)
        subprocess.run(["sips", "-z", str(sz), str(sz), masked_png, "--out", dest], check=True, stdout=subprocess.DEVNULL)

    out_dir = os.path.dirname(os.path.abspath(out_icns))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", out_icns], check=True)
    print(f"Compiled ICNS: {out_icns}")

def apply_icon_to_app(app_path, icns_path, restart_dock=True):
    app_path = os.path.abspath(os.path.expanduser(app_path))
    icns_path = os.path.abspath(os.path.expanduser(icns_path))

    if not os.path.exists(app_path):
        sys.exit(f"Error: Target app '{app_path}' does not exist.")

    print(f"Applying icon to '{app_path}'...")
    applescript = f"""
use framework "Cocoa"
set iconPath to "{icns_path}"
set destPath to "{app_path}"
set imageData to (current application's NSImage's alloc()'s initWithContentsOfFile:iconPath)
return (current application's NSWorkspace's sharedWorkspace()'s setIcon:imageData forFile:destPath options:2)
"""
    result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True, check=True)
    if "true" in result.stdout:
        subprocess.run(["touch", app_path], check=False)
        print(f"Successfully applied icon to {app_path}.")
        if restart_dock:
            subprocess.run(["killall", "Dock"], check=False)
            print("Restarted Dock.")
    else:
        print(f"\nWarning: Could not set icon directly. If {app_path} is owned by root, run with sudo or run 'darwin-rebuild switch'.", file=sys.stderr)

def main():
    args = parse_args()

    # Determine input type & data
    if args.query:
        icon_info = fetch_icon_or_create(args.query, fallback_letter=args.fallback_letter)
        base_name = icon_info.get("name") or "custom"
    elif args.letter:
        icon_info = {"type": "letter", "letter": args.letter}
        base_name = f"letter-{args.letter.lower()}"
    elif args.svg:
        with open(args.svg, "r") as f:
            svg_content = f.read()
        path_d, viewbox, fill_rule = extract_path_from_svg(svg_content)
        icon_info = {"type": "path", "path_d": path_d, "viewbox": viewbox, "fill_rule": fill_rule}
        base_name = os.path.splitext(os.path.basename(args.svg))[0].lower()
    else:
        icon_info = {"type": "path", "path_d": args.path, "viewbox": args.viewbox, "fill_rule": "evenodd"}
        base_name = "custom"

    # Automatically derive output ICNS path if omitted
    if not args.out:
        if args.apply:
            app_stem = os.path.splitext(os.path.basename(args.apply))[0].lower().replace(" ", "-")
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
            nix_icons_dir = os.path.join(repo_root, "nix/icons/light")
            if os.path.isdir(nix_icons_dir):
                args.out = os.path.join(nix_icons_dir, f"{app_stem}.icns")
            else:
                args.out = f"/tmp/{app_stem}.icns"
        else:
            args.out = f"/tmp/{base_name}.icns"

    # Handle preview path if --preview was passed as flag or path
    preview_path = None
    if args.preview is True:
        preview_path = f"/tmp/{base_name}-preview.png"
    elif isinstance(args.preview, str):
        preview_path = os.path.abspath(os.path.expanduser(args.preview))

    # Determine colors
    bg_top, bg_bottom, border, symbol_color = compute_styling(args)

    temp_dir = tempfile.mkdtemp(prefix="mac_icon_")
    try:
        if icon_info["type"] == "letter":
            svg_markup = build_letter_svg(
                icon_info["letter"],
                bg_top,
                bg_bottom,
                border,
                symbol_color,
                args.scale,
                shadow=args.shadow
            )
        else:
            svg_markup = build_svg(
                icon_info["path_d"],
                icon_info["viewbox"],
                bg_top,
                bg_bottom,
                border,
                symbol_color,
                args.scale,
                icon_info.get("fill_rule", "evenodd"),
                shadow=args.shadow
            )

        svg_file = os.path.join(temp_dir, "composed.svg")
        with open(svg_file, "w") as f:
            f.write(svg_markup)

        # Locate reference squircle mask: local dotfiles icon -> system generic icon
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        ref_mask = os.path.join(repo_root, "nix/icons/light/discord.icns")
        if not os.path.exists(ref_mask):
            ref_mask = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns"

        is_dark_bg = is_color_dark(bg_top) or is_color_dark(bg_bottom)
        masked_png = render_and_mask(svg_file, temp_dir, ref_mask, shadow=args.shadow, is_dark=is_dark_bg)

        # Optional preview save
        if preview_path:
            shutil.copy(masked_png, preview_path)
            print(f"Saved PNG preview: {preview_path}")

        # Compile ICNS
        out_icns = os.path.abspath(os.path.expanduser(args.out))
        compile_icns(masked_png, out_icns, temp_dir)

        # Optional application
        if args.apply:
            apply_icon_to_app(args.apply, out_icns, restart_dock=not args.no_dock_restart)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
