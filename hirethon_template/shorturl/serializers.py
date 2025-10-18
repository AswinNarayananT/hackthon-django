from rest_framework import serializers
from hirethon_template.shorturl.models import Organization, Membership, Namespace, ShortURL


class OrganizationSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'created_by', 'created_by_email', 'created_at', 'member_count']
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_member_count(self, obj):
        return obj.memberships.count()


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name']
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Create organization using Django ORM
        organization = Organization.objects.create(
            name=validated_data['name'],
            created_by=user
        )
        
        # Add creator as admin member
        Membership.objects.create(
            user=user,
            organization=organization,
            role='admin'
        )
        
        return organization


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Membership
        fields = ['id', 'user', 'user_email', 'user_name', 'organization', 'organization_name', 'role', 'invited_at']
        read_only_fields = ['id', 'invited_at']


class NamespaceSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    shorturl_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Namespace
        fields = ['id', 'name', 'organization', 'organization_name', 'created_by', 'created_by_email', 'created_at', 'shorturl_count']
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_shorturl_count(self, obj):
        return obj.shorturls.count()


class ShortURLSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    namespace_name = serializers.CharField(source='namespace.name', read_only=True)
    organization_name = serializers.CharField(source='namespace.organization.name', read_only=True)
    short_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ShortURL
        fields = ['id', 'namespace', 'namespace_name', 'organization_name', 'shortcode', 'original_url', 'created_by', 'created_by_email', 'created_at', 'click_count', 'expires_at', 'is_private', 'short_url']
        read_only_fields = ['id', 'created_by', 'created_at', 'click_count']
    
    def get_short_url(self, obj):
        request = self.context.get('request')
        if request:
            return f"{request.build_absolute_uri('/')}{obj.namespace.name}/{obj.shortcode}"
        return f"/{obj.namespace.name}/{obj.shortcode}"
