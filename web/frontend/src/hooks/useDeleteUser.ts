import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteUser } from "../api/biometric";
import { modalitiesQueryKey } from "./useModalities";
import { userDetailQueryKey } from "./useUserDetail";

export function useDeleteUser(
  modality: string,
  onSuccess?: () => void,
  onError?: (error: Error) => void,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => deleteUser(modality, userId),
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: modalitiesQueryKey });
      queryClient.invalidateQueries({ queryKey: userDetailQueryKey(modality, userId) });
      onSuccess?.();
    },
    onError,
  });
}

