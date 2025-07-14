from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.tests import Test
from ..models.patients import Patient
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Spacer
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.exceptions import NotFound
from ..serializers.patientsserializer import PatientCodeSerializer

class TestPatientsPDFView(APIView):
    def get(self, request, test_code, patient_code):
        try:
            test = Test.objects.get(test_code=test_code)
            patient = test.patients.get(code=patient_code)
        except Test.DoesNotExist:
            return Response(
                {"error": "Test no existe"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Patient.DoesNotExist:
            return Response(
                {"error": "Paciente no existe para el test"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear el PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Estilos
        styles = getSampleStyleSheet()
        elements = []
        
        # Título
        title = Paragraph(f"Informe Genético - Test: {test.test_code}", styles['Title'])
        elements.append(title)
        
        # Información del paciente
        patient_info = Paragraph(
            f"<b>Paciente:</b> {patient.code}<br/>"
            f"<b>Fecha del Test:</b> {test.created_at.strftime('%d/%m/%Y')}",
            styles['Normal']
        )
        elements.append(patient_info)
        elements.append(Spacer(1, 12))
        
        # Preparar datos para la tabla principal
        table_data = [
            ["Gene", "Haplo", "Marker", "Response"]  # Encabezados de la tabla
        ]

        # Procesar datos JSON
        list_data = patient.data_json
        previous_gene = None
        
        for diccionario in list_data:
            for gene, markers in diccionario.items():
                first_marker_processed = False
                
                for marker in markers:
                    if marker['marker'] == "None":
                        continue
                        
                    marker_name = marker.get('marker', '')
                    formula = marker.get('formula', [])
                    
                    # Formatear la columna Response
                    if formula is None:
                        response = "N/A"
                    else:
                        response = ",".join([str(f) for f in formula if f is not None])
                    
                    # Determinar el Haplo (solo para el primer marcador de cada gen)
                    haplo = "*?/*?" if not first_marker_processed else ""
                    
                    # Agregar fila en blanco si cambiamos de gen
                    if previous_gene and previous_gene != gene:
                        table_data.append(["", "", "", ""])  # Fila en blanco
                    
                    table_data.append([gene, haplo, marker_name, response])
                    
                    first_marker_processed = True
                    previous_gene = gene

        # Crear tabla principal
        table = Table(table_data, style=self._get_table_style(), colWidths=[80, 80, 100, 200])
        elements.append(table)
            
        # Construir el PDF
        doc.build(elements)
            
        # Preparar la respuesta
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="reporte_{test.test_code}_{patient.code}.pdf"'
        )
            
        return response
                
    def _get_table_style(self):
        """Estilo para las tablas con ajuste para filas en blanco"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),  # Encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Estilo especial para filas en blanco
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('LINEABOVE', (0, 1), (-1, -1), 0.5, colors.white),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.white),
        ])
   
class PatientCodesByTestView(generics.ListAPIView):
    serializer_class = PatientCodeSerializer
    
    def get_queryset(self):
        test_code = self.kwargs.get('test_code')
        
        try:
            test = Test.objects.get(test_code=test_code)
            return Patient.objects.filter(test=test)
        except Test.DoesNotExist:
            raise NotFound(detail="Test not found")
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        codes = [item['code'] for item in serializer.data]
        return Response({'patient_codes': codes})