#!/usr/bin/python3
"""
icon_tool.py - macOS Custom Application Icon Generator & Manager

Generates Apple continuous-curvature squircle icons (.icns) with transparent
corners, custom background gradients/colors, customizable symbol colors,
drop shadow toggles, and one-step application to macOS .app bundles.
"""

import argparse
import json
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
        "bg_top": "#161618",
        "bg_bottom": "#0D0D0E",
        "border": "#28282C",
        "symbol": "#FFFFFF",
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
    "nord": {
        "bg_top": "#2E3440",
        "bg_bottom": "#242933",
        "border": "#3B4252",
        "symbol": "#ECEFF4",
    },
    "catppuccin": {
        "bg_top": "#1E1E2E",
        "bg_bottom": "#181825",
        "border": "#313244",
        "symbol": "#CDD6F4",
    },
    "dracula": {
        "bg_top": "#282A36",
        "bg_bottom": "#1E1F29",
        "border": "#44475A",
        "symbol": "#F8F8F2",
    },
    "rose-pine": {
        "bg_top": "#191724",
        "bg_bottom": "#12101B",
        "border": "#26233A",
        "symbol": "#E0DEF4",
    },
    "solarized-dark": {
        "bg_top": "#073642",
        "bg_bottom": "#002B36",
        "border": "#586E75",
        "symbol": "#FDF6E3",
    },
    "solarized-light": {
        "bg_top": "#FDF6E3",
        "bg_bottom": "#EEE8D5",
        "border": "#93A1A1",
        "symbol": "#657B83",
    },
    "apple": {
        "bg_top": "#FFFFFF",
        "bg_bottom": "#EBECEF",
        "border": "#D8D9DC",
        "symbol": "#00C8FF,#0072FE",
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
    "nord": ("#2E3440", "#242933"),
    "catppuccin": ("#1E1E2E", "#181825"),
    "dracula": ("#282A36", "#1E1F29"),
    "rose-pine": ("#191724", "#12101B"),
}

SYMBOL_SHORTCUTS = {
    "black": "#202022",
    "dark": "#202022",
    "charcoal": "#202022",
    "white": "#FFFFFF",
    "light": "#FFFFFF",
    "blue": "#007AFF",
    "blue-light": "#0097FF",
    "finder": "#00C8FF,#0072FE",
    "apple": "#00C8FF,#0072FE",
    "gray": "#8E8E93",
    "red": "#FF3B30",
    "green": "#34C759",
    "purple": "#AF52DE",
    "cyan": "#00FFFF",
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
    source_group.add_argument(
        "--create-theme",
        metavar="THEME_NAME",
        help="Batch generate all existing icons into a new theme folder under nix/icons/<THEME_NAME>"
    )
    source_group.add_argument(
        "--sync-themes",
        action="store_true",
        help="Sync and regenerate all themes registered in nix/icons/themes.json"
    )

    parser.add_argument(
        "--fallback-letter",
        action="store_true",
        help="If --query is not found online, automatically fall back to an Apple lettermark monogram"
    )
    parser.add_argument(
        "--all-themes",
        action="store_true",
        help="When generating a single icon (--query, --svg, etc.), generate it for all registered themes in nix/icons/themes.json"
    )
    parser.add_argument(
        "--from-theme",
        default="light",
        help="Reference theme to discover icons from when using --create-theme (default: 'light')"
    )
    parser.add_argument(
        "--icons-dir",
        help="Base directory containing theme folders (default: auto-detected 'nix/icons')"
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

    KNOWN_ICONS = {
        "spark": {
            "path_d": "M126.861 28.8864L113.276 0.768583C113.051 0.295136 112.576 0 112.058 0C111.541 0 111.066 0.301284 110.834 0.768583L97.2555 28.8864C97.0059 29.4029 97.1033 30.0178 97.493 30.4359C97.8827 30.8478 98.4916 30.9769 99.0153 30.7494L107.948 26.8758C107.997 26.8512 108.052 26.8451 108.113 26.8451C108.283 26.8451 108.429 26.9496 108.49 27.0971L110.804 32.8892C111.011 33.4057 111.51 33.75 112.064 33.75H112.071C112.625 33.75 113.124 33.4057 113.331 32.883L115.59 27.0971C115.651 26.9557 115.797 26.8512 115.962 26.8512C116.01 26.8512 116.059 26.8573 116.102 26.8758L125.114 30.7617C125.637 30.9892 126.24 30.8601 126.63 30.4482C127.02 30.0362 127.111 29.4029 126.861 28.8864ZM111.726 2.33349L111.148 26.1435C111.136 26.6559 111.546 27.078 112.057 27.078C112.569 27.078 112.98 26.6526 112.965 26.1382L112.248 2.33195C112.244 2.19047 112.128 2.078 111.987 2.078C111.846 2.078 111.73 2.19139 111.726 2.33349Z",
            "viewbox": "97 0 30 34",
            "fill_rule": "evenodd",
            "name": "spark",
        },
        "notioncalendar": {
            "path_d": "M128.454 357.071C122.803 357.008 117.782 355.562 113.881 351.924C113.881 351.924 113.868 351.924 113.856 351.899C113.403 351.458 112.975 351.006 112.572 350.552C109.489 347.028 107.815 342.51 107.815 337.627L107.777 136.484C107.777 124.843 117.593 114.397 129.209 113.679L330.12 101.245C330.561 101.22 330.988 101.207 331.429 101.207C336.45 101.207 341.132 103.019 344.706 106.392C345.196 106.858 345.662 107.336 346.09 107.84C346.837 108.692 347.5 109.602 348.08 110.564C347.501 109.609 346.834 108.702 346.09 107.852C349.098 111.351 350.746 115.806 350.746 120.639V125.787C350.746 125.787 350.872 130.003 346.694 130.28L346.719 130.305L161.928 141.884C148.375 142.727 137.364 154.469 137.364 168.049C137.364 168.049 137.288 353.699 137.275 354C137.137 357.071 134.607 357.071 132.518 357.071H128.454Z M394.126 373.546C394.151 373.244 394.176 372.941 394.176 372.639L394.126 155.274C394.05 154.129 393.861 153.009 393.546 151.939C392.817 149.434 391.457 147.182 389.532 145.382C386.776 142.802 383.177 141.405 379.313 141.405C378.974 141.405 378.633 141.417 378.294 141.443L163.854 154.884C163.779 154.889 163.703 154.902 163.628 154.914C163.527 154.93 163.426 154.947 163.326 154.947C156.505 155.652 150.792 161.617 150.326 168.451C150.301 168.753 150.301 169.043 150.301 169.345V382.318C150.301 382.42 150.307 382.519 150.314 382.616C150.32 382.711 150.326 382.804 150.326 382.896C150.464 387.667 152.365 392.021 155.75 395.205C158.77 398.049 162.646 399.66 166.837 399.875H167.504L381.83 386.899C381.893 386.899 381.956 386.889 382.019 386.88C382.065 386.873 382.111 386.866 382.158 386.862C382.174 386.862 382.191 386.861 382.208 386.861C388.538 385.691 393.684 380.002 394.126 373.546ZM183.927 376.339C176.59 376.855 170.096 374.364 170.297 364.748V215.08C170.297 209.946 174.526 206.661 179.194 206.421L365.747 195.233C370.404 194.994 374.216 198.367 374.216 203.036V352.968C374.216 358.455 372.845 365.516 363.406 365.881H363.381L363.368 365.893L183.927 376.339Z M227.066 252.787C218.406 253.322 215.462 259.932 215.474 270.09V271.876C214.441 272.119 213.576 272.349 212.53 272.41C206.291 272.799 201.79 267.733 201.778 258.644C201.766 244.744 214.221 231.658 237.952 230.188C259.081 228.875 272.606 239.082 272.631 257.089C272.643 270.636 261.392 280.247 250.311 283.26C271.098 284.282 279.771 295.873 279.795 310.66C279.819 335.97 261.307 350.319 232.722 352.106L232.029 352.154C210.547 353.491 195.465 345.338 195.453 331.255C195.453 323.236 201.327 316.444 210.159 315.897C210.852 315.849 211.545 315.994 212.238 315.946C213.99 330.283 223.697 335.557 233.391 334.961C242.745 334.378 249.325 328.084 249.313 319.165V318.813C249.301 304.901 237.685 304.209 220.193 303.516L217.408 286.93C233.683 283.954 241.82 278.631 241.808 269.008C241.808 258.668 236.067 252.253 227.066 252.811V252.787Z M305.181 245.959C287.859 250.965 284.041 243.358 285.938 235.388C296.325 232.958 323.341 224.854 333.558 221.196L333.68 327.987L352.57 330.732C352.57 337.683 348.605 342.032 341.501 342.482C335.614 342.846 321.93 343.345 315.349 343.758C305.132 344.39 286.424 345.921 286.424 345.921C285.901 344.524 285.731 343.114 285.731 341.862C285.731 338.472 287.105 334.998 291.606 333.478L305.29 329.056L305.193 245.971L305.181 245.959Z",
            "viewbox": "94.5 88 312.85 325",
            "fill_rule": "evenodd",
            "name": "notion-calendar",
        },
        "systemsettings": {
            "path_d": "M91.6504-32.1289L95.0195-32.1289C96.1914-32.1289 97.1191-32.8613 97.4121-34.082L98.3398-37.9395C98.877-38.0859 99.5117-38.3301 100.049-38.5742L103.418-36.5723C104.443-35.9375 105.566-35.9375 106.445-36.8652L108.74-39.1602C109.57-40.0391 109.668-41.1621 108.984-42.2852L106.982-45.6543C107.324-46.1914 107.471-46.6797 107.666-47.2168L111.523-48.1445C112.744-48.3887 113.525-49.3164 113.525-50.5371L113.525-53.8574C113.525-55.0293 112.695-55.9082 111.523-56.2012L107.715-57.1289C107.471-57.8125 107.227-58.252 107.031-58.6914L109.131-62.1582C109.766-63.1836 109.668-64.4531 108.838-65.2344L106.445-67.5293C105.615-68.3594 104.443-68.5547 103.467-67.9688L100.049-65.8203C99.4141-66.1621 98.877-66.3086 98.3398-66.5039L97.4121-70.3613C97.1191-71.5332 96.1914-72.3145 95.0195-72.3145L91.6504-72.3145C90.4297-72.3145 89.4531-71.4844 89.209-70.3613L88.3301-66.5527C87.6465-66.3086 87.1094-66.1621 86.5723-65.8203L83.2031-67.9688C82.2754-68.5059 81.0547-68.3594 80.1758-67.5293L77.8809-65.2344C77.0996-64.4043 76.8066-63.1836 77.4414-62.1582L79.5898-58.6914C79.3945-58.252 79.1504-57.7148 78.9062-57.1289L75.1465-56.2012C73.9746-55.9082 73.1934-54.9805 73.1934-53.8574L73.1934-50.5371C73.1934-49.3164 73.9746-48.3887 75.1465-48.1445L78.9551-47.2168C79.1992-46.6797 79.3945-46.1914 79.6387-45.6543L77.6367-42.2363C77.002-41.1621 77.0996-39.9902 77.9297-39.1602L80.1758-36.8652C81.0547-35.9375 82.2266-35.9375 83.252-36.5723L86.6699-38.5742C87.2559-38.2812 87.793-38.0859 88.3301-37.9395L89.209-34.082C89.4531-32.9102 90.4297-32.1289 91.6504-32.1289ZM93.3594-45.752C89.6973-45.752 86.8652-48.584 86.8652-52.1973C86.8652-55.7617 89.6973-58.6426 93.3594-58.6914C96.8262-58.7402 99.8047-55.7617 99.8047-52.1973C99.8047-48.584 96.8262-45.752 93.3594-45.752Z",
            "viewbox": "73.19 -72.31 40.33 40.19",
            "fill_rule": "evenodd",
            "name": "systemsettings",
        },
    }

    COMMON_ALIASES = {
        "zed": "zedindustries",
        "gemini": "googlegemini",
        "vscode": "visualstudiocode",
        "sublime": "sublimetext",
        "notioncalendar": "notion-calendar",
        "notion-calendar": "notion-calendar",
        "cron": "notion-calendar",
        "settings": "systemsettings",
        "system-settings": "systemsettings",
        "systemsettings": "systemsettings",
        "systempreferences": "systemsettings",
        "system-preferences": "systemsettings",
        "preferences": "systemsettings",
    }

    slug = query_str.lower().strip().replace(" ", "").replace("-", "").replace("_", "")
    slug_hyphen = query_str.lower().strip().replace(" ", "-").replace("_", "-")

    if slug in COMMON_ALIASES and COMMON_ALIASES[slug] in KNOWN_ICONS:
        slug = COMMON_ALIASES[slug]
    elif slug_hyphen in COMMON_ALIASES and COMMON_ALIASES[slug_hyphen] in KNOWN_ICONS:
        slug = COMMON_ALIASES[slug_hyphen]

    if slug in KNOWN_ICONS:
        info = dict(KNOWN_ICONS[slug])
        info["type"] = "path"
        return info

    candidate_slugs = [slug]
    if slug_hyphen not in candidate_slugs:
        candidate_slugs.append(slug_hyphen)
    if slug in COMMON_ALIASES and COMMON_ALIASES[slug] not in candidate_slugs:
        candidate_slugs.append(COMMON_ALIASES[slug])
    if slug_hyphen in COMMON_ALIASES and COMMON_ALIASES[slug_hyphen] not in candidate_slugs:
        candidate_slugs.append(COMMON_ALIASES[slug_hyphen])
    for s in [f"{slug}industries", f"{slug}editor", f"{slug}app", f"{slug_hyphen}-app"]:
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

    # Support gradient symbol fill
    sym_grad_def = ""
    fill_attr = symbol_color
    if isinstance(symbol_color, (list, tuple)):
        sym_top, sym_bottom = symbol_color[0], symbol_color[1]
    elif "," in str(symbol_color):
        parts = [p.strip() for p in str(symbol_color).split(",")]
        sym_top, sym_bottom = parts[0], parts[1]
    else:
        sym_top, sym_bottom = None, None

    if sym_top and sym_bottom:
        sym_grad_def = f"""    <linearGradient id="symbol-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{sym_top}"/>
      <stop offset="100%" stop-color="{sym_bottom}"/>
    </linearGradient>"""
        fill_attr = "url(#symbol-grad)"

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
{sym_grad_def}
  </defs>

  <!-- Base Squircle -->
  <rect x="{TILE_X}" y="{TILE_Y}" width="{TILE_SIZE}" height="{TILE_SIZE}" rx="{CORNER_RADIUS}" fill="url(#bg-grad)" stroke="{border}" stroke-width="1.5"/>

  <!-- Centered Symbol -->
  <g transform="translate(512, 504) scale({calc_scale}) translate({-center_x}, {-center_y})"{filter_attr}>
    <path fill="{fill_attr}" fill-rule="{fill_rule}" d="{path_d}"/>
  </g>
</svg>"""
    return svg

def build_letter_svg(letter, bg_top, bg_bottom, border, symbol_color, scale, shadow=True):
    font_size = int(400 * scale) if len(letter) == 1 else int(280 * scale)
    y_pos = 635 if len(letter) == 1 else 600
    filter_attr = ' filter="url(#symbol-shadow)"' if shadow else ""

    sym_grad_def = ""
    fill_attr = symbol_color
    if isinstance(symbol_color, (list, tuple)):
        sym_top, sym_bottom = symbol_color[0], symbol_color[1]
    elif "," in str(symbol_color):
        parts = [p.strip() for p in str(symbol_color).split(",")]
        sym_top, sym_bottom = parts[0], parts[1]
    else:
        sym_top, sym_bottom = None, None

    if sym_top and sym_bottom:
        sym_grad_def = f"""    <linearGradient id="symbol-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{sym_top}"/>
      <stop offset="100%" stop-color="{sym_bottom}"/>
    </linearGradient>"""
        fill_attr = "url(#symbol-grad)"

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
{sym_grad_def}
  </defs>

  <!-- Base Squircle -->
  <rect x="{TILE_X}" y="{TILE_Y}" width="{TILE_SIZE}" height="{TILE_SIZE}" rx="{CORNER_RADIUS}" fill="url(#bg-grad)" stroke="{border}" stroke-width="1.5"/>

  <!-- Centered Lettermark -->
  <text x="512" y="{y_pos}" font-family="-apple-system, 'SF Pro Display', system-ui, sans-serif" font-size="{font_size}" font-weight="800" text-anchor="middle" fill="{fill_attr}"{filter_attr}>{letter}</text>
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

def find_repo_root():
    d = os.path.abspath(os.path.dirname(__file__))
    while d and d != "/":
        if os.path.isdir(os.path.join(d, "nix/icons")) or os.path.isfile(os.path.join(d, "nix/flake.nix")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))

def get_icons_base_dir(custom_path=None):
    if custom_path:
        return os.path.abspath(os.path.expanduser(custom_path))
    repo_root = find_repo_root()
    candidate = os.path.join(repo_root, "nix/icons")
    if os.path.isdir(candidate):
        return candidate
    return os.path.abspath("nix/icons")

def load_themes_manifest(manifest_path, icons_base_dir):
    data = {}
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}

    if "light" not in data and os.path.isdir(os.path.join(icons_base_dir, "light")):
        data["light"] = {
            "bg_top": "#FFFFFF",
            "bg_bottom": "#EBECEF",
            "border": "#D8D9DC",
            "symbol_color": "#202022",
            "shadow": True,
            "scale": 1.25,
        }
    if "dark" not in data and os.path.isdir(os.path.join(icons_base_dir, "dark")):
        data["dark"] = {
            "bg_top": "#161618",
            "bg_bottom": "#0D0D0E",
            "border": "#28282C",
            "symbol_color": "#FFFFFF",
            "shadow": False,
            "scale": 1.25,
        }
    return data

def save_themes_manifest(manifest_path, data):
    try:
        with open(manifest_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    except Exception as e:
        print(f"Warning: Could not save themes manifest to {manifest_path}: {e}", file=sys.stderr)

def generate_single_icon(icon_info, out_icns, bg_top, bg_bottom, border, symbol_color, scale=1.25, shadow=True, preview_path=None):
    temp_dir = tempfile.mkdtemp(prefix="mac_icon_")
    try:
        if icon_info["type"] == "letter":
            svg_markup = build_letter_svg(
                icon_info["letter"],
                bg_top,
                bg_bottom,
                border,
                symbol_color,
                scale,
                shadow=shadow
            )
        else:
            svg_markup = build_svg(
                icon_info["path_d"],
                icon_info["viewbox"],
                bg_top,
                bg_bottom,
                border,
                symbol_color,
                scale,
                icon_info.get("fill_rule", "evenodd"),
                shadow=shadow
            )

        svg_file = os.path.join(temp_dir, "composed.svg")
        with open(svg_file, "w") as f:
            f.write(svg_markup)

        repo_root = find_repo_root()
        ref_mask = os.path.join(repo_root, "nix/icons/light/discord.icns")
        if not os.path.exists(ref_mask):
            ref_mask = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns"

        is_dark_bg = is_color_dark(bg_top) or is_color_dark(bg_bottom)
        masked_png = render_and_mask(svg_file, temp_dir, ref_mask, shadow=shadow, is_dark=is_dark_bg)

        if preview_path:
            shutil.copy(masked_png, preview_path)
            print(f"Saved PNG preview: {preview_path}")

        out_icns = os.path.abspath(os.path.expanduser(out_icns))
        compile_icns(masked_png, out_icns, temp_dir)
        return out_icns
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def handle_create_theme(args):
    theme_name = args.create_theme.strip().lower()
    icons_base_dir = get_icons_base_dir(args.icons_dir)
    target_dir = os.path.join(icons_base_dir, theme_name)
    os.makedirs(target_dir, exist_ok=True)

    ref_theme = args.from_theme if args.from_theme else "light"
    ref_dir = os.path.join(icons_base_dir, ref_theme)
    if not os.path.isdir(ref_dir):
        candidates = ["light", "dark"] + [d for d in os.listdir(icons_base_dir) if os.path.isdir(os.path.join(icons_base_dir, d)) and not d.startswith(".")]
        for c in candidates:
            c_dir = os.path.join(icons_base_dir, c)
            if os.path.isdir(c_dir) and any(f.endswith(".icns") for f in os.listdir(c_dir)):
                ref_dir = c_dir
                ref_theme = c
                break

    if not os.path.isdir(ref_dir):
        sys.exit(f"Error: Could not find reference theme directory under '{icons_base_dir}'.")

    existing_icons = sorted([
        os.path.splitext(f)[0]
        for f in os.listdir(ref_dir)
        if f.endswith(".icns") and not f.startswith(".")
    ])

    if not existing_icons:
        sys.exit(f"Error: No .icns icons found in reference theme '{ref_theme}' ({ref_dir}).")

    if theme_name in THEME_PRESETS and not args.bg and args.theme == "light":
        args.theme = theme_name

    bg_top, bg_bottom, border, symbol_color = compute_styling(args)
    scale = args.scale
    shadow = args.shadow

    bg_display = bg_top if bg_top == bg_bottom else f"{bg_top} -> {bg_bottom}"
    print(f"\n🎨 Creating new icon theme '{theme_name}' with {len(existing_icons)} icons:")
    print(f"   Target Directory : {target_dir}")
    print(f"   Reference Theme  : {ref_theme} ({len(existing_icons)} icons)")
    print(f"   Background       : {bg_display}")
    print(f"   Border           : {border}")
    print(f"   Symbol Color     : {symbol_color}")
    print(f"   Shadow           : {'Enabled' if shadow else 'Disabled (flat)'}")
    print(f"   Scale            : {scale}\n")

    themes_file = os.path.join(icons_base_dir, "themes.json")
    themes_data = load_themes_manifest(themes_file, icons_base_dir)
    themes_data[theme_name] = {
        "bg_top": bg_top,
        "bg_bottom": bg_bottom,
        "border": border,
        "symbol_color": symbol_color,
        "shadow": shadow,
        "scale": scale,
    }
    save_themes_manifest(themes_file, themes_data)

    success_count = 0
    failed_icons = []

    for i, icon_name in enumerate(existing_icons, start=1):
        print(f"   [{i:2d}/{len(existing_icons)}] Generating {icon_name}.icns ... ", end="", flush=True)
        out_file = os.path.join(target_dir, f"{icon_name}.icns")
        try:
            icon_info = fetch_icon_or_create(icon_name, fallback_letter=True)
            generate_single_icon(
                icon_info=icon_info,
                out_icns=out_file,
                bg_top=bg_top,
                bg_bottom=bg_bottom,
                border=border,
                symbol_color=symbol_color,
                scale=scale,
                shadow=shadow
            )
            print("✓")
            success_count += 1
        except Exception as e:
            print(f"✗ ({e})")
            failed_icons.append((icon_name, str(e)))

    print(f"\n✨ Theme '{theme_name}' successfully generated ({success_count}/{len(existing_icons)} icons in '{target_dir}').")
    if failed_icons:
        print(f"⚠️  {len(failed_icons)} icons failed: {', '.join(k for k, _ in failed_icons)}")

    print(f"\n💡 To activate this theme in Nix:")
    print(f"   1. Set in nix/personal/default.nix or nix/shared.nix:")
    print(f"        theme.icons = \"{theme_name}\";")
    print(f"   2. Stage icons:")
    print(f"        git add nix/icons/{theme_name}")
    print(f"   3. Apply:")
    print(f"        darwin-rebuild switch --flake ~/dotfiles/nix#macbook-personal\n")

def handle_all_themes(args, icon_info, base_name):
    icons_base_dir = get_icons_base_dir(args.icons_dir)
    themes_file = os.path.join(icons_base_dir, "themes.json")
    themes_data = load_themes_manifest(themes_file, icons_base_dir)

    print(f"\n🌐 Generating icon '{base_name}.icns' across {len(themes_data)} registered theme(s):")
    success_count = 0
    for theme_name, cfg in themes_data.items():
        theme_dir = os.path.join(icons_base_dir, theme_name)
        os.makedirs(theme_dir, exist_ok=True)
        out_file = os.path.join(theme_dir, f"{base_name}.icns")

        bg_top = cfg.get("bg_top", "#FFFFFF")
        bg_bottom = cfg.get("bg_bottom", bg_top)
        border = cfg.get("border", "#D8D9DC")
        symbol_color = cfg.get("symbol_color", "#202022")
        scale = cfg.get("scale", args.scale)
        shadow = cfg.get("shadow", True)

        print(f"   • {theme_name:<14} -> {theme_name}/{base_name}.icns ... ", end="", flush=True)
        try:
            generate_single_icon(
                icon_info=icon_info,
                out_icns=out_file,
                bg_top=bg_top,
                bg_bottom=bg_bottom,
                border=border,
                symbol_color=symbol_color,
                scale=scale,
                shadow=shadow
            )
            print("✓")
            success_count += 1
        except Exception as e:
            print(f"✗ ({e})")

    print(f"\n✨ Successfully generated '{base_name}.icns' across {success_count}/{len(themes_data)} themes.")
    print(f"💡 Don't forget to track them with git:")
    print(f"   git add nix/icons/*/{base_name}.icns\n")

def handle_sync_themes(args):
    icons_base_dir = get_icons_base_dir(args.icons_dir)
    themes_file = os.path.join(icons_base_dir, "themes.json")
    themes_data = load_themes_manifest(themes_file, icons_base_dir)

    all_icon_names = set()
    for theme_name in themes_data:
        t_dir = os.path.join(icons_base_dir, theme_name)
        if os.path.isdir(t_dir):
            for f in os.listdir(t_dir):
                if f.endswith(".icns") and not f.startswith("."):
                    all_icon_names.add(os.path.splitext(f)[0])

    if not all_icon_names:
        sys.exit(f"Error: No .icns icons found across any themes in '{icons_base_dir}'.")

    all_icons_list = sorted(list(all_icon_names))
    print(f"\n🔄 Syncing {len(all_icons_list)} icons across {len(themes_data)} themes ({', '.join(themes_data.keys())})...\n")

    for theme_name, cfg in themes_data.items():
        print(f"📦 Theme: {theme_name}")
        t_dir = os.path.join(icons_base_dir, theme_name)
        os.makedirs(t_dir, exist_ok=True)
        bg_top = cfg.get("bg_top", "#FFFFFF")
        bg_bottom = cfg.get("bg_bottom", bg_top)
        border = cfg.get("border", "#D8D9DC")
        symbol_color = cfg.get("symbol_color", "#202022")
        scale = cfg.get("scale", 1.25)
        shadow = cfg.get("shadow", True)

        for icon_name in all_icons_list:
            out_file = os.path.join(t_dir, f"{icon_name}.icns")
            if not os.path.exists(out_file):
                print(f"   Adding missing {icon_name}.icns ... ", end="", flush=True)
                try:
                    icon_info = fetch_icon_or_create(icon_name, fallback_letter=True)
                    generate_single_icon(
                        icon_info=icon_info,
                        out_icns=out_file,
                        bg_top=bg_top,
                        bg_bottom=bg_bottom,
                        border=border,
                        symbol_color=symbol_color,
                        scale=scale,
                        shadow=shadow
                    )
                    print("✓")
                except Exception as e:
                    print(f"✗ ({e})")
    print(f"\n✨ All themes are now synchronized!\n")

def main():
    args = parse_args()

    if args.create_theme:
        handle_create_theme(args)
        return

    if args.sync_themes:
        handle_sync_themes(args)
        return

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

    if args.all_themes:
        handle_all_themes(args, icon_info, base_name)
        return

    # Automatically derive output ICNS path if omitted
    if not args.out:
        if args.apply:
            app_stem = os.path.splitext(os.path.basename(args.apply))[0].lower().replace(" ", "-")
            repo_root = find_repo_root()
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

    out_icns = generate_single_icon(
        icon_info=icon_info,
        out_icns=args.out,
        bg_top=bg_top,
        bg_bottom=bg_bottom,
        border=border,
        symbol_color=symbol_color,
        scale=args.scale,
        shadow=args.shadow,
        preview_path=preview_path
    )

    # Optional application
    if args.apply:
        apply_icon_to_app(args.apply, out_icns, restart_dock=not args.no_dock_restart)

if __name__ == "__main__":
    main()
