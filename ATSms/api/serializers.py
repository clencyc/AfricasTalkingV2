from rest_framework import serializers
from .models import User, Mentee, Mentor, Mentorship, Resource
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'is_mentor', 'is_mentee')
        read_only_fields = ('id', 'is_mentor', 'is_mentee')

class MenteeLanguageSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=['en', 'sw'])
    
    def update(self, instance, validated_data):
        instance.language = validated_data.get('language', instance.language)
        instance.save()
        return instance

class MenteeSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentee
        fields = ('name', 'age', 'county', 'device', 'interests', 'communication_preference')
    
    def create(self, validated_data):
        user = self.context['request'].user
        user.is_mentee = True
        user.save()
        
        mentee, created = Mentee.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return mentee

class MentorSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentor
        fields = ('name', 'expertise', 'language_preference', 'counties', 'max_mentees', 'visibility')
    
    def create(self, validated_data):
        user = self.context['request'].user
        user.is_mentor = True
        user.save()
        
        mentor, created = Mentor.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return mentor

class MentorshipSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source='mentor.name', read_only=True)
    mentee_name = serializers.CharField(source='mentee.name', read_only=True)
    
    class Meta:
        model = Mentorship
        fields = ('id', 'mentor', 'mentee', 'mentor_name', 'mentee_name', 'status', 'created_at')
        read_only_fields = ('id', 'created_at')

class TechPathwaySerializer(serializers.Serializer):
    goal = serializers.CharField(max_length=50)

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('id', 'title', 'description', 'tags', 'link', 'sms_text', 'created_by', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.mentor_profile
        return super().create(validated_data)