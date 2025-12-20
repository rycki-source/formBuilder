import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useSimpleTranslation } from '../hooks/useSimpleTranslation';
import { useAuth } from '../hooks/useAuth';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { ErrorAlert } from '../components/ErrorAlert';
import { Eye, EyeOff } from 'lucide-react';

export const LoginPage = () => {
  const { translate } = useSimpleTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
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
      setErrorMessage(translate('Identifiants invalides', 'Invalid credentials'));
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">FormBuilder</h1>
          <p className="text-gray-600">{translate('Connectez-vous à votre compte', 'Sign in to your account')}</p>
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
              label={translate('Email', 'Email')}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={translate('votreemail@exemple.com', 'youremail@example.com')}
              required
              autoComplete="email"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {translate('Mot de passe', 'Password')}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={translate('Entrez votre mot de passe', 'Enter your password')}
                  required
                  autoComplete="current-password"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                  aria-label={translate('Afficher/Masquer le mot de passe', 'Show/Hide password')}
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              <div className="mt-2 text-right">
                <Link 
                  to="/forgot-password" 
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  {translate('Mot de passe oublié ?', 'Forgot password?')}
                </Link>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={isLoading}
            >
              {translate('Se connecter', 'Sign in')}
            </Button>

            <div className="text-center text-sm text-gray-600">
              {translate('Pas encore de compte ?', 'No account yet?')}{' '}
              <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
                {translate('S\'inscrire', 'Register')}
              </Link>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};
