import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { patientsAPI } from '../services/api';
import {
  Users,
  PlusCircle,
  Search,
  FileText,
  Eye,
  Loader2,
  AlertCircle,
  Phone,
  Mail,
  CreditCard,
  Calendar,
} from 'lucide-react';

const PatientList = () => {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await patientsAPI.getAll();
      setPatients(data);
    } catch (err) {
      setError('Error al cargar pacientes: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCard = async (patientId, e) => {
    e.stopPropagation();
    try {
      const result = await patientsAPI.generateCard(patientId);
      alert(`PDF generado: ${result.filename}`);
    } catch (err) {
      alert('Error al generar PDF: ' + (err.response?.data?.detail || err.message));
    }
  };

  const filteredPatients = patients.filter(
    (patient) =>
      patient.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.ci.includes(searchTerm)
  );

  const calculateAge = (dateOfBirth) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    return age;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          <p className="text-sm text-gray-600">Cargando pacientes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Users className="w-8 h-8 text-primary-600" />
            Pacientes
          </h1>
          <p className="text-gray-600 mt-1">
            {filteredPatients.length} paciente{filteredPatients.length !== 1 ? 's' : ''} registrado{filteredPatients.length !== 1 ? 's' : ''}
          </p>
        </div>

        <button
          onClick={() => navigate('/patients/new')}
          className="btn btn-primary flex items-center gap-2"
        >
          <PlusCircle className="w-5 h-5" />
          Nuevo Paciente
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Search */}
      <div className="card p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por nombre o CI..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Patient list */}
      {filteredPatients.length === 0 ? (
        <div className="card p-12 text-center">
          <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {searchTerm ? 'No se encontraron pacientes' : 'No hay pacientes registrados'}
          </h3>
          <p className="text-gray-600 mb-6">
            {searchTerm
              ? 'Intenta con otro término de búsqueda'
              : 'Comienza registrando tu primer paciente'}
          </p>
          {!searchTerm && (
            <button
              onClick={() => navigate('/patients/new')}
              className="btn btn-primary inline-flex items-center gap-2"
            >
              <PlusCircle className="w-5 h-5" />
              Nuevo Paciente
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredPatients.map((patient) => (
            <div
              key={patient.id}
              onClick={() => navigate(`/patients/${patient.id}`)}
              className="card p-6 hover:shadow-lg transition-shadow cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                    <span className="text-primary-700 font-semibold text-lg">
                      {patient.first_name[0]}{patient.last_name[0]}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">
                      {patient.first_name} {patient.last_name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {calculateAge(patient.date_of_birth)} años
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <CreditCard className="w-4 h-4" />
                  <span>CI: {patient.ci}</span>
                </div>

                {patient.phone && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Phone className="w-4 h-4" />
                    <span>{patient.phone}</span>
                  </div>
                )}

                {patient.email && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Mail className="w-4 h-4" />
                    <span className="truncate">{patient.email}</span>
                  </div>
                )}

                <div className="flex items-center gap-2 text-gray-500 text-xs">
                  <Calendar className="w-3 h-3" />
                  <span>
                    Registrado: {new Date(patient.created_at).toLocaleDateString('es-ES')}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/patients/${patient.id}`);
                  }}
                  className="flex-1 px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors flex items-center justify-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  Ver Detalle
                </button>

                <button
                  onClick={(e) => handleGenerateCard(patient.id, e)}
                  className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  title="Generar ficha PDF"
                >
                  <FileText className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PatientList;
