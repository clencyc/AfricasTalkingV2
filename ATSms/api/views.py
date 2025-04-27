from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action

from django.shortcuts import get_object_or_404
from django.db.models import F, Q
import random

from .models import Mentee, Mentor, Mentorship, Resource
from .serializers import (
    MenteeLanguageSerializer, 
    MenteeSetupSerializer,
    MentorSetupSerializer,
    MentorshipSerializer,
    TechPathwaySerializer,
    ResourceSerializer
)
from .permissions import IsMentor, IsMentee

class MenteeLanguageSelectView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsMentee]
    serializer_class = MenteeLanguageSerializer
    
    def get_object(self):
        return get_object_or_404(Mentee, user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        mentee = self.get_object()
        serializer = self.get_serializer(mentee, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Language updated successfully"})

class MenteeSetupView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MenteeSetupSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MentorSetupView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MentorSetupSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MatchMentorView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsMentee]
    serializer_class = MentorshipSerializer
    
    def create(self, request, *args, **kwargs):
        mentee_id = request.data.get('mentee_id')
        
        # Get the mentee
        mentee = get_object_or_404(Mentee, id=mentee_id)
        
        # Get mentee's county and interests
        county = mentee.county
        interests = mentee.interests
        
        # Find eligible mentors
        # - Same or neighboring county
        # - Match at least one interest
        # - Still have available slots
        # Note: For simplicity, we're just checking same county here
        # In production, you'd need to define neighboring counties
        eligible_mentors = Mentor.objects.filter(
            counties__contains=[county],
            mentees_count__lt=F('max_mentees')
        )
        
        # Filter for mentors with matching interests
        matching_mentors = []
        for mentor in eligible_mentors:
            if any(interest in mentor.expertise for interest in interests):
                matching_mentors.append(mentor)
        
        if not matching_mentors:
            return Response({"message": "No matching mentors found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Randomly select a mentor
        selected_mentor = random.choice(matching_mentors)
        
        # Create mentorship relation
        mentorship = Mentorship.objects.create(
            mentee=mentee,
            mentor=selected_mentor,
            status='active'
        )
        
        # Update mentor's mentee count
        selected_mentor.mentees_count += 1
        selected_mentor.save()
        
        serializer = self.get_serializer(mentorship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TechPathwayView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsMentee]
    serializer_class = TechPathwaySerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        goal = serializer.validated_data['goal']
        
        # Get the mentee to check communication preference
        mentee = get_object_or_404(Mentee, user=request.user)
        comm_pref = mentee.communication_preference
        
        # Fetch resources based on goal/interest
        resources = Resource.objects.filter(tags__contains=[goal])
        
        # Format response based on communication preference
        if comm_pref == 'ussd':
            # For USSD, return short summaries
            result = [{"title": r.title, "sms_text": r.sms_text or r.description[:100]} for r in resources]
        else:
            # For app, return full resources
            serializer = ResourceSerializer(resources, many=True)
            result = serializer.data
        
        return Response({
            "goal": goal,
            "resources": result
        })

class MentorResourceView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsMentor]
    serializer_class = ResourceSerializer
    
    def get_queryset(self):
        return Resource.objects.filter(created_by=self.request.user.mentor_profile)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MenteeResourceView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMentee]
    serializer_class = ResourceSerializer
    
    def get_queryset(self):
        queryset = Resource.objects.all()
        
        # Filter by interest if provided
        interest = self.request.query_params.get('interest', None)
        if interest:
            queryset = queryset.filter(tags__contains=[interest])
            
        # Get mentee for communication preference
        mentee = self.request.user.mentee_profile
        
        # If USSD communication, we'll handle in get method
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        mentee = request.user.mentee_profile
        comm_pref = mentee.communication_preference
        
        if comm_pref == 'ussd':
            # For USSD, return short summaries
            result = [{"title": r.title, "sms_text": r.sms_text or r.description[:100]} for r in queryset]
            return Response(result)
        else:
            # For app, return full resources
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)