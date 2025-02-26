package com.example.model;

import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Component
public class Order {
    private UUID id;
    private UUID userId;
    private double totalPrice;
    private List<Product> products = new ArrayList<>();

    public Order() {
    }

    // 2️⃣ Constructor with all fields including UUID
    public Order(UUID id, UUID userId, double totalPrice, List<Product> products) {
        this.id = id;
        this.userId = userId;
        this.totalPrice = totalPrice;
        this.products = products;
    }

    // 3️⃣ Constructor without UUID (UUID is generated automatically)
    public Order(UUID userId, double totalPrice, List<Product> products) {
        this.id = UUID.randomUUID();
        this.userId = userId;
        this.totalPrice = totalPrice;
        this.products = products;
    }

    // Getters
    public UUID getId() {
        return id;
    }

    public UUID getUserId() {
        return userId;
    }

    public double getTotalPrice() {
        return totalPrice;
    }

    public List<Product> getProducts() {
        return products;
    }

    // Setters
    public void setId(UUID id) {
        this.id = id;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public void setTotalPrice(double totalPrice) {
        this.totalPrice = totalPrice;
    }

    public void setProducts(List<Product> products) {
        this.products = products;
    }

    // Method to calculate total price based on product prices
    public void calculateTotalPrice() {
        this.totalPrice = products.stream().mapToDouble(Product::getPrice).sum();
    }
}
