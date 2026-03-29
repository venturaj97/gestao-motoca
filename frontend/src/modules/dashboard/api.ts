import { http } from '@/shared/api/http'
import type { MonthlyView } from '@/shared/types/dashboard'

export const fetchMonthlyView = async () => {
  const { data } = await http.get<MonthlyView>('/visao-mes')
  return data
}
