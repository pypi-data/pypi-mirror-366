"""Integration tests with real-world examples"""

import pytest
from pathlib import Path
from yaal_parser import YaalParser, YaalExtractor


class TestRealWorldExamples:
    """Test with real-world YAAL examples"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.extractor = YaalExtractor()
        self.fixtures_dir = Path(__file__).parent / "fixtures"
    
    def test_pipeline_configuration(self):
        """Test CI/CD pipeline configuration"""
        text = """#!pipeline
# CI/CD Pipeline Configuration

checkout:
  repository: github.com/user/repo
  branch: main

build:
  docker build -t myapp .
  run tests
  
deploy:
  environment: production
  script: { kubectl apply -f k8s/ }
  notifications:
    slack: "#deployments"
    email: team@company.com
"""
        result = self.parser.parse(text)
        assert result is not None
        
        # Test extraction
        data = self.extractor.extract(result)
        assert "_shebang" in data
        assert data["_shebang"] == "pipeline"
    
    def test_configuration_file(self):
        """Test application configuration file"""
        text = """# Application Configuration
database:
  host: localhost
  port: 5432
  name: myapp_db
  credentials:
    username: admin
    password: secret123

api:
  host: 0.0.0.0
  port: 8080
  endpoints:
    health: /health
    metrics: /metrics
    
logging:
  level: info
  file: /var/log/myapp.log
  format: json

features:
  authentication: true
  rate_limiting: true
  caching: false
"""
        result = self.parser.parse(text)
        assert result is not None
        
        # Test extraction
        data = self.extractor.extract(result)
        assert "database" in data
        assert "api" in data
        assert "logging" in data
    
    def test_infrastructure_as_code(self):
        """Test infrastructure as code example"""
        text = """#!infrastructure
# Infrastructure Definition

vpc:
  cidr: 10.0.0.0/16
  subnets:
    public:
      cidr: 10.0.1.0/24
      availability_zone: us-west-2a
    private:
      cidr: 10.0.2.0/24
      availability_zone: us-west-2b

security_groups:
  web:
    ingress:
      - port: 80
        protocol: tcp
        source: 0.0.0.0/0
      - port: 443
        protocol: tcp
        source: 0.0.0.0/0
  
instances:
  web_server:
    type: t3.micro
    ami: ami-12345678
    security_group: web
    user_data: {
      #!/bin/bash
      yum update -y
      yum install -y httpd
      systemctl start httpd
    }
"""
        result = self.parser.parse(text)
        assert result is not None
    
    def test_documentation_structure(self):
        """Test documentation structure"""
        text = """# Project Documentation

overview:
  description: \"\"\"This project implements a YAAL parser that can handle
both data structures and executable programs using
the same syntax.\"\"\"  
getting_started:
  requirements:
    python 3.8 or higher
    lark parser library
  
  installation:
    clone the repository
    install dependencies: pip install -r requirements.txt
    run tests: pytest
  
  quick_start: \"\"\"from yaal_parser import YaalParser\n\nparser = YaalParser()\nresult = parser.parse_file('config.yaal')\"\"\"

api_reference:
  classes:
    YaalParser:
      description: Main parser class
      methods:
        parse: Parse YAAL text
        parse_file: Parse YAAL file
        validate: Validate YAAL syntax
"""
        result = self.parser.parse(text)
        assert result is not None
    
    def test_multi_language_script(self):
        """Test multi-language script example"""
        text = """#!hibrid-code
# Multi-language execution example

python: {
  for i in range(10):
      if i % 2 == 0:
          print(f"Even: {i}")
}

javascript: {
  const numbers = [1, 2, 3, 4, 5];
  numbers.forEach(n => {
      console.log(`Number: ${n}`);
  });
}

bash: {
  echo "Starting deployment..."
  for service in web api db; do
      echo "Deploying $service"
      kubectl apply -f "$service.yaml"
  done
  echo "Deployment complete"
}

sql: {
  SELECT u.name, COUNT(o.id) as order_count
  FROM users u
  LEFT JOIN orders o ON u.id = o.user_id
  WHERE u.created_at > '2023-01-01'
  GROUP BY u.id, u.name
  ORDER BY order_count DESC;
}
"""
        result = self.parser.parse(text)
        assert result is not None


class TestComplexStructures:
    """Test complex nested and mixed structures"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
        self.extractor = YaalExtractor()
    
    def test_deeply_nested_config(self):
        """Test deeply nested configuration"""
        text = """application:
  name: MyApp
  version: 1.0.0
  
  environments:
    development:
      database:
        host: localhost
        port: 5432
        settings:
          pool_size: 5
          timeout: 30
          ssl:
            enabled: false
            cert_path: /path/to/cert
            
    production:
      database:
        host: prod-db.example.com
        port: 5432
        settings:
          pool_size: 20
          timeout: 60
          ssl:
            enabled: true
            cert_path: /etc/ssl/certs/db.pem
            key_path: /etc/ssl/private/db.key
            
  features:
    authentication:
      enabled: true
      providers:
        oauth2:
          google:
            client_id: google-client-id
            client_secret: google-secret
          github:
            client_id: github-client-id
            client_secret: github-secret
"""
        result = self.parser.parse(text)
        assert result is not None
        
        # Test that deeply nested structures are handled
        data = self.extractor.extract(result)
        assert "application" in data
    
    def test_mixed_content_types(self):
        """Test mixing different content types"""
        text = """#!mixed-content
# This example mixes all YAAL features

# Simple statements
production
debug mode enabled

# Key-value pairs
name: MyApplication
version: 2.1.0

# Keys with spaces and colons
api endpoint: https://api.example.com:8080/v1
database url: postgresql://user:pass@host:5432/db
log timestamp: 2023-12-01T10:30:45Z

# Quoted strings
description: "A comprehensive application"
command: "echo 'Hello World'"

# Triple-quoted multiline
documentation: \"\"\"This is a comprehensive example that demonstrates\nall the features of the YAAL language:\n\n1. Simple statements (no colons)\n2. Key-value pairs with the first colon rule\n3. Nested structures with indentation\n4. Brace blocks for raw content\n5. Different string types\n6. Comments and shebang lines\n\nURLs like https://example.com:8080 work perfectly,\nas do timestamps like 12:30:45.\"\"\"

# Brace blocks
startup_script: {
  #!/bin/bash
  echo "Starting application..."
  export NODE_ENV=production
  npm start
}

# Nested structures
configuration:
  # Simple statements in nested context
  enable_logging
  enable_metrics
  
  # Key-value in nested context
  port: 8080
  host: 0.0.0.0
  
  # Further nesting
  database:
    primary:
      host: db1.example.com
      port: 5432
    replica:
      host: db2.example.com
      port: 5432
      
  # Mixed content in nesting
  services:
    web_service
    api_service
    worker_service
    cache:
      type: redis
      host: cache.example.com
      
# Complex brace block
deployment_script: {
  # Multi-line script with various syntax
  kubectl create namespace myapp || true
  
  # Apply configurations
  for config in configmap secret service deployment; do
    kubectl apply -f "k8s/$config.yaml"
  done
  
  # Wait for deployment
  kubectl rollout status deployment/myapp
  
  echo "Deployment completed successfully!"
}
"""
        result = self.parser.parse(text)
        assert result is not None


class TestPerformance:
    """Test parser performance with large inputs"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_large_file_parsing(self):
        """Test parsing large file"""
        # Generate a large YAAL structure
        lines = ["#!large-test"]
        
        # Add many key-value pairs
        for i in range(1000):
            lines.append(f"key_{i}: value_{i}")
        
        # Add nested structure
        lines.append("nested:")
        for i in range(100):
            lines.append(f"  nested_key_{i}: nested_value_{i}")
        
        # Add brace blocks
        for i in range(50):
            lines.append(f"script_{i}: {{ echo 'Script {i}'; exit 0 }}")
        
        text = "\n".join(lines) + "\n"
        
        # This should complete in reasonable time
        result = self.parser.parse(text)
        assert result is not None
    
    def test_deep_nesting_performance(self):
        """Test performance with deep nesting"""
        # Create deeply nested structure
        text = "root:\n"
        indent = "  "
        
        # 50 levels deep
        for i in range(50):
            text += f"{indent * (i + 1)}level_{i}:\n"
        
        text += f"{indent * 51}final_value: deep\n"
        
        result = self.parser.parse(text)
        assert result is not None
    
    def test_wide_structure_performance(self):
        """Test performance with wide structures"""
        # Create structure with many siblings
        text = "root:\n"
        
        # 500 sibling elements
        for i in range(500):
            text += f"  sibling_{i}: value_{i}\n"
        
        result = self.parser.parse(text)
        assert result is not None


class TestCompatibility:
    """Test compatibility with various input formats"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = YaalParser()
    
    def test_unix_line_endings(self):
        """Test Unix line endings (LF)"""
        text = "key1: value1\nkey2: value2\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_windows_line_endings(self):
        """Test Windows line endings (CRLF)"""
        text = "key1: value1\r\nkey2: value2\r\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_mixed_line_endings(self):
        """Test mixed line endings"""
        text = "key1: value1\nkey2: value2\r\nkey3: value3\n"
        result = self.parser.parse(text)
        assert result is not None
    
    def test_no_final_newline(self):
        """Test input without final newline"""
        text = "key1: value1\nkey2: value2"  # No final newline
        result = self.parser.parse(text)
        assert result is not None
    
    def test_multiple_final_newlines(self):
        """Test input with multiple final newlines"""
        text = "key1: value1\nkey2: value2\n\n\n"
        result = self.parser.parse(text)
        assert result is not None