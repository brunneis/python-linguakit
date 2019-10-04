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

    def list_to_perl_str(self, items):
        if isinstance(items, list):
            items = '", "'.join(items)
        return f'("{items}")'

    def _read(self):
        output = self.child.before
        output = output.replace('\r', '')
        output = output.split('\n')[2:]
        return output

    def exec(self, cmd):
        self.child.sendline(cmd)
        self._expect_prompt()
        return self._read()

    def run(self, items):
        items_str = self.list_to_perl_str(items)
        escaped_items_str = PerlModule.escape_perl_chars(items_str)
        # print(f'{escaped_items_str};')
        return self.exec(f'{escaped_items_str};')

    @staticmethod
    def escape_perl_chars(text):
        chars = ['@', '$']
        for char in chars:
            text = text.replace(char, f'\\{char}')
        return text


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
        self.child.sendline(f'load("{lang}");')

    def _read(self):
        return ' '.join(super()._read()).split('\t')[1:]


class Sentiment:
    def __init__(self, lang):
        self.sentences_es = SentencesModule(lang)
        self.tokens_es = TokensModule(lang)
        self.splitter_es = SplitterModule(lang)
        self.ner_es = NERModule(lang)
        self.tagger_es = TaggerModule(lang)
        self.sentiment = SentimentModule(lang)

    def exec(self, text):
        sentences_o = self.sentences_es.run(text)
        tokens_o = self.tokens_es.run(sentences_o)
        splitter_o = self.splitter_es.run(tokens_o)
        ner_o = self.ner_es.run(splitter_o)
        tagger_o = self.tagger_es.run(ner_o)
        sentiment_o = self.sentiment.run(tagger_o)

        tag, proba = sentiment_o
        if tag == 'POSITIVE':
            polarity = 1
        elif tag == 'NEGATIVE':
            polarity = -1
        elif tag == 'NONE':
            polarity = 0

        return {'polarity': polarity, 'proba': proba}