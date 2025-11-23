from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404, HttpResponse
from django.http import FileResponse
from django.conf import settings
import os
import uuid
import pandas as pd
import io
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Dataset
from .models import AppUser
from .serializers import UserSerializer, UserCreateSerializer, UserLoginSerializer, DatasetSerializer, DatasetDetailSerializer


class RootAPIView(APIView):
    def get(self, request):
        return Response({"message": "Chemical Equipment Parameter Visualizer API"})


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        else:
            errors = serializer.errors
            if 'email' in errors:
                return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
            elif 'username' in errors:
                return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            user = AppUser.objects.get(username=username)
        except AppUser.DoesNotExist:
            return Response({"error": "user not registered"}, status=404)

        if user.check_password(password):
            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "token": f"user_{user.id}"
            }, status=200)
        else:
            return Response({"error": "Invalid password"}, status=400)


class UploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # Extract token from form data or header
        token = request.data.get('token')
        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token or not token.startswith('user_'):
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = token.split('_')[1]
        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return Response({"error": "Invalid user"}, status=status.HTTP_401_UNAUTHORIZED)

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj.name.endswith('.csv'):
            return Response({"detail": "Only CSV files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contents = file_obj.read()
            df = pd.read_csv(io.BytesIO(contents))

            # Validate CSV
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_columns):
                return Response({
                    "detail": "CSV must contain columns: Equipment Name, Type, Flowrate, Pressure, Temperature"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Compute summary
            summary = self.compute_summary(df)

            # Save file
            upload_dir = Path(settings.MEDIA_ROOT)
            upload_dir.mkdir(exist_ok=True)
            file_path = upload_dir / f"{uuid.uuid4()}_{file_obj.name}"
            with open(file_path, 'wb') as f:
                f.write(contents)

            # Create dataset record
            dataset = Dataset(
                filename=file_obj.name,
                summary=summary,
                file_path=str(file_path),
                data=df.to_dict('records'),
                user=user
            )
            dataset.save()

            # Keep only last 5 datasets per user
            user_datasets = Dataset.objects.filter(user=user).order_by('-uploaded_at')
            if user_datasets.count() > 5:
                for old_dataset in user_datasets[5:]:
                    # Delete file
                    old_file_path = Path(old_dataset.file_path)
                    if old_file_path.exists():
                        old_file_path.unlink()
                    old_dataset.delete()
            
            return Response({
                "message": "File uploaded successfully",
                "dataset_id": dataset.id,
                "summary": summary,
                "data": df.to_dict('records')[:100]  # Return first 100 rows
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"detail": f"Error processing file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def compute_summary(self, df):
        summary = {
            'equipment_count': len(df),
            'avg_flowrate': float(df['Flowrate'].mean()),
            'avg_pressure': float(df['Pressure'].mean()),
            'avg_temperature': float(df['Temperature'].mean()),
            'type_distribution': df['Type'].value_counts().to_dict(),
            'min_flowrate': float(df['Flowrate'].min()),
            'max_flowrate': float(df['Flowrate'].max()),
            'min_pressure': float(df['Pressure'].min()),
            'max_pressure': float(df['Pressure'].max()),
            'min_temperature': float(df['Temperature'].min()),
            'max_temperature': float(df['Temperature'].max()),
        }
        return summary


class DatasetDetailAPIView(APIView):
    def get(self, request, dataset_id):
        # Extract token and get user
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        if not token.startswith('user_'):
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = token.split('_')[1]
        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return Response({"error": "Invalid user"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            dataset = Dataset.objects.get(id=dataset_id, user=user)
            serializer = DatasetDetailSerializer(dataset)
            return Response(serializer.data)
        except Dataset.DoesNotExist:
            raise Http404


class HistoryAPIView(APIView):
    def get(self, request):
        # Extract token and get user
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        if not token.startswith('user_'):
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = token.split('_')[1]
        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return Response({"error": "Invalid user"}, status=status.HTTP_401_UNAUTHORIZED)

        datasets = Dataset.objects.filter(user=user).order_by('-uploaded_at')[:5]
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)


class PDFReportAPIView(APIView):
    def get(self, request, dataset_id):
        # Extract token and get user
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        if not token.startswith('user_'):
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        user_id = token.split('_')[1]
        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return Response({"error": "Invalid user"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            dataset = Dataset.objects.get(id=dataset_id, user=user)
        except Dataset.DoesNotExist:
            raise Http404

        # Generate PDF
        upload_dir = Path(settings.MEDIA_ROOT)
        pdf_path = upload_dir / f"report_{dataset_id}.pdf"
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title = Paragraph(f"<b>Equipment Report: {dataset.filename}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Summary
        summary_text = f"""<b>Summary Statistics</b><br/>
        Equipment Count: {dataset.summary['equipment_count']}<br/>
        Average Flowrate: {dataset.summary['avg_flowrate']:.2f}<br/>
        Average Pressure: {dataset.summary['avg_pressure']:.2f}<br/>
        Average Temperature: {dataset.summary['avg_temperature']:.2f}<br/>
        """
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Type Distribution Table
        type_dist = dataset.summary['type_distribution']
        table_data = [['Equipment Type', 'Count']]
        for eq_type, count in type_dist.items():
            table_data.append([str(eq_type), str(count)])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        doc.build(elements)

        # Return PDF as HTTP response with download headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{dataset.filename}.pdf"'
        response.write(open(pdf_path, 'rb').read())
        return response