import { useTranslation } from 'react-i18next';

export const useSimpleTranslation = () => {
  const { i18n } = useTranslation();
  
  const translate = (frenchText: string, englishText: string): string => {
    return i18n.language === 'en' ? englishText : frenchText;
  };

  return { translate, currentLanguage: i18n.language };
};