# Copyright (C) 2021 Hyunwoong Ko <kevin.brain@kakaobrain.com> and Sang Park <sang.park@dnotitia.com>
# All rights reserved.

import numbers
import platform
import unicodedata
from typing import Union, Tuple, List, Any, Optional, Type, Callable, Iterable

from kss._modules.morphemes.analyzers import (
    MecabAnalyzer,
    PecabAnalyzer,
    Analyzer,
    CharacterAnalyzer,
    FastAnalyzer,
)
from kss._utils.logger import logger

MECAB_INFORM, KONLPY_MECAB_INFORM, PECAB_INFORM, FAST_INFORM = (
    False,
    False,
    False,
    False,
)

_mecab_info_linux_macos = "https://github.com/hyunwoongko/python-mecab-kor"
_konlpy_info_linux_macos = "https://konlpy.org/en/latest/api/konlpy.tag/#mecab-class"
_mecab_info_windows = "https://cleancode-ws.tistory.com/97"
_konlpy_info_windows = "https://uwgdqo.tistory.com/363"
_pecab_info = "https://github.com/hyunwoongko/pecab"


def _message_by_user_os(linux_macos: str, windows: str) -> str:
    user_os = platform.uname().system.lower()
    if user_os in ["linux", "darwin"]:
        return linux_macos
    elif user_os.startswith("win"):
        return windows


def _check_value(
    param: Any, param_name: str, predicate: Callable, suggestion: str
) -> Any:
    """
    Check param value

    Args:
        param (bool): param value
        param_name (str): param name
        predicate (Callable): callable
        suggestion (str): suggestion message

    Returns:
        Any: param value
    """
    available = predicate(param)

    if not available:
        raise TypeError(
            f"Oops! '{param}' is not supported value for `{param_name}`.\n"
            f"Currently kss only supports {suggestion} for this.\n"
            f"Please check `{param_name}` parameter again ;)\n"
        )

    return param


def _check_iterable_type(
    param: Iterable, param_name: str, iterable_type: Type, element_type: Type
) -> Any:
    """
    Check iterable param type

    Args:
        param (Iterable): iterable param value
        param_name (str): param name
        iterable_type (Type): iterable type
        element_type (Type): element type

    Returns:
        Any: param value
    """
    if not isinstance(param, iterable_type):
        raise TypeError(
            f"Oops! '{type(param)}' is not supported type for `{param_name}`.\n"
            f"Currently kss only supports {iterable_type} for this.\n"
            f"Please check `{param_name}` parameter again ;)\n"
        )

    for element in param:
        if not isinstance(element, element_type):
            raise TypeError(
                f"Oops! '{type(param).__qualname__.capitalize()}[{type(element).__qualname__}]' is not supported type for `{param_name}`.\n"
                f"Currently kss only supports {iterable_type.__qualname__.capitalize()}[{element_type.__qualname__}] for this.\n"
                f"Please check `{param_name}` parameter again ;)\n"
            )
    return param


def _check_type(param: Any, param_name: str, types: Union[Type, List[Type]]) -> Any:
    """
    Check param type

    Args:
        param (bool): param value
        param_name (str): param name
        types (Union[Type, List[Type]]): types

    Returns:
        Any: param value
    """
    was_list = True

    if types == int or types == float:
        types = numbers.Number

    if not isinstance(types, list) or not isinstance(types, tuple):
        types = [types]
        was_list = False

    available = any([isinstance(param, _type) for _type in types])

    if not available:
        raise TypeError(
            f"Oops! '{type(param)}' is not supported type for `{param_name}`.\n"
            f"Currently kss only supports {types if was_list else types[0]} {'types' if was_list else 'type'} for this.\n"
            f"Please check `{param_name}` parameter again ;)\n"
        )

    return param


def _check_char(text: str) -> str:
    """
    Check text length is 1.

    Args:
        text (str): text

    Returns:
        str: text
    """
    if len(text) != 1:
        raise ValueError(
            f"Oops! '{text}' is not a single character.\n"
            f"Currently kss only supports single character for this.\n"
            f"Please check `text` parameter again ;)"
        )

    return text


def _check_text(
    text: Union[str, List[str], Tuple[str]]
) -> Tuple[Union[str, List[str], Tuple[str]], bool]:
    """
    Check input text type.

    Args:
        text (Union[str, List[str], Tuple[str]]): single text or list/tuple of texts

    Returns:
        Tuple[Union[str, List[str], Tuple[str]], bool]: single text or list/tuple of texts
            and whether it can finish processing right now or not.
    """
    finish = False

    if (
        not isinstance(text, str)
        and not isinstance(text, list)
        and not isinstance(text, tuple)
    ):
        raise TypeError(
            f"Oops! '{type(text)}' is not supported type for `text`.\n"
            f"Currently kss only supports [str, List[str], Tuple[str]] types for this.\n"
            f"Please check `text` parameter again ;)\n"
        )

    elif (isinstance(text, list) or isinstance(text, tuple)) and len(text) != 0:
        are_strings = [isinstance(t, str) for t in text]
        if not all(are_strings):
            not_string_idx = are_strings.index(False)
            raise TypeError(
                "Oops! Some elements in `text` were not string.\n"
                f"For example, index {not_string_idx} was {type(text[not_string_idx])}.\n"
                f"Currently kss only supports [str, List[str], Tuple[str]] for this.\n"
                f"Please check `text` parameter again ;)\n"
            )

        # unwrap list or tuple with single text
        if len(text) == 1:
            text = text[0]

        if isinstance(text, list):
            text = tuple(text)

    elif len(text) == 0:
        finish = True

    return text, finish


def _check_analyzer_backend_mecab_pecab_only(backend: str) -> Analyzer:
    global MECAB_INFORM, KONLPY_MECAB_INFORM, PECAB_INFORM

    if isinstance(backend, str):
        backend = backend.lower()

    if backend not in ["auto", "mecab", "pecab"]:
        raise ValueError(
            f"Oops! '{backend}' is not supported value for spacing correction module.\n"
            f"Currently the spacing correction module only supports ['auto', 'pecab', 'mecab'] for this.\n"
            f"Please check `backend` parameter again ;)\n"
        )

    mecab_backend = MecabAnalyzer()
    pecab_backend = PecabAnalyzer()

    if backend == "mecab":
        if mecab_backend._backend is not None:
            return mecab_backend
        else:
            raise ImportError(
                _message_by_user_os(
                    linux_macos="Oops! You specified `backend` as 'mecab', but you don't have mecab in your environment.\n"
                    "If you want to use mecab backend, please install mecab or konlpy.tag.Mecab!\n"
                    "Please refer to following web sites for details:\n"
                    f"- mecab: {_mecab_info_linux_macos}\n"
                    f"- konlpy.tag.Mecab: {_konlpy_info_linux_macos}\n",
                    windows="Oops! You specified `backend` as 'mecab', but you don't have mecab in your environment.\n"
                    "If you want to use mecab backend, please install mecab or konlpy.tag.Mecab!\n"
                    "Please refer to following web sites for details:\n"
                    f"- mecab: {_mecab_info_windows}\n"
                    f"- konlpy.tag.Mecab: {_konlpy_info_windows}\n",
                )
            )

    elif backend == "pecab":
        if pecab_backend._backend is not None:
            return pecab_backend
        else:
            raise ImportError(
                "Oops! You specified `backend` as 'pecab', but you don't have pecab in your environment.\n"
                "If you want to use pecab backend, please install pecab!\n"
                "Please refer to following web sites for details:\n"
                "- pecab: https://github.com/hyunwoongko/pecab\n"
            )

    elif backend == "auto":
        if mecab_backend._backend == "mecab":
            if not MECAB_INFORM:
                logger.warning(
                    "Oh! You have mecab in your environment. Kss will take this as a backend! :D\n"
                )
                MECAB_INFORM = True
            return mecab_backend

        elif mecab_backend._backend == "konlpy":
            if not KONLPY_MECAB_INFORM:
                logger.warning(
                    "Oh! You have konlpy.tag.Mecab in your environment. Kss will take this as a backend! :D\n"
                )
                KONLPY_MECAB_INFORM = True
            return mecab_backend

        elif pecab_backend._backend == "pecab":
            if not PECAB_INFORM:

                installation_help_message = _message_by_user_os(
                    linux_macos="For your information, Kss also supports mecab backend.\n"
                    "We recommend you to install mecab or konlpy.tag.Mecab for faster execution of Kss.\n"
                    "Please refer to following web sites for details:\n"
                    f"- mecab: {_mecab_info_linux_macos}\n"
                    f"- konlpy.tag.Mecab: {_konlpy_info_linux_macos}\n",
                    windows="For your information, Kss also supports mecab backend.\n"
                    "We recommend you to install mecab or konlpy.tag.Mecab for faster execution of Kss.\n"
                    "Please refer to following web sites for details:\n"
                    f"- mecab: {_mecab_info_windows}\n"
                    f"- konlpy.tag.Mecab: {_konlpy_info_windows}\n",
                )

                logger.warning(
                    "Because there's no supported C++ morpheme analyzer, "
                    "Kss will take pecab as a backend. :D\n"
                    f"{installation_help_message}"
                )
                PECAB_INFORM = True

            return pecab_backend
        else:
            raise ImportError(
                f"Oops! You don't have any supported morpheme analyzer in your environment.\n"
                f"If you want to use spacing correction module, please install mecab or pecab!\n"
                f"Please refer to following web sites for details:\n"
                f"- mecab:\n"
                f"  - Linux/MacOS: {_mecab_info_linux_macos}\n"
                f"  - Windows: {_mecab_info_windows}\n"
                f"- pecab: {_pecab_info}\n"
            )


def _check_analyzer_backend(backend: str) -> Analyzer:
    """
    Check morpheme analyzer backend type.

    Args:
        backend (str):

    Returns:
        Analyzer: morpheme analyzer backend.
    """
    global MECAB_INFORM, KONLPY_MECAB_INFORM, PECAB_INFORM, FAST_INFORM

    if isinstance(backend, str):
        backend = backend.lower()

    if backend not in ["auto", "mecab", "pecab", "punct", "fast"]:
        raise ValueError(
            f"Oops! '{backend}' is not supported value for `backend`.\n"
            f"Currently kss only supports ['auto', 'pecab', 'mecab', 'punct', 'fast'] for this.\n"
            f"Please check `backend` parameter again ;)\n"
        )

    mecab_backend = MecabAnalyzer()
    pecab_backend = PecabAnalyzer()
    punct_backend = CharacterAnalyzer()
    fast_backed = FastAnalyzer()

    if backend == "fast":
        return fast_backed

    elif backend == "punct":
        return punct_backend

    elif backend == "mecab":
        if mecab_backend._backend is not None:
            return mecab_backend
        else:
            raise ImportError(
                _message_by_user_os(
                    linux_macos="Oops! You specified `backend` as 'mecab', but you don't have mecab in your environment.\n"
                    "If you want to use mecab backend, please install mecab or konlpy.tag.Mecab!\n"
                    "Please refer to following web sites for details:\n"
                    f"- mecab: {_mecab_info_linux_macos}\n"
                    f"- konlpy.tag.Mecab: {_konlpy_info_linux_macos}\n",
                    windows="Oops! You specified `backend` as 'mecab', but you don't have mecab in your environment.\n"
                    "If you want to use mecab backend, please install mecab or konlpy.tag.Mecab!\n"
                    "Please refer to following web sites for details:\n"
                    f"- mecab: {_mecab_info_windows}\n"
                    f"- konlpy.tag.Mecab: {_konlpy_info_windows}\n",
                )
            )

    elif backend == "pecab":
        if pecab_backend._backend is not None:
            return pecab_backend
        else:
            raise ImportError(
                "Oops! You specified `backend` as 'pecab', but you don't have pecab in your environment.\n"
                "If you want to use pecab backend, please install pecab!\n"
                "Please refer to following web sites for details:\n"
                "- pecab: https://github.com/hyunwoongko/pecab\n"
            )

    if backend == "auto":
        if mecab_backend._backend == "mecab":
            if not MECAB_INFORM:
                logger.warning(
                    "Oh! You have mecab in your environment. Kss will take this as a backend! :D\n"
                )
                MECAB_INFORM = True
            return mecab_backend

        elif mecab_backend._backend == "konlpy":
            if not KONLPY_MECAB_INFORM:
                logger.warning(
                    "Oh! You have konlpy.tag.Mecab in your environment. Kss will take this as a backend! :D\n"
                )
                KONLPY_MECAB_INFORM = True
            return mecab_backend

        elif pecab_backend._backend == "pecab":
            if not PECAB_INFORM:

                installation_help_message = _message_by_user_os(
                    linux_macos="For your information, Kss also supports mecab backend.\n"
                    "We recommend you to install mecab or konlpy.tag.Mecab for faster execution of Kss.\n"
                    "Please refer to following web sites for details:\n"
                    f"- mecab: {_mecab_info_linux_macos}\n"
                    f"- konlpy.tag.Mecab: {_konlpy_info_linux_macos}\n",
                    windows="For your information, Kss also supports mecab backend.\n"
                    "We recommend you to install mecab or konlpy.tag.Mecab for faster execution of Kss.\n"
                    "Please refer to following web sites for details:\n"
                    f"- mecab: {_mecab_info_windows}\n"
                    f"- konlpy.tag.Mecab: {_konlpy_info_windows}\n",
                )

                logger.warning(
                    "Because there's no supported C++ morpheme analyzer, "
                    "Kss will take pecab as a backend. :D\n"
                    f"{installation_help_message}"
                )
                PECAB_INFORM = True

            return pecab_backend
        else:
            if not FAST_INFORM:

                logger.warning(
                    "Both mecab and pecab are not supported in your environment.\n"
                    "Kss will take character-based analyzer as a backend. :D\n"
                    "For you information, this is the fast algorithm used Kss version < 3.0.\n"
                    "So it may be inaccurate than other backends.\n"
                )
                FAST_INFORM = True

            return fast_backed


def _check_num_workers(
    inputs: Any, num_workers: Union[int, str]
) -> Optional[Union[int, bool]]:
    """
    Check the number of multiprocessing workers.

    Args:
        inputs (Any): input data
        num_workers (Union[int, str]): the number of multiprocessing workers

    Returns:
        Optional[Union[int, bool]]: the number of multiprocessing workers.
            `None` means maximum number of workers which can be used for now.
            `False` means that it will not use multiprocessing.
    """

    if isinstance(num_workers, float):
        num_workers = int(num_workers)
    elif isinstance(num_workers, str):
        num_workers = num_workers.lower()

    if not isinstance(num_workers, int) and num_workers != "auto":
        raise TypeError(
            f"Oops! '{num_workers}' is not supported value for `num_workers`.\n"
            f"Currently kss only supports [int, 'auto'] for this.\n"
            f"Please check `num_workers` parameter again ;)"
        )
    elif isinstance(num_workers, int) and num_workers < 1:
        raise ValueError(
            f"Oops! `num_workers` must be same or greater than 1, but you input {num_workers}.\n"
            "- You can input 1 for no multiprocessing.\n"
            "- You can input 2 ~ n for multiprocessing.\n"
            "- You can input 'auto' for using maximum workers.\n"
            "Please check `num_workers` parameter again ;)"
        )

    if (
        isinstance(inputs, str)
        or (
            (isinstance(inputs, list) or isinstance(inputs, tuple)) and len(inputs) == 1
        )
        or (isinstance(num_workers, numbers.Number) and num_workers < 2)
    ):
        return False
        # no multiprocessing worker

    elif num_workers == "auto":
        num_workers = None
        # maximum multiprocessing workers

    return num_workers
