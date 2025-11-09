export interface Match {
  user_id: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface EnrollmentResponse {
  status: string;
  user_id: string;
  stored_samples?: string[];
}

export interface VerificationResponse {
  status: string;
  decision: boolean;
  threshold: number;
  matches: Match[];
}

export interface DeleteResponse {
  status: string;
  user_id: string;
}

export interface GetUserResponse {
  status: string;
  user_id: string;
  modality: string;
  samples?: string[];
}

export interface ModalitiesResponse {
  modalities: string[];
}

export interface EnrollmentPayload {
  modality: string;
  userId: string;
  samples: string[];
}

export interface VerificationPayload {
  modality: string;
  sample: string;
  topK?: number;
}

