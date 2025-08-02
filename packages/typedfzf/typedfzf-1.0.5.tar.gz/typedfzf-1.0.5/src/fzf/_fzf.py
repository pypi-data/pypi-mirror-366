# #!/usr/bin/env python3
from __future__ import annotations

import errno
import itertools
import subprocess
import typing
from typing import TYPE_CHECKING
from typing import Callable
from typing import TypeVar
from typing import overload

from typing_extensions import Literal
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Sequence
    from subprocess import _CMD


def piped_exec(
    cmd: subprocess._CMD,
    iterable: Iterable[str],
) -> list[str]:
    """
    Executes a command with input from an iterable and returns the output as a list of strings.

    Args:
    ----
        cmd (_CMD): The command to execute.
        iterable (Iterable[str]): An iterable containing the input to be passed to the command.

    Returns:
    -------
        list[str]: A list of strings representing the output of the command.

    """
    empty_return: list[str] = []
    proc = subprocess.Popen(
        args=cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None,
        encoding="utf-8",
    )

    stdin = proc.stdin

    if stdin is None:
        return empty_return

    for line in iterable:
        try:
            stdin.write(line + "\n")
            stdin.flush()
        except OSError as os_error:  # noqa: PERF203
            if errno.EPIPE not in (os_error.errno, 32):
                raise
            break
    try:
        stdin.close()
    except OSError as os_error:
        if errno.EPIPE not in (os_error.errno, 32):
            raise
    if proc.wait() not in [0, 1]:
        return empty_return
    stdout = proc.stdout
    if stdout is None:
        return empty_return

    return [line[:-1] for line in stdout]


T = TypeVar("T")


@overload
def select_helper(
    *,
    cmd: _CMD,
    items: Iterable[T],
    multi: Literal[True],
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
) -> list[T]: ...


@overload
def select_helper(
    *,
    cmd: _CMD,
    items: Iterable[T],
    multi: Literal[False],
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
) -> T | None: ...


def select_helper(
    *,
    cmd: _CMD,
    items: Iterable[T],
    multi: bool = False,
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
) -> list[T] | T | None:
    """
    Helper function to select items from a list using a command line tool.

    Args:
    ----
        cmd (str): The command line tool to use for selection.
        items (Iterable[T]): The items to select from.
        multi (bool, optional): Whether to allow multiple selections. Defaults to False.
        select_one (bool, optional): Whether to select only one item. Defaults to True.
        key (Callable[[T], str] | None, optional): A function to extract a key from each item. Defaults to None.

    Returns:
    -------
        list[T] | T | None: The selected item(s).

    """  # noqa: E501
    empty_return: None | list[T] = [] if multi else None
    sentinel = object()
    iterator = iter(items)
    _first_item = next(iterator, sentinel)
    if _first_item == sentinel:
        return empty_return
    first_item: T = typing.cast("T", _first_item)

    full_stream: Iterable[T]
    if select_one:
        _second_item = next(iterator, sentinel)
        if _second_item == sentinel:
            return [first_item] if multi else first_item
        second_item: T = typing.cast("T", _second_item)
        full_stream = itertools.chain((first_item, second_item), iterator)
    else:
        full_stream = itertools.chain((first_item,), iterator)

    dct: dict[str, T] = {}

    def _inner_(t: T, func: Callable[[T], str]) -> str:
        _key = func(t)
        dct[_key] = t
        return _key

    _iterable: Iterable[str]
    if key is not None:
        _iterable = (_inner_(x, key) for x in full_stream)
    elif not isinstance(first_item, str):
        _iterable = (_inner_(x, str) for x in full_stream)
    else:
        _iterable = typing.cast("Iterable[str]", full_stream)

    lines = piped_exec(cmd, _iterable)

    if not lines:
        return empty_return

    converted: list[T] = [dct[x] for x in lines] if dct else lines  # type:ignore[assignment]
    return converted if multi else converted[0]


# 0.44.1 (d7d2ac3)
# usage: fzf [options]

#   Search
#     -x, --extended         Extended-search mode
#                            (enabled by default; +x or --no-extended to disable)
#     -e, --exact            Enable Exact-match
#     -i                     Case-insensitive match (default: smart-case match)
#     +i                     Case-sensitive match
#     --scheme=SCHEME        Scoring scheme [default|path|history]
#     --literal              Do not normalize latin script letters before matching
#     -n, --nth=N[,..]       Comma-separated list of field index expressions
#                            for limiting search scope. Each can be a non-zero
#                            integer or a range expression ([BEGIN]..[END]).
#     --with-nth=N[,..]      Transform the presentation of each line using
#                            field index expressions
#     -d, --delimiter=STR    Field delimiter regex (default: AWK-style)
#     +s, --no-sort          Do not sort the result
#     --track                Track the current selection when the result is updated
#     --tac                  Reverse the order of the input
#     --disabled             Do not perform search
#     --tiebreak=CRI[,..]    Comma-separated list of sort criteria to apply
#                            when the scores are tied [length|chunk|begin|end|index]
#                            (default: length)

#   Interface
#     -m, --multi[=MAX]      Enable multi-select with tab/shift-tab
#     --no-mouse             Disable mouse
#     --bind=KEYBINDS        Custom key bindings. Refer to the man page.
#     --cycle                Enable cyclic scroll
#     --keep-right           Keep the right end of the line visible on overflow
#     --scroll-off=LINES     Number of screen lines to keep above or below when
#                            scrolling to the top or to the bottom (default: 0)
#     --no-hscroll           Disable horizontal scroll
#     --hscroll-off=COLS     Number of screen columns to keep to the right of the
#                            highlighted substring (default: 10)
#     --filepath-word        Make word-wise movements respect path separators
#     --jump-labels=CHARS    Label characters for jump and jump-accept

#   Layout
#     --height=[~]HEIGHT[%]  Display fzf window below the cursor with the given
#                            height instead of using fullscreen.
#                            If prefixed with '~', fzf will determine the height
#                            according to the input size.
#     --min-height=HEIGHT    Minimum height when --height is given in percent
#                            (default: 10)
#     --layout=LAYOUT        Choose layout: [default|reverse|reverse-list]
#     --border[=STYLE]       Draw border around the finder
#                            [rounded|sharp|bold|block|thinblock|double|horizontal|vertical|
#                             top|bottom|left|right|none] (default: rounded)
#     --border-label=LABEL   Label to print on the border
#     --border-label-pos=COL Position of the border label
#                            [POSITIVE_INTEGER: columns from left|
#                             NEGATIVE_INTEGER: columns from right][:bottom]
#                            (default: 0 or center)
#     --margin=MARGIN        Screen margin (TRBL | TB,RL | T,RL,B | T,R,B,L)
#     --padding=PADDING      Padding inside border (TRBL | TB,RL | T,RL,B | T,R,B,L)
#     --info=STYLE           Finder info style
#                            [default|right|hidden|inline[:SEPARATOR]|inline-right]
#     --separator=STR        String to form horizontal separator on info line
#     --no-separator         Hide info line separator
#     --scrollbar[=C1[C2]]   Scrollbar character(s) (each for main and preview window)
#     --no-scrollbar         Hide scrollbar
#     --prompt=STR           Input prompt (default: '> ')
#     --pointer=STR          Pointer to the current line (default: '>')
#     --marker=STR           Multi-select marker (default: '>')
#     --header=STR           String to print as header
#     --header-lines=N       The first N lines of the input are treated as header
#     --header-first         Print header before the prompt line
#     --ellipsis=STR         Ellipsis to show when line is truncated (default: '..')

#   Display
#     --ansi                 Enable processing of ANSI color codes
#     --tabstop=SPACES       Number of spaces for a tab character (default: 8)
#     --color=COLSPEC        Base scheme (dark|light|16|bw) and/or custom colors
#     --no-bold              Do not use bold text

#   History
#     --history=FILE         History file
#     --history-size=N       Maximum number of history entries (default: 1000)

#   Preview
#     --preview=COMMAND      Command to preview highlighted line ({})
#     --preview-window=OPT   Preview window layout (default: right:50%)
#                            [up|down|left|right][,SIZE[%]]
#                            [,[no]wrap][,[no]cycle][,[no]follow][,[no]hidden]
#                            [,border-BORDER_OPT]
#                            [,+SCROLL[OFFSETS][/DENOM]][,~HEADER_LINES]
#                            [,default][,<SIZE_THRESHOLD(ALTERNATIVE_LAYOUT)]
#     --preview-label=LABEL
#     --preview-label-pos=N  Same as --border-label and --border-label-pos,
#                            but for preview window

#   Scripting
#     -q, --query=STR        Start the finder with the given query
#     -1, --select-1         Automatically select the only match
#     -0, --exit-0           Exit immediately when there's no match
#     -f, --filter=STR       Filter mode. Do not start interactive finder.
#     --print-query          Print query as the first line
#     --expect=KEYS          Comma-separated list of keys to complete fzf
#     --read0                Read input delimited by ASCII NUL characters
#     --print0               Print output delimited by ASCII NUL characters
#     --sync                 Synchronous search for multi-staged filtering
#     --listen[=[ADDR:]PORT] Start HTTP server to receive actions (POST /)
#                            (To allow remote process execution, use --listen-unsafe)
#     --version              Display version information and exit

#   Environment variables
#     FZF_DEFAULT_COMMAND    Default command to use when input is tty
#     FZF_DEFAULT_OPTS       Default options
#                            (e.g. '--layout=reverse --inline-info')
#     FZF_API_KEY            X-API-Key header for HTTP server (--listen)


class _FzfOptions(TypedDict, total=False):
    # Search
    extended: bool
    exact: bool
    case_sensitive: bool
    scheme: Literal["default", "path", "history"]
    literal: bool
    nth: str
    with_nth: str
    delimiter: str
    no_sort: bool
    track: bool
    tac: bool
    disabled: bool
    tiebreak: list[Literal["length", "chunk", "begin", "end", "index"]]

    # Interface
    # multi: int
    no_mouse: bool
    bind: str
    cycle: bool
    keep_right: bool
    scroll_off: int
    no_hscroll: bool
    hscroll_off: int
    filepath_word: bool
    jump_labels: str

    # Layout
    height: str
    min_height: int
    layout: Literal["default", "reverse", "reverse-list"]
    border: Literal[
        "rounded",
        "sharp",
        "bold",
        "block",
        "thinblock",
        "double",
        "horizontal",
        "vertical",
        "top",
        "bottom",
        "left",
        "right",
        "none",
    ]
    border_label: str
    border_label_pos: str
    margin: str
    padding: str
    info: Literal["default", "right", "hidden", "inline", "inline-right"]
    separator: str
    no_separator: bool
    scrollbar: str
    no_scrollbar: bool
    prompt: str
    pointer: str
    marker: str
    header: str
    header_lines: int
    header_first: bool
    ellipsis: str

    # Display
    ansi: bool
    tabstop: int
    color: str
    no_bold: bool

    # History
    history: str
    history_size: int

    # Preview
    preview: str
    preview_window: str
    preview_label: str
    preview_label_pos: str

    # Scripting
    query: str
    select_1: bool
    exit_0: bool
    filter: str
    print_query: bool
    expect: str
    read0: bool
    print0: bool
    sync: bool
    listen: str
    additional_args: Sequence[str]


def _fzf_options(kwargs: _FzfOptions) -> list[str]:  # noqa: C901, PLR0915, PLR0912
    cmd = []
    # Search
    if "extended" in kwargs:
        cmd.append(f"--{'' if kwargs['extended'] else 'no-'}extended")
    if kwargs.get("exact"):
        cmd.append("--exact")
    if "case_sensitive" in kwargs:
        cmd.append(f"{'+' if kwargs['case_sensitive'] else '-'}i")
    if "scheme" in kwargs:
        cmd.append(f"--scheme={kwargs['scheme']}")
    if kwargs.get("literal"):
        cmd.append("--literal")
    if kwargs.get("nth"):
        cmd.append(f"--nth={kwargs['nth']}")
    if kwargs.get("with_nth"):
        cmd.append(f"--with-nth={kwargs['with_nth']}")
    if kwargs.get("delimiter"):
        cmd.append(f"--delimiter={kwargs['delimiter']}")
    if kwargs.get("no_sort"):
        cmd.append("--no-sort")
    if kwargs.get("track"):
        cmd.append("--track")
    if kwargs.get("tac"):
        cmd.append("--tac")
    if kwargs.get("disabled"):
        cmd.append("--disabled")
    if kwargs.get("tiebreak"):
        cmd.append(f"--tiebreak={','.join(kwargs['tiebreak'])}")

    # Interface
    # if 'multi' in kwargs and kwargs['multi']:
    #     cmd.append(f'--multi={kwargs["multi"]}')
    if kwargs.get("no_mouse"):
        cmd.append("--no-mouse")
    if kwargs.get("bind"):
        cmd.append(f"--bind={kwargs['bind']}")
    if kwargs.get("cycle"):
        cmd.append("--cycle")
    if kwargs.get("keep_right"):
        cmd.append("--keep-right")
    if kwargs.get("scroll_off"):
        cmd.append(f"--scroll-off={kwargs['scroll_off']}")
    if kwargs.get("no_hscroll"):
        cmd.append("--no-hscroll")
    if kwargs.get("hscroll_off"):
        cmd.append(f"--hscroll-off={kwargs['hscroll_off']}")
    if kwargs.get("filepath_word"):
        cmd.append("--filepath-word")
    if kwargs.get("jump_labels"):
        cmd.append(f"--jump-labels={kwargs['jump_labels']}")

    # Layout
    if kwargs.get("height"):
        cmd.append(f"--height={kwargs['height']}")
    if kwargs.get("min_height"):
        cmd.append(f"--min-height={kwargs['min_height']}")
    if kwargs.get("layout"):
        cmd.append(f"--layout={kwargs['layout']}")
    if kwargs.get("border"):
        cmd.append(f"--border={kwargs['border']}")
    if kwargs.get("border_label"):
        cmd.append(f"--border-label={kwargs['border_label']}")
    if kwargs.get("border_label_pos"):
        cmd.append(f"--border-label-pos={kwargs['border_label_pos']}")
    if kwargs.get("margin"):
        cmd.append(f"--margin={kwargs['margin']}")
    if kwargs.get("padding"):
        cmd.append(f"--padding={kwargs['padding']}")
    if kwargs.get("info"):
        cmd.append(f"--info={kwargs['info']}")
    if kwargs.get("separator"):
        cmd.append(f"--separator={kwargs['separator']}")
    if kwargs.get("no_separator"):
        cmd.append("--no-separator")
    if kwargs.get("scrollbar"):
        cmd.append(f"--scrollbar={kwargs['scrollbar']}")
    if kwargs.get("no_scrollbar"):
        cmd.append("--no-scrollbar")
    if kwargs.get("prompt"):
        cmd.append(f"--prompt={kwargs['prompt']}")
    if kwargs.get("pointer"):
        cmd.append(f"--pointer={kwargs['pointer']}")
    if kwargs.get("marker"):
        cmd.append(f"--marker={kwargs['marker']}")
    if kwargs.get("header"):
        cmd.append(f"--header={kwargs['header']}")
    if kwargs.get("header_lines"):
        cmd.append(f"--header-lines={kwargs['header_lines']}")
    if kwargs.get("header_first"):
        cmd.append("--header-first")
    if kwargs.get("ellipsis"):
        cmd.append(f"--ellipsis={kwargs['ellipsis']}")

    # Display
    if kwargs.get("ansi"):
        cmd.append("--ansi")
    if kwargs.get("tabstop"):
        cmd.append(f"--tabstop={kwargs['tabstop']}")
    if kwargs.get("color"):
        cmd.append(f"--color={kwargs['color']}")
    if kwargs.get("no_bold"):
        cmd.append("--no-bold")

    # History
    if kwargs.get("history"):
        cmd.append(f"--history={kwargs['history']}")
    if kwargs.get("history_size"):
        cmd.append(f"--history-size={kwargs['history_size']}")

    # Preview
    if kwargs.get("preview"):
        cmd.append(f"--preview={kwargs['preview']}")
    if kwargs.get("preview_window"):
        cmd.append(f"--preview-window={kwargs['preview_window']}")
    if kwargs.get("preview_label"):
        cmd.append(f"--preview-label={kwargs['preview_label']}")
    if kwargs.get("preview_label_pos"):
        cmd.append(f"--preview-label-pos={kwargs['preview_label_pos']}")

    # Scripting
    if kwargs.get("query"):
        cmd.append(f"--query={kwargs['query']}")
    if kwargs.get("select_1"):
        cmd.append("--select-1")
    if kwargs.get("exit_0"):
        cmd.append("--exit-0")
    if kwargs.get("filter"):
        cmd.append(f"--filter={kwargs['filter']}")
    if kwargs.get("print_query"):
        cmd.append("--print-query")
    if kwargs.get("expect"):
        cmd.append(f"--expect={kwargs['expect']}")
    if kwargs.get("read0"):
        cmd.append("--read0")
    if kwargs.get("print0"):
        cmd.append("--print0")
    if kwargs.get("sync"):
        cmd.append("--sync")
    if kwargs.get("listen"):
        cmd.append(f"--listen={kwargs['listen']}")
    if kwargs.get("additional_args"):
        cmd.extend(kwargs["additional_args"])
    return cmd


@overload
def fzf(  # pyright: ignore[reportOverlappingOverload]
    iterable: Iterable[T],
    *,
    multi: Literal[False] = False,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    _options: _FzfOptions | None = None,
) -> T | None: ...


@overload
def fzf(
    iterable: Iterable[T],
    *,
    multi: Literal[True] = True,
    select_one: bool = ...,
    key: Callable[[T], str] | None = ...,
    _options: _FzfOptions | None = None,
) -> list[T]: ...


def fzf(
    iterable: Iterable[T],
    *,
    multi: bool = False,
    select_one: bool = True,
    key: Callable[[T], str] | None = None,
    _options: _FzfOptions | None = None,
) -> T | None | list[T]:
    _options = _options or {}

    _options["select_1"] = select_one
    cmd = ["fzf", *(_fzf_options(_options))]
    if multi:
        cmd.append("--multi")

    return select_helper(  # type:ignore[call-overload]
        cmd=cmd,
        items=iterable,
        multi=multi,
        select_one=select_one,
        key=key,
    )
