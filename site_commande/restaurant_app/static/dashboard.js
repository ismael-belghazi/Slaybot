async function fetchOrders() {
    const response = await fetch('/api/orders');
    const orders = await response.json();
    const tbody = document.querySelector('#orders-table tbody');
    tbody.innerHTML = '';

    orders.forEach(order => {
        const tr = document.createElement('tr');

        const platCounts = {};
        order.plats.forEach(p => {
            platCounts[p] = (platCounts[p] || 0) + 1;
        });

        const platsText = Object.entries(platCounts)
            .map(([name, qty]) => `${name} x${qty}`)
            .join(', ');

        tr.innerHTML = `
            <td>${order.table_number}</td>
            <td>${platsText}</td>
            <td>${order.status}</td>
            <td>
                ${
                    order.status !== 'PRÊT'
                    ? `<button class="action-btn ready" onclick="markReady(${order.table_number})">Marquer prêt</button>`
                    : `<span class="status-ready">PRÊT</span>`
                }
            </td>
        `;

        tbody.appendChild(tr);
    });
}

async function markReady(table) {
    await fetch(`/api/orders/${table}/ready`, { method: 'POST' });
    fetchOrders();
}

setInterval(fetchOrders, 3000);
fetchOrders();