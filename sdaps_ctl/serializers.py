from django.forms import widgets
from rest_framework import serializers
from rest_framework import relations
from rest_framework import fields
from sdaps_ctl.models import QObject, QAnswer

class QObjectSerializer(serializers.ModelSerializer):
    #children = relations.PrimaryKeyRelatedField(many=False, read_only=True)
    #answers = relations.PrimaryKeyRelatedField(many=False, read_only=True)

    #children = fields.Field()
    #answers = fields.Field()

    class Meta:
        model = QObject
        fields = ('id', 'text', 'qtype', 'answers', 'children')

    # This ignores any write to "qtype".
    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.text = attrs.get('text', instance.text)
            return instance

        return QObject(survey=self.context['survey'], **attrs)

class QAnswerSerializer(serializers.ModelSerializer):
    qobject = relations.PrimaryKeyRelatedField(many=False, required=True)

    class Meta:
        model = QAnswer
        fields = ('id', 'text', 'qobject', 'btype', 'height', 'columns')

    # This ignores any write to "btype".
    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.text = attrs.get('text', instance.text)
            instance.height = attrs.get('height', instance.text)
            instance.columns = attrs.get('columns', instance.text)
            return instance

        return QAnswer(**attrs)

