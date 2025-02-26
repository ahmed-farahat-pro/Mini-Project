package com.example.service;

import com.example.model.Order;
import com.example.repository.OrderRepository;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class OrderService  extends  MainService<Order>{
    private final OrderRepository orderRepository ;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }


    public ArrayList<Order> getOrders(){
        return orderRepository.getOrders();
    }

    public Order getOrderById(UUID orderId){
        return orderRepository.getOrderById(orderId);
    }

    public List<Order> getOrdersByUserId(UUID userId) {
        return orderRepository.getOrdersByUserId(userId);
    }

    public void addOrder(Order order) {
        orderRepository.addOrder(order);
    }


    public void deleteOrderById(UUID orderId) throws IllegalArgumentException{
orderRepository.deleteOrderById(orderId);
    }

}
