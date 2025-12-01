import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { DashboardPage } from './pages/DashboardPage';
import { FormListPage } from './pages/FormListPage';
import { FormTypeSelectionPage } from './pages/FormTypeSelectionPage';
import { FormBuilderPage } from './pages/FormBuilderPage';
import { FormPreviewPage } from './pages/FormPreviewPage';
import { SoumissionsPage } from './pages/SoumissionsPage';
import { UsersManagementPage } from './pages/UsersManagementPage';
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Routes publiques */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />

        {/* Routes protégées */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/formulaires"
          element={
            <ProtectedRoute>
              <Layout>
                <FormListPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/formulaires/creer"
          element={
            <ProtectedRoute>
              <Layout>
                <FormTypeSelectionPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/formulaires/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <FormBuilderPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/formulaires/:id/preview"
          element={
            <ProtectedRoute>
              <Layout>
                <FormPreviewPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/formulaires/:id/soumissions"
          element={
            <ProtectedRoute>
              <Layout>
                <SoumissionsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/users"
          element={
            <ProtectedRoute>
              <Layout>
                <UsersManagementPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Redirection par défaut */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
