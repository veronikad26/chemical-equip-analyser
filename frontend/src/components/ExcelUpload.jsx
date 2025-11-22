import React from 'react';
import * as XLSX from 'xlsx';
import { toast } from 'sonner';

const ExcelUpload = ({ onFileChange }) => {
  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    const fileName = selectedFile.name.toLowerCase();

    // --- CASE 1: CSV file directly ---
    if (fileName.endsWith('.csv')) {
      onFileChange(selectedFile);
      return;
    }

    // --- CASE 2: XLSX → convert to CSV (original functionality preserved) ---
    if (fileName.endsWith('.xlsx')) {
      const reader = new FileReader();

      reader.onload = (event) => {
        const data = event.target.result;

        try {
          const workbook = XLSX.read(data, { type: 'binary' });
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];

          const csv = XLSX.utils.sheet_to_csv(worksheet);

          // Convert CSV string into file
          const csvBlob = new Blob([csv], { type: 'text/csv' });
          const csvFile = new File(
            [csvBlob],
            selectedFile.name.replace('.xlsx', '.csv'),
            { type: 'text/csv' }
          );

          onFileChange(csvFile);
        } catch (error) {
          toast.error('Error parsing .xlsx file. Please ensure it has the correct format.');
        }
      };

      reader.readAsBinaryString(selectedFile);
      return;
    }

    // --- INVALID FORMAT ---
    toast.error('Please upload a .xlsx or .csv file');
  };

  return (
    <input
      type="file"
      accept=".csv,.xlsx"
      onChange={handleFileSelect}
      className="file-input"
    />
  );
};

export default ExcelUpload;
