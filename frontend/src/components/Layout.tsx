import type { ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, FileText, LogOut, Users } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Button } from './Button';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Formulaires', href: '/formulaires', icon: FileText },
    ...(user?.role === 'ADMIN' ? [{ name: 'Utilisateurs', href: '/users', icon: Users }] : []),
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              {/* Logo */}
              <Link to="/dashboard" className="flex items-center">
                <span className="text-2xl font-bold text-blue-600">FormBuilder</span>
              </Link>

              {/* Navigation principale */}
              <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      inline-flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                      ${
                        isActive(item.href)
                          ? 'text-blue-700 bg-blue-50'
                          : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                      }
                    `}
                  >
                    <item.icon className="w-4 h-4 mr-2" />
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>

            {/* Menu utilisateur */}
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700 hidden sm:block">
                {user?.username || user?.email}
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Contenu principal */}
      <main>{children}</main>
    </div>
  );
};
