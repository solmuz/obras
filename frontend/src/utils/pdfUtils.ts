import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { SemaforoReport } from '@/types';

export const exportReportToPDF = (data: SemaforoReport[], filename: string = 'report.pdf') => {
  const doc = new jsPDF();

  // Add title
  doc.setFontSize(16);
  doc.text('OBRAS - Reporte de Equipos de Izaje', 20, 20);

  // Add timestamp
  doc.setFontSize(10);
  doc.text(`Generado: ${new Date().toLocaleString('es-CO')}`, 20, 30);

  // Create table
  autoTable(doc, {
    startY: 40,
    head: [['Código', 'Estado', 'Última Insp. Externa', 'Última Insp. Sitio', 'Próxima Externa', 'Próxima Sitio']],
    body: data.map((report) => [
      report.code_internal,
      report.status,
      report.external_inspection_date || '-',
      report.site_inspection_date || '-',
      report.next_external_date || '-',
      report.next_site_date || '-',
    ]),
    styles: {
      fontSize: 9,
      cellPadding: 5,
    },
    headStyles: {
      fillColor: [41, 128, 185],
      textColor: 255,
      fontStyle: 'bold',
    },
  });

  doc.save(filename);
};
