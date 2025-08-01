# Name2Gender

From names in multiple languages to gender.

## Installation

- From [PyPi](https://pypi.org/project/name2gender/)

```
pip install -U name2gender
```

or

```
uv add -U name2gender
```

- From [Github](https://github.com/vortezwohl/Name2Gender/releases)

```
pip install git+https://github.com/vortezwohl/Name2Gender.git
```

## Quick Start

1. Import SDKs

    ```python
    from name2gender import Name2Gender, Gender
    ```

2. Gender recognition based on names

    ```python
    n2g = Name2Gender()
    names = ['吴子豪', '吴彦祖', '梅艳芳', '张曼玉',
             'Donald Trump', 'Ivanka Trump',
             'Justin Bieber', 'The Weeknd',
             'Luigi Nicholas Mangione',
             'Elizabeth II', 'Henry VIII']
    for name in names:
        _gender, _prob = n2g(name, return_probability=True)
        print(name, 'is', _gender, 'with an probability of', f'{_prob * 100:.2f}%')

    ```

    stdout:

    ```
   吴子豪 is Gender.Male with an probability of 99.71%
   吴彦祖 is Gender.Male with an probability of 100.00%
   梅艳芳 is Gender.Female with an probability of 99.99%
   张曼玉 is Gender.Female with an probability of 99.92%
   Donald Trump is Gender.Male with an probability of 99.90%
   Ivanka Trump is Gender.Female with an probability of 99.66%
   Justin Bieber is Gender.Male with an probability of 100.00%
   The Weeknd is Gender.Male with an probability of 97.66%
   Luigi Nicholas Mangione is Gender.Male with an probability of 99.27%
   Elizabeth II is Gender.Female with an probability of 99.71%
   Henry VIII is Gender.Male with an probability of 99.90%
    ```