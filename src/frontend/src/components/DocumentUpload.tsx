'use client';

import React, { useState, useRef } from 'react';
import { Box, Button, Typography, LinearProgress, IconButton, Tooltip, Paper, Fade, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import DescriptionIcon from '@mui/icons-material/Description';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ArticleIcon from '@mui/icons-material/Article';
import { uploadDocument, checkDuplicateDocument } from '../lib/api';

interface DocumentUploadProps {
  onUploadSuccess?: () => void;
}

export default function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleFileSelect = async (file: File) => {
    // Proširena lista podržanih formata
    const supportedTypes = [
      'application/pdf', // PDF
      'application/msword', // DOC
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // DOCX
      'text/plain', // TXT
      'text/markdown', // MD
      'text/x-rst', // RST
      'text/x-python', // PY
      'application/javascript', // JS
      'application/typescript', // TS
      'text/x-java-source', // JAVA
      'text/x-c++src', // CPP
      'text/x-csrc', // C
      'text/html', // HTML
      'application/json', // JSON
      'application/x-yaml', // YAML
      'text/xml', // XML
      'text/csv' // CSV
    ];
    
    if (supportedTypes.includes(file.type) || file.name.match(/\.(pdf|doc|docx|txt|md|rst|py|js|ts|java|cpp|c|html|json|yaml|yml|xml|csv)$/i)) {
      
      // Proveravamo da li postoji duplikat
      const duplicateCheck = await checkDuplicateDocument(file.name);
      if (duplicateCheck.error) {
        throw new Error(duplicateCheck.error);
      }

      if (duplicateCheck.data) {
        setSelectedFile(file);
        setDuplicateDialogOpen(true);
        return;
      }

      setSelectedFile(file);
      setUploadProgress(0);
      
      try {
        const response = await uploadDocument(file);
        if (response.error) {
          throw new Error(response.error);
        }
        
        // Simuliramo progres za bolji UX
        const interval = setInterval(() => {
          setUploadProgress((prev) => {
            if (prev >= 100) {
              clearInterval(interval);
              return 100;
            }
            return prev + 10;
          });
        }, 100);

        // Pozivamo callback nakon uspešnog uploada
        onUploadSuccess?.();
      } catch (error) {
        console.error('Greška:', error);
        alert('Došlo je do greške pri otpremanju dokumenta');
        setSelectedFile(null);
        setUploadProgress(0);
      }
    } else {
      alert('Podržani formati su: PDF, DOC, DOCX, TXT, MD, RST, PY, JS, TS, JAVA, CPP, C, HTML, JSON, YAML, XML, CSV');
    }
  };

  const handleDelete = () => {
    setSelectedFile(null);
    setUploadProgress(0);
  };

  const handleDuplicateConfirm = async () => {
    if (!selectedFile) return;

    setDuplicateDialogOpen(false);
    setUploadProgress(0);
    
    try {
      const response = await uploadDocument(selectedFile);
      if (response.error) {
        throw new Error(response.error);
      }
      
      // Simuliramo progres za bolji UX
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 100);

      // Pozivamo callback nakon uspešnog uploada
      onUploadSuccess?.();
    } catch (error) {
      console.error('Greška:', error);
      alert('Došlo je do greške pri otpremanju dokumenta');
      setSelectedFile(null);
      setUploadProgress(0);
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'application/pdf':
        return <PictureAsPdfIcon />;
      case 'application/msword':
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return <ArticleIcon />;
      default:
        return <DescriptionIcon />;
    }
  };

  return (
    <>
      <Paper
        elevation={0}
        sx={{
          p: 2,
          border: '2px dashed',
          borderColor: isDragging ? 'primary.main' : 'divider',
          borderRadius: 2,
          bgcolor: isDragging ? 'action.hover' : 'background.paper',
          transition: 'all 0.2s',
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          accept=".pdf,.doc,.docx,.txt,.md,.rst,.py,.js,.ts,.java,.cpp,.c,.html,.json,.yaml,.yml,.xml,.csv"
        />

        {!selectedFile ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              py: 3,
            }}
          >
            <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary" align="center">
              Prevucite dokument ovde ili{' '}
              <Button
                variant="text"
                onClick={() => fileInputRef.current?.click()}
                sx={{ textTransform: 'none' }}
              >
                izaberite fajl
              </Button>
            </Typography>
            <Typography variant="caption" color="text.secondary" align="center">
              Podržani formati: PDF, DOC, DOCX, TXT, MD, RST, PY, JS, TS, JAVA, CPP, C, HTML, JSON, YAML, XML, CSV
            </Typography>
          </Box>
        ) : (
          <Fade in={!!selectedFile}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ color: 'text.secondary' }}>
                  {getFileIcon(selectedFile.type)}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle2" noWrap>
                    {selectedFile.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {selectedFile.size && !isNaN(selectedFile.size) 
                      ? `${(selectedFile.size / 1024).toFixed(1)} KB`
                      : 'Nepoznata veličina'
                    }
                  </Typography>
                </Box>
                <Tooltip title="Obriši">
                  <IconButton size="small" onClick={handleDelete}>
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </Box>

              {uploadProgress < 100 && (
                <Box sx={{ width: '100%' }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={uploadProgress}
                    sx={{
                      height: 4,
                      borderRadius: 2,
                      bgcolor: 'action.hover',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 2,
                      },
                    }}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                    {uploadProgress}% otpremljeno
                  </Typography>
                </Box>
              )}
            </Box>
          </Fade>
        )}
      </Paper>

      <Dialog
        open={duplicateDialogOpen}
        onClose={() => setDuplicateDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Duplikat dokumenta</DialogTitle>
        <DialogContent>
          <Typography>
            Dokument sa nazivom "{selectedFile?.name}" već postoji u sistemu.
            Da li želite da ga ipak otpremite?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDuplicateDialogOpen(false)}>Otkaži</Button>
          <Button
            onClick={handleDuplicateConfirm}
            color="primary"
            variant="contained"
          >
            Otpremi
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
} 