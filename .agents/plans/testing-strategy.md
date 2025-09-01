# Testing Strategy Plan for SimpleNote to Obsidian Importer

## Overview
This document outlines the comprehensive testing strategy for the SimpleNote to Obsidian importer, covering unit tests, integration tests, and test data management.

## Testing Framework
- **Primary Framework**: pytest (Python standard)
- **Mocking**: unittest.mock for dependency isolation
- **Coverage**: pytest-cov for code coverage reporting
- **Test Structure**: Standard pytest conventions with fixtures

## Test Data Strategy

### Sample Data Structure
Create realistic but synthetic test data that mirrors actual SimpleNote exports:

```
tests/
├── fixtures/
│   ├── sample_notes/
│   │   ├── simple_note_1.txt
│   │   ├── complex_note_with_tags.txt
│   │   ├── note_with_special_chars.txt
│   │   ├── empty_note.txt
│   │   └── long_note.txt
│   ├── sample_json/
│   │   ├── basic_metadata.json
│   │   ├── complex_metadata.json
│   │   ├── edge_cases.json
│   │   └── invalid_metadata.json
│   └── expected_outputs/
│       ├── basic_expected.md
│       ├── complex_expected.md
│       └── organized_expected/
```

### Test Data Characteristics
- **Simple Notes**: Basic text content, minimal metadata
- **Complex Notes**: Multiple tags, markdown formatting, special characters
- **Edge Cases**: Empty notes, very long content, unusual characters
- **Invalid Data**: Malformed JSON, missing files, corrupted content

## Unit Testing Strategy

### Core Components to Test

1. **MetadataParser** (`src/metadata_parser.py`)
   - JSON parsing accuracy
   - Filename generation logic
   - Error handling for malformed data
   - Date/time conversion

2. **ContentProcessor** (`src/content_processor.py`)
   - File discovery and reading
   - Content extraction accuracy
   - Error handling for missing/corrupted files

3. **EditorPipeline** (`src/editor/pipeline.py`)
   - Individual processor functionality
   - Pipeline orchestration
   - Configuration handling

4. **Editor Components**
   - **TagInjector**: Pattern matching and tag application
   - **FolderOrganizer**: Content-based categorization
   - **ContentTransformer**: Formatting and cleanup

5. **ObsidianFormatter** (`src/obsidian_formatter.py`)
   - YAML frontmatter generation
   - Filename sanitization
   - Folder structure creation

6. **Configuration System**
   - **ImportConfig**: Validation and defaults
   - **ConfigManager**: Preset loading and merging

### Unit Test Structure
```python
# Example test structure
class TestMetadataParser:
    def setup_method(self):
        # Setup test fixtures
        
    def test_parse_basic_json(self):
        # Test basic JSON parsing
        
    def test_filename_generation(self):
        # Test filename creation logic
        
    def test_invalid_json_handling(self):
        # Test error handling
```

## Integration Testing Strategy

### Full Pipeline Tests
1. **End-to-End Processing**
   - Complete import workflow from SimpleNote export to Obsidian vault
   - Multiple configuration presets (minimal, basic, organized, full)
   - Verify complete folder structure and file content

2. **Configuration Integration**
   - Preset application and merging
   - Custom configuration validation
   - CLI argument processing

3. **Error Recovery**
   - Partial import scenarios
   - Missing file handling
   - Invalid data recovery

### Integration Test Categories
- **Happy Path**: Standard successful imports with various configurations
- **Error Scenarios**: Missing files, corrupted data, permission issues
- **Edge Cases**: Empty exports, single note exports, maximum complexity
- **Regression Tests**: Verify Phase 1 compatibility, Phase 2 features

## Refactoring for Testability

### Dependency Injection
Current classes have tight coupling that makes testing difficult:

1. **File System Abstraction**
   - Create `FileSystemInterface` for mocking file operations
   - Inject file system dependency into processors

2. **Configuration Injection**
   - Pass configuration objects explicitly rather than loading internally
   - Make configuration validation separate from application logic

3. **Output Separation**
   - Separate formatting logic from file writing
   - Return structured data that can be verified independently

### Proposed Refactoring Changes

1. **MetadataParser**
   - Accept file content as parameter instead of reading directly
   - Return structured metadata dictionary
   - Separate filename generation into utility function

2. **ContentProcessor**
   - Accept file system interface for dependency injection
   - Return content dictionary instead of writing files
   - Separate file discovery from content processing

3. **EditorPipeline**
   - Make all processors configurable and injectable
   - Return transformation results for verification
   - Separate pipeline logic from configuration loading

4. **ObsidianFormatter**
   - Accept content and metadata as parameters
   - Return formatted content without writing files
   - Separate folder structure logic from file operations

## Test Implementation Steps

### Phase 1: Foundation (Days 1-2)
1. Set up pytest configuration and dependencies
2. Create sample test data fixtures
3. Implement basic test structure and utilities
4. Write initial unit tests for utility functions

### Phase 2: Unit Tests (Days 3-5)
1. Test MetadataParser components
2. Test ContentProcessor functionality
3. Test EditorPipeline and individual processors
4. Test ObsidianFormatter logic
5. Test Configuration system

### Phase 3: Integration Tests (Days 6-7)
1. End-to-end pipeline tests
2. Configuration integration tests
3. Error scenario testing
4. Performance and edge case testing

### Phase 4: Refactoring (Days 8-9)
1. Identify and implement testability improvements
2. Update existing tests for refactored code
3. Add additional test coverage for new abstractions
4. Verify all tests pass with refactored code

## Success Criteria
- **Unit Test Coverage**: >90% for core business logic
- **Integration Test Coverage**: All major user scenarios covered
- **Performance**: Tests run in <30 seconds total
- **Maintainability**: Clear test structure, good fixtures, minimal duplication
- **Reliability**: Tests are deterministic and don't depend on external factors

## Continuous Integration
- Tests run automatically on all commits
- Coverage reports generated and tracked
- Failure notifications for breaking changes
- Performance regression detection

## Test Data Management
- All test data is synthetic and safe for version control
- Test data represents realistic but non-sensitive scenarios
- Regular review of test data relevance and completeness
- Clear separation between test data and actual user data