from src.models import Finding


DEFAULT_BEFORE = "// legacy pattern detected"
DEFAULT_AFTER = "// modernized, safer pattern"


def suggest_before_after(finding: Finding) -> tuple[str, str]:
    title = finding.title.lower()
    desc = (finding.description or "").lower()

    if "sql injection" in title or "sql injection" in desc:
        return (
            "String sql = \"SELECT * FROM users WHERE username = '" + username + "'\";\n"
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
