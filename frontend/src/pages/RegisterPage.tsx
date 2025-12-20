import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useSimpleTranslation } from '../hooks/useSimpleTranslation';
import { UserPlus } from 'lucide-react';
import { authApi } from '../api/auth';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { ErrorAlert } from '../components/ErrorAlert';
import { 
  FormValidator, 
  PasswordValidator, 
  type FieldValidationResult 
} from '../utils/validation';

export const RegisterPage = () => {
  const { translate } = useSimpleTranslation();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    nom: '',
    prenom: '',
    email: '',
    mot_de_passe: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldValidationResult>({});
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [showValidation, setShowValidation] = useState(false);

  // Validation en temps réel
  useEffect(() => {
    if (showValidation) {
      const validationResults = FormValidator.validateRegistrationData(formData);
      setFieldErrors(validationResults);
    }
  }, [formData, showValidation]);

  // Calcul de la force du mot de passe
  useEffect(() => {
    setPasswordStrength(PasswordValidator.calculateStrength(formData.mot_de_passe));
  }, [formData.mot_de_passe]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(false);
    setShowValidation(true);

    // Validation stricte côté client
    const validationResults = FormValidator.validateRegistrationData(formData);
    setFieldErrors(validationResults);

    // 🔍 DEBUG: Log des résultats de validation
    console.log('=== VALIDATION DEBUG ===');
    console.log('Form data:', formData);
    console.log('Validation results:', validationResults);
    console.log('Is form valid?', FormValidator.isFormValid(validationResults));
    
    // ⚠️ BLOQUE LA SOUMISSION si validation échoue
    if (!FormValidator.isFormValid(validationResults)) {
      const allErrors = FormValidator.getAllErrors(validationResults);
      console.log('🛑 VALIDATION ÉCHOUÉE - Erreurs:', allErrors);
      
      const errorMessage = `❌ Veuillez corriger les erreurs suivantes :\n\n${allErrors.map(err => `• ${err}`).join('\n')}`;
      setError(errorMessage);
      
      // Scroll vers le premier champ en erreur
      setTimeout(() => {
        const firstErrorField = document.querySelector('[data-error="true"]');
        if (firstErrorField) {
          firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
      
      // 🛑 ARRÊTE ICI - ne soumet PAS au backend
      console.log('❌ SOUMISSION BLOQUÉE');
      return;
    }

    // ✅ Validation réussie, on peut soumettre
    console.log('✅ VALIDATION RÉUSSIE - Soumission au backend');
    try {
      setLoading(true);
      await authApi.register({
        username: formData.username,
        nom: formData.nom,
        prenom: formData.prenom,
        email: formData.email,
        mot_de_passe: formData.mot_de_passe,
      });
      
      alert('Compte créé avec succès !');
      navigate('/login');
    } catch (err: unknown) {
      console.error('Erreur d\'inscription:', err);
      const error = err as { 
        response?: { 
          data?: { 
            detail?: string | { 
              message?: string; 
              error?: string;
              validation_errors?: string[];
            } 
          } 
        } 
      };
      
      // Gestion des erreurs de validation du backend
      if (typeof error.response?.data?.detail === 'object' && error.response.data.detail.validation_errors) {
        const validationErrors = error.response.data.detail.validation_errors;
        setError(`Erreurs de validation: ${validationErrors.join('; ')}`);
      } else if (typeof error.response?.data?.detail === 'object' && error.response.data.detail.message) {
        setError(error.response.data.detail.message);
      } else if (typeof error.response?.data?.detail === 'string') {
        setError(error.response.data.detail);
      } else {
        setError('Erreur lors de l\'inscription');
      }
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrengthColor = (strength: number) => {
    if (strength < 30) return 'bg-red-500';
    if (strength < 60) return 'bg-yellow-500';
    if (strength < 80) return 'bg-blue-500';
    return 'bg-green-500';
  };

  const getPasswordStrengthText = (strength: number): string => {
    if (strength < 30) return 'Faible';
    if (strength < 60) return 'Moyen';
    if (strength < 80) return 'Fort';
    return 'Très fort';
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">FormBuilder</h1>
          <p className="text-gray-600">Créez votre compte pour commencer</p>
        </div>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <ErrorAlert 
                error={error} 
                type="error" 
                onClose={() => setError('')} 
              />
            )}

            <div data-error={showValidation && fieldErrors.username && !fieldErrors.username.isValid ? "true" : "false"}>
              <Input
                label="Nom d'utilisateur"
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Entrez votre nom d'utilisateur"
                required
                autoComplete="username"
              />
              {showValidation && fieldErrors.username && !fieldErrors.username.isValid && (
                <div className="mt-1 text-sm text-red-600 font-semibold">
                  {fieldErrors.username.errors.map((error, index) => (
                    <div key={index}>⚠️ {error}</div>
                  ))}
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div data-error={showValidation && fieldErrors.prenom && !fieldErrors.prenom.isValid ? "true" : "false"}>
                <Input
                  label={translate('Prénom', 'First Name')}
                  type="text"
                  name="prenom"
                  value={formData.prenom}
                  onChange={handleChange}
                  placeholder={translate('Entrez votre prénom', 'Enter your first name')}
                  required
                  autoComplete="given-name"
                />
                {showValidation && fieldErrors.prenom && !fieldErrors.prenom.isValid && (
                  <div className="mt-1 text-sm text-red-600 font-semibold">
                    {fieldErrors.prenom.errors.map((error, index) => (
                      <div key={index}>⚠️ {error}</div>
                    ))}
                  </div>
                )}
              </div>

              <div data-error={showValidation && fieldErrors.nom && !fieldErrors.nom.isValid ? "true" : "false"}>
                <Input
                  label={translate('Nom', 'Last Name')}
                  type="text"
                  name="nom"
                  value={formData.nom}
                  onChange={handleChange}
                  placeholder={translate('Entrez votre nom', 'Enter your last name')}
                  required
                  autoComplete="family-name"
                />
                {showValidation && fieldErrors.nom && !fieldErrors.nom.isValid && (
                  <div className="mt-1 text-sm text-red-600 font-semibold">
                    {fieldErrors.nom.errors.map((error, index) => (
                      <div key={index}>⚠️ {error}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div data-error={showValidation && fieldErrors.email && !fieldErrors.email.isValid ? "true" : "false"}>
              <Input
                label={translate('Email', 'Email')}
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder={translate('votreemail@exemple.com', 'youremail@example.com')}
                required
                autoComplete="email"
              />
              {showValidation && fieldErrors.email && !fieldErrors.email.isValid && (
                <div className="mt-1 text-sm text-red-600 font-semibold">
                  {fieldErrors.email.errors.map((error, index) => (
                    <div key={index}>⚠️ {error}</div>
                  ))}
                </div>
              )}
            </div>

            <div data-error={showValidation && fieldErrors.mot_de_passe && !fieldErrors.mot_de_passe.isValid ? "true" : "false"}>
              <Input
                label={translate('Mot de passe', 'Password')}
                type="password"
                name="mot_de_passe"
                value={formData.mot_de_passe}
                onChange={handleChange}
                placeholder={translate('Entrez votre mot de passe', 'Enter your password')}
                required
                autoComplete="new-password"
              />
              
              {/* Indicateur de force du mot de passe */}
              {formData.mot_de_passe && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-600">Force du mot de passe</span>
                    <span className={`font-medium ${passwordStrength < 30 ? 'text-red-600' : passwordStrength < 60 ? 'text-yellow-600' : passwordStrength < 80 ? 'text-blue-600' : 'text-green-600'}`}>
                      {getPasswordStrengthText(passwordStrength)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${getPasswordStrengthColor(passwordStrength)}`}
                      style={{ width: `${passwordStrength}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {showValidation && fieldErrors.mot_de_passe && !fieldErrors.mot_de_passe.isValid && (
                <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm font-semibold text-red-800 mb-2">⚠️ Erreurs de mot de passe :</p>
                  <ul className="text-sm text-red-700 space-y-1">
                    {fieldErrors.mot_de_passe.errors.map((error, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span>•</span>
                        <span>{error}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div data-error={showValidation && fieldErrors.confirmPassword && !fieldErrors.confirmPassword.isValid ? "true" : "false"}>
              <Input
                label={translate('Confirmer le mot de passe', 'Confirm Password')}
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder={translate('Confirmez votre mot de passe', 'Confirm your password')}
                required
                autoComplete="new-password"
              />
              {showValidation && fieldErrors.confirmPassword && !fieldErrors.confirmPassword.isValid && (
                <div className="mt-1 text-sm text-red-600 font-semibold">
                  {fieldErrors.confirmPassword.errors.map((error, index) => (
                    <div key={index}>⚠️ {error}</div>
                  ))}
                </div>
              )}
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              disabled={loading}
            >
              <UserPlus className="w-5 h-5 mr-2" />
              {loading ? translate('Chargement...', 'Loading...') : translate('Créer un compte', 'Create Account')}
            </Button>

            <div className="text-center text-sm text-gray-600">
              {translate('Vous avez déjà un compte ?', 'Already have an account?')}{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                {translate('Se connecter', 'Login')}
              </Link>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};
