import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Users, FileText, Activity, TrendingUp } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const stats = [
    { name: 'Pacientes', value: '—', icon: Users, color: 'bg-blue-500' },
    { name: 'Documentos', value: '—', icon: FileText, color: 'bg-green-500' },
    { name: 'Este Mes', value: '—', icon: TrendingUp, color: 'bg-purple-500' },
    { name: 'Actividad', value: '—', icon: Activity, color: 'bg-orange-500' },
  ];

  const quickActions = [
    {
      title: 'Ver Pacientes',
      description: 'Lista completa de pacientes registrados',
      icon: Users,
      action: () => navigate('/patients'),
      color: 'bg-blue-50 text-blue-700',
    },
    {
      title: 'Ver Documentos',
      description: 'Historial de documentos generados',
      icon: FileText,
      action: () => navigate('/documents'),
      color: 'bg-green-50 text-green-700',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Bienvenido, {user?.username}
        </h1>
        <p className="text-gray-600 mt-1">
          Sistema de Historia Clínica Electrónica - Galenos
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    {stat.name}
                  </p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Acciones Rápidas
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.title}
                onClick={action.action}
                className="card p-6 text-left hover:shadow-lg transition-shadow group"
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-lg ${action.color}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">
                      {action.title}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {action.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tip */}
      <div className="card p-6 bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-primary-600 rounded-lg">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">
              💡 Tip: Command Palette
            </h3>
            <p className="text-sm text-gray-700">
              Presiona <kbd className="px-2 py-1 bg-white rounded border border-gray-300 text-xs font-mono">Ctrl+K</kbd> o <kbd className="px-2 py-1 bg-white rounded border border-gray-300 text-xs font-mono">⌘K</kbd> para abrir el buscador global y acceder rápidamente a pacientes y acciones.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
