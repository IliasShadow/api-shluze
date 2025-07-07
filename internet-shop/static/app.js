document.addEventListener("DOMContentLoaded", () => {
    const productsContainer = document.getElementById('products');
    const cartItems = document.getElementById('cart-items');
    const cartModal = document.getElementById('cart-modal');

    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user') || 'default_user';

    function getCurrentUserId() {
        return userId;
    }

    fetch('/products')
        .then(res => res.json())
        .then(products => {
            for (const id in products) {
                const p = products[id];
                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    <strong>${p.name}</strong><br>
                    Цена: ${p.price} руб<br>
                    <button onclick="addToCart('${id}', '${userId}')">Добавить в корзину</button>
                    <div id="toast-${id}" class="toast" style="display:none;">Добавлено!</div>
                `;
                productsContainer.appendChild(card);
            }
        });

    window.addToCart = function(productId, userId) {
        fetch('/add_to_cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, product_id: productId, quantity: 1 })
        }).then(() => showAddedToast(productId));
    };

    function showAddedToast(id) {
        const toast = document.getElementById(`toast-${id}`);
        toast.style.display = 'block';
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.style.display = 'none', 1000);
        }, 2000);
    }

    window.showCart = function() {
        fetch(`/cart/${userId}`)
            .then(res => res.json())
            .then(cart => {
                cartItems.innerHTML = '';
                if (Object.keys(cart).length === 0) {
                    cartItems.innerHTML = '<li>Корзина пуста</li>';
                } else {
                    for (const pid in cart) {
                        const item = cart[pid];
                        cartItems.innerHTML += `<li>${item.name} — ${item.quantity} шт.</li>`;
                    }
                }
                cartModal.style.display = 'block';
            });
    }

    window.hideCart = function() {
        cartModal.style.display = 'none';
    }
});