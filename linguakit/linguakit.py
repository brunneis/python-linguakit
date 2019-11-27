#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pexpect
from pathlib import Path
from os import mkdir, rmdir, remove, rename, path
from shutil import rmtree
import urllib.request
import zipfile
import sys

BASE_PATH = f'{Path.home()}/'
LINGUAKIT_PATH = f'{BASE_PATH}.linguakit-streaming/'


def download_linguakit():
    try:
        rmtree(LINGUAKIT_PATH)
    except Exception:
        pass
    url = 'https://github.com/brunneis/linguakit-streaming/archive/master.zip'
    zip_path = f'{BASE_PATH}master.zip'
    print('Downloading linguakit-streaming...')
    urllib.request.urlretrieve(url, zip_path)
    print('[OK!]')
    print('Installing linguakit-streaming...')
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(BASE_PATH)
    remove(zip_path)
    rename(f'{BASE_PATH}/linguakit-streaming-master', LINGUAKIT_PATH)
    print('[OK!]')
    print('Installing the Python wrapper...')


if not path.exists(LINGUAKIT_PATH):
    download_linguakit()


class PerlModule:
    def __init__(self, path):
        self.child = pexpect.spawn(f"perl {path}", encoding='utf-8')

    def _expect_prompt(self):
        self.child.expect('\nEOC')

    @staticmethod
    def list_to_perl_str(items):
        if isinstance(items, list):
            items = '", "'.join(items)
        return f'("{items}")'

    @staticmethod
    def escape_perl_chars(items):
        if isinstance(items, str):
            items = [items]
        chars = ['@', '$', '"']
        escaped_items = []
        for item in items:
            escaped_item = item
            for char in chars:
                escaped_item = escaped_item.replace(char, f'\\{char}')
            escaped_items.append(escaped_item)
        return escaped_items

    def _read(self):
        output = self.child.before
        output = output.replace('\r', '')
        output = output.split('\n')[2:]
        return output

    def exec(self, items):
        escaped_items = PerlModule.escape_perl_chars(items)
        escaped_items_str = PerlModule.list_to_perl_str(escaped_items)
        self.child.sendline(f'{escaped_items_str};')
        self._expect_prompt()
        return self._read()


class SentencesModule(PerlModule):
    def __init__(self, lang):
        super().__init__(f'{LINGUAKIT_PATH}tagger/{lang}/sentences-{lang}_exe.perl')


class TokensModule(PerlModule):
    def __init__(self, lang):
        super().__init__(f'{LINGUAKIT_PATH}tagger/{lang}/tokens-{lang}_exe.perl')


class SplitterModule(PerlModule):
    def __init__(self, lang):
        super().__init__(f'{LINGUAKIT_PATH}tagger/{lang}/splitter-{lang}_exe.perl')


class NERModule(PerlModule):
    def __init__(self, lang):
        super().__init__(f'{LINGUAKIT_PATH}tagger/{lang}/ner-{lang}_exe.perl')


class TaggerModule(PerlModule):
    def __init__(self, lang):
        super().__init__(f'{LINGUAKIT_PATH}tagger/{lang}/tagger-{lang}_exe.perl')


class SentimentModule(PerlModule):
    def __init__(self, lang):
        super().__init__(f'{LINGUAKIT_PATH}sentiment/nbayes.perl')
        self.child.sendline(f'init("{lang}");')

    def _read(self):
        read = super()._read()
        print(f'READ ----> {read}')
        return ' '.join(read).split('\t')[1:]
        # return ' '.join(super()._read()).split('\t')[1:]


class LemmaModule(PerlModule):
    def __init__(self, lang):
        super().__init__(f'{LINGUAKIT_PATH}tagger/{lang}/lemma-{lang}_exe.perl')


class KeywordsModule(PerlModule):
    def __init__(self, lang):
        super().__init__(f'{LINGUAKIT_PATH}keywords/keywords_exe.perl')
        self.child.sendline(f'init("{lang}");')

    def exec(self, items, th=30):
        items = [str(th)] + items
        return super().exec(items)

    # def _read(self):
    #     return [tuple(item.split('\t')) for item in super()._read()]


# class SummarizerModule(PerlModule):
#     def __init__(self):
#         super().__init__(f'{LINGUAKIT_PATH}summarizer/summarizer_exe.perl')

#     def exec(self, sentences, keywords, percentage):
#         sentences_str = PerlModule.list_to_perl_str(sentences)
#         escaped_sentences_str = PerlModule.escape_perl_chars(sentences_str)
#         self.child.sendline(f'{escaped_sentences_str};')

#         keywords_str = PerlModule.list_to_perl_str(keywords)
#         escaped_keywords_str = PerlModule.escape_perl_chars(keywords_str)
#         self.child.sendline(f'{escaped_keywords_str};')

#         self.child.sendline(f'"{percentage}";')

#         self._expect_prompt()
#         return self._read()


class Sentiment:
    def __init__(self, lang):
        self.sentences_es = SentencesModule(lang)
        self.tokens_es = TokensModule(lang)
        self.splitter_es = SplitterModule(lang)
        self.ner_es = NERModule(lang)
        self.tagger_es = TaggerModule(lang)
        self.sentiment = SentimentModule(lang)

    def exec(self, text):
        sentences_o = self.sentences_es.exec(text)
        tokens_o = self.tokens_es.exec(sentences_o)
        splitter_o = self.splitter_es.exec(tokens_o)
        ner_o = self.ner_es.exec(splitter_o)
        tagger_o = self.tagger_es.exec(ner_o)
        sentiment_o = self.sentiment.exec(tagger_o)

        tag, proba = sentiment_o
        if tag == 'POSITIVE':
            polarity = 1
        elif tag == 'NEGATIVE':
            polarity = -1
        elif tag == 'NONE':
            polarity = 0

        return {'polarity': polarity, 'proba': proba}


class Summarizer:
    def __init__(self, lang):
        self.sentences_es = SentencesModule(lang)
        self.tokens_es = TokensModule(lang)
        self.splitter_es = SplitterModule(lang)
        self.lemma_es = LemmaModule(lang)
        self.tagger_es = TaggerModule(lang)
        self.keywords = KeywordsModule(lang)
        self.summarizer = SummarizerModule()

    def exec(self, text, percentage=50):
        sentences_o = self.sentences_es.exec(text)
        tokens_o = self.tokens_es.exec(sentences_o)
        splitter_o = self.splitter_es.exec(tokens_o)
        lemma_o = self.lemma_es.exec(splitter_o)
        tagger_o = self.tagger_es.exec(lemma_o)
        keywords_o = self.keywords.exec(tagger_o, percentage)

        summarizer_o = self.summarizer.exec(splitter_o, keywords_o, percentage)

        print(summarizer_o)
