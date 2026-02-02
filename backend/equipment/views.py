import pandas as pd
import io
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from .models import EquipmentUpload
from .serializers import EquipmentUploadSerializer

REQUIRED_COLUMNS = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']

def parse_csv_and_calculate_stats(csv_file):
    try:
        df = pd.read_csv(csv_file)
        
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"
        
        stats = {
            'total_equipment': len(df),
            'average_flowrate': float(df['Flowrate'].mean()),
            'average_pressure': float(df['Pressure'].mean()),
            'average_temperature': float(df['Temperature'].mean()),
            'equipment_distribution': df['Type'].value_counts().to_dict()
        }
        
        data = df.to_dict('records')
        
        return {'stats': stats, 'data': data}, None
    except Exception as e:
        return None, str(e)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_csv(request):
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    csv_file = request.FILES['file']
    
    if not csv_file.name.endswith('.csv'):
        return Response(
            {'error': 'File must be a CSV'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result, error = parse_csv_and_calculate_stats(csv_file)
    
    if error:
        return Response(
            {'error': error},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    csv_file.seek(0)
    stats = result['stats']
    # Store summary stats with the upload for history display.
    upload = EquipmentUpload.objects.create(
        csv_file=csv_file,
        total_equipment=stats['total_equipment'],
        average_flowrate=stats['average_flowrate'],
        average_pressure=stats['average_pressure'],
        average_temperature=stats['average_temperature'],
    )
    
    return Response({
        'id': upload.id,
        'uploaded_at': upload.uploaded_at,
        'stats': result['stats'],
        'data': result['data']
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_latest(request):
    try:
        latest_upload = EquipmentUpload.objects.first()
        
        if not latest_upload:
            return Response(
                {'error': 'No uploads found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        result, error = parse_csv_and_calculate_stats(latest_upload.csv_file)
        
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'id': latest_upload.id,
            'uploaded_at': latest_upload.uploaded_at,
            'stats': result['stats'],
            'data': result['data']
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_history(request):
    uploads = EquipmentUpload.objects.order_by('-uploaded_at')[:5]
    # Return last 5 uploads with stored summary stats.
    history = [
        {
            'id': upload.id,
            'uploaded_at': upload.uploaded_at,
            'total_equipment': upload.total_equipment,
            'average_flowrate': upload.average_flowrate,
            'average_pressure': upload.average_pressure,
            'average_temperature': upload.average_temperature,
        }
        for upload in uploads
    ]
    return Response(history)

@api_view(['GET'])
def generate_pdf(request):
    try:
        latest_upload = EquipmentUpload.objects.first()
        
        if not latest_upload:
            return Response(
                {'error': 'No uploads found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        result, error = parse_csv_and_calculate_stats(latest_upload.csv_file)
        
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        title = Paragraph("Chemical Equipment Summary Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        stats = result['stats']
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Equipment', str(stats['total_equipment'])],
            ['Average Flowrate', f"{stats['average_flowrate']:.2f}"],
            ['Average Pressure', f"{stats['average_pressure']:.2f}"],
            ['Average Temperature', f"{stats['average_temperature']:.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        subtitle = Paragraph("Equipment Type Distribution", styles['Heading2'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.2 * inch))
        
        dist_data = [['Equipment Type', 'Count']]
        for eq_type, count in stats['equipment_distribution'].items():
            dist_data.append([str(eq_type), str(count)])
        
        dist_table = Table(dist_data, colWidths=[3*inch, 2*inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(dist_table)
        
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="equipment_report.pdf"'
        
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
