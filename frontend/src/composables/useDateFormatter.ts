/**
 * Provides centralized standards for application-wide date formatting functions.
 */
export function useDateFormatter() {
  /**
   * Formats an ISO string date to the localized PT format `00/00/0000`.
   * @param dateStr - Target ISO string
   * @returns Formatted textual string or fallback symbol `-`.
   */
  function formatDate(dateStr: string | null | undefined): string {
    if (!dateStr) return "-";
    const d = new Date(dateStr);
    return d.toLocaleDateString("pt-PT");
  }

  /**
   * Formats an ISO string to a dense timestamp structure (e.g., `00/00/0000, 00:00`).
   * @param date - Target ISO string
   * @returns Explicit Portuguese time-aligned date block or fallback symbol `-`.
   */
  function formatDateTime(date: string | null | undefined): string {
    if (!date) return "-";
    const d = new Date(date);
    return d.toLocaleDateString("pt-PT", { 
      day: "2-digit", 
      month: "2-digit", 
      year: "numeric", 
      hour: "2-digit", 
      minute: "2-digit" 
    });
  }

  /**
   * Formats a date string to a long verbose Portuguese layout. (e.g. segunda-feira, 30 de outubro de 2024)
   */
  function formatDateLong(dateStr: string | null | undefined): string {
    if (!dateStr) return "-";
    let target = dateStr;
    if (target.length === 10) target += "T12:00:00";
    return new Date(target).toLocaleDateString("pt-PT", {
      weekday: "long", day: "numeric", month: "long", year: "numeric"
    });
  }

  /**
   * Formats a date string to a short verbose Portuguese layout. (e.g. seg, 30 de out)
   */
  function formatDateShort(dateStr: string | null | undefined): string {
    if (!dateStr) return "-";
    let target = dateStr;
    if (target.length === 10) target += "T12:00:00";
    return new Date(target).toLocaleDateString("pt-PT", {
      weekday: "short", day: "numeric", month: "short"
    });
  }

  return { formatDate, formatDateTime, formatDateLong, formatDateShort };
}
