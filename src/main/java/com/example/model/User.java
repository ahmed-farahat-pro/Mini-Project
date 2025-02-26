package com.example.model;

import org.springframework.stereotype.Component;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Component
public class User {
    private UUID id;
    private String name;
    private List<Order> orders = new ArrayList<>();

    // Default constructor
    public User() {
    }
    public User(String name, List<Order> orders) {
        this.id = UUID.randomUUID();
        this.name = name;
        this.orders = orders;
    }
    // Parameterized constructor
    public User(UUID id, String name, List<Order> orders) {
        this.id = id;
        this.name = name;
        this.orders = orders;
    }

    // Getters
    public UUID getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public List<Order> getOrders() {
        return orders;
    }

    // Setters
    public void setId(UUID id) {
        this.id = id;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setOrders(List<Order> orders) {
        this.orders = orders;
    }
}
