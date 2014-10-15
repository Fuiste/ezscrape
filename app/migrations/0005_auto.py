# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field topics on 'Property'
        m2m_table_name = db.shorten_name(u'app_property_topics')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('property', models.ForeignKey(orm[u'app.property'], null=False)),
            ('topic', models.ForeignKey(orm[u'app.topic'], null=False))
        ))
        db.create_unique(m2m_table_name, ['property_id', 'topic_id'])


    def backwards(self, orm):
        # Removing M2M table for field topics on 'Property'
        db.delete_table(db.shorten_name(u'app_property_topics'))


    models = {
        u'app.property': {
            'Meta': {'object_name': 'Property'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reviews': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['app.Review']", 'null': 'True', 'symmetrical': 'False'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['app.Topic']", 'null': 'True', 'symmetrical': 'False'}),
            'topics_analyzed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'topics_processing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'upstream_id': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'yelp_processing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'yelp_scraped': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'yelp_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'})
        },
        u'app.review': {
            'Meta': {'object_name': 'Review'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 15, 0, 0)'}),
            'grade': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        },
        u'app.scrapedtextprovider': {
            'Meta': {'object_name': 'ScrapedTextProvider'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rated': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'app.topic': {
            'Meta': {'object_name': 'Topic'},
            'category': ('django.db.models.fields.CharField', [], {'default': "'NGRAM'", 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'reviews': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['app.Review']", 'null': 'True', 'symmetrical': 'False'})
        }
    }

    complete_apps = ['app']