# 7-Zip Test Framework Makefile

PYTHON := python3
TEST_DIR := tests
RESULTS_DIR := results

.PHONY: help test clean setup benchmark report

# Default target
help:
	@echo "7-Zip Test Framework"
	@echo "====================="
	@echo ""
	@echo "Available targets:"
	@echo "  setup      - Setup test environment"
	@echo "  test       - Run all tests"
	@echo "  benchmark  - Run performance benchmarks"
	@echo "  report     - Generate test report"
	@echo "  clean      - Clean test artifacts"
	@echo "  help       - Show this help"

# Setup test environment
setup:
	@echo "Setting up test environment..."
	$(PYTHON) -m pip install pyyaml psutil --user
	@mkdir -p $(RESULTS_DIR)/logs
	@mkdir -p $(RESULTS_DIR)/reports
	@mkdir -p $(RESULTS_DIR)/benchmarks
	@mkdir -p test_data
	@echo "Setup complete"

# Run all tests
test: setup
	@echo "Running comprehensive test suite..."
	cd $(TEST_DIR) && $(PYTHON) run_tests.py

# Run performance benchmarks
benchmark: setup
	@echo "Running performance benchmarks..."
	cd $(TEST_DIR) && $(PYTHON) test_framework.py --benchmark

# Generate report only
report: setup
	@echo "Generating test report..."
	cd $(TEST_DIR) && $(PYTHON) test_framework.py --report

# Quick test (framework validation)
quick-test: setup
	@echo "Running quick framework validation..."
	cd $(TEST_DIR) && $(PYTHON) test_framework.py --formats 7z --no-performance --no-compatibility --no-integrity

# Generate test data
generate-data: setup
	@echo "Generating test data..."
	cd $(TEST_DIR) && $(PYTHON) -c "from utils.file_generator import FileGenerator; FileGenerator({'test_settings': {'temp_dir': '/tmp/7z_tests'}}).generate_all()"

# Test specific formats
test-formats: setup
	@echo "Testing specific formats..."
	cd $(TEST_DIR) && $(PYTHON) test_framework.py --formats 7z,zip,gz

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	rm -rf $(RESULTS_DIR)
	rm -rf test_data
	rm -rf /tmp/7z_tests*
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Build 7-Zip (if needed)
build:
	@echo "Building 7-Zip..."
	@if [ ! -f "./CPP/7zip/Bundles/Alone7z/7z" ]; then \
		echo "Building 7-Zip..."; \
		cd CPP/7zip/Bundles/Alone7z && make -f makefile.gcc; \
		cd ../../..; \
	else \
		echo "7-Zip executable found"; \
	fi

# Full test suite (build + test)
full-test: build test
	@echo "Full test suite completed"

# Install dependencies
install-deps:
	@echo "Installing Python dependencies..."
	$(PYTHON) -m pip install pyyaml psutil --user

# Check dependencies
check-deps:
	@echo "Checking dependencies..."
	@$(PYTHON) -c "import yaml, psutil; print('Dependencies satisfied')" || echo "Dependencies missing - run 'make install-deps'"

# Development setup (for framework developers)
dev-setup: install-deps
	@echo "Setting up development environment..."
	@mkdir -p $(RESULTS_DIR)/{logs,reports,benchmarks}
	@mkdir -p test_data/{binary,text,mixed,reference}

# Run continuous integration tests
ci: setup
	@echo "Running CI tests..."
	cd $(TEST_DIR) && $(PYTHON) test_framework.py --formats 7z,zip --no-compatibility --no-integrity

# Run integration tests
integration: setup
	@echo "Running integration tests..."
	cd $(TEST_DIR) && $(PYTHON) test_framework.py --compatibility

# Generate documentation
docs: setup
	@echo "Generating documentation..."
	cd $(TEST_DIR) && $(PYTHON) -c "import yaml; print('Documentation generation not implemented')"

# Validate configuration
validate-config:
	@echo "Validating test configuration..."
	cd $(TEST_DIR) && $(PYTHON) -c "import yaml; yaml.safe_load(open('test_config.yaml')); print('Configuration valid')"

# Performance comparison (compare multiple runs)
compare: setup
	@echo "Running performance comparison..."
	@cd $(TEST_DIR) && $(PYTHON) -c "import glob; print('Comparison tool not implemented')"

# Archive test results
archive-results:
	@echo "Archiving test results..."
	@if [ -d "$(RESULTS_DIR)" ]; then \
		tar -czf 7z_test_results_$$(date +%Y%m%d_%H%M%S).tar.gz $(RESULTS_DIR)/; \
		echo "Results archived"; \
	else \
		echo "No results to archive"; \
	fi

# Show test statistics
stats:
	@echo "Test Statistics:"
	@if [ -d "$(RESULTS_DIR)" ]; then \
		echo "Results directory: $(RESULTS_DIR)"; \
		echo "Log files: $$(find $(RESULTS_DIR) -name "*.log" | wc -l)"; \
		echo "Report files: $$(find $(RESULTS_DIR) -name "*.html" | wc -l)"; \
		echo "Benchmark files: $$(find $(RESULTS_DIR) -name "*.json" | wc -l)"; \
	else \
		echo "No results found"; \
	fi