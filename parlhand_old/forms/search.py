from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from haystack import connections
from haystack.constants import DEFAULT_ALIAS
from haystack.forms import ModelSearchForm, model_choices
from haystack.query import EmptySearchQuerySet, SearchQuerySet, SQ

class SpellingSearchQuerySet(SearchQuerySet):
    def models(self,*mods):
        # We have to redefine this because Whoosh & Haystack don't play well with model filtering
        from haystack.utils import get_model_ct
        mods = [get_model_ct(m) for m in mods]
        return self.filter(django_ct__in=mods)

class SpellingSearchForm(ModelSearchForm):
    """
        We need to make a new form as permissions to view objects are a bit finicky.
        This form allows us to perform the base query then restrict it to just those
        of interest.

        TODO: This might not scale well, so it may need to be looked at in production.
    """

    def __init__(self,*args, **kwargs):
        kwargs['searchqueryset'] = SpellingSearchQuerySet()
        super(SpellingSearchForm, self).__init__(*args, **kwargs)


    def get_models(self):
        """Return an alphabetical list of model classes in the index."""
        search_models = []

        if self.is_valid():
            for model in self.cleaned_data['models']:
                search_models.append(models.get_model(*model.split('.')))

        return search_models


    def search(self,repeat_search=False):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(SpellingSearchForm, self).search()
        sqs = sqs.models(*self.get_models())
        self.repeat_search = repeat_search

        self.has_spelling_suggestions = False
        if not self.repeat_search:

            if sqs.count() < 5:
                self.check_spelling(sqs)

            if sqs.count() == 0:
                if sqs.count() == 0 and self.has_spelling_suggestions:
                    self.auto_correct_spell_search = True
                    self.cleaned_data['q'] = self.suggested_query
                # Re run the query with the updated details
                sqs = self.search(repeat_search=True)
        return sqs

    def check_spelling(self,sqs):
        if self.cleaned_data.get('q',""):
            original_query = self.cleaned_data.get('q',"")

            from urllib import quote_plus
            suggestions = []
            has_suggestions = False
            suggested_query = []

            #lets assume the words are ordered in importance
            # So we suggest words in order
            optimal_query = original_query
            for token in self.cleaned_data.get('q',"").split(" "):
                if token: # remove blanks
                    suggestion = self.searchqueryset.spelling_suggestion(token)
                    print suggestion
                    if suggestion:
                        test_query = optimal_query.replace(token,suggestion)
                        # Haystack can *over correct* so we'll do a quick search with the
                        # suggested spelling to compare words against
                        try:
                            SpellingSearchQuerySet().auto_query(test_query)[0]
                            suggested_query.append(suggestion)
                            has_suggestions = True
                            optimal_query = test_query
                        except:
                            suggestion = None
                    else:
                        suggested_query.append(token)
                    suggestions.append((token,suggestion))
            self.spelling_suggestions = suggestions
            self.has_spelling_suggestions = has_suggestions
            self.original_query = self.cleaned_data.get('q')
            self.suggested_query = quote_plus(' '.join(suggested_query),safe="")
