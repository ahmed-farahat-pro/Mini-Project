package com.example.repository;

import com.example.model.Cart;
import com.example.model.Product;
import org.springframework.stereotype.Repository;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Repository
@SuppressWarnings("rawtypes")
public class CartRepository extends MainRepository<Cart> {

    private static final List<Cart> carts = new ArrayList<>();
    public CartRepository(){
    }
    @Override
    protected String getDataPath() {
        return "src/main/java/com/example/data/carts.json"; // JSON file path for carts
    }

    @Override
    protected Class<Cart[]> getArrayType() {
        return Cart[].class; // Deserialize JSON into Cart array
    }

    // Retrieve all carts
    public ArrayList<Cart> getCarts() {
        return findAll();
    }

    // Retrieve a cart by ID
    public Cart getCartById(UUID cartId) {
        return findAll().stream()
                .filter(cart -> cart.getId().equals(cartId))
                .findFirst()
                .orElse(null);
    }

    // Retrieve a cart by User ID
    public Cart getCartByUserId(UUID userId) {
        return findAll().stream()
                .filter(cart -> cart.getUserId().equals(userId))
                .findFirst()
                .orElse(null);
    }

    // Add a new cart
    public Cart addCart(Cart cart) {

        save(cart);
        return cart;
    }

    // Delete a cart by ID
    public boolean deleteCart(UUID cartId) {
        ArrayList<Cart> carts = findAll();
        boolean removed = carts.removeIf(cart -> cart.getId().equals(cartId));
        if (removed) {
            saveAll(carts);
        }
        return removed;
    }

    // Update an existing cart
    public boolean updateCart(Cart updatedCart) {
        ArrayList<Cart> carts = findAll();
        for (int i = 0; i < carts.size(); i++) {
            if (carts.get(i).getId().equals(updatedCart.getId())) {
                carts.set(i, updatedCart);
                saveAll(carts);
                return true;
            }
        }
        return false;
    }
    public void addProductToCart(UUID cartId, Product product) {
        ArrayList<Cart> carts = findAll();
        for (Cart cart : carts) {
            if (cart.getId().equals(cartId)) {
                cart.getProducts().add(product); // Add product to cart
                saveAll(carts);
                return;
            }
        }
        throw new IllegalArgumentException("Cart with ID " + cartId + " not found.");
    }


    public void deleteProductFromCart(UUID cartId, UUID productId) {
        ArrayList<Cart> carts = findAll();
        for (Cart cart : carts) {
            if (cart.getId().equals(cartId)) {
                boolean removed = cart.getProducts().removeIf(product -> product.getId().equals(productId));
                if (removed) {
                    saveAll(carts);
                    return;
                }
                throw new IllegalArgumentException("Product with ID " + productId + " not found in cart.");
            }
        }
        throw new IllegalArgumentException("Cart with ID " + cartId + " not found.");
    }
}
