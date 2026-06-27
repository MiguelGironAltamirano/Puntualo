# QA Test Execution & Validation Report ✅

**Date (UTC):** 2026-06-23 16:45:47
**Overall Status:** PASS

## Execution Metrics

| Metric | Value |
| --- | --- |
| **Total Tests** | 41 |
| **Passed** | 41 |
| **Failed** | 0 |
| **Errors** | 0 |
| **Skipped** | 0 |
| **Total Duration** | 3.91 seconds |

## Test Suite Breakdown

| Test Class | Test Case | Status | Duration (s) | Error Message |
| --- | --- | --- | --- | --- |
| tests.test_constraints | test_foreign_key_constraint | 🟢 Passed | 0.181 | - |
| tests.test_constraints | test_metric_check_constraints | 🟢 Passed | 0.230 | - |
| tests.test_constraints | test_modality_check_constraint | 🟢 Passed | 0.117 | - |
| tests.test_constraints | test_unique_evaluation_constraint | 🟢 Passed | 0.141 | - |
| tests.test_moderation.TestHeuristicFilter | test_allow_clean_comment | 🟢 Passed | 0.001 | - |
| tests.test_moderation.TestHeuristicFilter | test_banned_term_detection | 🟢 Passed | 0.002 | - |
| tests.test_moderation.TestHeuristicFilter | test_email_pattern_detection | 🟢 Passed | 0.001 | - |
| tests.test_moderation.TestHeuristicFilter | test_url_pattern_detection | 🟢 Passed | 0.001 | - |
| tests.test_moderation.TestHeuristicFilter | test_zero_width_chars_detection | 🟢 Passed | 0.001 | - |
| tests.test_moderation.TestHeuristicFilter | test_excessive_caps_scoring | 🟢 Passed | 0.002 | - |
| tests.test_moderation.TestHeuristicFilter | test_repeated_chars_scoring | 🟢 Passed | 0.002 | - |
| tests.test_moderation.TestHeuristicFilter | test_phone_pattern_detection | 🟢 Passed | 0.001 | - |
| tests.test_moderation.TestHeuristicFilter | test_l33t_speak_no_score_without_db | 🟢 Passed | 0.001 | - |
| tests.test_moderation.TestHeuristicFilter | test_gibberish_detection | 🟢 Passed | 0.001 | - |
| tests.test_moderation.TestHeuristicFilter | test_cumulative_violations | 🟢 Passed | 0.002 | - |
| tests.test_moderation.TestHeuristicFilter | test_normal_comment_with_numbers | 🟢 Passed | 0.002 | - |
| tests.test_moderation.TestHeuristicFilter | test_normal_comment_with_punctuation | 🟢 Passed | 0.001 | - |
| tests.test_moderation.TestHeuristicFilter | test_banned_term_detection_with_db | 🟢 Passed | 0.132 | - |
| tests.test_moderation.TestHeuristicFilter | test_banned_term_severity_filtering | 🟢 Passed | 0.084 | - |
| tests.test_moderation.TestHeuristicFilter | test_banned_term_cache_ttl | 🟢 Passed | 0.126 | - |
| tests.test_nlp_summary | test_select_reviews_sampling | 🟢 Passed | 0.191 | - |
| tests.test_nlp_summary | test_generate_and_store_guards_and_upsert | 🟢 Passed | 0.152 | - |
| tests.test_nlp_summary | test_run_summary_job_lifecycle | 🟢 Passed | 0.193 | - |
| tests.test_nlp_summary | test_find_stale_professor_ids | 🟢 Passed | 0.187 | - |
| tests.test_rate_limiter.TestReportRateLimiter | test_first_report_allowed | 🟢 Passed | 0.003 | - |
| tests.test_rate_limiter.TestReportRateLimiter | test_within_limit | 🟢 Passed | 0.003 | - |
| tests.test_rate_limiter.TestReportRateLimiter | test_rate_limit_exceeded | 🟢 Passed | 0.003 | - |
| tests.test_rate_limiter.TestReportRateLimiter | test_record_report | 🟢 Passed | 0.003 | - |
| tests.test_rate_limiter.TestReportRateLimiter | test_old_timestamps_filtered_out | 🟢 Passed | 0.003 | - |
| tests.test_rate_limiter.TestReportAbuseDetector | test_no_abuse_initially | 🟢 Passed | 0.003 | - |
| tests.test_rate_limiter.TestReportAbuseDetector | test_abuse_detection_at_threshold | 🟢 Passed | 0.004 | - |
| tests.test_rate_limiter.TestReportAbuseDetector | test_increment_abuse_count | 🟢 Passed | 0.003 | - |
| tests.test_rate_limiter.TestReportAbuseDetector | test_reset_abuse_count | 🟢 Passed | 0.003 | - |
| tests.test_report_service.TestReportService | test_create_report_success | 🟢 Passed | 0.155 | - |
| tests.test_report_service.TestReportService | test_create_report_rate_limited | 🟢 Passed | 0.163 | - |
| tests.test_report_service.TestReportService | test_create_report_abuse_detected | 🟢 Passed | 0.112 | - |
| tests.test_report_service.TestReportService | test_create_report_comment_not_found | 🟢 Passed | 0.119 | - |
| tests.test_report_service.TestReportService | test_create_report_escalates_on_high_score | 🟢 Passed | 0.166 | - |
| tests.test_report_service.TestReportService | test_weighted_score_calculation | 🟢 Passed | 0.160 | - |
| tests.test_transactions | test_atomic_rollback_on_failure | 🟢 Passed | 0.126 | - |
| tests.test_transactions | test_concurrent_transactions_acid | 🟢 Passed | 0.118 | - |

## Summary of Key Validations

- **Moderation Heuristic Filter:** Verified DB-backed detection of banned terms, matching against severity threshold ranks, and cache validation.
- **Database Schema Constraints:** Enforced foreign key checks in SQLite, validation status restrictions, modality rules, and evaluations unique indices.
- **NLP AI Summary Jobs:** Validated GeminiClient mocking, guard checks, background celery _run_summary task state updates, duplicate job controls, and stale summary detection query logic.
- **ACID Compliance:** Validated transactional rollbacks and nested transactions concurrency safety.
