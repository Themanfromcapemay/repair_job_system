import io

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.template.loader import get_template
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from xhtml2pdf import pisa

from .models import JobCard, Images
from .serializers import JobCardSerializer, QueriedJobCardSerializer, ImagesSerializer


def export_job_cards(request):
    job_cards = JobCard.objects.all().values()
    df = pd.DataFrame.from_records(job_cards)

    # Convert all entries to strings
    df = df.astype(str)

    # Fill NaN values with "Not provided"
    df.fillna("Not provided", inplace=True)

    # Save the DataFrame to a virtual file object
    virtual_file = io.BytesIO()
    df.to_excel(virtual_file, index=False, engine='openpyxl')

    # Serve the workbook as an Excel file
    virtual_file.seek(0)
    response = FileResponse(
        virtual_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=job_cards.xlsx'
    return response


class DatabaseDetailsView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        total_job_cards = JobCard.objects.count()
        open_and_in_progress_job_cards = JobCard.objects.filter(job_status__in=['Open', 'In Progress']).count()

        data = {
            'total_job_cards': total_job_cards,
            'open_and_in_progress_job_cards': open_and_in_progress_job_cards,
        }
        return Response(data)


@api_view(['POST'])
@login_required
def create_job(request):
    data = request.data.copy()
    customer_data = data.pop('customer')
    data['customer'] = customer_data
    serializer = JobCardSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobCardCreateView(generics.CreateAPIView):
    queryset = JobCard.objects.all()
    serializer_class = JobCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except ValidationError as e:
            raise ValidationError({"detail": str(e)})


class QueryJobView(generics.ListAPIView):
    serializer_class = QueriedJobCardSerializer

    def get_queryset(self):
        queryset = JobCard.objects.all().select_related('customer')
        search_type = self.request.query_params.get('search_type', None)
        search_param = self.request.query_params.get('search_param', None)

        if search_type is not None and search_param is not None:
            if search_type == "job_number":
                queryset = queryset.filter(job_number=search_param)
            elif search_type == "customer_name":
                queryset = queryset.filter(customer__name__icontains=search_param)
            elif search_type == "contact_number":
                queryset = queryset.filter(customer__contact_number__icontains=search_param)
            elif search_type == "job_status":
                queryset = queryset.filter(job_status=search_param)

        return queryset


class JobCardUpdateView(generics.UpdateAPIView):
    queryset = JobCard.objects.all()
    serializer_class = JobCardSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    http_method_names = ['patch']  # Allow only PATCH requests

    def perform_update(self, serializer):
        job_card = self.get_object()

        # Check if job status is already 'Closed'
        if job_card.job_status == 'Closed':
            raise APIException({"error": "Job card is already closed. No further updates can be made."},
                               code=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save(user=self.request.user)
        except ValidationError as e:
            raise ValidationError({"detail": str(e)})


# Return a list of Open or In-Progress Jobs:
class OpenInProgressJobsView(generics.ListAPIView):
    serializer_class = JobCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobCard.objects.filter(job_status__in=['Open', 'In Progress'])


# Query a job by job number:
class JobCardByNumberView(generics.RetrieveAPIView):
    serializer_class = JobCardSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'job_number'

    def get_queryset(self):
        return JobCard.objects.all()


# View to close job card
class CloseJobCardView(generics.UpdateAPIView):
    serializer_class = JobCardSerializer
    permission_classes = [IsAuthenticated]  # Only require authentication
    lookup_field = 'id'
    http_method_names = ['patch']  # Allow only PATCH requests

    def get_queryset(self):
        return JobCard.objects.all()

    def update(self, request, *args, **kwargs):
        job_card = self.get_object()

        resolution = request.data.get('resolution')
        if not resolution:
            raise APIException({"error": "Resolution field must be filled before closing the job card"},
                               code=status.HTTP_400_BAD_REQUEST)

        job_card.resolution = resolution
        job_card.job_status = 'Closed'
        job_card.save()

        serializer = self.get_serializer(job_card)
        return Response(serializer.data)


# View for creating and downloading JOB card pdf:
class JobCardPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_number, *args, **kwargs):
        try:
            job_card = JobCard.objects.get(job_number=job_number)
        except JobCard.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Define the template and context for the PDF
        template = get_template('job_card_pdf.html')
        context = {
            'job_card': job_card,
        }
        html = template.render(context)

        # Create the PDF file in memory
        buffer = io.BytesIO()
        pisa.CreatePDF(html, dest=buffer)
        buffer.seek(0)

        # Return the PDF as a response
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=JobCard_{job_card.job_number}.pdf'
        return response


# View for creating and downloading JOB card pdf:
class JobCardPDFViewAlt(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_number, *args, **kwargs):
        try:
            job_card = JobCard.objects.get(job_number=job_number)
        except JobCard.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Retrieve all images related to the job card
        images = Images.objects.filter(job_card=job_card)

        # Define the template and context for the PDF
        template = get_template('jobcardpdf.html')
        context = {
            'job_card': job_card,
            'images': images,
        }
        html = template.render(context)

        # Create the PDF file in memory
        buffer = io.BytesIO()
        pisa.CreatePDF(html, dest=buffer)
        buffer.seek(0)

        # Return the PDF as a response
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=JobCard_{job_card.job_number}.pdf'
        return response


class JobCardDetailView(generics.RetrieveUpdateAPIView):
    queryset = JobCard.objects.all()
    serializer_class = JobCardSerializer
    lookup_field = 'id'


class JobImagesView(APIView):
    def get(self, request, job_id):
        job_card = JobCard.objects.filter(pk=job_id)
        images = Images.objects.filter(job_card__in=job_card)
        serializer = ImagesSerializer(images, many=True)
        return Response(serializer.data)


class JobImagesUploadView(APIView):
    parser_classes = [MultiPartParser]

    def patch(self, request, job_id):
        try:
            job_card = JobCard.objects.get(pk=job_id)
        except JobCard.DoesNotExist:
            return Response({"error": "Job card not found."}, status=status.HTTP_404_NOT_FOUND)

        images, _ = Images.objects.get_or_create(job_card=job_card)

        serializer = ImagesSerializer(images, data=request.data, partial=True)
        if serializer.is_valid():
            # Save the images
            for image_field in ['pop_image', 'assessment_environment_image']:
                image_file = request.FILES.get(image_field)
                if image_file:
                    setattr(images, image_field, image_file)

            for prefix in ['before_assessment', 'after_assessment']:
                for i in range(1, 4):
                    image_field = f'{prefix}_image_{i}'
                    image_file = request.FILES.get(image_field)
                    if image_file:
                        setattr(images, image_field, image_file)

            images.save()

            # Update the serializer instance
            serializer = ImagesSerializer(images)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
