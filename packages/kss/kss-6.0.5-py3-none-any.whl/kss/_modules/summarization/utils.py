# Copyright (C) 2021 Hyunwoong Ko <kevin.brain@kakaobrain.com> and Sang Park <sang.park@dnotitia.com>
# All rights reserved.

# This code was copied from Text Rank KR [https://github.com/theeluwin/textrankr]
# And modified by Hyunwoong Ko [https://github.com/hyunwoongko]
from collections import Counter
from itertools import combinations
from typing import List

from kss._modules.morphemes.split_morphemes import split_morphemes
from kss._modules.sentences.split_sentences import split_sentences


class Sentence:
    """
    Notes:
        The purpose of this class is as follows:
            1. In order to use the 'pagerank' function in the networkx library, you need a hashable object.
            2. Summaries should keep the sentence order from its original text to improve the verbosity.

        Note that the 'bow' stands for 'bag-of-words'.
    """

    def __init__(self, index: int, text: str, bow: Counter) -> None:
        self.index: int = index
        self.text: str = text
        self.bow: Counter = bow

    def __str__(self) -> str:
        return self.text

    def __hash__(self) -> int:
        return self.index


def _parse_text_into_sentences(
    text: str, backend: str, strip: bool, ignores: List[str]
) -> List[Sentence]:
    """
    This function splits the given text into sentence candidates using a pre-defined splitter,
    then creates a list of `sentence.Sentence` instances which have bag-of-words inside, tokenized by the given tokenizer.
    """

    # init
    index: int = 0
    duplication_checker: set = set()
    sentences: List[Sentence] = []

    # parse text
    candidates: List[str] = split_sentences(
        text, backend=backend, num_workers=1, strip=strip, ignores=ignores
    )
    for candidate in candidates:
        # cleanse the candidate
        if not len(candidate):
            continue
        if candidate in duplication_checker:
            continue

        # tokenize the candidate
        tokens: List[str] = split_morphemes(candidate, backend=backend, num_workers=1)
        if len(tokens) < 2:
            continue
        duplication_checker.add(candidate)

        # create a sentence
        bow: Counter = Counter(tokens)
        sentence = Sentence(index, candidate, bow)
        sentences.append(sentence)
        index += 1

    # return
    return sentences


def _multiset_jaccard_index(counter1: Counter, counter2: Counter) -> float:
    """
    Calculates the jaccard index between two given multisets.
    Note that a `Counter` instance can be used for representing multisets.
    """
    intersection_count: int = sum((counter1 & counter2).values())
    union_count: int = sum((counter1 | counter2).values())
    try:
        return intersection_count / union_count
    except ZeroDivisionError:
        return 0.0


def _build_sentence_graph(sentences: List[Sentence], tolerance: float):
    """
    Builds a `networkx.Graph` instance, using sentences as nodes.
    An edge weight is determined by the jaccard index between two sentences,
    but the edge will be ignored if the weight is lower than the given tolerance.
    """
    from networkx import Graph

    # init
    graph: Graph = Graph()

    # add nodes
    graph.add_nodes_from(sentences)

    # add edges
    for sentence1, sentence2 in combinations(sentences, 2):
        weight: float = _multiset_jaccard_index(sentence1.bow, sentence2.bow)
        if weight > tolerance:
            graph.add_edge(sentence1, sentence2, weight=weight)

    # return
    return graph

