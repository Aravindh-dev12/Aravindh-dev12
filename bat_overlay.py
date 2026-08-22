from pathlib import Path

BAT_PATH = (
    "M0,-11 L-5,-17 L-3,-9 "
    "C-10,-11 -15,-17 -24,-20 L-39,-19 L-31,-12 L-45,-7 L-35,-2 "
    "L-43,5 L-31,4 L-26,12 L-18,7 L-12,14 L-7,5 "
    "C-6,10 -4,14 0,18 C4,14 6,10 7,5 "
    "L12,14 L18,7 L26,12 L31,4 L43,5 L35,-2 L45,-7 L31,-12 "
    "L39,-19 L24,-20 C15,-17 10,-11 3,-9 L5,-17 Z"
)

BAT_COUNT = 40
BAT_COLOR = "#000000"


def realistic_bat(scale):
    return f'<path d="{BAT_PATH}" transform="scale({scale:.2f})"/>'


def build_swarm():
    pieces = [f'<g fill="{BAT_COLOR}" pointer-events="none">']

    for index in range(BAT_COUNT):
        lane = index % 20
        reverse = index >= 20

        y = 35 + lane * 24
        arc = 28 + (index % 5) * 12
        begin = f"{(index % 20) * 0.018 + (0.009 if reverse else 0):.3f}s"
        duration = f"{2.10 + (index % 6) * 0.10:.2f}s"
        scale = 0.30 + (index % 7) * 0.035
        opacity = 0.50 + (index % 4) * 0.08

        if reverse:
            path = (
                f"M1035,{y} "
                f"C820,{max(5, y - arc)} 650,{y + arc} 495,{y} "
                f"C320,{max(5, y - arc)} 145,{y + arc} -50,{max(8, y - 8)}"
            )
        else:
            path = (
                f"M-50,{y} "
                f"C165,{max(5, y - arc)} 335,{y + arc} 500,{y} "
                f"C675,{max(5, y - arc)} 850,{y + arc} 1035,{max(8, y - 8)}"
            )

        pieces.append(
            '<g opacity="0">'
            f'{realistic_bat(scale)}'
            f'<animate attributeName="opacity" values="0;{opacity:.2f};{opacity:.2f};0" '
            f'keyTimes="0;0.05;0.90;1" begin="{begin}" dur="{duration}" '
            f'calcMode="linear" repeatCount="1" fill="freeze"/>'
            f'<animateMotion path="{path}" begin="{begin}" dur="{duration}" '
            f'calcMode="paced" repeatCount="1" fill="freeze" rotate="auto"/>'
            '</g>'
        )

    pieces.append("</g>")
    return "\n".join(pieces)


def patch_svg(path):
    svg_path = Path(path)
    svg = svg_path.read_text(encoding="utf-8")

    # today.py renders the swarm as the final <g> immediately before </svg>.
    start = svg.rfind('<g fill="')
    end = svg.rfind("</svg>")
    if start == -1 or end == -1 or start >= end:
        raise RuntimeError(f"Could not locate swarm in {svg_path}")

    patched = svg[:start] + build_swarm() + "\n" + svg[end:]
    svg_path.write_text(patched, encoding="utf-8")


def main():
    patch_svg("dark_mode.svg")
    patch_svg("light_mode.svg")
    print(f"Applied {BAT_COUNT} pure-black optimized bats to both SVG themes.")


if __name__ == "__main__":
    main()
