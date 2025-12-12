/**
 * Parser pour différents formats de référentiel
 * Supporte JSON, YAML, JavaScript et TypeScript
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import type { FormReferentiel } from '../types/referentiel.types';
import jsyaml from 'js-yaml';

export type SupportedFormat = 'json' | 'yaml' | 'yml' | 'js' | 'ts';

export interface ParseResult {
  success: boolean;
  data?: FormReferentiel;
  error?: string;
  format?: SupportedFormat;
}

/**
 * Détecte automatiquement le format d'un contenu
 */
export function detectFormat(content: string, filename?: string): SupportedFormat | 'excel' {
  // Détection par extension de fichier
  if (filename) {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'xlsx' || ext === 'xls') return 'excel';
    if (ext === 'json') return 'json';
    if (ext === 'yaml' || ext === 'yml') return 'yaml';
    if (ext === 'js') return 'js';
    if (ext === 'ts') return 'ts';
  }

  // Détection par contenu
  const trimmed = content.trim();

  // JSON commence par { ou [
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    return 'json';
  }

  // JS/TS commence par export ou module.exports
  if (
    trimmed.startsWith('export') ||
    trimmed.includes('module.exports') ||
    trimmed.includes('export default')
  ) {
    // Vérifier si c'est du TypeScript (présence de types)
    if (
      trimmed.includes(': ') &&
      (trimmed.includes('interface') || trimmed.includes('type ') || trimmed.includes('<'))
    ) {
      return 'ts';
    }
    return 'js';
  }

  // YAML par défaut (si pas JSON/JS/TS)
  return 'yaml';
}

/**
 * Parse du contenu JSON
 */
function parseJSON(content: string): ParseResult {
  try {
    const data = JSON.parse(content) as FormReferentiel;
    return {
      success: true,
      data,
      format: 'json'
    };
  } catch (error: any) {
    return {
      success: false,
      error: `Erreur de parsing JSON: ${error.message}`,
      format: 'json'
    };
  }
}

/**
 * Parse du contenu YAML
 */
function parseYAML(content: string): ParseResult {
  try {
    const data = jsyaml.load(content) as FormReferentiel;
    return {
      success: true,
      data,
      format: 'yaml'
    };
  } catch (error: any) {
    return {
      success: false,
      error: `Erreur de parsing YAML: ${error.message}`,
      format: 'yaml'
    };
  }
}

/**
 * Parse du contenu JavaScript/TypeScript
 * 
 * Note: Cette fonction utilise une évaluation sécurisée limitée.
 * Pour une utilisation en production, il serait préférable d'utiliser
 * un environnement sandbox approprié ou un transpileur comme Babel.
 */
function parseJavaScript(content: string, format: 'js' | 'ts'): ParseResult {
  try {
    // Supprimer les imports et types TypeScript
    const cleanedContent = content
      .replace(/^import\s+.*?from\s+['"].*?['"];?\s*/gm, '')
      .replace(/^export\s+type\s+.*?;/gm, '')
      .replace(/^export\s+interface\s+.*?\{[\s\S]*?\}/gm, '')
      .replace(/:\s*\w+(<.*?>)?(\[\])?/g, '') // Supprimer les annotations de type
      .replace(/as\s+\w+(<.*?>)?/g, ''); // Supprimer les assertions de type

    // Extraire l'objet exporté
    let dataString = '';

    // export default { ... }
    const defaultExportMatch = cleanedContent.match(
      /export\s+default\s+(\{[\s\S]*\});?$/m
    );
    if (defaultExportMatch) {
      dataString = defaultExportMatch[1];
    } else {
      // module.exports = { ... }
      const moduleExportMatch = cleanedContent.match(
        /module\.exports\s*=\s*(\{[\s\S]*\});?$/m
      );
      if (moduleExportMatch) {
        dataString = moduleExportMatch[1];
      } else {
        // const referentiel = { ... }; export default referentiel;
        const constMatch = cleanedContent.match(
          /const\s+\w+\s*=\s*(\{[\s\S]*\});/
        );
        if (constMatch) {
          dataString = constMatch[1];
        }
      }
    }

    if (!dataString) {
      return {
        success: false,
        error: 'Impossible de trouver l\'objet exporté dans le fichier',
        format
      };
    }

    // Évaluation sécurisée (limitée aux objets JSON)
    // Note: En production, utiliser un vrai parser/sandbox
    const data = JSON.parse(dataString) as FormReferentiel;

    return {
      success: true,
      data,
      format
    };
  } catch (error: any) {
    return {
      success: false,
      error: `Erreur de parsing ${format.toUpperCase()}: ${error.message}`,
      format
    };
  }
}

/**
 * Parse du contenu selon le format détecté
 */
export function parseReferentiel(
  content: string,
  filename?: string
): ParseResult {
  const format = detectFormat(content, filename);

  switch (format) {
    case 'json':
      return parseJSON(content);

    case 'yaml':
    case 'yml':
      return parseYAML(content);

    case 'js':
      return parseJavaScript(content, 'js');

    case 'ts':
      return parseJavaScript(content, 'ts');

    default:
      return {
        success: false,
        error: `Format non supporté: ${format}`
      };
  }
}

/**
 * Parse un fichier
 */
export async function parseFile(file: File): Promise<ParseResult> {
  try {
    // Vérifier si c'est un fichier Excel
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext === 'xlsx' || ext === 'xls') {
      return {
        success: false,
        error: 'Les fichiers Excel doivent être traités par le backend. Utilisez l\'API /api/v1/referentiels/import/excel',
        format: 'json'
      };
    }

    const content = await file.text();
    return parseReferentiel(content, file.name);
  } catch (error: any) {
    return {
      success: false,
      error: `Erreur de lecture du fichier: ${error.message}`
    };
  }
}

/**
 * Parse depuis une URL
 */
export async function parseFromURL(url: string): Promise<ParseResult> {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      return {
        success: false,
        error: `Erreur HTTP: ${response.status} ${response.statusText}`
      };
    }

    const content = await response.text();
    const filename = url.split('/').pop() || undefined;

    return parseReferentiel(content, filename);
  } catch (error: any) {
    return {
      success: false,
      error: `Erreur de récupération depuis l'URL: ${error.message}`
    };
  }
}

/**
 * Valide que le contenu parsé est bien un FormReferentiel
 */
export function isValidReferentiel(data: any): data is FormReferentiel {
  return (
    data &&
    typeof data === 'object' &&
    data.version &&
    data.metadata &&
    data.config &&
    data.config.sections &&
    Array.isArray(data.config.sections)
  );
}

/**
 * Convertit un référentiel en JSON formaté
 */
export function stringifyReferentiel(
  referentiel: FormReferentiel,
  pretty = true
): string {
  return JSON.stringify(referentiel, null, pretty ? 2 : 0);
}

/**
 * Convertit un référentiel en YAML
 */
export function toYAML(referentiel: FormReferentiel): string {
  return jsyaml.dump(referentiel, {
    indent: 2,
    lineWidth: 120,
    noRefs: true
  });
}

/**
 * Exemple d'utilisation:
 * 
 * // Parse depuis un string
 * const result = parseReferentiel(jsonString);
 * if (result.success) {
 *   console.log(result.data);
 * }
 * 
 * // Parse depuis un fichier
 * const fileResult = await parseFile(file);
 * 
 * // Parse depuis une URL
 * const urlResult = await parseFromURL('https://example.com/form.json');
 */
