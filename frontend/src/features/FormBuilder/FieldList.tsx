import { useSortable } from '@dnd-kit/sortable';
import { GripVertical, Trash2 } from 'lucide-react';
import type { ChampFormulaire } from '../../types';

interface FieldListProps {
  fields: ChampFormulaire[];
  selectedIndex: number | null;
  onSelectField: (index: number) => void;
  onDeleteField: (index: number) => void;
}

interface FieldItemProps {
  field: ChampFormulaire;
  index: number;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

const FieldItem = ({ field, index, isSelected, onSelect, onDelete }: FieldItemProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
  } = useSortable({ id: index });

  return (
    <div
      ref={setNodeRef}
      className={`dnd-sortable-item p-4 bg-white border-2 rounded-lg cursor-pointer transition-all ${
        isSelected ? 'border-blue-500 shadow-md' : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-center gap-3">
        <div
          {...attributes}
          {...listeners}
          className="cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600"
        >
          <GripVertical className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-medium text-gray-900 truncate">{field.label}</h4>
            {field.obligatoire && (
              <span className="text-red-500 text-xs">*</span>
            )}
          </div>
          <p className="text-sm text-gray-500">{field.type_champ}</p>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="text-gray-400 hover:text-red-500 transition-colors"
          title="Supprimer le champ"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export const FieldList = ({ fields, selectedIndex, onSelectField, onDeleteField }: FieldListProps) => {
  return (
    <div className="space-y-3">
      {fields.map((field, index) => (
        <FieldItem
          key={index}
          field={field}
          index={index}
          isSelected={selectedIndex === index}
          onSelect={() => onSelectField(index)}
          onDelete={() => onDeleteField(index)}
        />
      ))}
    </div>
  );
};
