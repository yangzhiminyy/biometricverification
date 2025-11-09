import { useQuery } from "@tanstack/react-query";
import { fetchModalities } from "../api/biometric";

export const modalitiesQueryKey = ["modalities"];

export function useModalities() {
  return useQuery({
    queryKey: modalitiesQueryKey,
    queryFn: fetchModalities,
  });
}

