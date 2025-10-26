#!/bin/bash
# Test script to verify NHScribe deployment on Raspberry Pi

echo "🧪 NHScribe Deployment Test Suite"
echo "=================================="
echo ""

PI_IP="10.249.84.213"
BACKEND_PORT="8000"
FRONTEND_PORT="3000"

BACKEND_URL="http://${PI_IP}:${BACKEND_PORT}"
FRONTEND_URL="http://${PI_IP}:${FRONTEND_PORT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local url=$1
    local name=$2
    
    echo -n "Testing ${name}... "
    
    if curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${url}" | grep -q "200\|404"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to check if server is reachable
check_server() {
    local ip=$1
    echo -n "Checking if Raspberry Pi is reachable... "
    
    if ping -c 1 -W 2 "${ip}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Cannot reach ${ip}. Check network connection."
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "1. Network Connectivity Tests"
echo "------------------------------"
check_server "${PI_IP}"
echo ""

echo "2. Backend API Tests"
echo "--------------------"
test_endpoint "${BACKEND_URL}/" "API Root"
test_endpoint "${BACKEND_URL}/patients/" "Patients Endpoint"
test_endpoint "${BACKEND_URL}/letters/recent" "Recent Letters Endpoint"
test_endpoint "${BACKEND_URL}/docs" "API Documentation"
echo ""

echo "3. Frontend Tests"
echo "-----------------"
test_endpoint "${FRONTEND_URL}" "Frontend Homepage"
echo ""

echo "4. Summary"
echo "----------"
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Deployment is successful.${NC}"
    echo ""
    echo "Access your application at:"
    echo "  Frontend: ${FRONTEND_URL}"
    echo "  API Docs: ${BACKEND_URL}/docs"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Check the output above.${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Ensure both backend and frontend are running"
    echo "  2. Check firewall settings: sudo ufw status"
    echo "  3. Verify services with: ps aux | grep -E 'python|node'"
    echo "  4. Check logs in the terminal where services are running"
    echo ""
    echo "For more help, see DEPLOYMENT_CHECKLIST.md"
    exit 1
fi

