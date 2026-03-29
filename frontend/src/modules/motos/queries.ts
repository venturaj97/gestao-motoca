import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import {
  createMotoByPlate,
  createMotoManual,
  deleteMoto,
  fetchMotos,
  lookupPlate,
  setMotoActive,
  updateMoto,
} from './api'

export const useMotosQuery = () =>
  useQuery({
    queryKey: ['motos'],
    queryFn: fetchMotos,
  })

export const useCreateMotoManualMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createMotoManual,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['motos'] })
      await queryClient.invalidateQueries({ queryKey: ['monthly-view'] })
    },
  })
}

export const useCreateMotoByPlateMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createMotoByPlate,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['motos'] })
      await queryClient.invalidateQueries({ queryKey: ['monthly-view'] })
    },
  })
}

export const useUpdateMotoMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ motoId, payload }: { motoId: number; payload: Parameters<typeof updateMoto>[1] }) =>
      updateMoto(motoId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['motos'] })
    },
  })
}

export const useDeleteMotoMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteMoto,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['motos'] })
      await queryClient.invalidateQueries({ queryKey: ['monthly-view'] })
    },
  })
}

export const useSetMotoActiveMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ motoId, ativa }: { motoId: number; ativa: boolean }) => setMotoActive(motoId, ativa),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['motos'] })
    },
  })
}

export const usePlateLookupMutation = () =>
  useMutation({
    mutationFn: lookupPlate,
  })
