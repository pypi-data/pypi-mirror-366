# Basic Usage Examples

This guide demonstrates common TaskPriority MCP Server usage patterns with Claude Desktop.

## Getting Started

Once you've configured the TaskPriority server in Claude Desktop, you can start managing tasks using natural language.

## Creating Tasks

### Simple Task Creation

```
User: Create a task to fix the login page bug

Claude: I'll create that task for you.

[Uses create_task tool]

✓ Task created successfully!

Task Details:
- ID: 123e4567-e89b-12d3-a456-426614174000
- Description: Fix the login page bug
- Status: pending
- AI Analysis:
  - Priority: 7/10 (High)
  - Category: bug
  - Complexity: medium
  - Estimated Time: 4 hours
  - Similar tasks found: 2
```

### Detailed Task Creation

```
User: Create a feature task to implement OAuth2 authentication with Google. 
This is requested by the product team for the Q1 release.

Claude: I'll create that feature task with the additional context.

[Uses create_task tool with customer_info]

✓ Task created successfully!

Task Details:
- ID: 456e7890-e89b-12d3-a456-426614174001
- Description: Implement OAuth2 authentication with Google
- Status: pending
- Source: internal
- Customer Info: Requested by the product team for the Q1 release
- AI Analysis:
  - Priority: 9/10 (Critical)
  - Category: feature
  - Complexity: hard
  - Estimated Time: 16 hours
  - Implementation Spec:
    1. Set up Google OAuth2 credentials
    2. Implement OAuth2 flow
    3. Create callback endpoints
    4. Handle token management
    5. Update user authentication logic
```

## Listing and Filtering Tasks

### List All Tasks

```
User: Show me all my tasks

Claude: I'll retrieve all your tasks.

[Uses list_tasks tool]

Found 15 tasks total:

Pending (8):
1. Fix login page bug - Priority: 7/10
2. Implement OAuth2 authentication - Priority: 9/10
3. Optimize database queries - Priority: 6/10
...

In Progress (4):
1. Update user dashboard - Priority: 5/10
2. Add error logging - Priority: 8/10
...

Completed (3):
1. Set up CI/CD pipeline - Completed yesterday
2. Fix memory leak - Completed 2 days ago
...
```

### Filter by Status

```
User: Show me only the tasks in progress

Claude: I'll show you the tasks currently in progress.

[Uses list_tasks tool with status filter]

Found 4 tasks in progress:

1. Update user dashboard
   - Priority: 5/10
   - Category: improvement
   - Started: 2 days ago

2. Add error logging
   - Priority: 8/10
   - Category: feature
   - Started: Today
...
```

### Filter by Category

```
User: List all the bugs

Claude: I'll show you all bug tasks.

[Uses list_tasks tool with category filter]

Found 6 bug tasks:

High Priority Bugs:
1. Fix login page bug - Priority: 7/10 (pending)
2. Memory leak in image processor - Priority: 8/10 (pending)

Medium Priority Bugs:
1. Incorrect date formatting - Priority: 5/10 (in_progress)
...
```

## Managing Tasks

### Update Task Status

```
User: Mark the login page bug as in progress

Claude: I'll update the login page bug task to in progress.

[Uses update_task tool]

✓ Task updated successfully!

Task "Fix login page bug" is now in progress.
```

### Update Task Description

```
User: Update the OAuth task description to include "and Facebook login"

Claude: I'll update the OAuth task description.

[Uses update_task tool]

✓ Task updated successfully!

Updated description: "Implement OAuth2 authentication with Google and Facebook login"
```

### Complete a Task

```
User: Mark task 123e4567 as completed

Claude: I'll mark that task as completed.

[Uses update_task tool]

✓ Task completed!

Task "Fix login page bug" has been marked as completed.
Total time spent: 3.5 hours (vs 4 hour estimate)
```

## Getting Task Details

### Get Specific Task

```
User: Show me details for task 456e7890

Claude: I'll retrieve the details for that task.

[Uses get_task_details tool]

Task Details:
- ID: 456e7890-e89b-12d3-a456-426614174001
- Description: Implement OAuth2 authentication with Google
- Status: pending
- Created: 2 hours ago
- Updated: 1 hour ago
- Priority: 9/10 (Critical)
- Category: feature
- Complexity: hard
- Estimated Time: 16 hours
- Similar Tasks:
  - "Add social login" (completed 2 months ago)
  - "Implement SAML authentication" (completed last month)
```

### Get AI Analysis

```
User: What's the AI analysis for the database optimization task?

Claude: I'll get the AI analysis for the database optimization task.

[Uses get_ai_analysis tool]

AI Analysis for "Optimize database queries":
- Priority: 6/10 (Medium-High)
- Category: improvement
- Complexity: medium
- Estimated Time: 8 hours
- Confidence Score: 82%
- Implementation Recommendations:
  1. Analyze slow query log
  2. Add missing indexes
  3. Optimize N+1 queries
  4. Implement query caching
  5. Consider database connection pooling
- Similar Tasks: Found 3 related optimization tasks
```

## Deleting Tasks

### Delete a Task

```
User: Delete the old test task 789e0123

Claude: I'll delete that task for you. This action cannot be undone.

[Uses delete_task tool]

✓ Task deleted successfully!

Task 789e0123 has been permanently removed.
```

## Advanced Workflows

### Find Similar Tasks

```
User: Are there any tasks similar to implementing payment processing?

Claude: I'll search for tasks similar to payment processing.

[Creates a temporary task, gets analysis, then checks similar tasks]

Found 3 similar tasks:

1. "Integrate Stripe payment gateway" - completed last month
   - Took 20 hours (estimated 24)
   - Implementation notes available

2. "Add PayPal support" - in progress
   - 60% complete
   - Assigned to backend team

3. "Implement subscription billing" - pending
   - Priority: 8/10
   - Scheduled for next sprint
```

### Bulk Operations

```
User: Show me all high-priority bugs that are still pending

Claude: I'll find all high-priority pending bugs.

[Uses list_tasks with filters and analyzes results]

Found 3 high-priority pending bugs:

1. "Memory leak in image processor"
   - Priority: 8/10
   - Affects: 15% of users
   - Estimated fix: 6 hours

2. "API timeout on large requests"
   - Priority: 7/10
   - Affects: API consumers
   - Estimated fix: 4 hours

3. "Data corruption on concurrent writes"
   - Priority: 9/10
   - Critical issue
   - Estimated fix: 8 hours

Total estimated time: 18 hours
Recommendation: Prioritize the data corruption issue first.
```

## Tips and Best Practices

1. **Be Specific**: More detailed descriptions lead to better AI analysis
2. **Use Natural Language**: Claude understands context and intent
3. **Check Similar Tasks**: Avoid duplicates by reviewing similar tasks
4. **Regular Updates**: Keep task statuses current for accurate tracking
5. **Leverage AI Insights**: Use priority scores and time estimates for planning

---

Next: [Advanced Examples](advanced-usage.md) | [API Reference](../docs/api-reference.md)