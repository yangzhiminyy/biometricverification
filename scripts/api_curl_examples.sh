#!/usr/bin/env bash
# Simple curl helpers for Biometric Verification API.
# Usage:
#   bash scripts/api_curl_examples.sh start    # Print available commands
#   bash scripts/api_curl_examples.sh enroll   # Enroll demo user
#   bash scripts/api_curl_examples.sh verify   # Verify sample
#   bash scripts/api_curl_examples.sh get      # Query stored info
#   bash scripts/api_curl_examples.sh delete   # Remove demo user
#
# Ensure the FastAPI server is running:
#   uvicorn biometric_platform.interfaces.api.app:app --reload

set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost:8000}
MODALITY=${MODALITY:-face}
USER_ID=${USER_ID:-demo_user}

function enroll() {
  curl -sS -X POST "${BASE_URL}/biometric/${MODALITY}/enroll" \
    -H "Content-Type: application/json" \
    -d @"-"<<'JSON'
{
  "user_id": "'${USER_ID}'",
  "samples": [
    "sample_frame_1",
    "sample_frame_2"
  ]
}
JSON
}

function verify() {
  curl -sS -X POST "${BASE_URL}/biometric/${MODALITY}/verify" \
    -H "Content-Type: application/json" \
    -d @"-"<<'JSON'
{
  "sample": "sample_frame_1",
  "top_k": 3
}
JSON
}

function get_user() {
  curl -sS "${BASE_URL}/biometric/${MODALITY}/${USER_ID}"
}

function delete_user() {
  curl -sS -X DELETE "${BASE_URL}/biometric/${MODALITY}/${USER_ID}"
}

function list_modalities() {
  curl -sS "${BASE_URL}/biometric/modalities"
}

function usage() {
  cat <<EOF
Available commands:
  enroll           Enroll demo data for user '${USER_ID}'
  verify           Verify sample against stored embeddings
  get              Fetch stored information for '${USER_ID}'
  delete           Delete stored data for '${USER_ID}'
  modalities       List enabled modalities

Environment overrides:
  BASE_URL=<url>        (default http://localhost:8000)
  MODALITY=<modality>   (default face)
  USER_ID=<user>        (default demo_user)
EOF
}

case "${1:-help}" in
  enroll) enroll ;;
  verify) verify ;;
  get) get_user ;;
  delete) delete_user ;;
  modalities) list_modalities ;;
  help|start|*) usage ;;
esac

