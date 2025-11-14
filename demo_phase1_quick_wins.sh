#!/bin/bash

# Thai TTS Phase 1 Quick Wins Demo Script
# This script demonstrates all the implemented Quick Wins

echo "🎯 Thai TTS Phase 1 Quick Wins Demo"
echo "=================================="
echo

# Function to print colored output
print_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

print_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

# Check if we're in the right directory
if [ ! -f "THAI_TTS_DEVELOPMENT_ROADMAP.md" ]; then
    print_error "Please run this script from the Thai TTS project root directory"
    exit 1
fi

echo "1. Quick Win #2: Docker Compose Development Environment"
echo "-----------------------------------------------------"
print_info "Generated files:"
ls -la docker-compose.thai.yml Dockerfile.thai-tts requirements.thai.txt start_thai_tts_dev.sh 2>/dev/null | awk '{print "  " $9}'

if [ -f "docker-compose.thai.yml" ]; then
    print_success "Docker Compose configuration ready!"
    print_info "To start the development environment:"
    print_info "  ./start_thai_tts_dev.sh"
    print_info "Then access:"
    print_info "  - Jupyter: http://localhost:8888"
    print_info "  - Grafana: http://localhost:3000"
    print_info "  - Prometheus: http://localhost:9090"
else
    print_error "Docker Compose files not found. Run: python create_docker_compose.py"
fi

echo
echo "2. Quick Win #3: Jupyter Notebooks for Voice Cloning"
echo "---------------------------------------------------"
if [ -f "notebooks/thai_voice_cloning_examples.ipynb" ]; then
    print_success "Voice cloning notebook created!"
    print_info "Features:"
    print_info "  - Thai text preprocessing"
    print_info "  - Voice cloning from reference audio"
    print_info "  - Emotion control"
    print_info "  - Speaker verification"
    print_info "  - Voice mixing and style transfer"
    
    if [ -f "notebooks/advanced_thai_tts_features.ipynb" ]; then
        print_success "Advanced features notebook also available!"
        print_info "  - Real-time streaming TTS"
        print_info "  - Thai phoneme analysis"
        print_info "  - Voice conversion"
        print_info "  - Batch processing"
        print_info "  - Performance optimization"
    fi
else
    print_error "Jupyter notebooks not found"
fi

echo
echo "3. Quick Win #4: Enhanced CLI Interface"
echo "-----------------------------------------"
if [ -f "thai_tts_cli.py" ]; then
    print_success "Enhanced CLI created!"
    print_info "Features:"
    print_info "  - Interactive menu-driven interface"
    print_info "  - Color-coded output"
    print_info "  - Voice cloning support"
    print_info "  - Batch processing"
    print_info "  - Progress bars"
    
    echo
    print_info "Usage examples:"
    print_info "  # Interactive mode"
    print_info "  python thai_tts_cli.py"
    print_info "  "
    print_info "  # Direct TTS"
    print_info "  python thai_tts_cli.py tts \"สวัสดีครับ\" --output hello.wav"
    print_info "  "
    print_info "  # Voice cloning"
    print_info "  python thai_tts_cli.py clone --reference speaker.wav --texts \"สวัสดี\" \"ลาก่อน\""
else
    print_error "CLI interface not found"
fi

echo
echo "4. Quick Win #5: Simple REST API"
echo "--------------------------------"
if [ -f "thai_tts_api.py" ]; then
    print_success "REST API created!"
    print_info "Features:"
    print_info "  - FastAPI-based REST API"
    print_info "  - Text-to-speech endpoint"
    print_info "  - Voice cloning with file upload"
    print_info "  - Batch processing"
    print_info "  - Real-time streaming"
    print_info "  - Thai text preprocessing"
    
    echo
    print_info "API Endpoints:"
    print_info "  POST /tts/synthesize - Synthesize speech"
    print_info "  POST /tts/clone - Clone voice"
    print_info "  POST /tts/batch - Batch processing"
    print_info "  POST /tts/stream - Stream TTS"
    print_info "  GET /tts/health - Health check"
    print_info "  GET /docs - API documentation"
    
    echo
    print_info "To start the API server:"
    print_info "  python thai_tts_api.py"
    print_info "  Then access: http://localhost:8000/docs"
else
    print_error "REST API not found"
fi

echo
echo "5. Testing the Implementation"
echo "-------------------------------"
if [ -f "test_phase1_quick_wins.py" ]; then
    print_success "Test script available!"
    print_info "Run: python test_phase1_quick_wins.py"
    print_info "This will verify all Quick Wins are working correctly."
else
    print_error "Test script not found"
fi

echo
echo "=================================="
echo "🎯 Phase 1 Quick Wins Summary"
echo "=================================="

# Count successful implementations
success_count=0
total_count=4

[ -f "docker-compose.thai.yml" ] && success_count=$((success_count + 1))
[ -f "notebooks/thai_voice_cloning_examples.ipynb" ] && success_count=$((success_count + 1))
[ -f "thai_tts_cli.py" ] && success_count=$((success_count + 1))
[ -f "thai_tts_api.py" ] && success_count=$((success_count + 1))

echo "Completed: $success_count/$total_count Quick Wins"

if [ $success_count -eq $total_count ]; then
    print_success "🎉 All Phase 1 Quick Wins implemented successfully!"
    echo
    echo "Next steps:"
    echo "1. Install dependencies: pip install -r requirements.enhanced.txt"
    echo "2. Start Docker environment: ./start_thai_tts_dev.sh"
    echo "3. Test CLI: python thai_tts_cli.py"
    echo "4. Test API: python thai_tts_api.py"
    echo "5. Explore notebooks: jupyter notebook"
    echo
    echo "Ready for Phase 2 implementation!"
else
    print_warning "Some Quick Wins are missing. Please check the implementation."
fi

echo
echo "For more details, see: THAI_TTS_DEVELOPMENT_ROADMAP.md"