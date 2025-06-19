import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, Select, MenuItem, FormControl, InputLabel, TextField, IconButton, Tooltip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TableSortLabel, Dialog, DialogTitle, DialogContent, Button, DialogActions, Alert, Snackbar, CircularProgress, Divider, Menu, Popover, Stack } from '@mui/material';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ArticleIcon from '@mui/icons-material/Article';
import DescriptionIcon from '@mui/icons-material/Description';
import RefreshIcon from '@mui/icons-material/Refresh';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import { TextField as MuiTextField } from '@mui/material';
import { Box as MuiBox } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CloseIcon from '@mui/icons-material/Close';
import DocumentUpload from './DocumentUpload';
import { Document, DocumentPage, fetchDocuments, fetchDocumentPages, deleteDocument } from '../lib/api';
import { List, ListItem, ListItemText, ListItemIcon, Chip } from '@mui/material';
import {
  Search as SearchIcon,
  Sort as SortIcon,
  FilterList as FilterIcon,
  Delete as DeleteIcon,
  DateRange as DateRangeIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon
} from '@mui/icons-material';
import { InputAdornment } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { sr } from 'date-fns/locale';

function getFileIcon(type: string) {
  switch (type) {
    case '.pdf':
      return <PictureAsPdfIcon sx={{ color: 'error.main' }} />;
    case '.doc':
    case '.docx':
      return <ArticleIcon sx={{ color: 'primary.main' }} />;
    case '.txt':
      return <DescriptionIcon sx={{ color: 'text.secondary' }} />;
    default:
      return <DescriptionIcon sx={{ color: 'text.secondary' }} />;
  }
}

const statusOptions = [
  { value: '', label: 'Svi' },
  { value: 'processed', label: 'Obrađeni' },
  { value: 'pending', label: 'Na čekanju' },
  { value: 'error', label: 'Greška' },
];

const typeOptions = [
  { value: '', label: 'Svi' },
  { value: '.pdf', label: 'PDF' },
  { value: '.doc', label: 'DOC' },
  { value: '.docx', label: 'DOCX' },
  { value: '.txt', label: 'TXT' },
];

function highlightText(text: string, query: string) {
  if (!query) return text;
  const parts = text.split(new RegExp(`(${query})`, 'gi'));
  return (
    <span>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <mark key={i} style={{ background: 'yellow' }}>{part}</mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
}

const copyWithReference = (text: string, page: DocumentPage, doc: Document) => {
  const reference = `\n\nIzvor: ${doc.filename}, Stranica ${page.page_number}`;
  navigator.clipboard.writeText(text + reference);
};

interface FilterState {
  type: string | null;
  status: string | null;
  dateFrom: Date | null;
  dateTo: Date | null;
}

export default function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [filtered, setFiltered] = useState<Document[]>([]);
  const [type, setType] = useState('');
  const [status, setStatus] = useState('');
  const [date, setDate] = useState('');
  const [sortBy, setSortBy] = useState<'created_at' | 'filename'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openDoc, setOpenDoc] = useState<Document | null>(null);
  const [pages, setPages] = useState<DocumentPage[]>([]);
  const [pageSearch, setPageSearch] = useState('');
  const [loadingPages, setLoadingPages] = useState(false);
  const [showFullDocument, setShowFullDocument] = useState(false);
  const [showImagePreview, setShowImagePreview] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<Document | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    type: null,
    status: null,
    dateFrom: null,
    dateTo: null
  });
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [datePickerAnchorEl, setDatePickerAnchorEl] = useState<null | HTMLElement>(null);

  const fetchDocumentsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchDocuments();
      if (response.error) {
        throw new Error(response.error);
      }
      if (response.data) {
        setDocuments(response.data);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Greška pri dohvatanju dokumenata');
      setDocuments([]);
      setSnackbar({
        open: true,
        message: error instanceof Error ? error.message : 'Greška pri dohvatanju dokumenata',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocumentsData();
  }, []);

  useEffect(() => {
    let result = [...documents];
    if (type) result = result.filter(doc => doc.file_type === type);
    if (status) result = result.filter(doc => doc.status === status);
    if (date) result = result.filter(doc => doc.created_at && doc.created_at.startsWith(date));
    if (search) result = result.filter(doc => doc.filename.toLowerCase().includes(search.toLowerCase()));
    result = result.sort((a, b) => {
      if (sortBy === 'created_at') {
        return sortOrder === 'asc'
          ? new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          : new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      } else {
        return sortOrder === 'asc'
          ? a.filename.localeCompare(b.filename)
          : b.filename.localeCompare(a.filename);
      }
    });
    setFiltered(result);
  }, [documents, type, status, date, sortBy, sortOrder, search]);

  const handleOpenDoc = async (doc: Document) => {
    setOpenDoc(doc);
    
    if (doc.file_type === '.jpg' || doc.file_type === '.jpeg' || doc.file_type === '.png' || doc.file_type === '.gif') {
      setShowImagePreview(true);
      return;
    }

    setLoadingPages(true);
    try {
      const response = await fetchDocumentPages(doc.id);
      if (response.error) {
        throw new Error(response.error);
      }
      if (response.data) {
        setPages(response.data);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Greška pri dohvatanju stranica');
      setPages([]);
      setSnackbar({
        open: true,
        message: error instanceof Error ? error.message : 'Greška pri dohvatanju stranica',
        severity: 'error'
      });
    } finally {
      setLoadingPages(false);
    }
  };

  const handleCloseDialog = () => {
    setOpenDoc(null);
    setPages([]);
    setPageSearch('');
  };

  const handleUploadSuccess = () => {
    fetchDocumentsData();
    setSnackbar({
      open: true,
      message: 'Dokument uspešno otpremljen',
      severity: 'success'
    });
  };

  const handleSortToggle = () => {
    setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc');
  };

  const handleFilterChange = (key: keyof FilterState, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleDeleteClick = (doc: Document, event: React.MouseEvent) => {
    event.stopPropagation();
    setDocumentToDelete(doc);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!documentToDelete) return;

    try {
      const response = await deleteDocument(documentToDelete.id);
      if (response.error) {
        throw new Error(response.error);
      }

      setSnackbar({
        open: true,
        message: 'Dokument uspešno obrisan',
        severity: 'success'
      });

      fetchDocumentsData();
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Greška pri brisanju dokumenta',
        severity: 'error'
      });
    } finally {
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    }
  };

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleDateFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setDatePickerAnchorEl(event.currentTarget);
  };

  const handleDateFilterClose = () => {
    setDatePickerAnchorEl(null);
  };

  const clearFilters = () => {
    setFilters({
      type: null,
      status: null,
      dateFrom: null,
      dateTo: null
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'processed':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'pending':
        return <PendingIcon color="warning" />;
      default:
        return <PendingIcon />;
    }
  };

  const filteredDocuments = documents
    .filter(doc => {
      const matchesSearch = doc.filename.toLowerCase().includes(search.toLowerCase());
      const matchesType = !filters.type || doc.file_type === filters.type;
      const matchesStatus = !filters.status || doc.status === filters.status;
      const matchesDate = (!filters.dateFrom || new Date(doc.created_at) >= filters.dateFrom) &&
                         (!filters.dateTo || new Date(doc.created_at) <= filters.dateTo);
      return matchesSearch && matchesType && matchesStatus && matchesDate;
    })
    .sort((a, b) => {
      const dateA = new Date(a.created_at).getTime();
      const dateB = new Date(b.created_at).getTime();
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    });

  const activeFiltersCount = Object.values(filters).filter(Boolean).length;

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Dokumenti
        </Typography>
        <DocumentUpload onUploadSuccess={handleUploadSuccess} />
      </Paper>

      <Paper sx={{ p: 2, flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
          <TextField
            size="small"
            placeholder="Pretraži dokumente..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, opacity: 0.5 }} />,
            }}
            sx={{ flex: 1 }}
          />
          <Tooltip title="Sortiraj po datumu">
            <IconButton onClick={handleSortToggle}>
              <SortIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Filtriraj dokumente">
            <IconButton onClick={handleFilterClick}>
              <FilterIcon />
              {activeFiltersCount > 0 && (
                <Chip
                  label={activeFiltersCount}
                  size="small"
                  color="primary"
                  sx={{
                    position: 'absolute',
                    top: -8,
                    right: -8,
                    height: 20,
                    minWidth: 20,
                    fontSize: '0.75rem'
                  }}
                />
              )}
            </IconButton>
          </Tooltip>
          <Tooltip title="Filtriraj po datumu">
            <IconButton onClick={handleDateFilterClick}>
              <DateRangeIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {activeFiltersCount > 0 && (
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap', mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Aktivni filteri:
            </Typography>
            {filters.type && (
              <Chip
                label={`Tip: ${filters.type}`}
                onDelete={() => handleFilterChange('type', null)}
                size="small"
              />
            )}
            {filters.status && (
              <Chip
                label={`Status: ${filters.status}`}
                onDelete={() => handleFilterChange('status', null)}
                size="small"
              />
            )}
            {filters.dateFrom && (
              <Chip
                label={`Od: ${filters.dateFrom.toLocaleDateString('sr-RS')}`}
                onDelete={() => handleFilterChange('dateFrom', null)}
                size="small"
              />
            )}
            {filters.dateTo && (
              <Chip
                label={`Do: ${filters.dateTo.toLocaleDateString('sr-RS')}`}
                onDelete={() => handleFilterChange('dateTo', null)}
                size="small"
              />
            )}
            <Button
              size="small"
              onClick={clearFilters}
              sx={{ ml: 'auto' }}
            >
              Obriši sve filtere
            </Button>
          </Box>
        )}

        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <List>
              {filteredDocuments.map((doc) => (
                <ListItem
                  key={doc.id}
                  onClick={() => handleOpenDoc(doc)}
                  sx={{
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                  }}
                >
                  <ListItemIcon>
                    {getFileIcon(doc.file_type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box component="span">
                        {highlightText(doc.filename, search)}
                      </Box>
                    }
                  />
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 1 }}>
                    <Box component="span" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                      {new Date(doc.created_at).toLocaleDateString('sr-RS')}
                    </Box>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Chip
                        label={doc.file_type}
                        size="small"
                        variant="outlined"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleFilterChange('type', doc.file_type);
                        }}
                      />
                      <Chip
                        icon={getStatusIcon(doc.status)}
                        label={doc.status}
                        size="small"
                        variant="outlined"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleFilterChange('status', doc.status);
                        }}
                      />
                    </Stack>
                  </Box>
                  <Tooltip title="Obriši dokument">
                    <IconButton
                      onClick={(e) => handleDeleteClick(doc, e)}
                      sx={{ opacity: 0.5, '&:hover': { opacity: 1 } }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Paper>

      <Dialog
        open={!!openDoc}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        {openDoc && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">{openDoc.filename}</Typography>
                <IconButton onClick={handleCloseDialog}>
                  <CloseIcon />
                </IconButton>
              </Box>
            </DialogTitle>
            <DialogContent>
              {showImagePreview && openDoc.image_url ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                  <img
                    src={openDoc.image_url}
                    alt={openDoc.filename}
                    style={{ maxWidth: '100%', maxHeight: '70vh' }}
                  />
                </Box>
              ) : (
                <>
                  <Box sx={{ mb: 2 }}>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder="Pretraži stranice..."
                      value={pageSearch}
                      onChange={(e) => setPageSearch(e.target.value)}
                    />
                  </Box>
                  {loadingPages ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                      <Typography>Učitavanje stranica...</Typography>
                    </Box>
                  ) : (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      {pages
                        .filter(page =>
                          page.content.toLowerCase().includes(pageSearch.toLowerCase())
                        )
                        .map((page) => (
                          <Paper
                            key={page.id}
                            elevation={0}
                            sx={{
                              p: 2,
                              border: '1px solid',
                              borderColor: 'divider',
                              borderRadius: 2,
                            }}
                          >
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="subtitle2">
                                Stranica {page.page_number}
                              </Typography>
                              <Box>
                                <Tooltip title="Kopiraj sa referencom">
                                  <IconButton
                                    size="small"
                                    onClick={() => copyWithReference(page.content, page, openDoc)}
                                  >
                                    <ContentCopyIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            </Box>
                            <Typography
                              variant="body2"
                              sx={{
                                whiteSpace: 'pre-wrap',
                                fontFamily: 'monospace',
                                fontSize: '0.875rem',
                              }}
                            >
                              {highlightText(page.content, pageSearch)}
                            </Typography>
                          </Paper>
                        ))}
                    </Box>
                  )}
                </>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Zatvori</Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Potvrda brisanja</DialogTitle>
        <DialogContent>
          <Typography>
            Da li ste sigurni da želite da obrišete dokument "{documentToDelete?.filename}"?
            Ova akcija je nepovratna.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Otkaži</Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
          >
            Obriši
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={handleFilterClose}
      >
        <MenuItem>
          <FormControl fullWidth size="small">
            <InputLabel>Tip fajla</InputLabel>
            <Select
              value={filters.type || ''}
              label="Tip fajla"
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <MenuItem value="">Svi tipovi</MenuItem>
              <MenuItem value="pdf">PDF</MenuItem>
              <MenuItem value="doc">DOC</MenuItem>
              <MenuItem value="docx">DOCX</MenuItem>
              <MenuItem value="txt">TXT</MenuItem>
            </Select>
          </FormControl>
        </MenuItem>
        <MenuItem>
          <FormControl fullWidth size="small">
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status || ''}
              label="Status"
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <MenuItem value="">Svi statusi</MenuItem>
              <MenuItem value="processed">Obrađeno</MenuItem>
              <MenuItem value="pending">Na čekanju</MenuItem>
              <MenuItem value="error">Greška</MenuItem>
            </Select>
          </FormControl>
        </MenuItem>
      </Menu>

      <Popover
        open={Boolean(datePickerAnchorEl)}
        anchorEl={datePickerAnchorEl}
        onClose={handleDateFilterClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
      >
        <Box sx={{ p: 2 }}>
          <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={sr}>
            <Stack spacing={2}>
              <DatePicker
                label="Od datuma"
                value={filters.dateFrom}
                onChange={(date) => handleFilterChange('dateFrom', date)}
                slotProps={{ textField: { size: 'small' } }}
              />
              <DatePicker
                label="Do datuma"
                value={filters.dateTo}
                onChange={(date) => handleFilterChange('dateTo', date)}
                slotProps={{ textField: { size: 'small' } }}
              />
            </Stack>
          </LocalizationProvider>
        </Box>
      </Popover>
    </Box>
  );
} 