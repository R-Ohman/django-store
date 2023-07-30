function updateDiscountTimeToExpiration() {
        const discountTimeElements = document.querySelectorAll('.product-discount-time-to-expiration');
        discountTimeElements.forEach((element) => {
            const productId = element.dataset.productId;
            fetch(`/products/discount_expiration/${productId}/`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        console.error(data.error);
                    } else {
                        element.innerText = data.time_to_expiration;
                    }
                })
                .catch((error) => {
                    console.error(error);
                });
        });
    }

    setInterval(updateDiscountTimeToExpiration, 1000); // 1000 ms
