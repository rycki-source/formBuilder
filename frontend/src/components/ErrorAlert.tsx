import { XCircle, AlertTriangle, Info } from 'lucide-react';

interface ErrorAlertProps {
  error: string | null;
  onClose?: () => void;
  type?: 'error' | 'warning' | 'info';
}

export const ErrorAlert = ({ error, onClose, type = 'error' }: ErrorAlertProps) => {
  if (!error) return null;

  // Parser le message structuré
  const lines = error.split('\n');
  const errorCode = lines[0]?.includes(':') ? lines[0].split(':')[0].trim() : '';
  const message = lines[0]?.includes(':') ? lines[0].split(':').slice(1).join(':').trim() : lines[0];
  const action = lines.find(line => line.startsWith('➜'))?.replace('➜', '').trim();
  const details = lines.filter(line => !line.startsWith('➜') && line !== lines[0]).join('\n').trim();

  const getStyles = () => {
    switch (type) {
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: 'text-yellow-600',
          title: 'text-yellow-800',
          text: 'text-yellow-700',
          Icon: AlertTriangle
        };
      case 'info':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          icon: 'text-blue-600',
          title: 'text-blue-800',
          text: 'text-blue-700',
          Icon: Info
        };
      default:
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: 'text-red-600',
          title: 'text-red-800',
          text: 'text-red-700',
          Icon: XCircle
        };
    }
  };

  const styles = getStyles();
  const IconComponent = styles.Icon;

  return (
    <div className={`${styles.bg} ${styles.border} border rounded-lg p-4 mb-4`}>
      <div className="flex items-start">
        <div className="shrink-0">
          <IconComponent className={`h-5 w-5 ${styles.icon}`} />
        </div>
        <div className="ml-3 flex-1">
          {errorCode && (
            <h3 className={`text-sm font-medium ${styles.title} mb-1`}>
              {errorCode}
            </h3>
          )}
          <p className={`text-sm ${styles.text}`}>
            {message}
          </p>
          {details && (
            <p className={`text-sm ${styles.text} mt-2 whitespace-pre-line`}>
              {details}
            </p>
          )}
          {action && (
            <div className="mt-3 pt-3 border-t border-current border-opacity-20">
              <p className={`text-sm font-medium ${styles.text}`}>
                <span className="mr-2">➜</span>
                {action}
              </p>
            </div>
          )}
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <button
              onClick={onClose}
              className={`inline-flex ${styles.icon} hover:opacity-75 focus:outline-none`}
            >
              <span className="sr-only">Fermer</span>
              <XCircle className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
