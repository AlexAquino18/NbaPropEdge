declare module '@/components/ui/modal' {
  import React from 'react';

  interface ModalProps {
    children: React.ReactNode;
    onClose: () => void;
  }

  export const Modal: React.FC<ModalProps>;
}