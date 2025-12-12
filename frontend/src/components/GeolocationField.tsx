import React, { useState } from 'react';
import { MapPin, Loader } from 'lucide-react';

interface GeolocationFieldProps {
  value?: { latitude: number; longitude: number; accuracy?: number };
  onChange: (value: { latitude: number; longitude: number; accuracy?: number }) => void;
  label: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
}

export const GeolocationField: React.FC<GeolocationFieldProps> = ({
  value,
  onChange,
  label,
  required = false,
  disabled = false,
  error
}) => {
  const [loading, setLoading] = useState(false);
  const [geoError, setGeoError] = useState<string | null>(null);

  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setGeoError('La géolocalisation n\'est pas supportée par votre navigateur');
      return;
    }

    setLoading(true);
    setGeoError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        };
        onChange(location);
        setLoading(false);
      },
      (err) => {
        setGeoError(
          err.code === 1 ? 'Permission refusée' :
          err.code === 2 ? 'Position indisponible' :
          err.code === 3 ? 'Délai d\'attente dépassé' :
          'Erreur de géolocalisation'
        );
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="flex gap-2 items-start">
        <button
          type="button"
          onClick={getCurrentLocation}
          disabled={disabled || loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Localisation...
            </>
          ) : (
            <>
              <MapPin className="w-4 h-4" />
              Obtenir ma position
            </>
          )}
        </button>

        {value && (
          <div className="flex-1 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="text-sm">
              <p className="font-medium text-gray-700">Position enregistrée :</p>
              <p className="text-gray-600">
                Lat: {value.latitude.toFixed(6)}, Long: {value.longitude.toFixed(6)}
              </p>
              {value.accuracy && (
                <p className="text-xs text-gray-500 mt-1">
                  Précision: ±{Math.round(value.accuracy)}m
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {(error || geoError) && (
        <p className="text-sm text-red-600">{error || geoError}</p>
      )}

      {!value && !loading && !error && !geoError && (
        <p className="text-sm text-gray-500">
          Cliquez sur le bouton pour obtenir votre position actuelle
        </p>
      )}
    </div>
  );
};

export default GeolocationField;
