import type { ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useSimpleTranslation } from '../hooks/useSimpleTranslation';
import { Home, FileText, LogOut, Users, Code, Menu, X } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Button } from './Button';
import { LanguageSwitcher } from './LanguageSwitcher';
import { useState } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  const { translate } = useSimpleTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: translate('Tableau de bord', 'Dashboard'), href: '/dashboard', icon: Home },
    { name: translate('Formulaires', 'Forms'), href: '/formulaires', icon: FileText },
    { name: translate('Documentation API', 'API Docs'), href: '/api-docs', icon: Code },
    ...(user?.role === 'ADMIN' ? [{ name: translate('Utilisateurs', 'Users'), href: '/users', icon: Users }] : []),
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
    setMobileMenuOpen(false);
  };

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

  const handleNavClick = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="w-full max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16">
            <div className="flex items-center">
              {/* Logo */}
              <Link to="/dashboard" className="flex items-center" onClick={handleNavClick}>
                <span className="text-xl sm:text-2xl font-bold text-blue-600">FormBuilder</span>
              </Link>

              {/* Navigation principale - Desktop */}
              <div className="hidden md:ml-8 md:flex md:space-x-2 lg:space-x-4">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      inline-flex items-center px-2 lg:px-3 py-2 text-sm font-medium rounded-lg transition-colors
                      ${
                        isActive(item.href)
                          ? 'text-blue-700 bg-blue-50'
                          : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                      }
                    `}
                  >
                    <item.icon className="w-4 h-4 mr-1 lg:mr-2" />
                    <span className="hidden lg:inline">{item.name}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Menu utilisateur - Desktop */}
            <div className="hidden md:flex items-center gap-2 lg:gap-4">
              <LanguageSwitcher />
              <span className="text-sm text-gray-700 hidden lg:block truncate max-w-[150px]">
                {user?.username || user?.email}
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 lg:mr-2" />
                <span className="hidden lg:inline">{translate('Déconnexion', 'Logout')}</span>
              </Button>
            </div>

            {/* Bouton menu mobile */}
            <div className="flex md:hidden items-center">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100 focus:outline-none"
                aria-expanded="false"
              >
                <span className="sr-only">Open main menu</span>
                {mobileMenuOpen ? (
                  <X className="block h-6 w-6" aria-hidden="true" />
                ) : (
                  <Menu className="block h-6 w-6" aria-hidden="true" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Menu mobile */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-3 sm:px-4 pt-2 pb-3 space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={handleNavClick}
                  className={`
                    flex items-center px-3 py-2 text-base font-medium rounded-lg transition-colors
                    ${
                      isActive(item.href)
                        ? 'text-blue-700 bg-blue-50'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                    }
                  `}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              ))}
            </div>
            <div className="border-t border-gray-200 px-3 sm:px-4 py-3 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs sm:text-sm text-gray-700 truncate flex-1">
                  {user?.username || user?.email}
                </span>
                <div className="shrink-0">
                  <LanguageSwitcher />
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout} className="w-full justify-center">
                <LogOut className="w-4 h-4 mr-2" />
                {translate('Déconnexion', 'Logout')}
              </Button>
            </div>
          </div>
        )}
      </nav>

      {/* Contenu principal */}
      <main className="pb-8">{children}</main>
    </div>
  );
};
