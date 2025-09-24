import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from config.settings import AppSettings

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        AppSettings.create_directories()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Title'],
                fontSize=20,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2563EB')
            ),
            'CustomHeader': ParagraphStyle(
                'CustomHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.HexColor('#374151')
            ),
            'CustomBody': ParagraphStyle(
                'CustomBody',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                alignment=TA_LEFT
            )
        }
    
    def export_workouts_pdf(self, user, workouts):
        """Export member's workouts to PDF"""
        filename = f"workouts_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(AppSettings.EXPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=72)
        story = []
        
        # Title
        title = Paragraph(f"Workout Plans - {user.full_name}", self.custom_styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Member info
        member_info = [
            ['Member Name:', user.full_name],
            ['Username:', user.username],
            ['Email:', user.email or 'Not provided'],
            ['Export Date:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        info_table = Table(member_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Workouts
        if workouts:
            for i, workout in enumerate(workouts, 1):
                # Workout header
                workout_header = Paragraph(f"Workout {i}: {workout.name}", self.custom_styles['CustomHeader'])
                story.append(workout_header)
                
                # Workout description
                if workout.description:
                    desc = Paragraph(f"<b>Description:</b> {workout.description}", self.custom_styles['CustomBody'])
                    story.append(desc)
                
                # Exercise list
                if workout.exercises:
                    exercises_header = Paragraph("<b>Exercises:</b>", self.custom_styles['CustomBody'])
                    story.append(exercises_header)
                    
                    exercise_data = [['Exercise', 'Sets', 'Reps', 'Weight', 'Notes']]
                    
                    for exercise in workout.exercises:
                        exercise_data.append([
                            exercise.get('name', 'Unknown Exercise'),
                            exercise.get('sets', '-'),
                            exercise.get('reps', '-'),
                            exercise.get('weight', '-'),
                            exercise.get('notes', '')
                        ])
                    
                    exercise_table = Table(exercise_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 2*inch])
                    exercise_table.setStyle(TableStyle([
                        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                        ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    
                    story.append(exercise_table)
                
                story.append(Spacer(1, 20))
        else:
            no_workouts = Paragraph("No workout plans found.", self.custom_styles['CustomBody'])
            story.append(no_workouts)
        
        # Build PDF
        doc.build(story)
        return filepath
    
    def export_member_progress_pdf(self, user, progress_records):
        """Export member's progress to PDF"""
        filename = f"progress_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(AppSettings.EXPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=72)
        story = []
        
        # Title
        title = Paragraph(f"Progress Report - {user.full_name}", self.custom_styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 30))
        
        # Progress data table
        if progress_records:
            progress_data = [['Date', 'Weight (lbs)', 'Body Fat %', 'Muscle Mass', 'Notes']]
            
            for record in progress_records:
                progress_data.append([
                    record.record_date or 'N/A',
                    f"{record.weight:.1f}" if record.weight else 'N/A',
                    f"{record.body_fat:.1f}%" if record.body_fat else 'N/A',
                    f"{record.muscle_mass:.1f}" if record.muscle_mass else 'N/A',
                    record.notes[:50] + "..." if record.notes and len(record.notes) > 50 else record.notes or ''
                ])
            
            progress_table = Table(progress_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 2.3*inch])
            progress_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(progress_table)
        else:
            no_progress = Paragraph("No progress records found.", self.custom_styles['CustomBody'])
            story.append(no_progress)
        
        doc.build(story)
        return filepath
    
    def export_trainer_report_pdf(self, trainer, members, sessions):
        """Export trainer's client report to PDF"""
        filename = f"trainer_report_{trainer.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(AppSettings.EXPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter, topMargin=72)
        story = []
        
        # Title
        title = Paragraph(f"Trainer Report - {trainer.full_name}", self.custom_styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report summary
        summary_data = [
            ['Total Clients:', str(len(members))],
            ['Total Sessions:', str(len(sessions))],
            ['Completed Sessions:', str(len([s for s in sessions if s.status == 'completed']))],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Client list
        if members:
            clients_header = Paragraph("Client List", self.custom_styles['CustomHeader'])
            story.append(clients_header)
            
            client_data = [['Client Name', 'Email', 'Phone', 'Join Date']]
            
            for member in members:
                client_data.append([
                    member.full_name,
                    member.email or 'Not provided',
                    member.phone or 'Not provided',
                    member.created_at[:10] if member.created_at else 'Unknown'
                ])
            
            client_table = Table(client_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1*inch])
            client_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(client_table)
        
        doc.build(story)
        return filepath