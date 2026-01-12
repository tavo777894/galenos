import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Command } from 'cmdk';
import {
  Search,
  Users,
  FileText,
  PlusCircle,
  User,
  Phone,
  CreditCard,
  X,
} from 'lucide-react';
import { searchAPI } from '../services/api';
import { cn } from '../utils/cn';

const CommandPalette = ({ open, onClose }) => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [results, setResults] = useState({ patients: [], actions: [] });
  const [loading, setLoading] = useState(false);

  // Debounced search
  useEffect(() => {
    if (!search) {
      setResults({ patients: [], actions: [] });
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        const data = await searchAPI.globalSearch(search, 10);
        setResults(data);
      } catch (error) {
        console.error('Search failed:', error);
        setResults({ patients: [], actions: [] });
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  const handleSelect = useCallback(
    (callback) => {
      callback();
      onClose();
      setSearch('');
    },
    [onClose]
  );

  // Default quick actions
  const quickActions = [
    {
      id: 'new-patient',
      title: 'Nuevo Paciente',
      icon: PlusCircle,
      action: () => navigate('/patients/new'),
    },
    {
      id: 'list-patients',
      title: 'Ver Pacientes',
      icon: Users,
      action: () => navigate('/patients'),
    },
    {
      id: 'list-documents',
      title: 'Ver Documentos',
      icon: FileText,
      action: () => navigate('/documents'),
    },
  ];

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 animate-in fade-in">
      <div className="fixed left-1/2 top-[20%] w-full max-w-2xl -translate-x-1/2 animate-in zoom-in-95">
        <Command
          className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-2xl"
          shouldFilter={false}
        >
          <div className="flex items-center border-b border-gray-200 px-4">
            <Search className="mr-2 h-5 w-5 shrink-0 text-gray-400" />
            <Command.Input
              value={search}
              onValueChange={setSearch}
              placeholder="Buscar pacientes o acciones... (Ctrl+K)"
              className="flex h-14 w-full bg-transparent py-3 text-sm outline-none placeholder:text-gray-400"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="h-4 w-4 text-gray-400" />
              </button>
            )}
            <button
              onClick={onClose}
              className="ml-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-gray-300 bg-gray-100 px-1.5 font-mono text-xs font-medium text-gray-600">
                ESC
              </kbd>
            </button>
          </div>

          <Command.List className="max-h-[400px] overflow-y-auto p-2">
            {loading && (
              <div className="py-6 text-center text-sm text-gray-500">
                Buscando...
              </div>
            )}

            {!loading && !search && (
              <Command.Group heading="Acciones Rápidas" className="mb-4">
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <Command.Item
                      key={action.id}
                      onSelect={() => handleSelect(action.action)}
                      className={cn(
                        'flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2.5 text-sm outline-none',
                        'hover:bg-primary-50 data-[selected]:bg-primary-50'
                      )}
                    >
                      <Icon className="h-5 w-5 text-gray-500" />
                      <span className="font-medium">{action.title}</span>
                    </Command.Item>
                  );
                })}
              </Command.Group>
            )}

            {!loading && search && results.patients.length > 0 && (
              <Command.Group heading="Pacientes" className="mb-4">
                {results.patients.map((patient) => (
                  <Command.Item
                    key={patient.id}
                    onSelect={() =>
                      handleSelect(() => navigate(`/patients/${patient.id}`))
                    }
                    className={cn(
                      'flex cursor-pointer flex-col gap-1 rounded-lg px-3 py-2.5 outline-none',
                      'hover:bg-primary-50 data-[selected]:bg-primary-50'
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-gray-400" />
                      <span className="font-medium text-gray-900">
                        {patient.full_name}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 pl-6 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <CreditCard className="h-3 w-3" />
                        CI: {patient.ci}
                      </span>
                      {patient.phone && (
                        <span className="flex items-center gap-1">
                          <Phone className="h-3 w-3" />
                          {patient.phone}
                        </span>
                      )}
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {!loading && search && results.actions && results.actions.length > 0 && (
              <Command.Group heading="Acciones" className="mb-4">
                {results.actions.map((action) => (
                  <Command.Item
                    key={action.id}
                    onSelect={() => handleSelect(() => navigate(action.route))}
                    className={cn(
                      'flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2.5 text-sm outline-none',
                      'hover:bg-primary-50 data-[selected]:bg-primary-50'
                    )}
                  >
                    <span className="font-medium">{action.title}</span>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {!loading &&
              search &&
              results.patients.length === 0 &&
              (!results.actions || results.actions.length === 0) && (
                <Command.Empty className="py-6 text-center text-sm text-gray-500">
                  No se encontraron resultados para "{search}"
                </Command.Empty>
              )}
          </Command.List>

          <div className="border-t border-gray-200 bg-gray-50 px-4 py-2 text-xs text-gray-500">
            <div className="flex items-center justify-between">
              <span>
                Navega con <kbd className="kbd">↑</kbd> <kbd className="kbd">↓</kbd>
              </span>
              <span>
                Selecciona con <kbd className="kbd">Enter</kbd>
              </span>
            </div>
          </div>
        </Command>
      </div>
    </div>
  );
};

export default CommandPalette;
