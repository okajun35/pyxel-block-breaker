PAGES = [
    [
        "1/2/3: むずかしさ",
        "TAB: きりかえ",
        "SPACE: すたーと",
        "C: ほぞん",
    ],
    [
        "W: ばーをのばす",
        "S: たまをおそく",
        "M: たまをふやす",
        "F: たまをはやく",
    ],
]


def tutorial_page(frame_count: int) -> int:
    return (max(0, frame_count) // 120) % len(PAGES)


def tutorial_lines(page: int) -> list[str]:
    return PAGES[page % len(PAGES)]
