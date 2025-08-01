# Copyright (C) 2021 Hyunwoong Ko <kevin.brain@kakaobrain.com> and Sang Park <sang.park@dnotitia.com>
# All rights reserved.

from typing import List, Tuple


def _get_linux_mecab():
    from mecab import MeCab

    analyzer = MeCab()
    analyzer.morphs("_")
    backend = "mecab"
    return analyzer, backend


def _get_linux_konlpy_mecab():
    from konlpy.tag import Mecab

    analyzer = Mecab()
    analyzer.morphs("_")
    backend = "konlpy"
    return analyzer, backend


def _get_windows_mecab():
    import MeCab

    analyzer = MeCab.Tagger()

    def pos(text: str) -> List[Tuple[str, str]]:
        """Mecab MSVC wrapper"""
        node = analyzer.parseToNode(text)
        outputs = []

        while node:
            surface = node.surface
            tag = node.feature.split(",")[0]
            if "BOS" not in tag and "EOS" not in tag:
                outputs.append((surface, tag))
            node = node.next

        return outputs

    setattr(analyzer, "pos", pos)
    analyzer.pos("_")
    backend = "mecab"
    return analyzer, backend


def _get_windows_konlpy_mecab():
    from konlpy.tag import Mecab

    analyzer = Mecab(dicpath=r"C:\mecab\mecab-ko-dic")
    analyzer.pos("_")
    backend = "konlpy"
    return analyzer, backend


def _get_mecab():
    """
    Try to import and get mecab morpheme analyzer

    Returns:
        Tuple[Optional[Union[mecab.MeCab, konlpy.tag.Mecab, Mecab.Tagger]], Optional[str]]:
            mecab morpheme analyzer and its backend
    """
    try:
        # python-mecab-kor (Linux/MacOS)
        return _get_linux_mecab()
    except Exception:
        try:
            # konlpy (Linux/MacOS)
            return _get_linux_konlpy_mecab()
        except Exception:
            try:
                # mecab-python-msvc (Windows)
                return _get_windows_mecab()
            except Exception:
                try:
                    # konlpy (Windows)
                    return _get_windows_konlpy_mecab()
                except Exception:
                    return None, None


def _get_pecab():
    """
    Try to import and get pecab morpheme analyzer

    Returns:
        Tuple[Optional[pecab.PeCab], Optional[str]]:
            pecab morpheme analyzer and its backend
    """
    try:
        from pecab import PeCab

        analyzer = PeCab()
        analyzer.morphs("_")
        backend = "pecab"
        return analyzer, backend
    except Exception:
        return None, None


def _preserve_space(
    text: str,
    tokens: List[Tuple[str, str]],
    spaces: str,
) -> List[Tuple[str, str]]:
    """
    Restore spaces from analyzed results

    Args:
        text (str): input text
        tokens (List[Tuple[str, str]]): analyzed results
        spaces (str): space tokens to add

    Returns:
        List[Tuple[str, str]]: analyzed results with space
    """
    results = list()
    len_text = len(text)
    len_tokens = len(tokens)
    text_idx = 0
    token_idx = 0

    while text_idx < len_text:
        character = text[text_idx]
        if character in spaces:
            results.append((character, "SP"))
            text_idx += 1
        else:
            if token_idx < len_tokens:
                token = tokens[token_idx]
                results.append(token)
                text_idx += len(token[0])
                token_idx += 1
            else:
                break
    return results


def _reset_spaces(text: str, tokens: List[Tuple[str, str]]):
    tokens = [(text, pos) for text, pos in tokens if pos != "SP"]
    return _preserve_space(text, tokens, " \n\r\t\v\f")
