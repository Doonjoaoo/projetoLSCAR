// Confirmação antes de excluir
// ...existing code...
function confirmarExclusao(id, nome) {
    if (confirm(`Tem certeza que deseja excluir o endereço de ${nome}?`)) {
        // redireciona para a rota de exclusão (GET). Preferível usar POST/CSRF em produção.
        window.location.href = `/excluir/${id}`;
    }
    return false;
}
// ...existing code...

// ------------------------------
// Filtro estilo Excel com checkboxes
// ------------------------------

function coletarValoresUnicos(colIndex) {
    const valores = new Set();
    const linhas = document.querySelectorAll('#tabela-enderecos tbody tr');
    linhas.forEach(tr => {
        const tds = tr.getElementsByTagName('td');
        if (tds[colIndex]) valores.add(tds[colIndex].textContent.trim());
    });
    return Array.from(valores).sort((a,b)=>a.localeCompare(b));
}

function construirMenu(menuEl, colIndex) {
    menuEl.innerHTML = '';
    const valores = coletarValoresUnicos(colIndex);

    // Ações
    const actions = document.createElement('div');
    actions.className = 'actions';
    const btnSelectAll = document.createElement('button');
    btnSelectAll.type = 'button';
    btnSelectAll.textContent = 'Selecionar tudo';
    const btnClear = document.createElement('button');
    btnClear.type = 'button';
    btnClear.textContent = 'Limpar';
    actions.appendChild(btnSelectAll);
    actions.appendChild(btnClear);
    menuEl.appendChild(actions);

    const search = document.createElement('input');
    search.type = 'text';
    search.placeholder = 'Pesquisar...';
    search.style.width = '100%';
    search.style.marginBottom = '6px';
    menuEl.appendChild(search);

    const container = document.createElement('div');
    valores.forEach(valor => {
        const id = `f-${colIndex}-${valor}`;
        const label = document.createElement('label');
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = true;
        cb.dataset.value = valor;
        cb.dataset.col = String(colIndex);
        label.appendChild(cb);
        label.appendChild(document.createTextNode(' ' + valor));
        container.appendChild(label);
    });
    menuEl.appendChild(container);

    // Eventos
    btnSelectAll.onclick = () => container.querySelectorAll('input[type="checkbox"]').forEach(c=>c.checked=true);
    btnClear.onclick = () => container.querySelectorAll('input[type="checkbox"]').forEach(c=>c.checked=false);
    search.oninput = () => {
        const q = search.value.toLowerCase();
        container.querySelectorAll('label').forEach(l => {
            const text = l.textContent.toLowerCase();
            l.style.display = text.includes(q) ? '' : 'none';
        });
    };

    menuEl.onchange = aplicarFiltrosExcel;
}

function abrirFiltro(button) {
    fecharTodosMenus();
    const th = button.parentElement;
    const colIndex = Number(th.dataset.col);
    const menu = th.querySelector('.filter-menu');
    construirMenu(menu, colIndex);
    menu.style.left = (button.offsetLeft) + 'px';
    menu.style.top = (button.offsetTop + button.offsetHeight + 4) + 'px';
    menu.style.display = 'block';
    button.classList.add('active');
}

function fecharTodosMenus() {
    document.querySelectorAll('.filter-menu').forEach(m => m.style.display = 'none');
    document.querySelectorAll('.filter-trigger').forEach(b => b.classList.remove('active'));
}

document.addEventListener('click', (e) => {
    if (!e.target.closest('.filter-menu') && !e.target.classList.contains('filter-trigger')) {
        fecharTodosMenus();
    }
});

// Acessibilidade básica: fechar no ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') fecharTodosMenus();
});

function aplicarFiltrosExcel() {
    const filtrosPorColuna = new Map();
    document.querySelectorAll('.filter-menu').forEach(menu => {
        if (menu.style.display === 'none' || menu.children.length === 0) return;
        const col = Number(menu.dataset.col);
        const selecionados = Array.from(menu.querySelectorAll('input[type="checkbox"]'))
            .filter(cb => cb.checked)
            .map(cb => cb.dataset.value);
        filtrosPorColuna.set(col, selecionados);
    });

    const linhas = document.querySelectorAll('#tabela-enderecos tbody tr');
    linhas.forEach(tr => {
        const tds = tr.getElementsByTagName('td');
        let visivel = true;
        filtrosPorColuna.forEach((selecionados, col) => {
            const valor = (tds[col] ? tds[col].textContent.trim() : '');
            if (selecionados.length > 0 && !selecionados.includes(valor)) {
                visivel = false;
            }
        });
        tr.style.display = visivel ? '' : 'none';
    });
}

function resetarFiltrosExcel() {
    fecharTodosMenus();
    const linhas = document.querySelectorAll('#tabela-enderecos tbody tr');
    linhas.forEach(tr => tr.style.display = '');
}
