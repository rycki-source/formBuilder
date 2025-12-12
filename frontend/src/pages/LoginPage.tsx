import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../hooks/useAuth';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { ErrorAlert } from '../components/ErrorAlert';

export const LoginPage = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(''); // Réinitialiser l'erreur avant la tentative
    
    try {
      await login({ username: email, password });
      navigate('/dashboard');
    } catch (err) {
      console.error('Erreur de connexion:', err);
      setErrorMessage(t('auth.invalidCredentials'));
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">{t('app.title')}</h1>
          <p className="text-gray-600">{t('auth.loginDescription')}</p>
        </div>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-6">
            {errorMessage && (
              <ErrorAlert 
                error={errorMessage} 
                type="error" 
                onClose={() => setErrorMessage('')} 
              />
            )}

            <Input
              label={t('auth.email')}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t('auth.emailPlaceholder')}
              required
              autoComplete="email"
            />

            <div>
              <Input
                label={t('auth.password')}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t('auth.passwordPlaceholder')}
                required
                autoComplete="current-password"
              />
              <div className="mt-2 text-right">
                <Link 
                  to="/forgot-password" 
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  {t('auth.forgotPassword')}
                </Link>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={isLoading}
            >
              {t('auth.loginButton')}
            </Button>

            <div className="text-center text-sm text-gray-600">
              {t('auth.noAccount')}{' '}
              <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
                {t('auth.registerButton')}
              </Link>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};
