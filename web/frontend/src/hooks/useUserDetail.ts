import { useQuery } from "@tanstack/react-query";
import { getUser } from "../api/biometric";

export function userDetailQueryKey(modality: string, userId: string) {
  return ["user", modality, userId] as const;
}

export function useUserDetail(modality: string | undefined, userId: string | undefined, enabled = true) {
  return useQuery({
    queryKey: modality && userId ? userDetailQueryKey(modality, userId) : ["user", modality, userId],
    queryFn: () => {
      if (!modality || !userId) {
        throw new Error("modality and userId required");
      }
      return getUser(modality, userId);
    },
    enabled: Boolean(modality && userId && enabled),
  });
}

