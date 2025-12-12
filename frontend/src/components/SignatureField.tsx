import React, { useRef, useState } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { Eraser, Download } from 'lucide-react';
import { Button } from './Button';

interface SignatureFieldProps {
  value?: string; // Base64 de l'image
  onChange: (value: string) => void;
  label: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
}

export const SignatureField: React.FC<SignatureFieldProps> = ({
  value,
  onChange,
  label,
  required = false,
  disabled = false,
  error
}) => {
  const sigCanvas = useRef<SignatureCanvas>(null);
  const [isEmpty, setIsEmpty] = useState(true);

  const handleEnd = () => {
    if (sigCanvas.current) {
      const dataUrl = sigCanvas.current.toDataURL('image/png');
      onChange(dataUrl);
      setIsEmpty(sigCanvas.current.isEmpty());
    }
  };

  const handleClear = () => {
    if (sigCanvas.current) {
      sigCanvas.current.clear();
      onChange('');
      setIsEmpty(true);
    }
  };

  const handleDownload = () => {
    if (sigCanvas.current && !isEmpty) {
      const dataUrl = sigCanvas.current.toDataURL('image/png');
      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = `signature_${Date.now()}.png`;
      link.click();
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="border-2 border-gray-300 rounded-lg overflow-hidden bg-white">
        <SignatureCanvas
          ref={sigCanvas}
          canvasProps={{
            className: 'w-full h-48',
            style: { touchAction: 'none' }
          }}
          onEnd={handleEnd}
          backgroundColor="white"
        />
      </div>

      <div className="flex gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleClear}
          disabled={disabled || isEmpty}
        >
          <Eraser className="w-4 h-4 mr-2" />
          Effacer
        </Button>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleDownload}
          disabled={disabled || isEmpty}
        >
          <Download className="w-4 h-4 mr-2" />
          Télécharger
        </Button>

        <div className="flex-1 text-right">
          <p className="text-xs text-gray-500 leading-8">
            {isEmpty ? 'Signez dans la zone ci-dessus' : 'Signature enregistrée'}
          </p>
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      {value && !isEmpty && (
        <div className="mt-2 p-2 bg-gray-50 rounded border border-gray-200">
          <p className="text-xs text-gray-600 mb-1">Aperçu :</p>
          <img src={value} alt="Signature" className="max-h-20 border border-gray-300 rounded" />
        </div>
      )}
    </div>
  );
};

export default SignatureField;
