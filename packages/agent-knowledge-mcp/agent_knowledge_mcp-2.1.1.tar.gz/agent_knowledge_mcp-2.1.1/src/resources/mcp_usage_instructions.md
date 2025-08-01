# 🚀 AgentKnowledgeMCP - Complete Usage Guide

## 📋 **Table of Contents**

1. [Quick Start](#-quick-start---first-5-minutes)
2. [Core Features](#-core-features-overview)
3. [Workflow Scenarios](#-workflow-scenarios)
4. [Step-by-Step Tutorials](#-step-by-step-tutorials)
5. [Tool Reference](#-tool-reference)
6. [Troubleshooting](#-troubleshooting)
7. [Best Practices](#-best-practices)

---

## ⚡ **Before Getting Started - IMPORTANT!**

> 💡 **Pro Tip for Maximum Effectiveness**: 
> For the most effective experience with this MCP server, you should attach this instructions file to each prompt:
> 
> 📚 **https://github.com/itshare4u/AgentKnowledgeMCP/blob/main/.github/copilot-instructions.md**
> 
> This file contains guidelines that help AI assistants understand and use the MCP server optimally!

---

## 🚀 **Quick Start - First 5 Minutes**

### Step 1: Check System Status
```
"Show me server status and available indices"
```
**Expected Result**: 
- Server version and health
- Elasticsearch connection status
- List of available knowledge base indices
- System configuration overview

### Step 2: Create Your First Document  
```
"Create a document template for 'My First Knowledge Entry'"
```
**Expected Result**: 
- Document template with AI-generated metadata
- Proper structure with title, summary, content fields
- Relevant tags automatically assigned

### Step 3: Index Content
```
"Index this content into the knowledge base: [paste your content here]"
```
**Expected Result**: 
- Content stored with full-text search capability
- AI-enhanced metadata generated
- Document assigned to appropriate index

### Step 4: Search Your Content
```
"Search for [keywords related to your content]"
```
**Expected Result**: 
- Relevant documents ranked by relevance
- Context highlighting and snippets
- Related document suggestions

### Step 5: Batch Operations
```
"Batch index all markdown files from [directory path]"
```
**Expected Result**: 
- Multiple files processed automatically
- Progress tracking and status updates
- Summary of indexed content

---

## 🎯 **Core Features Overview**

### 🔍 **Knowledge Management**
- **Document Creation**: Templates with AI-enhanced metadata
- **Full-Text Search**: Advanced Elasticsearch-powered search
- **Batch Indexing**: Process multiple files at once
- **Schema Validation**: Ensure document structure consistency
- **Index Management**: Multiple specialized knowledge bases

### 🛠️ **Administrative Tools**
- **Configuration Management**: Update server settings on-the-fly
- **Index Operations**: Create, delete, manage indices
- **Server Control**: Restart, status monitoring
- **User Interaction**: Ask for guidance when uncertain

### 🔐 **Security & Confirmation**
- **Confirmation Middleware**: Safety checks for destructive operations
- **User Approval**: Human-in-the-loop for critical decisions
- **Secure Paths**: Validated file system access

### 🤖 **AI Enhancement**
- **Smart Metadata**: AI-generated tags and key points
- **Content Analysis**: Automatic categorization
- **Search Optimization**: Intelligent query processing

---

## 🎬 **Workflow Scenarios**

### 📊 **Scenario 1: Project Documentation Management**

**Goal**: Organize and search project documentation

**Step-by-Step Process**:

1. **Setup Project Index**
   ```
   "Create a new index called 'my-project-docs' for project documentation"
   ```

2. **Batch Import Documentation**
   ```
   "Batch index all markdown files from ./docs/ directory into my-project-docs index"
   ```

3. **Search Documentation**
   ```
   "Search my-project-docs for 'API authentication setup'"
   ```

4. **Add New Documentation**
   ```
   "Create a document about new feature implementation and index it"
   ```

**Expected Outcomes**:
- Centralized searchable documentation
- Fast retrieval of specific information
- Automatic categorization and tagging
- Version tracking and updates

---

### 🧠 **Scenario 2: Knowledge Base Building**

**Goal**: Build a comprehensive knowledge base from various sources

**Step-by-Step Process**:

1. **Discover Available Indices**
   ```
   "List all available indices and their purposes"
   ```

2. **Create Specialized Knowledge Areas**
   ```
   "Create index 'technical-solutions' for troubleshooting guides"
   "Create index 'best-practices' for methodology documentation"
   ```

3. **Import Existing Knowledge**
   ```
   "Batch index from ./technical-docs/ into technical-solutions"
   "Batch index from ./methodologies/ into best-practices"
   ```

4. **Cross-Reference Search**
   ```
   "Search across all indices for 'performance optimization'"
   ```

**Expected Outcomes**:
- Organized knowledge by topic areas
- Cross-reference capabilities
- Searchable historical decisions
- Team knowledge sharing

---

### 🔧 **Scenario 3: Troubleshooting & Support**

**Goal**: Create searchable troubleshooting database

**Step-by-Step Process**:

1. **Create Support Index**
   ```
   "Create index 'support-kb' for troubleshooting documentation"
   ```

2. **Document Common Issues**
   ```
   "Create document: 'Connection Timeout Error - Elasticsearch' with solution steps"
   ```

3. **Add Resolution Details**
   ```
   "Index detailed troubleshooting guide for database connection issues"
   ```

4. **Search Solutions**
   ```
   "Search support-kb for 'timeout connection elasticsearch'"
   ```

**Expected Outcomes**:
- Quick problem resolution
- Reduced support ticket volume
- Knowledge accumulation over time
- Consistent solution quality

---

### 📈 **Scenario 4: Research & Analysis**

**Goal**: Aggregate and analyze research materials

**Step-by-Step Process**:

1. **Setup Research Repository**
   ```
   "Create index 'research-materials' for research documents and findings"
   ```

2. **Import Research Content**
   ```
   "Batch index PDF content extracts from ./research-papers/ directory"
   ```

3. **Create Research Summaries**
   ```
   "Create summary document of key findings from recent AI research"
   ```

4. **Cross-Reference Analysis**
   ```
   "Search for connections between 'machine learning' and 'performance optimization'"
   ```

**Expected Outcomes**:
- Centralized research repository
- Pattern recognition across sources
- Quick reference and citation
- Research insight aggregation

---

## 📚 **Step-by-Step Tutorials**

### 🎯 **Tutorial 1: Setting Up Your First Knowledge Base**

**Duration**: 10 minutes  
**Difficulty**: Beginner

**Prerequisites**: 
- MCP server running
- Basic understanding of your content structure

**Steps**:

1. **Check System Health**
   ```
   Ask: "What's the current server status and what indices are available?"
   ```
   
2. **Plan Your Index Structure**
   ```
   Ask: "Help me plan an index structure for a software development team's knowledge base"
   ```

3. **Create Your First Index**
   ```
   Ask: "Create an index called 'dev-kb' for development knowledge with proper metadata"
   ```

4. **Add Initial Content**
   ```
   Ask: "Create a document template for 'Git Workflow Guidelines' in the dev-kb index"
   ```

5. **Verify Setup**
   ```
   Ask: "Search dev-kb to confirm the document was indexed correctly"
   ```

**Success Criteria**:
- Index created successfully
- Document indexed and searchable
- Metadata properly generated
- Search returns expected results

---

### 🔍 **Tutorial 2: Advanced Search Techniques**

**Duration**: 15 minutes  
**Difficulty**: Intermediate

**Learning Objectives**:
- Master search syntax and operators
- Use filters and date ranges
- Understand relevance scoring
- Implement search workflows

**Steps**:

1. **Basic Search**
   ```
   Ask: "Search for 'API documentation' across all indices"
   ```

2. **Filtered Search**
   ```
   Ask: "Search for documents with tag 'security' from the last 30 days"
   ```

3. **Field-Specific Search**
   ```
   Ask: "Search for 'authentication' in document titles only"
   ```

4. **Complex Query**
   ```
   Ask: "Search for documents about 'database optimization' with high priority"
   ```

5. **Related Document Discovery**
   ```
   Ask: "Find documents related to [specific document ID]"
   ```

**Advanced Techniques**:
- Boolean operators (AND, OR, NOT)
- Wildcard and fuzzy matching
- Date range filtering
- Priority and tag-based filtering
- Cross-index searching

---

### 🔧 **Tutorial 3: Administrative Operations**

**Duration**: 20 minutes  
**Difficulty**: Advanced

**Learning Objectives**:
- Manage server configuration
- Perform maintenance operations
- Handle user interactions
- Monitor system health

**Steps**:

1. **Configuration Review**
   ```
   Ask: "Show me the current server configuration"
   ```

2. **Update Settings**
   ```
   Ask: "Update the AI enhancement settings to use claude-3-opus as primary model"
   ```

3. **Index Management**
   ```
   Ask: "Create metadata documentation for all indices"
   ```

4. **Server Restart** (with confirmation)
   ```
   Ask: "Restart the server to apply configuration changes"
   ```

5. **Health Verification**
   ```
   Ask: "Verify all services are running correctly after restart"
   ```

**Advanced Operations**:
- Configuration backup and restore
- Index optimization
- Performance monitoring
- Security audit
- User permission management

---

## 🛠️ **Tool Reference**

### 📝 **Document Management Tools**

#### `create_document_template`
**Purpose**: Create structured document templates  
**Parameters**:
- `title` (required): Document title
- `summary`: Brief description
- `content`: Document content
- `tags`: Classification tags
- `priority`: Importance level (low/medium/high)
- `use_ai_enhancement`: Enable AI metadata generation

**Example**:
```
"Create a document template for 'Database Backup Procedures' with high priority"
```

#### `index_document` 
**Purpose**: Store documents in knowledge base  
**Parameters**:
- `index` (required): Target index name
- `document` (required): Document data
- `doc_id`: Custom document ID
- `validate_schema`: Enable structure validation

**Example**:
```
"Index this troubleshooting guide into the support-kb index"
```

#### `batch_index_directory`
**Purpose**: Process multiple files at once  
**Parameters**:
- `index` (required): Target index
- `directory_path` (required): Source directory
- `file_pattern`: File matching pattern (e.g., "*.md")
- `recursive`: Include subdirectories
- `use_ai_enhancement`: Enable AI processing

**Example**:
```
"Batch index all markdown files from ./docs/ into project-docs index"
```

### 🔍 **Search Tools**

#### `search`
**Purpose**: Find documents using advanced queries  
**Parameters**:
- `index` (required): Search target index
- `query` (required): Search terms
- `size`: Number of results (default: 10)
- `fields`: Specific fields to search
- `date_from`/`date_to`: Date range filters
- `sort_by_time`: Time-based sorting

**Example**:
```
"Search agentknowledgemcp index for 'FastMCP tools' returning 5 results"
```

#### `get_document`
**Purpose**: Retrieve specific document by ID  
**Parameters**:
- `index` (required): Index name
- `doc_id` (required): Document identifier

**Example**:
```
"Get document with ID 'fastmcp-guide-123' from the documentation index"
```

### 🏗️ **Index Management Tools**

#### `list_indices`
**Purpose**: Show all available indices with metadata  
**Parameters**: None

**Example**:
```
"List all available indices and their documentation status"
```

#### `create_index`
**Purpose**: Create new knowledge base index  
**Parameters**:
- `index` (required): Index name
- `mapping` (required): Field structure definition
- `settings`: Index configuration

**Example**:
```
"Create a new index called 'product-specs' for product documentation"
```

#### `delete_index`
**Purpose**: Remove index and all documents  
**Parameters**:
- `index` (required): Index to delete

**Example**:
```
"Delete the temporary-test index permanently"
```

### ⚙️ **Administrative Tools**

#### `server_status`
**Purpose**: Check system health and version  
**Parameters**:
- `check_updates`: Look for available updates

**Example**:
```
"Show comprehensive server status including update availability"
```

#### `get_config`
**Purpose**: Display current configuration  
**Parameters**: None

**Example**:
```
"Show me the current server configuration settings"
```

#### `update_config`
**Purpose**: Modify server settings  
**Parameters**:
- `config_section`: Configuration section
- `config_key`: Specific setting
- `config_value`: New value

**Example**:
```
"Update the AI enhancement model preference to claude-3-opus"
```

#### `ask_user_advice`
**Purpose**: Request human guidance for uncertain situations  
**Parameters**:
- `problem_description`: Description of the uncertainty
- `context_information`: Background details
- `specific_question`: Targeted question
- `options_considered`: Alternative approaches
- `urgency_level`: Priority (low/normal/high/urgent)

**Example**:
```
"I'm uncertain about whether to merge these conflicting configurations or replace them entirely. Let me ask for guidance."
```

---

## 🚨 **Troubleshooting**

### ❌ **Common Issues & Solutions**

#### **Problem**: "Index not found" error
**Symptoms**: Search or document operations fail  
**Solution**:
1. List available indices: `"Show me all available indices"`
2. Check index name spelling
3. Create index if needed: `"Create index [name] for [purpose]"`

#### **Problem**: Document indexing fails
**Symptoms**: Content not searchable after indexing  
**Solution**:
1. Check document structure: `"Validate this document structure"`
2. Verify index exists: `"List indices"`
3. Review error messages for specific issues
4. Try with AI enhancement disabled

#### **Problem**: Search returns no results
**Symptoms**: Expected documents not found  
**Solution**:
1. Verify search index: `"List documents in [index] to confirm content"`
2. Try broader search terms
3. Check for typos in query
4. Use cross-index search: `"Search across all indices"`

#### **Problem**: Configuration changes not applied
**Symptoms**: Settings updates don't take effect  
**Solution**:
1. Verify configuration: `"Show current config"`
2. Restart server: `"Restart server to apply changes"`
3. Check for syntax errors in config values

#### **Problem**: Elasticsearch connection issues
**Symptoms**: "Connection failed" or timeout errors  
**Solution**:
1. Check service status: `"Show Elasticsearch status"`
2. Restart Elasticsearch: `"Setup Elasticsearch with force recreate"`
3. Verify network connectivity
4. Check Docker containers if using containerized setup

### 🔧 **Performance Optimization**

#### **Slow Search Performance**
**Solutions**:
- Use specific indices instead of searching all
- Limit result size with `size` parameter
- Use field-specific searches when possible
- Consider index optimization for large datasets

#### **Large File Processing**
**Solutions**:
- Use batch indexing for multiple files
- Process files in smaller groups
- Enable AI enhancement selectively
- Monitor memory usage during operations

#### **Index Size Management**
**Solutions**:
- Regular cleanup of outdated documents
- Archive old content to separate indices
- Use retention policies for automatic cleanup
- Monitor index size with `list_indices`

---

## ✨ **Best Practices**

### 📋 **Content Organization**

#### **Index Strategy**
- **Use specific indices** for different content types
- **Logical grouping**: Group related documents together
- **Clear naming**: Use descriptive index names
- **Metadata consistency**: Maintain consistent tagging

#### **Document Structure**
- **Descriptive titles**: Clear, searchable titles
- **Comprehensive summaries**: Include key points
- **Relevant tags**: Use consistent, meaningful tags
- **Priority levels**: Assign appropriate importance
- **Regular updates**: Keep content current

### 🔍 **Search Strategy**

#### **Effective Searching**
- **Start broad, narrow down**: Begin with general terms
- **Use multiple approaches**: Try different keywords
- **Leverage metadata**: Search by tags, dates, priority
- **Cross-reference**: Use related document suggestions

#### **Query Optimization**
- **Specific terms**: Use precise vocabulary
- **Boolean operators**: Combine terms effectively
- **Field targeting**: Search specific fields when known
- **Date filtering**: Use time ranges for recent content

### 🛡️ **Security & Maintenance**

#### **Regular Maintenance**
- **Backup configurations**: Save config before changes
- **Monitor health**: Regular status checks
- **Update content**: Keep information current
- **Clean up**: Remove outdated documents

#### **Security Practices**
- **Validate inputs**: Check file paths and content
- **Use confirmation**: Enable for destructive operations
- **Monitor access**: Track document modifications
- **Regular audits**: Review indices and content

### 🤝 **Collaboration**

#### **Team Usage**
- **Consistent tagging**: Establish tagging conventions
- **Documentation standards**: Maintain quality guidelines
- **Knowledge sharing**: Regular content reviews
- **Training**: Ensure team understands best practices

#### **User Interaction**
- **Ask for guidance**: Use `ask_user_advice` when uncertain
- **Provide context**: Give clear problem descriptions
- **Follow workflows**: Use established procedures
- **Feedback loops**: Incorporate user suggestions

---

## 🎯 **Advanced Use Cases**

### 🏢 **Enterprise Knowledge Management**

**Scenario**: Large organization with multiple teams  
**Implementation**:
- Separate indices per department
- Cross-departmental search capabilities
- Role-based content organization
- Automated content lifecycle management

**Key Features**:
- Centralized search across all departments
- Department-specific knowledge bases
- Automated content categorization
- Integration with existing tools

### 🔬 **Research Data Management**

**Scenario**: Research institution with academic papers  
**Implementation**:
- Research paper metadata extraction
- Citation and reference tracking
- Keyword and topic clustering
- Collaborative annotation system

**Key Features**:
- Full-text search across research papers
- Automatic metadata extraction
- Research trend analysis
- Citation network visualization

### 🛠️ **DevOps Knowledge Base**

**Scenario**: Development team with operational knowledge  
**Implementation**:
- Incident response procedures
- Troubleshooting guides
- Configuration documentation
- Runbook automation

**Key Features**:
- Real-time search during incidents
- Automated runbook execution
- Historical incident analysis
- Knowledge gap identification

---

## 📞 **Getting Help**

### 🆘 **When You Need Assistance**

#### **Use the ask_user_advice Tool**
```
"I'm encountering [describe problem]. I've tried [list attempts]. Should I [option 1] or [option 2]?"
```

#### **System Diagnostics**
```
"Run comprehensive system diagnostics and show me any issues"
```

#### **Documentation Search**
```
"Search for documentation about [specific feature or problem]"
```

### 📚 **Additional Resources**

- **GitHub Repository**: https://github.com/itshare4u/AgentKnowledgeMCP
- **Issue Tracking**: GitHub Issues for bug reports
- **Feature Requests**: GitHub Discussions
- **Community Support**: Discussion forums

### 🔄 **Updates and Maintenance**

#### **Staying Current**
```
"Check for server updates and show me what's new"
```

#### **Configuration Backup**
```
"Show me how to backup my current configuration"
```

#### **Performance Monitoring**
```
"Show me system performance metrics and recommendations"
```

---

## 🎉 **Conclusion**

This MCP server provides a powerful, flexible knowledge management system with advanced search capabilities, AI enhancement, and robust administrative tools. By following these guidelines and using the provided workflows, you can build and maintain an effective knowledge base that grows with your needs.

**Remember**: The key to success is consistent organization, regular maintenance, and leveraging the AI enhancement features to automatically improve your content quality and searchability.

Start with the Quick Start guide, progress through the tutorials, and gradually implement more advanced features as your knowledge base grows!

---

*Generated for AgentKnowledgeMCP v1.0.28+ - Last Updated: 2025-07-24*
