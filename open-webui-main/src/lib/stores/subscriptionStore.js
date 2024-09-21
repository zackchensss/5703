import { writable } from 'svelte/store';

export const subscriptionStatus = writable("");
export const message = writable("");

// Function to check subscription status
export async function checkSubscriptionStatus() {
    try {
      //const token = localStorage.token;
      const response = await fetch("http://localhost:8080/api/subscription/status", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      });
  
      if (response.ok) {
        return await response.json(); // Return the JSON response
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }
    } catch (error) {
      throw new Error("An error occurred!");
    }
  }
  
