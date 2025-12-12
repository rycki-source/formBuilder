// Configuration ESLint pour les formulaires dynamiques
// Désactive certaines règles strictes pour les fichiers de validation et parsing

module.exports = {
  overrides: [
    {
      files: [
        'src/features/DynamicForm/utils/referentielValidator.ts',
        'src/features/DynamicForm/utils/parser.ts',
        'src/features/DynamicForm/utils/validationEngine.ts'
      ],
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-unused-vars': ['warn', { 
          argsIgnorePattern: '^_',
          varsIgnorePattern': '^_'
        }]
      }
    }
  ]
};
