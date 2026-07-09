# Example evaluation dataset
EVAL_QUERIES = [
    # {
    #     "query": "What is the current status of the Q1 implementation?",
    #     "expected_answer_snippet": "on track",
    #     "relevant_email_ids": ["email_1"],
    #     "difficulty": "easy"
    # },
    {
        "query": "Which completed items were listed in the project status update?",
        "expected_answer_snippet": "Backend API development (95% complete)",
        "relevant_email_ids": ["f1caa00df8afc309"],
        "difficulty": "medium"
    },
    # {
    #     "query": "What are the next steps after the current implementation update?",
    #     "expected_answer_snippet": "Frontend development and integration testing",
    #     "relevant_email_ids": ["email_1"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "Who sent the project implementation status update?",
    #     "expected_answer_snippet": "Sarah Johnson",
    #     "relevant_email_ids": ["email_1"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "By when should assigned tasks be completed?",
    #     "expected_answer_snippet": "by EOW",
    #     "relevant_email_ids": ["email_1"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "What daily activity must be updated according to the email?",
    #     "expected_answer_snippet": "Update the project tracking system daily",
    #     "relevant_email_ids": ["email_1"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "What time are the standup meetings scheduled?",
    #     "expected_answer_snippet": "10 AM",
    #     "relevant_email_ids": ["email_1"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "When is the project scheduled to launch?",
    #     "expected_answer_snippet": "by end of Q1",
    #     "relevant_email_ids": ["email_1"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "What was discussed about implementation?",
    #     "expected_answer_snippet": "implementation",
    #     "relevant_email_ids": ["email_1"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "When is the next planning meeting?",
    #     "expected_answer_snippet": "next planning meeting",
    #     "relevant_email_ids": ["email_3"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "Who is responsible for QA on release Y?",
    #     "expected_answer_snippet": "QA on release Y",
    #     "relevant_email_ids": ["email_4", "email_5"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "What are the action items from the last sprint review?",
    #     "expected_answer_snippet": "action items",
    #     "relevant_email_ids": ["email_2", "email_6"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "Has the client approved the budget?",
    #     "expected_answer_snippet": "approved the budget",
    #     "relevant_email_ids": ["email_7"],
    #     "difficulty": "hard"
    # },
    # {
    #     "query": "What is the deadline for the marketing deck?",
    #     "expected_answer_snippet": "deadline for the marketing deck",
    #     "relevant_email_ids": ["email_8"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "Which team member owns the deployment task?",
    #     "expected_answer_snippet": "deployment task",
    #     "relevant_email_ids": ["email_9"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "Are there any blockers for the data migration?",
    #     "expected_answer_snippet": "blockers for the data migration",
    #     "relevant_email_ids": ["email_10", "email_11"],
    #     "difficulty": "hard"
    # },
    # {
    #     "query": "What did Sarah say about the server upgrade?",
    #     "expected_answer_snippet": "server upgrade",
    #     "relevant_email_ids": ["email_12"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "What is the agreed follow-up date with vendor Z?",
    #     "expected_answer_snippet": "follow-up date",
    #     "relevant_email_ids": ["email_13"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "Which documents need legal review?",
    #     "expected_answer_snippet": "legal review",
    #     "relevant_email_ids": ["email_14"],
    #     "difficulty": "hard"
    # },
    # {
    #     "query": "What was the decision about remote work policy?",
    #     "expected_answer_snippet": "remote work policy",
    #     "relevant_email_ids": ["email_15"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "Who sent the volunteer confirmation email for GDG DevFest?",
    #     "expected_answer_snippet": "Shasanka Acharya",
    #     "relevant_email_ids": ["email_23"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "What does the email ask the recipient to do next?",
    #     "expected_answer_snippet": "confirm your participation by replying",
    #     "relevant_email_ids": ["email_23"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "What event is the volunteer opportunity for?",
    #     "expected_answer_snippet": "GDG DevFest",
    #     "relevant_email_ids": ["email_23"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "What will happen after the recipient confirms participation?",
    #     "expected_answer_snippet": "we'll reach out to you shortly with further details and next steps",
    #     "relevant_email_ids": ["email_23"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "What tone does the email use to welcome the volunteer?",
    #     "expected_answer_snippet": "excited to have you on board",
    #     "relevant_email_ids": ["email_23"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "Who is the sender of the security audit email?",
    #     "expected_answer_snippet": "Alex Chen",
    #     "relevant_email_ids": ["email_24"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "Which vulnerability is labeled critical and must be fixed immediately?",
    #     "expected_answer_snippet": "SQL injection vulnerability in user auth module",
    #     "relevant_email_ids": ["email_24"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "What specific fix is recommended for the missing CORS validation?",
    #     "expected_answer_snippet": "Restrict origins to whitelisted domains",
    #     "relevant_email_ids": ["email_24"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "Which weak password hashing algorithm is currently being used?",
    #     "expected_answer_snippet": "MD5 instead of bcrypt",
    #     "relevant_email_ids": ["email_24"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "Where should exposed API keys be moved according to the audit?",
    #     "expected_answer_snippet": "Move to Secrets Manager",
    #     "relevant_email_ids": ["email_24"],
    #     "difficulty": "medium"
    # },
    # {
    #     "query": "When is the security standup scheduled?",
    #     "expected_answer_snippet": "Wednesday at 2 PM",
    #     "relevant_email_ids": ["email_24"],
    #     "difficulty": "easy"
    # },
    # {
    #     "query": "What is the deadline expectation for fixing critical issues?",
    #     "expected_answer_snippet": "before the next production release",
    #     "relevant_email_ids": ["email_24"],
    #     "difficulty": "medium"
    # },
]
