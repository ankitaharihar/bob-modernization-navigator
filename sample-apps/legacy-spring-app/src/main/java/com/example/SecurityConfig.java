package com.example;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Legacy Security Configuration — DEPRECATED.
 *
 * Problems:
 * 1. Extends WebSecurityConfigurerAdapter (deprecated in Spring Security 5.7,
 * removed in 6.x).
 * 2. Disables CSRF protection entirely.
 * 3. Allows all requests without authentication.
 *
 * IBM Bob will modernize this to use SecurityFilterChain.
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
                        .anyRequest().permitAll() // ⚠️ UNSAFE: all endpoints are public
                );

        return http.build();
    }
}
