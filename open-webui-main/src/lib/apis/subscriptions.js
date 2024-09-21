// src/lib/apis/subscriptions.js

export async function getCurrentSubscription() {
    try {
        const response = await fetch("http://localhost:8080/api/subscription/status", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
        });
        if (!response.ok) {
            throw new Error('Failed to fetch current subscription');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching current subscription:', error);
        throw error;
    }
}

export async function getSubscriptionHistory() {
    // Implement if there is a corresponding endpoint in main.py
    try {
        const response = await fetch("http://localhost:8080/api/subscription/status", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
        });// Update this endpoint if necessary
        if (!response.ok) {
            throw new Error('Failed to fetch subscription history');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching subscription history:', error);
        throw error;
    }
}
