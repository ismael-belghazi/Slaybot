async function loadMenu() {
    const response = await fetch('/api/menu');
    const data = await response.json();

    const menuDiv = document.getElementById('menu');
    menuDiv.innerHTML = '';

    for (const category in data) {
        const section = document.createElement('div');
        section.className = 'menu-section';

        const title = document.createElement('h3');
        title.textContent = category;
        section.appendChild(title);

        data[category].forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'menu-item';

            itemDiv.innerHTML = `
                <div class="item-info">
                    <img src="${item.image}" 
                        alt="${item.name}" 
                        class="item-img"
                        onerror="this.onerror=null;this.src='/static/images/placeholder.jpg';">
                    <span>${item.name} - ${item.price}€</span>
                </div>
                <div class="quantity-controls">
                    <button type="button" class="qty-btn" data-action="decrease">-</button>
                    <input type="number" class="qty" value="0" min="0">
                    <button type="button" class="qty-btn" data-action="increase">+</button>
                </div>
            `;

            section.appendChild(itemDiv);
        });

        menuDiv.appendChild(section);
    }

    document.querySelectorAll('.qty-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            const input = e.target.parentElement.querySelector('.qty');
            let val = parseInt(input.value);
            if (e.target.dataset.action === 'increase') val++;
            if (e.target.dataset.action === 'decrease' && val > 0) val--;
            input.value = val;
        });
    });
}

document.getElementById('order-form').addEventListener('submit', async function(e){
    e.preventDefault();

    const items = document.querySelectorAll('.menu-item');
    const plats = [];

    items.forEach(item => {
        const qty = parseInt(item.querySelector('.qty').value);
        const name = item.querySelector('span').textContent.split(' - ')[0];
        if (qty > 0) {
            for (let i = 0; i < qty; i++) plats.push(name);
        }
    });

    const table = new URLSearchParams(window.location.search).get('table');

    if (plats.length === 0) {
        document.getElementById('status').textContent = "Veuillez sélectionner au moins un produit";
        return;
    }

    const response = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table, plats })
    });

    const data = await response.json();
    const status = document.getElementById('status');

    if (data.success) {
        status.textContent = "Commande envoyée";
        document.getElementById('order-form').reset();
    } else {
        status.textContent = "Erreur : " + data.error;
    }
});

loadMenu();