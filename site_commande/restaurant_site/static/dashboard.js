// =========================
// DASHBOARD TEMPS RÉEL (WEBSOCKET)
// =========================
const socket = io.connect(location.origin);

socket.on('connect', () => {
    console.log('Dashboard connecté au serveur WebSocket.');
    socket.emit('join_dashboard');
});

socket.on('join_error', data => {
    console.error('Erreur dashboard:', data.message);
});

// =========================
// TABLE THEMES
// =========================
const tableThemes = {
    1: { bg: '#6b0000', menu: '#a00000' },
    2: { bg: '#004d00', menu: '#007f00' },
    3: { bg: '#996600', menu: '#cc9900' },
    4: { bg: '#00194d', menu: '#0033a0' }
};

// =========================
// RENDER ORDERS
// =========================
function renderOrders(orders) {
    const ordersBody = document.getElementById('orders-body');
    const summaryBody = document.getElementById('summary-body');
    if (!ordersBody || !summaryBody) return;

    ordersBody.innerHTML = '';
    summaryBody.innerHTML = '';

    const summary = {};

    orders.forEach(order => {
        if (!order || !order.table || !order.plats) return;

        const status = (order.status || 'EN_ATTENTE').toLowerCase();
        if (status === 'cancelled' || status === 'payee') return;

        const theme = tableThemes[order.table] || { bg: '#fff', menu: '#000' };
        const tr = document.createElement('tr');
        tr.classList.add('order-row');
        tr.style.backgroundColor = theme.bg;
        tr.style.color = theme.menu;

        // Compter les plats
        const platsCount = {};
        order.plats.forEach(p => platsCount[p] = (platsCount[p] || 0) + 1);
        const platsDisplay = Object.entries(platsCount)
            .map(([plat, qty]) => `${qty}x ${plat}`).join(', ');

        // Couleur du statut
        const statusColors = { 'en_attente': '#ffcc00', 'pret': '#00ff00', 'prêt': '#00ff00', 'preparation': '#ffaa00' };
        const statusColor = statusColors[status] || theme.menu;

        tr.innerHTML = `
            <td>${order.table}</td>
            <td>${platsDisplay}</td>
            <td style="color:${statusColor}; font-weight:bold;">${status}</td>
            <td>
                <button class="confirm-btn" data-table="${order.table}">Confirmer</button>
                <button class="cancel-btn" data-table="${order.table}">Annuler</button>
            </td>
        `;
        ordersBody.appendChild(tr);

        // Récapitulatif par table
        if (!summary[order.table]) {
            summary[order.table] = { plats: [], total: 0, ready: true };
        }
        summary[order.table].plats.push(...order.plats);
        summary[order.table].total += order.plats.length * 5; // prix fixe pour simplifier
        if (status !== 'prêt') summary[order.table].ready = false;
    });

    // Générer le tableau récapitulatif
    Object.keys(summary).forEach(table => {
        const theme = tableThemes[table] || { bg: '#fff', menu: '#000' };
        const tr = document.createElement('tr');
        tr.classList.add('summary-row');
        tr.style.backgroundColor = theme.bg;
        tr.style.color = theme.menu;

        const platsCount = {};
        summary[table].plats.forEach(p => platsCount[p] = (platsCount[p] || 0) + 1);
        const platsDisplay = Object.entries(platsCount)
            .map(([plat, qty]) => `${qty}x ${plat}`).join(', ');

        tr.innerHTML = `
            <td>${table}</td>
            <td>${platsDisplay}</td>
            <td>${summary[table].total.toFixed(2)} €</td>
            <td>
                <button class="pay-btn" data-table="${table}" ${!summary[table].ready ? 'disabled' : ''}>Payer</button>
            </td>
        `;
        summaryBody.appendChild(tr);
    });

    bindButtonEvents();
}

// =========================
// BIND BUTTON EVENTS
// =========================
function bindButtonEvents() {
    document.querySelectorAll('.confirm-btn').forEach(btn => {
        btn.onclick = () => {
            btn.disabled = true;
            socket.emit('confirm_order', { table: parseInt(btn.dataset.table) });
        };
    });

    document.querySelectorAll('.cancel-btn').forEach(btn => {
        btn.onclick = () => {
            btn.disabled = true;
            socket.emit('cancel_order', { table: parseInt(btn.dataset.table) });
        };
    });

    document.querySelectorAll('.pay-btn').forEach(btn => {
        btn.onclick = () => {
            btn.disabled = true;
            socket.emit('pay_order', { table: parseInt(btn.dataset.table) });
        };
    });
}

// =========================
// SOCKET EVENTS
// =========================
socket.on('update_orders', data => {
    renderOrders(data);
});

socket.on('disconnect', () => {
    console.warn('Déconnecté du serveur WebSocket. Tentative de reconnexion...');
});

// =========================
// INITIALIZE DASHBOARD
// =========================
document.addEventListener('DOMContentLoaded', () => {
    console.log("Dashboard prêt, WebSocket actif !");
});