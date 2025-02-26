package com.example.repository;

import com.example.model.Product;
import org.springframework.stereotype.Repository;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Repository
@SuppressWarnings("rawtypes")
public class ProductRepository extends MainRepository<Product> {
    public ProductRepository() {}
    public static List<Product> products = new ArrayList<>();

    @Override
    protected String getDataPath() {
        return "src/main/java/com/example/data/products.json"; // JSON file path for products
    }

    @Override
    protected Class<Product[]> getArrayType() {
        return Product[].class; // Deserialize JSON into Product array
    }

    // Retrieve all products
    public ArrayList<Product> getProducts() {
        return findAll();
    }

    // Retrieve product by ID
    public Product getProductById(UUID productId) {
        return findAll().stream()
                .filter(product -> product.getId().equals(productId))
                .findFirst()
                .orElse(null);
    }

    // Add a new product
    public Product addProduct(Product product) {

        save(product);
        return product;
    }

    // Delete a product by ID
    public void deleteProduct(UUID productId) {
        ArrayList<Product> products = findAll();
        boolean removed = products.removeIf(product -> product.getId().equals(productId));
        if (removed) {
            saveAll(products);
        }

    }



    public Product updateProduct(UUID productId, String newName, double newPrice) {
        ArrayList<Product> products = findAll();
        for (Product product : products) {
            if (product.getId().equals(productId)) {
                product.setName(newName);
                product.setPrice(newPrice);
                saveAll(products);
                return product;
            }
        }
        return null; // Return null if product is not found
    }


    public void applyDiscount(double discount, ArrayList<UUID> productIds) {
        if (discount < 0 || discount > 100) {
            throw new IllegalArgumentException("Discount must be between 0 and 100");
        }

        List<Product> products = findAll();
        for (Product product : products) {
            if (productIds.contains(product.getId())) {
                double newPrice = product.getPrice() * (1 - (discount / 100));
                product.setPrice(newPrice);
            }
        }
        saveAll((ArrayList<Product>) products); // Save the updated product list
    }
}
