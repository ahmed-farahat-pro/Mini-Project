package com.example.repository;

import com.example.model.User;
import com.example.model.Order;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Repository
public class UserRepository extends MainRepository<User> {
    public UserRepository() {
    }
    @Override
    protected String getDataPath() {
        return "src/main/java/com/example/data/users.json"; // Path to the JSON file
    }

    @Override
    protected Class<User[]> getArrayType() {
        return User[].class; // Defines how to deserialize JSON into a User array
    }

    // Retrieve all users
    public ArrayList<User> getUsers() {
        return findAll();
    }

    // Retrieve a user by ID
    public User getUserById(UUID userId) {
        return findAll().stream()
                .filter(user -> user.getId().equals(userId))
                .findFirst()
                .orElse(null);
    }

    // Add a new user
    public User addUser(User user) {

        save(user);
        return user;

    }

    // Delete a user by ID
    public void deleteUserById(UUID userId) {
        ArrayList<User> users = findAll();
        boolean removed = users.removeIf(user -> user.getId().equals(userId));
        if (removed) {
            saveAll(users);
        }

    }

    public List<Order> getOrdersByUserId(UUID userId) {
        User user = findAll().stream()
                .filter(u -> u.getId().equals(userId))
                .findFirst()
                .orElse(null);

        return (user != null) ? user.getOrders() : new ArrayList<>();
    }


    public void addOrderToUser(UUID userId, Order order) {
        List<User> users = findAll();
        for (User user : users) {
            if (user.getId().equals(userId)) {
                order.setId(UUID.randomUUID()); // Generate order ID
                user.getOrders().add(order);
                saveAll((ArrayList<User>) users); // Save updated list
                return;
            }
        }
    }


    public void removeOrderFromUser(UUID userId, UUID orderId) {
        List<User> users = findAll();
        for (User user : users) {
            if (user.getId().equals(userId)) {
                user.getOrders().removeIf(order -> order.getId().equals(orderId));
                saveAll((ArrayList<User>) users); // Save updated list
                return;
            }
        }
    }
}
