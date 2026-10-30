function switchCustomerTab(tabId, btnElement) {
    const buttons = document.querySelectorAll('.c-tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    btnElement.classList.add('active');

    const contents = document.querySelectorAll('.c-tab-content');
    contents.forEach(content => content.classList.remove('active'));

    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add('active');
    }
}

function showCustomerDetail(customerId) {
    if (customerId) {
        window.location.href = `/khach-hang/?view=detail&id=${customerId}`;
    }
}

function showAddCustomerForm() {
    window.location.href = '/khach-hang/?view=add';
}

function showCustomerMain() {
    window.location.href = '/khach-hang/';
}   