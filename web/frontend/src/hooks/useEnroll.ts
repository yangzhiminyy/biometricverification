import { useMutation } from "@tanstack/react-query";
import { enrollUser } from "../api/biometric";
import type { EnrollmentResponse } from "../types/biometric";

export function useEnroll(onSuccess?: (data: EnrollmentResponse) => void, onError?: (error: Error) => void) {
  return useMutation({
    mutationFn: enrollUser,
    onSuccess,
    onError,
  });
}

