import { useEffect, useRef, useState, useCallback } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

interface ScannerProps {
  onScan: (isbn: string) => void;
  onError?: (error: string) => void;
}

export default function Scanner({ onScan, onError }: ScannerProps) {
  const [isRunning, setIsRunning] = useState(false);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const containerId = 'isbn-scanner';

  const start = useCallback(async () => {
    if (scannerRef.current) return;

    const scanner = new Html5Qrcode(containerId);
    scannerRef.current = scanner;

    try {
      await scanner.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 250, height: 100 } },
        (decodedText) => {
          // Only accept EAN-13 / ISBN-like barcodes
          const cleaned = decodedText.replace(/[\s\-]/g, '');
          if (/^\d{10}(\d{3})?$/.test(cleaned) || /^\d{9}[Xx]$/.test(cleaned)) {
            onScan(cleaned);
          }
        },
        () => {
          // Scan failure – ignored, keep scanning
        },
      );
      setIsRunning(true);
    } catch (err) {
      let msg = err instanceof Error ? err.message : 'Camera access denied';
      if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
        msg = 'Camera requires HTTPS. Please access this page via https:// to enable barcode scanning.';
      }
      onError?.(msg);
    }
  }, [onScan, onError]);

  const stop = useCallback(async () => {
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop();
      } catch {
        // ignore
      }
      scannerRef.current = null;
      setIsRunning(false);
    }
  }, []);

  useEffect(() => {
    start();
    return () => {
      stop();
    };
  }, [start, stop]);

  return (
    <div className="scanner-container">
      <div id={containerId} className="scanner-video" />
      {isRunning && <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Point your camera at a barcode…</p>}
    </div>
  );
}
