/**
 * Hijri Calendar Utilities
 * Converts Gregorian dates to Hijri (Islamic) calendar dates
 */

/**
 * Convert a Gregorian date to Hijri date
 * @param {Date} gregorianDate - The Gregorian date to convert
 * @returns {Object} - {day: number, month: number, year: number}
 */
export function convertToHijri(gregorianDate) {
  // Use Intl.DateTimeFormat with Islamic calendar
  const formatter = new Intl.DateTimeFormat('en-US-u-ca-islamic', {
    day: 'numeric',
    month: 'numeric',
    year: 'numeric'
  });

  const parts = formatter.formatToParts(gregorianDate);

  const hijriDate = {
    day: parseInt(parts.find(p => p.type === 'day')?.value || '1'),
    month: parseInt(parts.find(p => p.type === 'month')?.value || '1'),
    year: parseInt(parts.find(p => p.type === 'year')?.value || '1444')
  };

  return hijriDate;
}

/**
 * Get Hijri month names
 * @param {string} lang - Language code ('en' or 'ar')
 * @returns {Array<string>} - Array of month names
 */
export function getHijriMonthNames(lang = 'en') {
  const months = {
    ar: [
      'محرم',
      'صفر',
      'ربيع الأول',
      'ربيع الآخر',
      'جمادى الأولى',
      'جمادى الآخرة',
      'رجب',
      'شعبان',
      'رمضان',
      'شوال',
      'ذو القعدة',
      'ذو الحجة'
    ],
    en: [
      'Muharram',
      'Safar',
      'Rabi\' al-Awwal',
      'Rabi\' al-Thani',
      'Jumada al-Awwal',
      'Jumada al-Thani',
      'Rajab',
      'Sha\'ban',
      'Ramadan',
      'Shawwal',
      'Dhul-Qi\'dah',
      'Dhul-Hijjah'
    ]
  };

  return months[lang] || months.en;
}

/**
 * Format a Hijri date as a string
 * @param {Object} hijriDate - {day, month, year}
 * @param {string} lang - Language code ('en' or 'ar')
 * @returns {string} - Formatted date string
 */
export function formatHijriDate(hijriDate, lang = 'en') {
  const monthNames = getHijriMonthNames(lang);
  const monthName = monthNames[hijriDate.month - 1];

  if (lang === 'ar') {
    return `${hijriDate.day} ${monthName} ${hijriDate.year} هـ`;
  }

  return `${monthName} ${hijriDate.day}, ${hijriDate.year} AH`;
}
