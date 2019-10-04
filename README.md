# python-linguakit

## Local Installation

### Install dependencies (Ubuntu)
```bash
$ apt-get update \
&& apt-get -y install git build-essential zlib1g-dev \
&& cpan PerlIO::gzip \
&& cpan LWP::UserAgent
```

### Install the Python wrapper
```python
$ pip install linguakit
```
> After the installation, the first import of the `linguakit` package will trigger the download of `linguakit-streaming` with all the needed Perl scripts if they are not yet present.

```bash
$ python -c "import linguakit"
Downloading linguakit-streaming...
[OK!]
Installing linguakit-streaming...
[OK!]
Installing the Python wrapper...
```

## Docker Container

```bash
$ docker run -ti brunneis/python-linguakit
Python 3.7.3 (default, Jun 19 2019, 08:47:56) 
[GCC 7.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

## Existing Modules
### Sentiment

#### `class linguakit.Sentiment(lang)`
##### `exec(input_text)`

```python
>>> from linguakit import Sentiment

>>> sent = Sentiment('es')

>>> result = sent.exec('Hacía bastante que no salía del cine tan feliz. Gracias Christopher Nolan por @Interstellar, merece la pena cada una de las 3h que dura.')

>>> print(result)
{'polarity': 1, 'proba': '0.999866470435652'}
```