export function formatDate(dateString: string, format: 'short' | 'long' | 'shortwithtime' = 'short'): string {
  const date = new Date(dateString);
  
  if (format === 'short') {
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  } else if (format === 'shortwithtime') {
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${day}/${month}/${year} ${hours}:${minutes}`;
  } else {
    return date.toLocaleDateString('en-US', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  }
}

export function formatCurrency(amount: number): string {
  if (amount === 0) return '-';
  
  return new Intl.NumberFormat('th-TH', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
}

// ฟังก์ชันสำหรับจัดรูปแบบระยะเวลา รวมถึงวัน เดือน ปี
export function formatDuration(duration: number, options?: { hourOnly?: boolean }): string {
  if (options?.hourOnly) {
    // แปลงจากวินาทีเป็นชั่วโมงและนาที
    const totalMinutes = Math.floor(duration / 60);
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    
    // แสดงผลแบบชั่วโมงและนาที
    if (hours > 0 && minutes > 0) {
      return `${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h`;
    } else {
      return `${minutes}m`;
    }
  }

  const seconds = Math.floor(duration % 60)
  const minutes = Math.floor((duration / 60) % 60)
  const hours = Math.floor((duration / 3600) % 24)
  const days = Math.floor((duration / 86400) % 30)
  const months = Math.floor((duration / 2592000) % 12)
  const years = Math.floor(duration / 31536000)
  
  let result = []

  // กรณีมีปี แสดงแค่ปีและเดือน
  if (years > 0) {
    result.push(`${years} years`)
    if (months > 0) result.push(`${months} months`)
    return result.join(' ')
  }

  // กรณีมีเดือน แสดงแค่เดือนและวัน
  if (months > 0) {
    result.push(`${months} months`)
    if (days > 0) result.push(`${days} days`)
    return result.join(' ')
  }

  // กรณีมีวัน แสดงแค่วันและชั่วโมง
  if (days > 0) {
    result.push(`${days} days`)
    if (hours > 0) result.push(`${hours} hours`)
    return result.join(' ')
  }

  // กรณีมีชั่วโมง แสดงแค่ชั่วโมงและนาที
  if (hours > 0) {
    result.push(`${hours} hours`)
    if (minutes > 0) result.push(`${minutes} minutes`)
    return result.join(' ')
  }

  // กรณีมีแค่นาทีและวินาที
  if (minutes > 0) {
    result.push(`${minutes} minutes`)
    if (seconds > 0) result.push(`${seconds} seconds`)
    return result.join(' ')
  }

  // กรณีมีแค่วินาที
  if (seconds > 0) {
    return `${seconds} seconds`
  }

  return '0 seconds'
}