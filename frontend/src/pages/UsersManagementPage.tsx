import { useEffect, useState } from 'react';
import { Users, UserPlus, Trash2, Shield, User, Eye, EyeOff, Edit2 } from 'lucide-react';
import { useSimpleTranslation } from '../hooks/useSimpleTranslation';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import type { User as UserType } from '../types';
import { apiClient } from '../api/axios';

export const UsersManagementPage = () => {
  const { translate } = useSimpleTranslation();
  const [users, setUsers] = useState<UserType[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showEditPassword, setShowEditPassword] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    nom: '',
    prenom: '',
    mot_de_passe: '',
    role: 'UTILISATEUR',
  });
  const [editUser, setEditUser] = useState({
    id: 0,
    username: '',
    email: '',
    nom: '',
    prenom: '',
    role: 'UTILISATEUR',
    mot_de_passe: '',
  });

  // Validation du mot de passe en temps réel
  const validatePassword = (password: string) => {
    const errors: string[] = [];
    if (password.length < 8) errors.push(translate('8+ caractères', '8+ characters'));
    if (!/[A-Z]/.test(password)) errors.push(translate('1 majuscule', '1 uppercase'));
    if (!/[a-z]/.test(password)) errors.push(translate('1 minuscule', '1 lowercase'));
    if (!/[0-9]/.test(password)) errors.push(translate('1 chiffre', '1 number'));
    if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) errors.push(translate('1 spécial', '1 special'));
    
    // Vérifier les séquences faibles
    const weakSequences = ['123', '234', '345', '456', '567', '678', '789', '890', 
                          '321', '432', '543', '654', '765', '876', '987',
                          'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 
                          'hij', 'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop',
                          'opq', 'pqr', 'qrs', 'rst', 'stu', 'tuv', 'uvw', 
                          'vwx', 'wxy', 'xyz', 'cba', 'dcb', 'edc', 'fed'];
    const hasWeakSequence = weakSequences.some(seq => password.toLowerCase().includes(seq));
    
    // Vérifier les répétitions (aaa, 111, etc.)
    const hasRepetition = /(.)\1{2,}/.test(password);
    
    if (hasWeakSequence || hasRepetition) {
      errors.push(translate('Pas de séquence', 'No sequence'));
    }
    
    return errors;
  };

  const passwordErrors = newUser.mot_de_passe ? validatePassword(newUser.mot_de_passe) : [];

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<UserType[]>('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des utilisateurs:', error);
      alert(translate('Erreur lors du chargement des utilisateurs', 'Error loading users'));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log('Données envoyées:', newUser);
      await apiClient.post('/users', newUser);
      alert(translate('Utilisateur créé avec succès', 'User created successfully'));
      setShowCreateModal(false);
      setNewUser({ username: '', email: '', nom: '', prenom: '', mot_de_passe: '', role: 'UTILISATEUR' });
      setShowPassword(false);
      loadUsers();
    } catch (err: unknown) {
      console.error('Erreur lors de la création:', err);
      const error = err as { response?: { data?: { detail?: string | { message?: string } | Array<{ msg?: string, loc?: string[] }> } } };
      const detail = error.response?.data?.detail;
      let errorMessage = translate('Erreur lors de la création', 'Error creating user');
      
      if (typeof detail === 'string') {
        errorMessage = detail;
      } else if (detail && typeof detail === 'object' && 'message' in detail) {
        errorMessage = detail.message || errorMessage;
      } else if (Array.isArray(detail)) {
        // Erreurs de validation Pydantic
        const messages = detail.map(e => `${e.loc?.join('.') || 'field'}: ${e.msg}`).join('\n');
        errorMessage = messages || errorMessage;
      }
      
      alert(errorMessage);
    }
  };

  const handleDeleteUser = async (userId: number, username: string) => {
    if (!window.confirm(translate('Voulez-vous vraiment supprimer cet utilisateur ?', 'Do you really want to delete this user?'))) return;

    try {
      await apiClient.delete(`/users/${userId}`);
      alert(translate('Utilisateur supprimé avec succès', 'User deleted successfully'));
      loadUsers();
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      alert(translate('Erreur lors de la suppression', 'Error deleting user'));
    }
  };

  const handleToggleStatus = async (userId: number, currentStatus: string) => {
    const newStatus = currentStatus === 'ACTIF' ? 'INACTIF' : 'ACTIF';
    try {
      await apiClient.put(`/users/${userId}/status`, { statut: newStatus });
      loadUsers();
    } catch (error) {
      console.error('Erreur lors du changement de statut:', error);
      alert(translate('Erreur lors du changement de statut', 'Error changing status'));
    }
  };

  const openEditModal = (user: UserType) => {
    setEditUser({
      id: user.id,
      username: user.username,
      email: user.email,
      nom: user.nom || '',
      prenom: user.prenom || '',
      role: user.role,
      mot_de_passe: '',
    });
    setShowEditModal(true);
    setShowEditPassword(false);
  };

  const handleEditUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updateData: Record<string, unknown> = {
        username: editUser.username,
        email: editUser.email,
        nom: editUser.nom,
        prenom: editUser.prenom,
        role: editUser.role,
      };
      
      // Ajouter le mot de passe seulement s'il est fourni
      if (editUser.mot_de_passe && editUser.mot_de_passe.trim()) {
        updateData.mot_de_passe = editUser.mot_de_passe;
      }
      
      await apiClient.put(`/users/${editUser.id}`, updateData);
      alert(translate('Utilisateur modifié avec succès', 'User updated successfully'));
      setShowEditModal(false);
      setEditUser({ id: 0, username: '', email: '', nom: '', prenom: '', role: 'UTILISATEUR', mot_de_passe: '' });
      setShowEditPassword(false);
      loadUsers();
    } catch (err: unknown) {
      console.error('Erreur lors de la modification:', err);
      const error = err as { response?: { data?: { detail?: string | { message?: string } | Array<{ msg?: string, loc?: string[] }> } } };
      const detail = error.response?.data?.detail;
      let errorMessage = translate('Erreur lors de la modification', 'Error updating user');
      
      if (typeof detail === 'string') {
        errorMessage = detail;
      } else if (detail && typeof detail === 'object' && 'message' in detail) {
        errorMessage = detail.message || errorMessage;
      } else if (Array.isArray(detail)) {
        const messages = detail.map(e => `${e.loc?.join('.') || 'field'}: ${e.msg}`).join('\n');
        errorMessage = messages || errorMessage;
      }
      
      alert(errorMessage);
    }
  };

  const handleChangeRole = async (userId: number, newRole: string) => {
    try {
      await apiClient.put(`/users/${userId}/role`, { role: newRole });
      loadUsers();
    } catch (error) {
      console.error('Erreur lors du changement de rôle:', error);
      alert(translate('Erreur lors du changement de rôle', 'Error changing role'));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">{translate('Chargement...', 'Loading...')}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{translate('Gestion des utilisateurs', 'Users Management')}</h1>
            <p className="text-gray-600">{translate('Gérer les utilisateurs de la plateforme', 'Manage platform users')}</p>
          </div>
          <Button variant="primary" onClick={() => setShowCreateModal(true)}>
            <UserPlus className="w-5 h-5 mr-2" />
            {translate('Créer un utilisateur', 'Create User')}
          </Button>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{translate('Total utilisateurs', 'Total Users')}</p>
                <p className="text-2xl font-bold text-gray-900">{users.length}</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{translate('Administrateurs', 'Administrators')}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {users.filter(u => u.role === 'ADMIN').length}
                </p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <User className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{translate('Utilisateurs actifs', 'Active Users')}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {users.filter(u => u.statut === 'ACTIF').length}
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Liste des utilisateurs */}
        <Card title={translate('Liste des utilisateurs', 'Users List')}>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {translate('Utilisateur', 'User')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {translate('Email', 'Email')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {translate('Rôle', 'Role')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {translate('Statut', 'Status')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {translate('Dernière connexion', 'Last Login')}
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {translate('Actions', 'Actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{user.username}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">{user.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select
                        value={user.role}
                        onChange={(e) => handleChangeRole(user.id, e.target.value)}
                        aria-label={`Rôle de ${user.username}`}
                        className="text-sm border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="UTILISATEUR">{translate('Utilisateur', 'User')}</option>
                        <option value="ADMIN">{translate('Administrateur', 'Administrator')}</option>
                        <option value="MODERATEUR">{translate('Modérateur', 'Moderator')}</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleToggleStatus(user.id, user.statut)}
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.statut === 'ACTIF'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {user.statut}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {user.derniere_connexion
                        ? new Date(user.derniere_connexion).toLocaleDateString('fr-FR')
                        : translate('Jamais', 'Never')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex gap-2 justify-end">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => openEditModal(user)}
                          title={translate('Modifier', 'Edit')}
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleDeleteUser(user.id, user.username)}
                          title={translate('Supprimer', 'Delete')}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Modal de création */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <h3 className="text-xl font-bold text-gray-900 mb-4">{translate('Créer un utilisateur', 'Create User')}</h3>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <Input
                  label={translate('Nom d\'utilisateur', 'Username')}
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                  required
                />
                <Input
                  label={translate('Nom', 'Last Name')}
                  value={newUser.nom}
                  onChange={(e) => setNewUser({ ...newUser, nom: e.target.value })}
                  required
                />
                <Input
                  label={translate('Prénom', 'First Name')}
                  value={newUser.prenom}
                  onChange={(e) => setNewUser({ ...newUser, prenom: e.target.value })}
                  required
                />
                <Input
                  label={translate('Email', 'Email')}
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {translate('Mot de passe', 'Password')}
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={newUser.mot_de_passe}
                      onChange={(e) => setNewUser({ ...newUser, mot_de_passe: e.target.value })}
                      required
                      placeholder={translate('Entrez le mot de passe', 'Enter password')}
                      aria-label={translate('Mot de passe', 'Password')}
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
                  {newUser.mot_de_passe && (
                    <div className="mt-2">
                      {passwordErrors.length === 0 ? (
                        <div className="flex items-center text-green-600 text-sm">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          {translate('Mot de passe valide', 'Password valid')}
                        </div>
                      ) : (
                        <div className="space-y-1">
                          <p className="text-sm text-red-600 font-medium">
                            {translate('Requis:', 'Required:')}
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {passwordErrors.map((error, index) => (
                              <span key={index} className="text-xs bg-red-50 text-red-700 px-2 py-1 rounded">
                                ✗ {error}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  <p className="mt-1 text-xs text-gray-500">
                    {translate(
                      'Minimum 8 caractères : 1 majuscule, 1 minuscule, 1 chiffre, 1 caractère spécial (!@#$%^&*). Évitez les séquences (123, abc)',
                      'Minimum 8 characters: 1 uppercase, 1 lowercase, 1 number, 1 special character (!@#$%^&*). Avoid sequences (123, abc)'
                    )}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {translate('Rôle', 'Role')}
                  </label>
                  <select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                    aria-label="Rôle du nouvel utilisateur"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="UTILISATEUR">{translate('Utilisateur', 'User')}</option>
                    <option value="ADMIN">{translate('Administrateur', 'Administrator')}</option>
                    <option value="MODERATEUR">{translate('Modérateur', 'Moderator')}</option>
                  </select>
                </div>
                <div className="flex gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setShowCreateModal(false)} className="flex-1">
                    {translate('Annuler', 'Cancel')}
                  </Button>
                  <Button type="submit" variant="primary" className="flex-1">
                    {translate('Créer', 'Create')}
                  </Button>
                </div>
              </form>
            </Card>
          </div>
        )}

        {/* Modal d'édition d'utilisateur */}
        {showEditModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card title={translate('Modifier un utilisateur', 'Edit User')} className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <form onSubmit={handleEditUser} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={translate('Nom d\'utilisateur', 'Username')}
                    value={editUser.username}
                    onChange={(e) => setEditUser({ ...editUser, username: e.target.value })}
                    required
                    placeholder="johndoe"
                  />
                  <Input
                    label={translate('Email', 'Email')}
                    type="email"
                    value={editUser.email}
                    onChange={(e) => setEditUser({ ...editUser, email: e.target.value })}
                    required
                    placeholder="john@example.com"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={translate('Nom', 'Last Name')}
                    value={editUser.nom}
                    onChange={(e) => setEditUser({ ...editUser, nom: e.target.value })}
                    required
                    placeholder="Doe"
                  />
                  <Input
                    label={translate('Prénom', 'First Name')}
                    value={editUser.prenom}
                    onChange={(e) => setEditUser({ ...editUser, prenom: e.target.value })}
                    required
                    placeholder="John"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {translate('Mot de passe', 'Password')} <span className="text-gray-500 text-xs">({translate('Optionnel - Laissez vide pour ne pas modifier', 'Optional - Leave empty to keep current')})</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showEditPassword ? 'text' : 'password'}
                      value={editUser.mot_de_passe}
                      onChange={(e) => setEditUser({ ...editUser, mot_de_passe: e.target.value })}
                      placeholder={translate('Nouveau mot de passe (optionnel)', 'New password (optional)')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowEditPassword(!showEditPassword)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      {showEditPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  {editUser.mot_de_passe && (
                    <div className="mt-2">
                      {validatePassword(editUser.mot_de_passe).length > 0 && (
                        <div className="text-xs text-red-600 space-y-1">
                          <p className="font-semibold">{translate('Manquant:', 'Missing:')}</p>
                          <ul className="list-disc list-inside">
                            {validatePassword(editUser.mot_de_passe).map((error, idx) => (
                              <li key={idx}>{error}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {validatePassword(editUser.mot_de_passe).length === 0 && (
                        <p className="text-xs text-green-600">
                          ✓ {translate('Mot de passe fort', 'Strong password')}
                        </p>
                      )}
                    </div>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {translate('Rôle', 'Role')}
                  </label>
                  <select
                    value={editUser.role}
                    onChange={(e) => setEditUser({ ...editUser, role: e.target.value })}
                    aria-label={translate('Rôle', 'Role')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="UTILISATEUR">{translate('Utilisateur', 'User')}</option>
                    <option value="ADMIN">{translate('Administrateur', 'Administrator')}</option>
                    <option value="MODERATEUR">{translate('Modérateur', 'Moderator')}</option>
                  </select>
                </div>
                <div className="flex gap-2 pt-4">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => {
                      setShowEditModal(false);
                      setEditUser({ id: 0, username: '', email: '', nom: '', prenom: '', role: 'UTILISATEUR', mot_de_passe: '' });
                      setShowEditPassword(false);
                    }} 
                    className="flex-1"
                  >
                    {translate('Annuler', 'Cancel')}
                  </Button>
                  <Button 
                    type="submit" 
                    variant="primary" 
                    className="flex-1"
                    disabled={editUser.mot_de_passe && validatePassword(editUser.mot_de_passe).length > 0}
                  >
                    {translate('Enregistrer', 'Save')}
                  </Button>
                </div>
              </form>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};
