import datetime
from haystack import indexes
from parlhand import models


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='name')
    phid = indexes.CharField(model_attr='phid')

    def get_model(self):
        return models.Person

class MinisterialIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='label')

    def get_model(self):
        return models.MinisterialPosition

class MinistryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='name')

    def get_model(self):
        return models.Ministry
