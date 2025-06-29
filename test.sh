#!/usr/bin/env bash

set -e

API="http://localhost:8000"
AGENT="http://localhost:9000"
USER_ID=1

echo "1) Health check:"
curl -s $API/ && echo -e "\n"

echo "2) Intake (ASRS-5):"
IN=$(curl -s -X POST $API/intake/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","birthdate":"1990-01-01","answers":[0,1,2,3,4,0]}')
echo "$IN" | jq    # requires jq; just for pretty-print
SESSION_UID=$(echo "$IN" | jq -r .session_uid)
echo "→ session_uid = $SESSION_UID"
echo

echo "3) Calibration start:"
curl -s -X POST $AGENT/calibrate/start && echo
echo

# Example calibration points (you’d do all your 9 points here)
for POINT in "100 100" "640 360" "1180 620"; do
  read X Y <<<"$POINT"
  echo "3.x) Calibrate point ($X,$Y):"
  curl -s -X POST $AGENT/calibrate/point \
    -H "Content-Type: application/json" \
    -d "{\"session_uid\":\"$SESSION_UID\",\"x\":$X,\"y\":$Y,\"duration\":1.0,\"samples\":30}" \
    | jq
  echo
done

echo "3.4) Finish calibration:"
curl -s -X POST $AGENT/calibrate/finish | jq
echo

echo "4) Start (or validate) session:"
curl -s -X POST $API/session/start \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":$USER_ID,\"session_uid\":\"$SESSION_UID\"}" \
  | jq
echo

echo "5) Launch acquisition client via agent:"
curl -s -X POST $AGENT/start \
  -H "Content-Type: application/json" \
  -d "{\"session_uid\":\"$SESSION_UID\",\"user_id\":$USER_ID,\"api_url\":\"$API/acquisition/batch\",\"fps\":20}" \
  | jq
echo

echo "6) Simulate a few acquisition samples (batched ingestion):"
curl -s -X POST $API/acquisition/batch \
  -H "Content-Type: application/json" \
  -d "[ 
    {\"user_id\":$USER_ID,\"session_uid\":\"$SESSION_UID\",\"timestamp\":1000,\"left_eye\":{\"x\":100,\"y\":100},\"right_eye\":{\"x\":105,\"y\":100},\"ear\":0.3,\"blink\":false},
    {\"user_id\":$USER_ID,\"session_uid\":\"$SESSION_UID\",\"timestamp\":1020,\"left_eye\":{\"x\":101,\"y\":101},\"right_eye\":{\"x\":106,\"y\":101},\"ear\":0.28,\"blink\":true}
  ]" \
  | jq
echo

echo "7) Log Go/No-Go events:"
# Stimulus onset (Go = O)
curl -s -X POST $API/session/event \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":$USER_ID,\"session_uid\":\"$SESSION_UID\",\"timestamp\":1000.0,\"event_type\":\"stimulus_onset\",\"stimulus\":\"O\"}"
echo
# Correct response
curl -s -X POST $API/session/event \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":$USER_ID,\"session_uid\":\"$SESSION_UID\",\"timestamp\":1000.35,\"event_type\":\"response\",\"stimulus\":\"O\",\"response\":true}"
echo
# Stimulus onset (No-Go = X)
curl -s -X POST $API/session/event \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":$USER_ID,\"session_uid\":\"$SESSION_UID\",\"timestamp\":1050.0,\"event_type\":\"stimulus_onset\",\"stimulus\":\"X\"}"
echo
# (no response → correct inhibition; skip POST for response=false)
echo

echo "8) Stop acquisition client:"
curl -s -X POST $AGENT/stop | jq
echo

echo "9) Stop session:"
curl -s -X POST $API/session/stop \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":$USER_ID}" \
  | jq
echo

echo "10) Compute session features:"
curl -s -X POST $API/features/compute/$SESSION_UID | jq
echo

echo "11) Fetch session features:"
curl -s $API/features/sessions/$SESSION_UID | jq
echo

echo "12) Fetch raw calibration points stored:"
curl -s $API/session/$SESSION_UID/calibration | jq
echo

echo "13) Fetch raw results:"
curl -s $API/results/$SESSION_UID | jq
echo

echo "14) (Optional) Delete raw results:"
curl -s -X DELETE $API/results/$SESSION_UID | jq
echo

echo "✅ All done! Replace or extend the simulated data with real camera & user interactions as you integrate the frontend."
