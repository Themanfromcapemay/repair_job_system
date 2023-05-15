from rest_framework import serializers

from authentication.models import CustomUser
from .models import Customer, JobCard, Images


class QueriedJobCardSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name')

    class Meta:
        model = JobCard
        fields = ('id', 'job_number', 'customer_name', 'product_name', 'complaint_or_query', 'job_status')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class JobCardSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    pop_image = serializers.ImageField(required=False)
    before_assessment_image = serializers.ImageField(required=False)
    after_assessment_image = serializers.ImageField(required=False)
    assessment_environment_image = serializers.ImageField(required=False)

    class Meta:
        model = JobCard
        fields = '__all__'
        read_only_fields = ('job_number', 'date_created', 'last_modified_by', 'last_modified_at')

    def create(self, validated_data):
        customer_data = validated_data.pop('customer')
        customer = Customer.objects.create(**customer_data)

        job_card = JobCard(customer=customer, **validated_data)
        job_card.save()
        return job_card


# List Jobs and Job status
class OpenInProgressJobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCard
        fields = ('job_number', 'job_status')


class TechnicalInfoJobCardSerializer(serializers.ModelSerializer):
    pop_image = serializers.ImageField(required=False)
    before_assessment_image = serializers.ImageField(required=False)
    after_assessment_image = serializers.ImageField(required=False)
    assessment_environment_image = serializers.ImageField(required=False)

    class Meta:
        model = JobCard
        fields = '__all__'


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = [
            'id',
            'pop_image',
            'before_assessment_image1',
            'before_assessment_image2',
            'before_assessment_image3',
            'after_assessment_image1',
            'after_assessment_image2',
            'after_assessment_image3',
            'assessment_environment_image'
        ]