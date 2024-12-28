# fascism-news-tracker


# Requirements
## Setting up Keyring
To properly run the package you will need to set up a keyring with your API key. Run the following in an empty .py file after installing the "keyring" package. You only need to do this once.
```python
import keyring as kr

kr.set_password('OpenNewsAPI','api_key',"your_api_key")
```

## Setting up SpaCY
To properly run the package we will need to install a NLP pipeline. Run the following code in your pip/conda terminal. You will only need to do this once.
```shell
python -m spacy download en_core_web_lg
```

## Python Version
Python 3.10
