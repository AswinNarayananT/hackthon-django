from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction, models

from hirethon_template.shorturl.models import Organization, Membership, Namespace
from hirethon_template.shorturl.serializers import (
    OrganizationSerializer, 
    OrganizationCreateSerializer,
    MembershipSerializer,
    NamespaceSerializer
)


class OrganizationListCreateAPIView(generics.ListCreateAPIView):
    """API view to list and create organizations"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    def get_queryset(self):
        # Get organizations where user is a member or owner
        user = self.request.user
        return Organization.objects.filter(
            models.Q(created_by=user) | 
            models.Q(memberships__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save()


class OrganizationDetailAPIView(generics.RetrieveAPIView):
    """API view to get organization details"""
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(
            models.Q(created_by=user) | 
            models.Q(memberships__user=user)
        ).distinct()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_members(request, pk):
    """API view to get organization members"""
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user has access to this organization
    if not (organization.created_by == request.user or 
            organization.memberships.filter(user=request.user).exists()):
        return Response({'error': 'You do not have access to this organization.'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    members = organization.memberships.all().select_related('user')
    serializer = MembershipSerializer(members, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_namespaces(request, pk):
    """API view to get organization namespaces"""
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user has access to this organization
    if not (organization.created_by == request.user or 
            organization.memberships.filter(user=request.user).exists()):
        return Response({'error': 'You do not have access to this organization.'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    namespaces = organization.namespaces.all()
    serializer = NamespaceSerializer(namespaces, many=True, context={'request': request})
    return Response(serializer.data)