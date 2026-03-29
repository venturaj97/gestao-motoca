import { useQuery } from '@tanstack/vue-query'
import { fetchMonthlyView } from './api'

export const useMonthlyViewQuery = () =>
  useQuery({
    queryKey: ['monthly-view'],
    queryFn: fetchMonthlyView,
  })
