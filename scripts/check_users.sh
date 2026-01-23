#!/bin/bash
# Quick script to check what users exist in the database
# Usage: bash scripts/check_users.sh

API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_KEY="${FRONTEND_API_KEY}"

if [ -z "$FRONTEND_KEY" ]; then
  echo "Error: FRONTEND_API_KEY not set"
  exit 1
fi

echo "Checking users in database..."
echo ""

# Try to search for common test names
for name in "Test User" "test user" "Test"; do
  echo "Searching for: '$name'"
  curl -s -X GET "$API_URL/users/search?name=$name" \
    -H "X-API-Key: $FRONTEND_KEY" | python3 -m json.tool 2>/dev/null || echo "No results or error"
  echo ""
done

echo ""
echo "To test with a specific user, use:"
echo "  curl -X GET \"$API_URL/users/results/by-credentials?name=Test%20User&birthdate=1990-05-15\" -H \"X-API-Key: \$FRONTEND_API_KEY\""
