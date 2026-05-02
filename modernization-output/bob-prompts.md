# IBM Bob IDE — Copy-Paste Prompts

## Prompt 1: Understand the Repository
```
You are my enterprise modernization architect.

Analyze this workspace and explain:
1. What this project does and its purpose.
2. The main modules, packages, and key files.
3. The highest modernization risks based on modernization-output-before/modernization-report.md.
4. Which findings are the safest AND most impactful to fix first.
5. A recommended implementation order for a hackathon demo.

Keep suggestions scoped to changes safe for a demo.
```

## Prompt 2: Implement the First Fix (SQL Injection)
```
Using modernization-output-before/modernization-report.md, implement the safest high-impact fix.

Focus on: fixing unsafe SQL string concatenation in the legacy Spring Boot app.

Requirements:
1. Keep the change small and reviewable (one class or method).
2. Preserve existing behavior exactly.
3. Use PreparedStatement or Spring Data JPA repository pattern.
4. Add or update a focused unit test if practical.
5. Explain every file you change and why.
6. Give me the exact command to validate the fix.

Do NOT migrate the full Spring Boot version yet.
```

## Prompt 3: Add Focused Tests
```
Add focused tests for the component you just changed.

Requirements:
1. Cover the normal successful case.
2. Cover an invalid or malicious input case (SQL injection attempt).
3. Keep tests minimal and runnable with the existing test framework.
4. Explain clearly how each test proves the modernization improvement.
```

## Prompt 4: Improve the Analyzer
```
Review this modernization-navigator project itself.

Add improvements to the analyzer:
1. Add one new Spring Boot modernization detection rule.
2. Add one new security detection rule.
3. Add or update tests for both new rules.
4. Keep changes small and explain implementation + validation steps.

Good rule ideas:
- Detect csrf().disable() in security config
- Detect @CrossOrigin("*")
- Detect javax.servlet imports
- Detect JUnit 4 imports (org.junit.Test)
- Detect old maven-compiler-plugin source/target values
- Detect missing GitHub Actions CI
```

## Prompt 5: Generate Final Docs
```
Generate a hackathon-ready README section for this project.

Include:
1. Problem statement
2. Solution overview
3. IBM Bob's role in the workflow
4. Step-by-step workflow
5. How to run the analyzer
6. Before/after modernization results
7. Demo script for judges
8. Judging artifacts location
9. Limitations and next steps

Mention that Bob IDE was used to validate findings, implement fixes,
generate tests, and create documentation.
```

## Prompt 6: Judge Summary
```
Generate a concise judge summary from the modernization reports.

Make it easy for judges to understand:
1. What the agent does
2. Why it matters for enterprise software teams
3. How IBM Bob is central to the workflow
4. What changed after Bob-assisted implementation
5. Measurable improvement shown by before/after scans
```
