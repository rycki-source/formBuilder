import { useState } from 'react';
import { Copy, Check, Code } from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';

export const APIDocumentationPage = () => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const API_BASE_URL = 'http://localhost:8000/api/v1';

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const endpoints = [
    {
      method: 'GET',
      path: '/formulaires/{id}/json',
      title: 'Récupérer la structure JSON',
      description: 'Obtenir la définition complète d\'un formulaire publié en JSON',
      public: true,
      example: `fetch('${API_BASE_URL}/formulaires/1/json')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));`,
      response: `{
  "id": 1,
  "nom": "Formulaire de contact",
  "description": "Un formulaire simple",
  "type_structurel": "simple",
  "structure_json": {
    "champs": [
      {
        "label": "Nom",
        "type_champ": "text",
        "obligatoire": true
      }
    ]
  },
  "api_endpoints": {
    "submit": "/api/v1/formulaires/1/submit",
    "json": "/api/v1/formulaires/1/json"
  }
}`
    },
    {
      method: 'POST',
      path: '/formulaires/{id}/submit',
      title: 'Soumettre un formulaire',
      description: 'Envoyer les données d\'un formulaire publié',
      public: true,
      example: `fetch('${API_BASE_URL}/formulaires/1/submit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    donnees: {
      "Nom": "Jean Dupont",
      "Email": "jean@example.com"
    },
    metadata: {
      source: "mon_site_web"
    }
  })
})
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));`,
      response: `{
  "success": true,
  "message": "Formulaire soumis avec succès",
  "soumission_id": 123,
  "statut": "en_attente"
}`
    },
    {
      method: 'GET',
      path: '/formulaires/{id}/embed',
      title: 'Code HTML embarquable',
      description: 'Obtenir le code HTML prêt à intégrer',
      public: true,
      example: `fetch('${API_BASE_URL}/formulaires/1/embed')
  .then(res => res.text())
  .then(html => {
    document.getElementById('form-container').innerHTML = html;
  });`,
      response: `<!-- HTML complet avec styles et JavaScript inclus -->
<div class="form-container">
  <form id="formulaire-1">
    <!-- Champs du formulaire -->
  </form>
  <script>
    // Code de soumission inclus
  </script>
</div>`
    }
  ];

  const reactExample = `// Exemple d'intégration React
import { useState, useEffect } from 'react';

function MyForm() {
  const [formStructure, setFormStructure] = useState(null);
  const [formData, setFormData] = useState({});
  
  useEffect(() => {
    // Récupérer la structure du formulaire
    fetch('${API_BASE_URL}/formulaires/1/json')
      .then(res => res.json())
      .then(data => setFormStructure(data))
      .catch(err => console.error(err));
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('${API_BASE_URL}/formulaires/1/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ donnees: formData })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert('Formulaire soumis avec succès !');
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };
  
  if (!formStructure) return <div>Chargement...</div>;
  
  return (
    <form onSubmit={handleSubmit}>
      {formStructure.structure_json.champs.map(field => (
        <div key={field.label}>
          <label>{field.label}</label>
          <input
            type={field.type_champ}
            required={field.obligatoire}
            onChange={(e) => setFormData({
              ...formData,
              [field.label]: e.target.value
            })}
          />
        </div>
      ))}
      <button type="submit">Envoyer</button>
    </form>
  );
}`;

  const vueExample = `<!-- Exemple d'intégration Vue.js -->
<template>
  <form @submit.prevent="handleSubmit" v-if="formStructure">
    <div v-for="field in formStructure.structure_json.champs" :key="field.label">
      <label>{{ field.label }}</label>
      <input
        :type="field.type_champ"
        :required="field.obligatoire"
        v-model="formData[field.label]"
      />
    </div>
    <button type="submit">Envoyer</button>
  </form>
</template>

<script>
export default {
  data() {
    return {
      formStructure: null,
      formData: {}
    };
  },
  mounted() {
    fetch('${API_BASE_URL}/formulaires/1/json')
      .then(res => res.json())
      .then(data => this.formStructure = data);
  },
  methods: {
    async handleSubmit() {
      const response = await fetch('${API_BASE_URL}/formulaires/1/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ donnees: this.formData })
      });
      
      const result = await response.json();
      if (result.success) {
        alert('Formulaire soumis avec succès !');
      }
    }
  }
};
</script>`;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Documentation API REST
          </h1>
          <p className="text-gray-600">
            Intégrez vos formulaires dans n'importe quelle application web
          </p>
        </div>

        {/* Introduction */}
        <Card className="mb-8">
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-900">🚀 Démarrage rapide</h2>
            <p className="text-gray-700">
              Notre API REST vous permet d'intégrer vos formulaires dans n'importe quel site web ou application.
              Tous les formulaires <strong>publiés</strong> sont accessibles via l'API publique sans authentification.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">URL de base</h3>
              <code className="text-sm text-blue-800">{API_BASE_URL}</code>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <h3 className="font-semibold text-amber-900 mb-2">⚠️ Important</h3>
              <p className="text-sm text-amber-800">
                Seuls les formulaires <strong>publiés</strong> sont accessibles via l'API publique.
                Les formulaires en brouillon nécessitent une authentification.
              </p>
            </div>
          </div>
        </Card>

        {/* Endpoints */}
        <div className="space-y-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900">📡 Endpoints disponibles</h2>
          
          {endpoints.map((endpoint, index) => (
            <Card key={index}>
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-lg font-mono text-sm font-bold ${
                      endpoint.method === 'GET' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {endpoint.method}
                    </span>
                    <code className="text-gray-700 font-mono">{endpoint.path}</code>
                  </div>
                  {endpoint.public && (
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-semibold rounded">
                      Public
                    </span>
                  )}
                </div>

                {/* Description */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{endpoint.title}</h3>
                  <p className="text-gray-600 text-sm">{endpoint.description}</p>
                </div>

                {/* Example */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold text-gray-700">Exemple de requête</h4>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleCopy(endpoint.example, index * 2)}
                    >
                      {copiedIndex === index * 2 ? (
                        <Check className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    <code>{endpoint.example}</code>
                  </pre>
                </div>

                {/* Response */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Réponse</h4>
                  <pre className="bg-gray-50 border border-gray-200 text-gray-800 p-4 rounded-lg overflow-x-auto text-sm">
                    <code>{endpoint.response}</code>
                  </pre>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Exemples d'intégration */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">💻 Exemples d'intégration</h2>

          {/* React */}
          <Card>
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Code className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-bold text-gray-900">React</h3>
              </div>
              <div className="relative">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopy(reactExample, 100)}
                  className="absolute top-4 right-4 z-10"
                >
                  {copiedIndex === 100 ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </Button>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{reactExample}</code>
                </pre>
              </div>
            </div>
          </Card>

          {/* Vue */}
          <Card>
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Code className="w-5 h-5 text-green-600" />
                <h3 className="text-lg font-bold text-gray-900">Vue.js</h3>
              </div>
              <div className="relative">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopy(vueExample, 101)}
                  className="absolute top-4 right-4 z-10"
                >
                  {copiedIndex === 101 ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </Button>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{vueExample}</code>
                </pre>
              </div>
            </div>
          </Card>
        </div>

        {/* Codes d'erreur */}
        <Card className="mt-8">
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-900">⚠️ Codes d'erreur</h2>
            <div className="space-y-2">
              <div className="flex gap-4 text-sm">
                <code className="font-mono font-bold text-red-600">404</code>
                <span className="text-gray-700">Formulaire non trouvé</span>
              </div>
              <div className="flex gap-4 text-sm">
                <code className="font-mono font-bold text-red-600">403</code>
                <span className="text-gray-700">Formulaire non publié ou accès refusé</span>
              </div>
              <div className="flex gap-4 text-sm">
                <code className="font-mono font-bold text-red-600">400</code>
                <span className="text-gray-700">Données invalides</span>
              </div>
              <div className="flex gap-4 text-sm">
                <code className="font-mono font-bold text-red-600">500</code>
                <span className="text-gray-700">Erreur serveur</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
