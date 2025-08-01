#include "test_helpers.hpp"

TEST(Integration, pipeline_configuration) {
    std::string text = "#!pipeline\n"
                      "# CI/CD Pipeline Configuration\n"
                      "\n"
                      "checkout:\n"
                      "  repository: github.com/user/repo\n"
                      "  branch: main\n"
                      "\n"
                      "build:\n"
                      "  docker build -t myapp .\n"
                      "  run tests\n"
                      "\n"
                      "deploy:\n"
                      "  environment: production\n"
                      "  script: { kubectl apply -f k8s/ }\n"
                      "  notifications:\n"
                      "    slack: \"#deployments\"\n"
                      "    email: team@company.com\n";
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
    
    std::string output = TestHelpers::parse_with_output(text);
    ASSERT_TRUE(TestHelpers::output_contains(output, "Shebang: #!pipeline"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: checkout"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: build"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: deploy"));
}

TEST(Integration, configuration_file) {
    std::string text = "# Application Configuration\n"
                      "database:\n"
                      "  host: localhost\n"
                      "  port: 5432\n"
                      "  name: myapp_db\n"
                      "  credentials:\n"
                      "    username: admin\n"
                      "    password: secret123\n"
                      "\n"
                      "api:\n"
                      "  host: 0.0.0.0\n"
                      "  port: 8080\n"
                      "  endpoints:\n"
                      "    health: /health\n"
                      "    metrics: /metrics\n"
                      "\n"
                      "logging:\n"
                      "  level: info\n"
                      "  file: /var/log/myapp.log\n"
                      "  format: json\n"
                      "\n"
                      "features:\n"
                      "  authentication: true\n"
                      "  rate_limiting: true\n"
                      "  caching: false\n";
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
    
    std::string output = TestHelpers::parse_with_output(text);
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: database"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: api"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: logging"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: features"));
}

TEST(Integration, infrastructure_as_code) {
    std::string text = "#!infrastructure\n"
                      "# Infrastructure Definition\n"
                      "\n"
                      "vpc:\n"
                      "  cidr: 10.0.0.0/16\n"
                      "  subnets:\n"
                      "    public:\n"
                      "      cidr: 10.0.1.0/24\n"
                      "      availability_zone: us-west-2a\n"
                      "    private:\n"
                      "      cidr: 10.0.2.0/24\n"
                      "      availability_zone: us-west-2b\n"
                      "\n"
                      "security_groups:\n"
                      "  web:\n"
                      "    ingress:\n"
                      "      - port: 80\n"
                      "        protocol: tcp\n"
                      "        source: 0.0.0.0/0\n"
                      "      - port: 443\n"
                      "        protocol: tcp\n"
                      "        source: 0.0.0.0/0\n"
                      "\n"
                      "instances:\n"
                      "  web_server:\n"
                      "    type: t3.micro\n"
                      "    ami: ami-12345678\n"
                      "    security_group: web\n"
                      "    user_data: {\n"
                      "      #!/bin/bash\n"
                      "      yum update -y\n"
                      "      yum install -y httpd\n"
                      "      systemctl start httpd\n"
                      "    }\n";
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(Integration, multi_language_script) {
    std::string text = "#!hibrid-code\n"
                      "# Multi-language execution example\n"
                      "\n"
                      "python: {\n"
                      "  for i in range(10):\n"
                      "      if i % 2 == 0:\n"
                      "          print(f\"Even: {i}\")\n"
                      "}\n"
                      "\n"
                      "javascript: {\n"
                      "  const numbers = [1, 2, 3, 4, 5];\n"
                      "  numbers.forEach(n => {\n"
                      "      console.log(`Number: ${n}`);\n"
                      "  });\n"
                      "}\n"
                      "\n"
                      "bash: {\n"
                      "  echo \"Starting deployment...\"\n"
                      "  for service in web api db; do\n"
                      "      echo \"Deploying $service\"\n"
                      "      kubectl apply -f \"$service.yaml\"\n"
                      "  done\n"
                      "  echo \"Deployment complete\"\n"
                      "}\n";
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
    
    std::string output = TestHelpers::parse_with_output(text);
    ASSERT_TRUE(TestHelpers::output_contains(output, "Shebang: #!hibrid-code"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: python"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: javascript"));
    ASSERT_TRUE(TestHelpers::output_contains(output, "Key: bash"));
}

TEST(Integration, deeply_nested_config) {
    std::string text = "application:\n"
                      "  name: MyApp\n"
                      "  version: 1.0.0\n"
                      "\n"
                      "  environments:\n"
                      "    development:\n"
                      "      database:\n"
                      "        host: localhost\n"
                      "        port: 5432\n"
                      "        settings:\n"
                      "          pool_size: 5\n"
                      "          timeout: 30\n"
                      "          ssl:\n"
                      "            enabled: false\n"
                      "            cert_path: /path/to/cert\n"
                      "\n"
                      "    production:\n"
                      "      database:\n"
                      "        host: prod-db.example.com\n"
                      "        port: 5432\n"
                      "        settings:\n"
                      "          pool_size: 20\n"
                      "          timeout: 60\n"
                      "          ssl:\n"
                      "            enabled: true\n"
                      "            cert_path: /etc/ssl/certs/db.pem\n"
                      "            key_path: /etc/ssl/private/db.key\n";
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(Integration, mixed_content_types) {
    std::string text = "#!mixed-content\n"
                      "# This example mixes all YAAL features\n"
                      "\n"
                      "# Simple statements\n"
                      "production\n"
                      "debug mode enabled\n"
                      "\n"
                      "# Key-value pairs\n"
                      "name: MyApplication\n"
                      "version: 2.1.0\n"
                      "\n"
                      "# Keys with spaces and colons\n"
                      "api endpoint: https://api.example.com:8080/v1\n"
                      "database url: postgresql://user:pass@host:5432/db\n"
                      "log timestamp: 2023-12-01T10:30:45Z\n"
                      "\n"
                      "# Quoted strings\n"
                      "description: \"A comprehensive application\"\n"
                      "command: \"echo 'Hello World'\"\n"
                      "\n"
                      "# Brace blocks\n"
                      "startup_script: {\n"
                      "  #!/bin/bash\n"
                      "  echo \"Starting application...\"\n"
                      "  export NODE_ENV=production\n"
                      "  npm start\n"
                      "}\n"
                      "\n"
                      "# Nested structures\n"
                      "configuration:\n"
                      "  # Simple statements in nested context\n"
                      "  enable_logging\n"
                      "  enable_metrics\n"
                      "\n"
                      "  # Key-value in nested context\n"
                      "  port: 8080\n"
                      "  host: 0.0.0.0\n"
                      "\n"
                      "  # Further nesting\n"
                      "  database:\n"
                      "    primary:\n"
                      "      host: db1.example.com\n"
                      "      port: 5432\n"
                      "    replica:\n"
                      "      host: db2.example.com\n"
                      "      port: 5432\n";
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(Integration, large_file_parsing) {
    // Generate a large YAAL structure
    std::string text = "#!large-test\n";
    
    // Add many key-value pairs
    for (int i = 0; i < 1000; i++) {
        text += "key_" + std::to_string(i) + ": value_" + std::to_string(i) + "\n";
    }
    
    // Add nested structure
    text += "nested:\n";
    for (int i = 0; i < 100; i++) {
        text += "  nested_key_" + std::to_string(i) + ": nested_value_" + std::to_string(i) + "\n";
    }
    
    // Add brace blocks
    for (int i = 0; i < 50; i++) {
        text += "script_" + std::to_string(i) + ": { echo 'Script " + std::to_string(i) + "'; exit 0 }\n";
    }
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(Integration, deep_nesting_performance) {
    // Create deeply nested structure
    std::string text = "root:\n";
    
    // 50 levels deep
    for (int i = 0; i < 50; i++) {
        text += std::string((i + 1) * 2, ' ') + "level_" + std::to_string(i) + ":\n";
    }
    
    text += std::string(51 * 2, ' ') + "final_value: deep\n";
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
}

TEST(Integration, wide_structure_performance) {
    // Create structure with many siblings
    std::string text = "root:\n";
    
    // 500 sibling elements
    for (int i = 0; i < 500; i++) {
        text += "  sibling_" + std::to_string(i) + ": value_" + std::to_string(i) + "\n";
    }
    
    ASSERT_TRUE(TestHelpers::parse_text(text));
}