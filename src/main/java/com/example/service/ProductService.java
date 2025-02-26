package com.example.service;

import com.example.model.Product;
import com.example.repository.ProductRepository;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.UUID;

@Service
public class ProductService extends MainService<Product> {

    private final ProductRepository productRepository;

    // Constructor-based Dependency Injection
    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public ArrayList<Product> getProducts() {
        return productRepository.getProducts();
    }

    public Product getProductById(UUID productId) {
        return productRepository.getProductById(productId);
    }

    public Product addProduct(Product product) {
        return  productRepository.addProduct(product);
    }

    public Product updateProduct(UUID productId, String newName, double newPrice)
    {
        return productRepository.updateProduct( productId,  newName,  newPrice);
    }

    public void applyDiscount(double discount, ArrayList<UUID> productIds)
    {
        productRepository.applyDiscount(discount,productIds);
    }
    public void deleteProductById(UUID productId){
        productRepository.deleteProduct(productId);
    }


}
