function updatePaymentTimeToExpiration() {
        const orderTimeElement = document.querySelectorAll('[data-order-id]');
        orderTimeElement.forEach((element) => {
            const orderId = element.dataset.orderId;
            fetch(`/user/orders/payment/expiration/${orderId}/`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        showNotification(data.error, false);
                        window.location.href = '/user/orders/history/';
                    } else {
                        element.innerText = data.time_to_expiration;
                    }
                })
                .catch((error) => {
                    console.error(error);
                });
        });
    }

    setInterval(updatePaymentTimeToExpiration, 1000); // 1000 ms
