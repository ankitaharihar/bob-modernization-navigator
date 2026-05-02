package com.example.controller;

import com.example.model.User;
import com.example.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Legacy UserController — has permissive CORS (@CrossOrigin("*")).
 * IBM Bob will restrict this to known trusted origins.
 */
@RestController
@RequestMapping("/api/users")
@CrossOrigin("*")   // ⚠️ UNSAFE: allows any origin
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping("/search")
    public List<User> search(@RequestParam String q) {
        return userService.searchUsers(q);
    }

    @GetMapping("/{username}")
    public User getByUsername(@PathVariable String username) {
        return userService.findByUsername(username);
    }
}
