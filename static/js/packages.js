function hideAllViews() {
    const views = [
        'view-list',
        'view-add',
        'view-edit',
        'view-detail',
        'reg-step-1',
        'reg-step-2',
        'reg-step-3'
    ];

    views.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.display = 'none';
        }
    });
}

function showPackageList() {
    window.location.href = '/goi-tap/';
}

function showAddPackage() {
    window.location.href = '/goi-tap/?view=add';
}

function showEditPackage(id) {
    if (id) {
        window.location.href = `/goi-tap/?view=edit&id=${id}`;
    }
}

function showPackageDetail(id) {
    if (id) {
        window.location.href = `/goi-tap/?view=detail&id=${id}`;
    }
}

function showDeletePopup(id, tenGoi) {
    const popup = document.getElementById('popup-delete');
    const deleteForm = document.getElementById('delete-form');
    const deleteMessage = document.getElementById('delete-message');

    if (popup && deleteForm) {
        popup.style.display = 'flex';
        deleteForm.action = `/goi-tap/xoa/${id}/`;
    }

    if (deleteMessage && tenGoi) {
        deleteMessage.textContent = `Bạn có chắc chắn muốn xóa gói tập "${tenGoi}" không?`;
    }
}

function hideDeletePopup() {
    const popup = document.getElementById('popup-delete');
    if (popup) {
        popup.style.display = 'none';
    }
}

function showRegStep1() {
    hideAllViews();
    const el = document.getElementById('reg-step-1');
    if (el) el.style.display = 'block';
}

function showRegStep2() {
    hideAllViews();
    const el = document.getElementById('reg-step-2');
    if (el) el.style.display = 'block';
}

function showRegStep3() {
    hideAllViews();
    const el = document.getElementById('reg-step-3');
    if (el) el.style.display = 'block';
}

function finishRegistration() {
    alert("Xác nhận tạo và đăng ký gói tập thành công!");
    showPackageList();
}
function showAddCustomerForm() {
    window.location.href = '/khach-hang/?view=add';
}

function showCustomerMain() {
    window.location.href = '/khach-hang/';
}