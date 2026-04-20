import { toPng } from 'html-to-image';
import download from 'downloadjs';

/**
 * Exports a DOM element as a PNG image.
 * @param element The DOM element to capture
 * @param filename The name of the file to download
 * @param options Additional options for html-to-image
 */
export async function exportElementAsPng(element: HTMLElement, filename: string, options: any = {}) {
  try {
    await document.fonts.ready;
    await new Promise(r => setTimeout(r, 500));
    const dataUrl = await toPng(element, {
      cacheBust: true,
      pixelRatio: 2,
      fontEmbedCSS: '',
      ...options
    });
    download(dataUrl, `${filename}.png`, 'image/png');
    return true;
  } catch (error) {
    console.error('Error exporting image:', error);
    return false;
  }
}

/**
 * Triggers the browser print dialog.
 */
export function triggerPrint() {
  window.print();
}
