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
    print(n2g('吴子豪'))
    print(n2g('Donald Trump', return_probability=True))
    ```

    stdout:

    ```
    Gender.Male
    (<Gender.Male: 'male'>, 0.9990234375)
    ```