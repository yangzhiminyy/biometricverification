import { apiClient } from "./client";
import type {
  DeleteResponse,
  EnrollmentPayload,
  EnrollmentResponse,
  GetUserResponse,
  ModalitiesResponse,
  VerificationPayload,
  VerificationResponse,
} from "../types/biometric";

export async function fetchModalities(): Promise<ModalitiesResponse> {
  const { data } = await apiClient.get<ModalitiesResponse>("/biometric/modalities");
  return data;
}

export async function enrollUser(payload: EnrollmentPayload): Promise<EnrollmentResponse> {
  const { modality, userId, samples } = payload;
  const { data } = await apiClient.post<EnrollmentResponse>(
    `/biometric/${modality}/enroll`,
    {
      user_id: userId,
      samples,
    },
  );
  return data;
}

export async function verifySample(payload: VerificationPayload): Promise<VerificationResponse> {
  const { modality, sample, topK } = payload;
  const { data } = await apiClient.post<VerificationResponse>(
    `/biometric/${modality}/verify`,
    {
      sample,
      top_k: topK ?? 5,
    },
  );
  return data;
}

export async function getUser(modality: string, userId: string): Promise<GetUserResponse> {
  const { data } = await apiClient.get<GetUserResponse>(`/biometric/${modality}/${userId}`);
  return data;
}

export async function deleteUser(modality: string, userId: string): Promise<DeleteResponse> {
  const { data } = await apiClient.delete<DeleteResponse>(`/biometric/${modality}/${userId}`);
  return data;
}

