package com.example.repository;

import com.example.model.User;
import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;
import java.util.List;

/**
 * Legacy UserRepository — UNSAFE: uses string-concatenated SQL (SQL injection
 * risk).
 * 
 * This class is intentionally written in a legacy style for demonstration
 * purposes.
 * IBM Bob will be used to modernize this to use parameterized queries.
 */
@Repository
public class UserRepository {

    @Autowired
    private EntityManager entityManager;

    // ⚠️ UNSAFE: SQL injection vulnerability — string concatenation
    public List<User> findByUsername(String username) {
        String sql = "SELECT * FROM users WHERE username = '" + username + "'";
        Query query = entityManager.createNativeQuery(sql, User.class);
        return query.getResultList();
    }

    // ⚠️ UNSAFE: another SQL injection risk
    public List<User> searchUsers(String searchTerm) {
        String sql = "SELECT * FROM users WHERE name LIKE '%" + searchTerm + "%'";
        Query query = entityManager.createNativeQuery(sql, User.class);
        return query.getResultList();
    }

    // ⚠️ LEGACY: uses old Date API
    public void updateLastLogin(Long userId) {
        java.util.Date loginTime = new java.util.Date();
        String sql = "UPDATE users SET last_login = '" + loginTime + "' WHERE id = " + userId;
        entityManager.createNativeQuery(sql).executeUpdate();
    }
}
