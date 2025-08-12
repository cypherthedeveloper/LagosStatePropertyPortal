from rest_framework import serializers
from .models import ComplianceReport, PropertyCompliance, ComplianceRequirement, PropertyRequirementCheck
from properties.serializers import PropertyListSerializer
from users.serializers import UserSerializer


class ComplianceRequirementSerializer(serializers.ModelSerializer):
    """Serializer for compliance requirements."""
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ComplianceRequirement
        fields = ['id', 'title', 'description', 'is_active', 'created_at', 'updated_at', 'created_by']
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PropertyRequirementCheckSerializer(serializers.ModelSerializer):
    """Serializer for property requirement checks."""
    requirement = ComplianceRequirementSerializer(read_only=True)
    requirement_id = serializers.PrimaryKeyRelatedField(
        queryset=ComplianceRequirement.objects.all(),
        write_only=True,
        source='requirement'
    )
    checked_by = UserSerializer(read_only=True)
    
    class Meta:
        model = PropertyRequirementCheck
        fields = ['id', 'property_compliance', 'requirement', 'requirement_id', 'status', 
                  'checked_by', 'checked_at', 'notes']
        read_only_fields = ['checked_at']
    
    def update(self, instance, validated_data):
        validated_data['checked_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class PropertyComplianceSerializer(serializers.ModelSerializer):
    """Serializer for property compliance."""
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=PropertyCompliance.objects.all(),
        write_only=True,
        source='property',
        required=False
    )
    reviewed_by = UserSerializer(read_only=True)
    requirement_checks = PropertyRequirementCheckSerializer(many=True, read_only=True)
    
    class Meta:
        model = PropertyCompliance
        fields = ['id', 'property', 'property_id', 'compliance_status', 'reviewed_by', 
                  'reviewed_at', 'notes', 'last_inspection_date', 'next_inspection_date',
                  'requirement_checks']
        read_only_fields = ['reviewed_at']
    
    def update(self, instance, validated_data):
        validated_data['reviewed_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class ComplianceReportSerializer(serializers.ModelSerializer):
    """Serializer for compliance reports."""
    generated_by = UserSerializer(read_only=True)
    report_file = serializers.FileField(required=False)
    
    class Meta:
        model = ComplianceReport
        fields = ['id', 'title', 'description', 'generated_by', 'created_at', 
                  'updated_at', 'status', 'report_file']
        read_only_fields = ['created_at', 'updated_at', 'generated_by']
    
    def create(self, validated_data):
        validated_data['generated_by'] = self.context['request'].user
        return super().create(validated_data)