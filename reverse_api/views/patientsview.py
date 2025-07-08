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
        doc = SimpleDocTemplate(buffer, pagesize=(8.5*inch, 11*inch))  # Tamaño carta
        
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
        elements.append(Paragraph("<br/>", styles['Normal']))
        
        # Procesar datos JSON
        
        data_json = patient.data_json[0]
        #print(data_json)

        
        for gen, markers in data_json.items():
            # Encabezado del gen
            gen_style = ParagraphStyle(
                name='GenHeader',
                fontSize=14,
                leading=16,
                alignment=1,  # Centro
                textColor=colors.black,
                backColor=colors.grey,
                fontName="Helvetica-Bold"
            )
            elements.append(Paragraph(f"Gen: {gen}", gen_style))
            
            # Preparar datos para la tabla
            table_data = [["Marker", "Fórmula", "Frecuencia"]]  # Agregué "Frecuencia"
            
            for marker in markers:
                marker_name = marker.get('marker', '')
                formula = marker.get('formula', [])
                freq = marker.get('freq', '')
                
                formatted_formula = "" # o algún valor por defecto si formula es None
                if formula is not None:
                    if isinstance(formula, (list, tuple)):  # Verificar si es iterable
                        formatted_formula = "<br/>".join(formula)
                    else:
                        formatted_formula = str(formula)  # Convertir a string si no es iterable

                formula_paragraph = Paragraph(formatted_formula, styles['Normal'])
                
                table_data.append([marker_name, formula_paragraph, freq])
            
            # Crear tabla
            table = Table(table_data, style=self._get_table_style())
            elements.append(table)
            elements.append(Paragraph("<br/>", styles['Normal']))
        
        #print(elements)
        
        # Construir el PDF
        doc.build(elements)
        
        # Preparar la respuesta
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="reporte_{test.test_code}_{patient.code}.pdf"'
        )
        
        return response
        #"""
        #return Response({"res": True})


    def _get_table_style(self):
        """Estilo para las tablas"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
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