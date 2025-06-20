'use client';

import React from 'react';
import { Box, Paper, Typography, Chip, IconButton, Tooltip } from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ArticleIcon from '@mui/icons-material/Article';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { motion } from 'framer-motion';

interface SearchResult {
  content: string;
  metadata: {
    source: string;
    page?: number;
    type: string;
  };
  rerank_score?: number;
  semantic_score?: number;
  lexical_score?: number;
  relevance_score?: number;
}

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  highlightText: (text: string, query: string) => React.ReactNode;
}

export default function SearchResults({ results, query, highlightText }: SearchResultsProps) {
  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return <PictureAsPdfIcon />;
      case 'doc':
      case 'docx':
        return <ArticleIcon />;
      default:
        return <DescriptionIcon />;
    }
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const handleOpen = (source: string) => {
    window.open(source, '_blank');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {results.map((result, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          <Paper
            elevation={0}
            sx={{
              p: 2,
              bgcolor: 'background.paper',
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
              '&:hover': {
                borderColor: 'primary.main',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <Box sx={{ color: 'text.secondary' }}>
                {getFileIcon(result.metadata.type)}
              </Box>
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {result.metadata.source}
                  </Typography>
                  {result.metadata.page && (
                    <Chip
                      size="small"
                      label={`Strana ${result.metadata.page}`}
                      sx={{ bgcolor: 'action.selected' }}
                    />
                  )}
                  <Chip
                    size="small"
                    label={result.metadata.type.toUpperCase()}
                    sx={{ bgcolor: 'action.selected' }}
                  />
                  {result.rerank_score !== undefined && (
                    <Chip
                      size="small"
                      label={`Rerank: ${result.rerank_score.toFixed(1)}%`}
                      sx={{ 
                        bgcolor: 'success.light', 
                        color: 'success.contrastText',
                        fontSize: '0.7rem'
                      }}
                    />
                  )}
                  {result.relevance_score !== undefined && (
                    <Chip
                      size="small"
                      label={`Relevance: ${result.relevance_score.toFixed(1)}%`}
                      sx={{ 
                        bgcolor: 'info.light', 
                        color: 'info.contrastText',
                        fontSize: '0.7rem'
                      }}
                    />
                  )}
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    color: 'text.secondary',
                    mb: 1,
                    lineHeight: 1.5,
                  }}
                >
                  {highlightText(result.content, query)}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Tooltip title="Kopiraj sadržaj">
                    <IconButton
                      size="small"
                      onClick={() => handleCopy(result.content)}
                      sx={{ color: 'text.secondary' }}
                    >
                      <ContentCopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Otvori dokument">
                    <IconButton
                      size="small"
                      onClick={() => handleOpen(result.metadata.source)}
                      sx={{ color: 'text.secondary' }}
                    >
                      <OpenInNewIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            </Box>
          </Paper>
        </motion.div>
      ))}
    </Box>
  );
} 