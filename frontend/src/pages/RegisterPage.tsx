import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { UserPlus } from 'lucide-react';
import { authApi } from '../api/auth';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { ErrorAlert } from '../components/ErrorAlert';

export const RegisterPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    mot_de_passe: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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

    // Validation
    if (formData.mot_de_passe !== formData.confirmPassword) {
      setError(t('auth.passwordMismatch'));
      return;
    }

    if (formData.mot_de_passe.length < 8) {
      setError(t('auth.passwordTooShort'));
      return;
    }

    if (!formData.email.includes('@')) {
      setError(t('auth.invalidEmail'));
      return;
    }

    try {
      setLoading(true);
      await authApi.register({
        username: formData.username,
        email: formData.email,
        mot_de_passe: formData.mot_de_passe,
      });
      
      alert(t('auth.accountCreated'));
      navigate('/login');
    } catch (err: unknown) {
      console.error('Erreur d\'inscription:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || t('auth.registrationError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">{t('app.title')}</h1>
          <p className="text-gray-600">{t('auth.registerDescription')}</p>
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

            <Input
              label={t('auth.username')}
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder={t('auth.usernamePlaceholder')}
              required
              autoComplete="username"
            />

            <Input
              label={t('auth.email')}
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder={t('auth.emailPlaceholder')}
              required
              autoComplete="email"
            />

            <Input
              label={t('auth.password')}
              type="password"
              name="mot_de_passe"
              value={formData.mot_de_passe}
              onChange={handleChange}
              placeholder={t('auth.passwordPlaceholder')}
              required
              autoComplete="new-password"
            />

            <Input
              label={t('auth.confirmPassword')}
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="••••••••"
              required
              autoComplete="new-password"
            />

            <div className="text-sm text-gray-600">
              <ul className="list-disc list-inside space-y-1">
                <li>Au moins 8 caractères</li>
                <li>Une majuscule et une minuscule recommandées</li>
                <li>Un chiffre et un caractère spécial recommandés</li>
              </ul>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              disabled={loading}
            >
              <UserPlus className="w-5 h-5 mr-2" />
              {loading ? t('common.loading') : t('auth.createAccount')}
            </Button>

            <div className="text-center text-sm text-gray-600">
              {t('auth.alreadyAccount')}{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                {t('auth.loginButton')}
              </Link>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};
