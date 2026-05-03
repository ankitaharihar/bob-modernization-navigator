from src.models import Finding


DEFAULT_BEFORE = "// legacy pattern detected"
DEFAULT_AFTER = "// modernized, safer pattern"


def get_fix_suggestion(issue_title):
    mapping = {
        "Possible hardcoded secret": {
            "why": "Secrets code me hardcoded hone se security risk hota hai (credentials leak ho sakte hain).",
            "fix": "Secrets ko environment variables ya config server me move karo.",
            "impact": "Sensitive data exposure risk significantly reduce hoga.",
        },
        "Possible SQL injection risk": {
            "why": "User input directly query me use ho raha hai, attacker SQL inject kar sakta hai.",
            "fix": "Prepared statements / parameterized queries use karo.",
            "impact": "Database attack risk eliminate hoga.",
        },
        "Deprecated Spring Security": {
            "why": "Old API future versions me support nahi hogi.",
            "fix": "SecurityFilterChain use karke migrate karo.",
            "impact": "Future compatibility + better security milegi.",
        },
        "WebSecurityConfigurerAdapter": {
            "why": "Old API future versions me support nahi hogi.",
            "fix": "SecurityFilterChain use karke migrate karo.",
            "impact": "Future compatibility + better security milegi.",
        },
    }

    for key in mapping:
        if key.lower() in issue_title.lower():
            return mapping[key]

    return {
        "why": "General issue detected.",
        "fix": "Code update required.",
        "impact": "Improves maintainability.",
    }


def suggest_before_after(finding: Finding) -> tuple[str, str]:
    title = finding.title.lower()
    desc = (finding.description or "").lower()

    if "sql injection" in title or "sql injection" in desc:
        return (
            "String sql = \"SELECT * FROM users WHERE username = '" + "${username}" + "'\";\n"
            "Query query = entityManager.createNativeQuery(sql, User.class);",
            "String sql = \"SELECT * FROM users WHERE username = :username\";\n"
            "Query query = entityManager.createNativeQuery(sql, User.class);\n"
            "query.setParameter(\"username\", username);",
        )

    if "hardcoded secret" in title:
        return (
            "spring.datasource.password=super-secret\n"
            "jwt.secret=hardcoded-secret",
            "spring.datasource.password=${DB_PASSWORD}\n"
            "jwt.secret=${JWT_SECRET}",
        )

    if "websecurityconfigureradapter" in title or "deprecated spring security" in title:
        return (
            "public class SecurityConfig extends WebSecurityConfigurerAdapter {\n"
            "  protected void configure(HttpSecurity http) throws Exception {\n"
            "    http.csrf().disable();\n"
            "  }\n"
            "}",
            "@Bean\n"
            "SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {\n"
            "  http.csrf(csrf -> csrf.disable());\n"
            "  return http.build();\n"
            "}",
        )

    if "cors" in title:
        return (
            "@CrossOrigin(\"*\")",
            "@CrossOrigin(origins = {\"https://app.company.com\"})",
        )

    return DEFAULT_BEFORE, DEFAULT_AFTER
