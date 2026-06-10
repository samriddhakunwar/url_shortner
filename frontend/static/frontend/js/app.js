/**
 * app.js — URL Shortener Frontend Core
 * =====================================
 * Provides:
 *   - JWT token management (localStorage)
 *   - Authenticated fetch() wrapper (apiRequest)
 *   - Toast notification system
 *   - Button loading state helpers
 *   - Clipboard copy helper
 *   - Date/text formatting utilities
 *   - Auth guards (requireAuth / redirectIfLoggedIn)
 *   - Sidebar mobile toggle
 *   - Active nav-item highlighting
 */

'use strict';

/* ─── Storage Keys ──────────────────────────────────────────────────────── */
const KEYS = { access: 'ls_access', refresh: 'ls_refresh' };

/* ─── Token Management ──────────────────────────────────────────────────── */
const Auth = {
  getAccess  : ()        => localStorage.getItem(KEYS.access),
  getRefresh : ()        => localStorage.getItem(KEYS.refresh),
  setTokens  : (a, r)   => {
    localStorage.setItem(KEYS.access, a);
    if (r) localStorage.setItem(KEYS.refresh, r);
  },
  clear      : ()        => {
    localStorage.removeItem(KEYS.access);
    localStorage.removeItem(KEYS.refresh);
  },
  isLoggedIn : ()        => !!localStorage.getItem(KEYS.access),
};

/* ─── API Request Wrapper ───────────────────────────────────────────────── */
/**
 * Authenticated fetch wrapper.
 * Automatically attaches Authorization: Bearer header.
 * On 401, clears tokens and redirects to login.
 *
 * @param {string} endpoint  - Path relative to /api (e.g. '/urls/')
 * @param {object} options   - Standard fetch init options
 * @returns {Response|null}
 */
async function apiRequest(endpoint, options = {}) {
  const token = Auth.getAccess();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const res = await fetch(`/api${endpoint}`, { ...options, headers });

    if (res.status === 401) {
      Auth.clear();
      const next = encodeURIComponent(window.location.pathname);
      window.location.href = `/login/?next=${next}`;
      return null;
    }

    return res;
  } catch (err) {
    showToast('Network error — please check your connection.', 'error');
    throw err;
  }
}

/* ─── Toast Notifications ───────────────────────────────────────────────── */
/**
 * Display a slide-in toast notification.
 * @param {string} message
 * @param {'success'|'error'|'warning'|'info'} type
 */
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  const id    = 'toast-' + Date.now();

  const el = document.createElement('div');
  el.id        = id;
  el.className = `toast-item toast-${type}`;
  el.innerHTML = `
    <span class="toast-icon">${icons[type] || '●'}</span>
    <span class="toast-msg">${escapeHtml(message)}</span>
    <button class="toast-close" onclick="document.getElementById('${id}')?.remove()">×</button>
  `;

  container.appendChild(el);
  requestAnimationFrame(() => el.classList.add('show'));

  setTimeout(() => {
    el.classList.remove('show');
    el.classList.add('hide');
    setTimeout(() => el.remove(), 350);
  }, 4500);
}

/* ─── Button Loading State ──────────────────────────────────────────────── */
/**
 * Toggle a button between normal and loading states.
 * @param {HTMLButtonElement} btn
 * @param {boolean} loading
 * @param {string} text   Label shown while loading
 */
function setLoading(btn, loading, text = 'Loading…') {
  if (loading) {
    btn._orig    = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="btn-spin"></span>${text}`;
  } else {
    btn.disabled  = false;
    btn.innerHTML = btn._orig || btn.innerHTML;
  }
}

/* ─── Clipboard ─────────────────────────────────────────────────────────── */
/**
 * Copy text to clipboard and give visual feedback on a button.
 * @param {string}      text
 * @param {HTMLElement} btn  (optional) — button to show "Copied!" on
 */
async function copyText(text, btn) {
  try {
    await navigator.clipboard.writeText(text);
    if (btn) {
      const orig = btn.textContent;
      btn.textContent = 'Copied!';
      btn.classList.add('btn-success');
      setTimeout(() => {
        btn.textContent = orig;
        btn.classList.remove('btn-success');
      }, 2000);
    }
    return true;
  } catch {
    showToast('Copy failed — please copy manually.', 'error');
    return false;
  }
}

/* ─── Formatting Helpers ────────────────────────────────────────────────── */
function fmtDate(str) {
  if (!str) return '—';
  return new Date(str).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

function fmtDateTime(str) {
  if (!str) return '—';
  return new Date(str).toLocaleString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function truncate(str, n = 55) {
  if (!str) return '';
  return str.length > n ? str.slice(0, n) + '…' : str;
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

/** Returns true if the given ISO date string is in the past. */
function isExpired(expiresAt) {
  if (!expiresAt) return false;
  return new Date(expiresAt) < new Date();
}

/** Build a status badge HTML string. */
function statusBadge(expiresAt) {
  if (isExpired(expiresAt)) return '<span class="badge badge-danger">Expired</span>';
  return '<span class="badge badge-success">Active</span>';
}

/* ─── Auth Guards ───────────────────────────────────────────────────────── */
/** Redirect to login if no access token exists. Call at top of protected pages. */
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    const next = encodeURIComponent(window.location.pathname);
    window.location.href = `/login/?next=${next}`;
  }
}

/** Redirect away from auth pages if already logged in. */
function redirectIfLoggedIn() {
  if (Auth.isLoggedIn()) window.location.href = '/';
}

/* ─── Logout ────────────────────────────────────────────────────────────── */
async function doLogout() {
  const refresh = Auth.getRefresh();
  if (refresh) {
    try {
      // Attempt to blacklist the refresh token
      await apiRequest('/auth/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh }),
      });
    } catch { /* ignore network errors on logout */ }
  }
  Auth.clear();
  window.location.href = '/login/';
}

/* ─── Load & Display Current User ──────────────────────────────────────── */
async function loadUserInfo() {
  const nameEl   = document.getElementById('user-display');
  const avatarEl = document.getElementById('user-avatar');
  if (!nameEl) return;

  try {
    const res = await apiRequest('/auth/me/');
    if (res && res.ok) {
      const data = await res.json();
      const name = data.username || data.email || 'User';
      nameEl.textContent   = name;
      if (avatarEl) avatarEl.textContent = name.charAt(0).toUpperCase();
    }
  } catch { /* silent */ }
}

/* ─── Delete Confirmation Modal ─────────────────────────────────────────── */
let _deleteCallback = null;

function openDeleteModal(onConfirm) {
  _deleteCallback = onConfirm;
  document.getElementById('delete-modal')?.classList.add('show');
}

function closeDeleteModal() {
  _deleteCallback = null;
  document.getElementById('delete-modal')?.classList.remove('show');
}

/* ─── Form Field Error Helpers ──────────────────────────────────────────── */
function showFieldError(fieldId, message) {
  const field = document.getElementById(fieldId);
  const errEl = document.getElementById(fieldId + '-error');
  if (field) field.classList.add('is-invalid');
  if (errEl) { errEl.textContent = message; errEl.style.display = 'block'; }
}

function clearFieldErrors(formEl) {
  formEl.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  formEl.querySelectorAll('.field-error').forEach(el => {
    el.textContent = ''; el.style.display = 'none';
  });
}

/** Parse DRF validation error response into { field: message } map. */
async function parseApiErrors(res) {
  try {
    const data = await res.json();
    return data;
  } catch { return {}; }
}

/* ─── DOMContentLoaded — Global Setup ──────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {

  /* Sidebar mobile toggle */
  document.getElementById('sidebar-toggle')?.addEventListener('click', () => {
    document.getElementById('sidebar')?.classList.toggle('open');
  });

  /* Close sidebar on overlay click (mobile) */
  document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const toggle  = document.getElementById('sidebar-toggle');
    if (sidebar?.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        e.target !== toggle) {
      sidebar.classList.remove('open');
    }
  });

  /* Highlight active nav item based on current path */
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item[data-path]').forEach(item => {
    const itemPath = item.dataset.path;
    const isActive = itemPath === '/'
      ? path === '/'
      : path.startsWith(itemPath);
    if (isActive) item.classList.add('active');
  });

  /* Wire up logout button */
  document.getElementById('logout-btn')?.addEventListener('click', doLogout);

  /* Wire up delete modal confirm button */
  document.getElementById('confirm-delete-btn')?.addEventListener('click', async () => {
    if (typeof _deleteCallback === 'function') {
      await _deleteCallback();
    }
    closeDeleteModal();
  });

  /* Close modal on overlay backdrop click */
  document.getElementById('delete-modal')?.addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeDeleteModal();
  });
});
