import { Type, Mail, Hash, Calendar, List, AlignLeft, CheckSquare, Circle, Upload, MousePointerClick, MapPin, PenTool } from 'lucide-react';
import { Card } from '../../components/Card';
import type { ChampFormulaire } from '../../types';

interface FieldPaletteProps {
  onAddField: (type: ChampFormulaire['type_champ']) => void;
}

const fieldTypes = [
  { type: 'text' as const, label: 'Texte', icon: Type },
  { type: 'email' as const, label: 'Email', icon: Mail },
  { type: 'number' as const, label: 'Nombre', icon: Hash },
  { type: 'date' as const, label: 'Date', icon: Calendar },
  { type: 'select' as const, label: 'Liste déroulante', icon: List },
  { type: 'textarea' as const, label: 'Zone de texte', icon: AlignLeft },
  { type: 'checkbox' as const, label: 'Case à cocher', icon: CheckSquare },
  { type: 'radio' as const, label: 'Bouton radio', icon: Circle },
  { type: 'file' as const, label: 'Fichier', icon: Upload },
  { type: 'geolocation' as const, label: 'Géolocalisation', icon: MapPin },
  { type: 'signature' as const, label: 'Signature', icon: PenTool },
  { type: 'button' as const, label: 'Bouton', icon: MousePointerClick },
];

export const FieldPalette = ({ onAddField }: FieldPaletteProps) => {
  return (
    <Card title="Types de champs" className="sticky top-24">
      <div className="space-y-2">
        {fieldTypes.map((field) => (
          <button
            key={field.type}
            onClick={() => onAddField(field.type)}
            className="w-full flex items-center gap-3 px-4 py-3 text-left bg-blue-600 text-white border-2 border-blue-800 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-sm cursor-pointer"
          >
            <field.icon className="w-5 h-5" />
            <span>{field.label}</span>
          </button>
        ))}
      </div>
    </Card>
  );
};
