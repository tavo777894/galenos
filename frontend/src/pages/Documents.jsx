import React from 'react';
import { FileText } from 'lucide-react';

const Documents = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <FileText className="w-8 h-8 text-primary-600" />
          Documentos
        </h1>
        <p className="text-gray-600 mt-1">
          Historial de documentos generados
        </p>
      </div>

      <div className="card p-12 text-center">
        <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Próximamente
        </h3>
        <p className="text-gray-600">
          Esta sección estará disponible en el próximo sprint
        </p>
      </div>
    </div>
  );
};

export default Documents;
