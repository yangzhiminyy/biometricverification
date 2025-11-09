import { useMutation } from "@tanstack/react-query";
import { verifySample } from "../api/biometric";
import type { VerificationResponse } from "../types/biometric";

export function useVerify(onSuccess?: (data: VerificationResponse) => void, onError?: (error: Error) => void) {
  return useMutation({
    mutationFn: verifySample,
    onSuccess,
    onError,
  });
}

