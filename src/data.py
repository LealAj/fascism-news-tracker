"""
This file will define all the data objects
associated with handling data
"""
from typing import Optional
import keyring as kr
import requests as rq
import spacy
import string


class GetNewsData:
    def __init__(self):
        # lazy loading keyring implementation
        self._api_key = None
    
    
    def make_request(self) -> dict:
        """
        Method to make request
        to the Open News API.

        Returns:
            dict: headlines dictionary
        """
        return rq.get(self._make_api_url()).json()
        
    
    def _make_api_url(self) -> str:
        """
        Helper method to generate 
        open news API url. Given
        the parameters of the
        project, we will variables
        values consistent but able
        to update at some point later
        if interested

        Returns:
            str: url to make request
        """            
        return f"https://newsapi.org/v2/top-headlines?country=us&category=politics&pageSize=60&apiKey={self.api_key}"
    
        
    @property
    def api_key(self) -> None:
        """
        Property method to call api setter
        """
        if self._api_key is None:
            self._api_key = kr.get_password('OpenNewsAPI', 'api_key')
        return self._api_key
    
    
    @api_key.setter
    def api_key(self, key:str) -> None:
        """
        property method to set API key

        Args:
            key (str): API key retrieved from key ring
        """
        if isinstance(str, key) is True:
            self._api_key = key
        else:
            raise ValueError("No API key found on Keyring. Please see README for keyring implementation")




class ArticleScorer:
    def __init__(self, articles_json:dict, comp_txt:str):
        """
        This object will score the articles json produced
        by GetNewsData object using cosign similarity
        with the provided text.

        Args:
            articles_json (dict): json of news articles created by GetNewsData
            comp_txt (str): text to compare article data with for cosign similarity calculation

        Raises:
            article_json (ValueError):  Value error if value is not dictionary
            comp_txt (ValueError): value error if not a valid string
        """
        # setting NLP pipeline
        self._nlp = spacy.load('en_core_web_lg')
        
        # setting articles
        if isinstance(articles_json, dict) is True:
            self.articles = articles_json
        else:
            raise ValueError('Please pass a valid dictionary of articles to score.')
        
        # setting comparison text
        if isinstance(comp_txt, str) is True:
            self.comp_txt = comp_txt                
        else:
            raise ValueError('Please pass a valid comparison text to use when scoring.')
        

    def calc_scores(self, write_file_path: Optional[str] = None, sort:bool = True,) -> dict:
        """
        Method to calculate scores of articles by calculating
        cosign similarity between provided text and article info.

        Args:
            sort (bool, optional): Sort articles from highest similarity to lowest. Defaults to True.

        Returns:
            dict: articles dictionary with sim score key for each article
        """
        # creating copy of articles
        scored_articles = self.articles
        
        # iterating through each article
        for idx, article in enumerate(scored_articles['articles']):
            # making article tup for each characteristic to score
            article_tup = (article['title'], article['description'], article['content'])
            # adding score to JSON
            scored_articles['articles'][idx]['sim_score'] = self._score_article(article_tup)
        
        # sorting if requested
        if sort is True:
            scored_articles['articles'] = sorted(scored_articles['articles'], key = lambda x: x['sim_score'], reverse = True)  
        
        # implementing file writing
        if isinstance(write_file_path, str) is True: 
            with open(write_file_path, 'w') as file_writer: 
                file_writer.write(str(scored_articles))
                        
        # returning scored json copy
        return scored_articles
        
            
    def _score_article(self, article_tup:tuple) -> float:
        """
        Method that takes article tuple and calculates sim score
        based on article text and passed value/phrase
        

        Args:
            article_tup (tuple): article tuple consisting of (title, description, content)

        Returns:
            float: avg sim score across all 3 texts
        """
        # setting values
        score_list = []
        comp_doc = self._nlp(self.comp_txt)
        
        # iterating through values in tuple
        for text in article_tup:
            # text is None, skip
            if text != None:
                # clean text
                clean_text = self._clean_text(text)
                # passing text through NLP
                doc = self._nlp(clean_text)
                # appending similarity score to value
                score_list.append(self._calc_sim_score(doc, comp_doc))
        
        # returning average of all scores
        return round(sum(score_list)/len(score_list),2)
            
            
    def _calc_sim_score(self, text_doc:spacy.language.Doc,  comp_doc:spacy.language.Doc) -> float:
        """
        helper method to calculate the similarity score between two docs

        Args:
            text (str): article text as spacy Doc
            comp_text (str): compare text as spacy Doc

        Returns:
            float: similarity score
        """
        return text_doc.similarity(comp_doc)
        
    
    def _clean_text(self, text:Optional[str]) -> Optional[str]:
        """
        Prepares string for NLP process in the following way:
        
        1. removes punc
        2. lower
        3. strip
        4. removes stop words
        5. removes digits

        Args:
            text (str): text to clean

        Returns:
            str: clean text
        """
        
        # if text is not none
        if text != None:
            # lower string removing punctuation            
            text = text.lower().strip().translate(str.maketrans('','', string.punctuation))
            doc_text = self._nlp(text)
            # removing stop words
            return ' '.join([token.text for token in doc_text if not ((token.is_stop) or (token.is_digit) or (token.is_punct))])
        
